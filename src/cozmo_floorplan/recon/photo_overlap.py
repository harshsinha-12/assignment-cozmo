"""Within-room connectivity and cross-room overlap candidate graphs."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from cozmo_floorplan.io.photos import PhotoRoom
from cozmo_floorplan.recon.photo_feature_ensemble import (
    extract_photo_feature_ensemble,
)
from cozmo_floorplan.recon.photo_features import (
    PhotoFeatures,
    PhotoMatchEvidence,
    match_photo_features,
)
from cozmo_floorplan.recon.photos_config import (
    DEFAULT_PHOTO_OVERLAP,
    PhotoOverlapConfig,
)


@dataclass(frozen=True, slots=True)
class PhotoPairDiagnostics:
    """One within-room or cross-room image-pair decision."""

    left_room: str
    left_image: str
    right_room: str
    right_image: str
    relationship: str
    matches: int
    geometric_inliers: int
    geometric_model: str
    geometric_inlier_ratio: float
    coverage_fraction: float
    eligible: bool
    rejection_reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PhotoRoomConnectivity:
    """Connected-component evidence for one room's unordered images."""

    identifier: str
    image_count: int
    eligible_edges: int
    possible_edges: int
    component_count: int
    connected: bool
    components: tuple[tuple[str, ...], ...]


@dataclass(frozen=True, slots=True)
class CrossRoomCandidate:
    """Strongest eligible pair supporting a possible room connection."""

    left_room: str
    right_room: str
    supporting_pairs: int
    best_left_image: str
    best_right_image: str
    best_geometric_inliers: int
    best_coverage_fraction: float


@dataclass(frozen=True, slots=True)
class PhotoOverlapDiagnostics:
    """Complete photo evidence graph without metric or adjacency claims."""

    rooms: tuple[PhotoRoomConnectivity, ...]
    cross_room_candidates: tuple[CrossRoomCandidate, ...]
    pairs: tuple[PhotoPairDiagnostics, ...]


def analyze_photo_overlap(
    rooms: tuple[PhotoRoom, ...],
    *,
    config: PhotoOverlapConfig = DEFAULT_PHOTO_OVERLAP,
) -> PhotoOverlapDiagnostics:
    """Build deterministic within-room and cross-room image evidence graphs."""

    _validate_config(config)
    features = {
        (room.identifier, frame.path.name): extract_photo_feature_ensemble(
            frame.path, config
        )
        for room in rooms
        for frame in room.frames
    }
    pair_results: list[PhotoPairDiagnostics] = []
    room_results: list[PhotoRoomConnectivity] = []

    for room in rooms:
        room_pairs: list[PhotoPairDiagnostics] = []
        for left_frame, right_frame in combinations(room.frames, 2):
            pair = _analyze_pair(
                room.identifier,
                features[(room.identifier, left_frame.path.name)],
                room.identifier,
                features[(room.identifier, right_frame.path.name)],
                "within_room",
                config,
            )
            room_pairs.append(pair)
            pair_results.append(pair)
        components = _components(
            tuple(frame.path.name for frame in room.frames),
            room_pairs,
        )
        room_results.append(
            PhotoRoomConnectivity(
                identifier=room.identifier,
                image_count=len(room.frames),
                eligible_edges=sum(pair.eligible for pair in room_pairs),
                possible_edges=len(room_pairs),
                component_count=len(components),
                connected=len(components) == 1,
                components=components,
            )
        )

    cross_candidates: list[CrossRoomCandidate] = []
    for left_room, right_room in combinations(rooms, 2):
        cross_pairs = [
            _analyze_pair(
                left_room.identifier,
                features[(left_room.identifier, left_frame.path.name)],
                right_room.identifier,
                features[(right_room.identifier, right_frame.path.name)],
                "cross_room",
                config,
            )
            for left_frame in left_room.frames
            for right_frame in right_room.frames
        ]
        pair_results.extend(cross_pairs)
        eligible = [pair for pair in cross_pairs if pair.eligible]
        if eligible:
            best = max(
                eligible,
                key=lambda pair: (
                    pair.geometric_inliers,
                    pair.coverage_fraction,
                    pair.left_image,
                    pair.right_image,
                ),
            )
            cross_candidates.append(
                CrossRoomCandidate(
                    left_room=left_room.identifier,
                    right_room=right_room.identifier,
                    supporting_pairs=len(eligible),
                    best_left_image=best.left_image,
                    best_right_image=best.right_image,
                    best_geometric_inliers=best.geometric_inliers,
                    best_coverage_fraction=best.coverage_fraction,
                )
            )
    return PhotoOverlapDiagnostics(
        rooms=tuple(room_results),
        cross_room_candidates=tuple(cross_candidates),
        pairs=tuple(pair_results),
    )


