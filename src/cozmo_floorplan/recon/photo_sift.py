"""CLAHE-assisted SIFT fallback for difficult indoor photo pairs."""

from pathlib import Path

import cv2

from cozmo_floorplan.recon.photo_features import PhotoFeatures
from cozmo_floorplan.recon.photo_image import load_resized_gray
from cozmo_floorplan.recon.photos_config import PhotoOverlapConfig


def extract_sift_photo_features(
    path: Path, config: PhotoOverlapConfig
) -> PhotoFeatures:
    """Extract bounded SIFT features after local-contrast normalization."""

    gray = load_resized_gray(path, config.sift_resize_max_dimension_px)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    detector = cv2.SIFT_create(
        nfeatures=config.sift_feature_count,
        contrastThreshold=config.sift_contrast_threshold,
        edgeThreshold=config.sift_edge_threshold,
    )
    keypoints, descriptors = detector.detectAndCompute(gray, None)
    height, width = gray.shape
    return PhotoFeatures(
        path=path,
        keypoints=tuple(keypoints),
        descriptors=descriptors,
        image_size_px=(width, height),
        method="sift_clahe",
        norm_type=cv2.NORM_L2,
    )
