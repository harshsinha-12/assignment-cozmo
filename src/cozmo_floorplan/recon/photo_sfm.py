"""Incremental per-room photo SfM with a disclosed handheld-height scale."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import cv2
import numpy as np

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.photos import PhotoRoom
from cozmo_floorplan.recon.photo_feature_ensemble import extract_photo_feature_ensemble
from cozmo_floorplan.recon.photo_features import (
    PhotoCorrespondences,
    PhotoFeatures,
    match_photo_correspondences,
)
from cozmo_floorplan.recon.photos_config import (
    DEFAULT_PHOTO_OVERLAP,
    DEFAULT_PHOTO_SFM,
    PhotoOverlapConfig,
    PhotoSfmConfig,
)
from cozmo_floorplan.recon.video_native_scale import OPENCV_TO_Y_UP
from cozmo_floorplan.recon.video_rooms import VideoRoomCandidate, fit_video_room_candidate
from cozmo_floorplan.utils.point_clouds import voxel_centroids


@dataclass(frozen=True, slots=True)
class PhotoCameraPose:
    """OpenCV world-to-camera pose in the first-camera frame."""

    name: str
    rotation: np.ndarray
    translation: np.ndarray
    image_size_px: tuple[int, int]
    intrinsic_matrix: np.ndarray


@dataclass(frozen=True, slots=True)
class PhotoRoomReconstruction:
    """Metric Manhattan room recovered from a connected photo graph."""

    identifier: str
    room: VideoRoomCandidate
    points_m: np.ndarray
    camera_positions_m: np.ndarray
    image_count: int
    registered_cameras: int
    triangulated_points: int


def reconstruct_photo_room(
    room: PhotoRoom,
    *,
    overlap_config: PhotoOverlapConfig = DEFAULT_PHOTO_OVERLAP,
    sfm_config: PhotoSfmConfig = DEFAULT_PHOTO_SFM,
) -> PhotoRoomReconstruction:
    """Recover a scaled room envelope from overlapping stills, or refuse."""

    features = {
        frame.path.name: extract_photo_feature_ensemble(frame.path, overlap_config)
        for frame in room.frames
    }
    names = tuple(frame.path.name for frame in room.frames)
    pairs: dict[tuple[str, str], PhotoCorrespondences] = {}
    for left_name, right_name in combinations(names, 2):
        correspondence = _best_correspondence(
            features[left_name], features[right_name], overlap_config
        )
        if correspondence.evidence.geometric_inliers >= sfm_config.minimum_pose_inliers:
            pairs[(left_name, right_name)] = correspondence
    cameras, points = _incremental_sfm(names, pairs, sfm_config)
    yup_points, yup_cameras = _to_y_up(points, cameras)
    scaled_points, scaled_cameras = _apply_handheld_height(
        yup_points, yup_cameras, sfm_config
    )
    indoor = (
        (scaled_points[:, 1] >= -0.3)
        & (scaled_points[:, 1] <= 4.2)
    )
    if int(np.count_nonzero(indoor)) >= 16:
        scaled_points = scaled_points[indoor]
    try:
        fitted = fit_video_room_candidate(scaled_points, scaled_cameras)
    except ReconstructionError as exc:
        raise ReconstructionError(
            f"Photo room {room.identifier!r} recovered {len(cameras)} cameras and "
            f"{len(scaled_points)} points, but they did not support a complete "
            f"floor/wall envelope: {exc}",
            warning_code="low_confidence",
        ) from exc
    return PhotoRoomReconstruction(
        identifier=room.identifier,
        room=fitted,
        points_m=scaled_points,
        camera_positions_m=scaled_cameras,
        image_count=len(room.frames),
        registered_cameras=len(cameras),
        triangulated_points=len(scaled_points),
    )


def _best_correspondence(
    left_variants: tuple[PhotoFeatures, ...],
    right_variants: tuple[PhotoFeatures, ...],
    config: PhotoOverlapConfig,
) -> PhotoCorrespondences:
    candidates = [
        match_photo_correspondences(left, right, config)
        for left, right in zip(left_variants, right_variants, strict=True)
    ]
    return max(
        candidates,
        key=lambda item: (
            item.evidence.geometric_inliers,
            item.evidence.coverage_fraction,
            item.evidence.matches,
        ),
    )


def _incremental_sfm(
    names: tuple[str, ...],
    pairs: dict[tuple[str, str], PhotoCorrespondences],
    config: PhotoSfmConfig,
) -> tuple[dict[str, PhotoCameraPose], np.ndarray]:
    seed = _best_seed_pair(pairs, config)
    if seed is None:
        raise ReconstructionError(
            "Connected photo overlap did not yield a two-view pose with "
            "sufficient parallax; centimetres will not be guessed.",
            warning_code="low_confidence",
        )
    left_name, right_name, correspondence, rotation, translation = seed
    cameras = {
        left_name: PhotoCameraPose(
            left_name,
            np.eye(3),
            np.zeros(3),
            correspondence.left.image_size_px,
            _intrinsic_matrix(correspondence.left.image_size_px, config),
        ),
        right_name: PhotoCameraPose(
            right_name,
            rotation,
            translation.reshape(3),
            correspondence.right.image_size_px,
            _intrinsic_matrix(correspondence.right.image_size_px, config),
        ),
    }
    seeded = _triangulate_pair(
        cameras[left_name],
        cameras[right_name],
        correspondence.left_points_px,
        correspondence.right_points_px,
        config,
    )
    points = [item[0] for item in seeded]
    observations = _observations_from_triangulation(left_name, right_name, seeded)
    remaining = [name for name in names if name not in cameras]
    while remaining:
        progressed = False
        ranked = sorted(
            remaining,
            key=lambda name: _pnp_support(name, cameras, pairs, observations),
            reverse=True,
        )
        for name in ranked:
            pose = _solve_pnp(name, cameras, pairs, observations, config)
            if pose is None:
                continue
            cameras[name] = pose
            remaining.remove(name)
            progressed = True
            for other in list(cameras):
                if other == name:
                    continue
                pair = _pair_lookup(pairs, name, other)
                if pair is None:
                    continue
                triangulated = _triangulate_pair(
                    cameras[pair.left.path.name],
                    cameras[pair.right.path.name],
                    pair.left_points_px,
                    pair.right_points_px,
                    config,
                )
                points.extend(item[0] for item in triangulated)
                _extend_observations(observations, pair, triangulated)
            break
        if not progressed:
            break
    if len(cameras) < 2 or len(points) < 16:
        raise ReconstructionError(
            "Photo SfM registered too few cameras or triangulated points to "
            "authorize centimetres.",
            warning_code="low_confidence",
        )
    cloud = voxel_centroids(np.asarray(points, dtype=np.float64), config.voxel_size_m)
    if len(cloud) < 16:
        raise ReconstructionError(
            "Photo SfM voxels were too sparse to authorize centimetres.",
            warning_code="low_confidence",
        )
    return cameras, cloud


def _best_seed_pair(
    pairs: dict[tuple[str, str], PhotoCorrespondences],
    config: PhotoSfmConfig,
) -> tuple[str, str, PhotoCorrespondences, np.ndarray, np.ndarray] | None:
    ranked: list[tuple[int, float, str, str, PhotoCorrespondences, np.ndarray, np.ndarray]] = []
    for (left_name, right_name), correspondence in pairs.items():
        recovered = _recover_pose(correspondence, config)
        if recovered is None:
            continue
        rotation, translation, inliers, cheirality = recovered
        ranked.append(
            (
                inliers,
                cheirality,
                left_name,
                right_name,
                correspondence,
                rotation,
                translation,
            )
        )
    if not ranked:
        return None
    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    _inliers, _ratio, left_name, right_name, correspondence, rotation, translation = ranked[0]
    return left_name, right_name, correspondence, rotation, translation


def _recover_pose(
    correspondence: PhotoCorrespondences,
    config: PhotoSfmConfig,
) -> tuple[np.ndarray, np.ndarray, int, float] | None:
    left = correspondence.left_points_px
    right = correspondence.right_points_px
    if len(left) < 8:
        return None
    if correspondence.left.image_size_px != correspondence.right.image_size_px:
        return None
    intrinsic = _intrinsic_matrix(correspondence.left.image_size_px, config)
    cv2.setRNGSeed(0)
    essential, mask = cv2.findEssentialMat(
        left.astype(np.float32),
        right.astype(np.float32),
        intrinsic,
        method=cv2.RANSAC,
        prob=0.999,
        threshold=1.0,
    )
    if essential is None or mask is None:
        return None
    supported = int(np.count_nonzero(mask))
    pose_inliers, rotation, translation, pose_mask = cv2.recoverPose(
        essential,
        left.astype(np.float32),
        right.astype(np.float32),
        intrinsic,
        mask=mask.copy(),
    )
    cheirality = int(np.count_nonzero(pose_mask)) / supported if supported else 0.0
    if pose_inliers < config.minimum_pose_inliers:
        return None
    if cheirality < config.minimum_cheirality_ratio:
        return None
    if float(np.linalg.norm(translation)) <= 1e-12:
        return None
    return rotation, translation.reshape(3), int(pose_inliers), cheirality


def _triangulate_pair(
    left: PhotoCameraPose,
    right: PhotoCameraPose,
    left_points: np.ndarray,
    right_points: np.ndarray,
    config: PhotoSfmConfig,
) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    if len(left_points) < 8 or len(left_points) != len(right_points):
        return []
    left_projection = left.intrinsic_matrix @ np.hstack(
        (left.rotation, left.translation.reshape(3, 1))
    )
    right_projection = right.intrinsic_matrix @ np.hstack(
        (right.rotation, right.translation.reshape(3, 1))
    )
    homogeneous = cv2.triangulatePoints(
        left_projection,
        right_projection,
        left_points.T.astype(np.float64),
        right_points.T.astype(np.float64),
    )
    finite = np.abs(homogeneous[3]) > 1e-12
    points = np.full((len(left_points), 3), np.nan)
    points[finite] = (homogeneous[:3, finite] / homogeneous[3, finite]).T
    valid = finite & np.all(np.isfinite(points), axis=1)
    valid &= _camera_depth(points, left) >= config.minimum_depth_m
    valid &= _camera_depth(points, left) <= config.maximum_depth_m
    valid &= _camera_depth(points, right) >= config.minimum_depth_m
    valid &= _camera_depth(points, right) <= config.maximum_depth_m
    valid &= _reprojection_error(points, left_projection, left_points) <= (
        config.maximum_reprojection_error_px
    )
    valid &= _reprojection_error(points, right_projection, right_points) <= (
        config.maximum_reprojection_error_px
    )
    valid &= _triangulation_angles(points, left, right) >= (
        config.minimum_triangulation_angle_degrees
    )
    accepted: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    for point, left_px, right_px in zip(
        points[valid], left_points[valid], right_points[valid], strict=True
    ):
        accepted.append((point.copy(), np.asarray(left_px), np.asarray(right_px)))
    return accepted


def _observations_from_triangulation(
    left_name: str,
    right_name: str,
    triangulated: list[tuple[np.ndarray, np.ndarray, np.ndarray]],
) -> dict[str, list[tuple[np.ndarray, np.ndarray]]]:
    observations: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {
        left_name: [],
        right_name: [],
    }
    for point, left_px, right_px in triangulated:
        observations[left_name].append((left_px, point))
        observations[right_name].append((right_px, point))
    return observations


def _extend_observations(
    observations: dict[str, list[tuple[np.ndarray, np.ndarray]]],
    pair: PhotoCorrespondences,
    triangulated: list[tuple[np.ndarray, np.ndarray, np.ndarray]],
) -> None:
    left_name = pair.left.path.name
    right_name = pair.right.path.name
    observations.setdefault(left_name, [])
    observations.setdefault(right_name, [])
    for point, left_px, right_px in triangulated:
        observations[left_name].append((left_px, point))
        observations[right_name].append((right_px, point))


def _pnp_support(
    name: str,
    cameras: dict[str, PhotoCameraPose],
    pairs: dict[tuple[str, str], PhotoCorrespondences],
    observations: dict[str, list[tuple[np.ndarray, np.ndarray]]],
) -> int:
    object_points, _image_points = _pnp_correspondences(
        name, cameras, pairs, observations
    )
    return len(object_points)


def _solve_pnp(
    name: str,
    cameras: dict[str, PhotoCameraPose],
    pairs: dict[tuple[str, str], PhotoCorrespondences],
    observations: dict[str, list[tuple[np.ndarray, np.ndarray]]],
    config: PhotoSfmConfig,
) -> PhotoCameraPose | None:
    object_points, image_points = _pnp_correspondences(
        name, cameras, pairs, observations
    )
    if len(object_points) < config.minimum_pnp_inliers:
        return None
    sample_pair = next(
        pair
        for pair in pairs.values()
        if pair.left.path.name == name or pair.right.path.name == name
    )
    image_size = (
        sample_pair.left.image_size_px
        if sample_pair.left.path.name == name
        else sample_pair.right.image_size_px
    )
    intrinsic = _intrinsic_matrix(image_size, config)
    cv2.setRNGSeed(0)
    success, rotation_vec, translation, inliers = cv2.solvePnPRansac(
        object_points.astype(np.float64),
        image_points.astype(np.float64),
        intrinsic,
        None,
        flags=cv2.SOLVEPNP_EPNP,
        reprojectionError=config.pnp_reprojection_error_px,
        confidence=0.99,
    )
    if not success or inliers is None or len(inliers) < config.minimum_pnp_inliers:
        return None
    rotation, _ = cv2.Rodrigues(rotation_vec)
    return PhotoCameraPose(
        name, rotation, translation.reshape(3), image_size, intrinsic
    )


def _pnp_correspondences(
    name: str,
    cameras: dict[str, PhotoCameraPose],
    pairs: dict[tuple[str, str], PhotoCorrespondences],
    observations: dict[str, list[tuple[np.ndarray, np.ndarray]]],
) -> tuple[np.ndarray, np.ndarray]:
    object_points: list[np.ndarray] = []
    image_points: list[np.ndarray] = []
    for other in cameras:
        pair = _pair_lookup(pairs, name, other)
        if pair is None:
            continue
        stored = observations.get(other, ())
        if pair.left.path.name == other:
            known_px, query_px = pair.left_points_px, pair.right_points_px
        else:
            known_px, query_px = pair.right_points_px, pair.left_points_px
        for known, query in zip(known_px, query_px, strict=True):
            world = _nearest_world(known, stored)
            if world is None:
                continue
            object_points.append(world)
            image_points.append(query)
    if not object_points:
        return np.empty((0, 3)), np.empty((0, 2))
    return np.asarray(object_points), np.asarray(image_points)


def _nearest_world(
    pixel: np.ndarray,
    stored: tuple[tuple[np.ndarray, np.ndarray], ...] | list[tuple[np.ndarray, np.ndarray]],
) -> np.ndarray | None:
    if not stored:
        return None
    best: tuple[float, np.ndarray] | None = None
    for stored_pixel, world in stored:
        distance = float(np.linalg.norm(stored_pixel - pixel))
        if distance > 2.5:
            continue
        if best is None or distance < best[0]:
            best = (distance, world)
    return None if best is None else best[1]


def _pair_lookup(
    pairs: dict[tuple[str, str], PhotoCorrespondences],
    left: str,
    right: str,
) -> PhotoCorrespondences | None:
    if (left, right) in pairs:
        return pairs[(left, right)]
    if (right, left) in pairs:
        return pairs[(right, left)]
    return None


def _to_y_up(
    points: np.ndarray, cameras: dict[str, PhotoCameraPose]
) -> tuple[np.ndarray, np.ndarray]:
    yup_points = (OPENCV_TO_Y_UP @ points.T).T
    centers = []
    for pose in cameras.values():
        center = -pose.rotation.T @ pose.translation
        centers.append(OPENCV_TO_Y_UP @ center)
    return yup_points, np.asarray(centers, dtype=np.float64)


def _apply_handheld_height(
    points: np.ndarray,
    cameras: np.ndarray,
    config: PhotoSfmConfig,
) -> tuple[np.ndarray, np.ndarray]:
    if len(cameras) < 2:
        raise ReconstructionError(
            "Photo SfM needs at least two cameras for a handheld-height scale.",
            warning_code="low_confidence",
        )
    camera_y = float(np.median(cameras[:, 1]))
    below = points[points[:, 1] < camera_y - config.camera_floor_clearance_m]
    if len(below) < config.minimum_floor_points:
        raise ReconstructionError(
            "Photo SfM did not observe a floor band for the disclosed 1.45 m "
            "handheld-height prior; centimetres will not be guessed.",
            warning_code="low_confidence",
        )
    bins = np.round(below[:, 1] / config.floor_bin_m) * config.floor_bin_m
    values, counts = np.unique(np.round(bins, 6), return_counts=True)
    floor_y = float(values[int(np.argmax(counts))])
    height = camera_y - floor_y
    if height <= 1e-6:
        raise ReconstructionError(
            "Photo SfM floor and camera height collapsed; centimetres will not "
            "be guessed.",
            warning_code="low_confidence",
        )
    scale = config.handheld_camera_height_m / height
    scaled_points = (points - np.array([0.0, floor_y, 0.0])) * scale
    scaled_cameras = (cameras - np.array([0.0, floor_y, 0.0])) * scale
    return scaled_points, scaled_cameras


def _intrinsic_matrix(
    image_size_px: tuple[int, int], config: PhotoSfmConfig
) -> np.ndarray:
    width, height = image_size_px
    focal = config.assumed_focal_length_fraction * max(width, height)
    return np.array(
        [[focal, 0.0, width / 2.0], [0.0, focal, height / 2.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )


def _camera_depth(points: np.ndarray, pose: PhotoCameraPose) -> np.ndarray:
    camera = (pose.rotation @ points.T).T + pose.translation
    return camera[:, 2]


def _reprojection_error(
    points: np.ndarray, projection: np.ndarray, pixels: np.ndarray
) -> np.ndarray:
    homogeneous = np.column_stack((points, np.ones(len(points))))
    projected = homogeneous @ projection.T
    valid = np.abs(projected[:, 2]) > 1e-12
    pixels_hat = np.full((len(points), 2), np.inf)
    pixels_hat[valid] = projected[valid, :2] / projected[valid, 2:3]
    return np.linalg.norm(pixels_hat - pixels, axis=1)


def _triangulation_angles(
    points: np.ndarray, left: PhotoCameraPose, right: PhotoCameraPose
) -> np.ndarray:
    left_center = -left.rotation.T @ left.translation
    right_center = -right.rotation.T @ right.translation
    left_rays = points - left_center
    right_rays = points - right_center
    left_norm = np.linalg.norm(left_rays, axis=1)
    right_norm = np.linalg.norm(right_rays, axis=1)
    valid = (left_norm > 1e-12) & (right_norm > 1e-12)
    cosine = np.full(len(points), 1.0)
    cosine[valid] = np.sum(
        left_rays[valid] * right_rays[valid], axis=1
    ) / (left_norm[valid] * right_norm[valid])
    cosine = np.clip(cosine, -1.0, 1.0)
    return np.degrees(np.arccos(cosine))