def _analyze_pair(
    left_room: str,
    left: tuple[PhotoFeatures, ...],
    right_room: str,
    right: tuple[PhotoFeatures, ...],
    relationship: str,
    config: PhotoOverlapConfig,
) -> PhotoPairDiagnostics:
    candidates = []
    for left_variant, right_variant in zip(left, right, strict=True):
        evidence = match_photo_features(left_variant, right_variant, config)
        reasons = _rejection_reasons(
            left_variant, right_variant, evidence, relationship, config
        )
        candidates.append((left_variant, right_variant, evidence, reasons))
    left_variant, right_variant, evidence, reasons = max(
        candidates,
        key=lambda item: (
            not item[3],
            -len(item[3]),
            item[2].coverage_fraction,
            item[2].geometric_inliers,
            item[2].matches,
        ),
    )
    return PhotoPairDiagnostics(
        left_room=left_room,
        left_image=left_variant.path.name,
        right_room=right_room,
        right_image=right_variant.path.name,
        relationship=relationship,
        matches=evidence.matches,
        geometric_inliers=evidence.geometric_inliers,
        geometric_model=f"{left_variant.method}:{evidence.geometric_model}",
        geometric_inlier_ratio=evidence.geometric_inlier_ratio,
        coverage_fraction=evidence.coverage_fraction,
        eligible=not reasons,
        rejection_reasons=reasons,
    )


def _rejection_reasons(
    left: PhotoFeatures,
    right: PhotoFeatures,
    evidence: PhotoMatchEvidence,
    relationship: str,
    config: PhotoOverlapConfig,
) -> tuple[str, ...]:
    cross = relationship == "cross_room"
    minimum_matches = (
        config.minimum_cross_matches if cross else config.minimum_within_matches
    )
    minimum_inliers = (
        config.minimum_cross_inliers if cross else config.minimum_within_inliers
    )
    minimum_ratio = (
        config.minimum_cross_inlier_ratio
        if cross
        else config.minimum_within_inlier_ratio
    )
    minimum_coverage = (
        config.minimum_cross_coverage_fraction
        if cross
        else config.minimum_within_coverage_fraction
    )
    reasons: list[str] = []
    if (
        min(len(left.keypoints), len(right.keypoints))
        < config.minimum_keypoints_per_image
    ):
        reasons.append("low_keypoint_yield")
    if evidence.matches < minimum_matches:
        reasons.append("too_few_mutual_matches")
    if evidence.geometric_inliers < minimum_inliers:
        reasons.append("too_few_geometric_inliers")
    if evidence.geometric_inlier_ratio < minimum_ratio:
        reasons.append("low_geometric_inlier_ratio")
    if evidence.coverage_fraction < minimum_coverage:
        reasons.append("poor_image_coverage")
    return tuple(reasons)


def _components(
    image_names: tuple[str, ...],
    pairs: list[PhotoPairDiagnostics],
) -> tuple[tuple[str, ...], ...]:
    parents = {name: name for name in image_names}

    def find(name: str) -> str:
        while parents[name] != name:
            parents[name] = parents[parents[name]]
            name = parents[name]
        return name

    for pair in pairs:
        if not pair.eligible:
            continue
        left_root = find(pair.left_image)
        right_root = find(pair.right_image)
        if left_root != right_root:
            parents[right_root] = left_root
    groups: dict[str, list[str]] = {}
    for name in image_names:
        groups.setdefault(find(name), []).append(name)
    return tuple(
        sorted(
            (tuple(sorted(names)) for names in groups.values()),
            key=lambda names: (-len(names), names),
        )
    )


def _validate_config(config: PhotoOverlapConfig) -> None:
    if (
        config.resize_max_dimension_px <= 0
        or config.orb_feature_count <= 0
        or config.sift_resize_max_dimension_px <= 0
        or config.sift_feature_count <= 0
    ):
        raise ValueError("photo overlap image and feature bounds must be positive")
    if (
        config.orb_fast_threshold < 0
        or config.sift_contrast_threshold <= 0
        or config.sift_edge_threshold <= 0
    ):
        raise ValueError("photo overlap detector thresholds are invalid")
    counts = (
        config.minimum_keypoints_per_image,
        config.minimum_within_matches,
        config.minimum_within_inliers,
        config.minimum_cross_matches,
        config.minimum_cross_inliers,
    )
    if any(value <= 0 for value in counts):
        raise ValueError("photo overlap evidence counts must be positive")
    if (
        config.ransac_reprojection_threshold_px <= 0
        or config.sift_ransac_reprojection_threshold_px <= 0
    ):
        raise ValueError("photo overlap RANSAC threshold must be positive")
    ratios = (
        config.ratio_test,
        config.sift_ratio_test,
        config.minimum_within_inlier_ratio,
        config.minimum_within_coverage_fraction,
        config.minimum_cross_inlier_ratio,
        config.minimum_cross_coverage_fraction,
    )
    if any(not 0 < value <= 1 for value in ratios):
        raise ValueError("photo overlap ratios must be in (0, 1]")
