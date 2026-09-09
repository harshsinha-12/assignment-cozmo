"""Compose bounded complementary photo feature extractors."""

from pathlib import Path

from cozmo_floorplan.recon.photo_features import PhotoFeatures, extract_photo_features
from cozmo_floorplan.recon.photo_sift import extract_sift_photo_features
from cozmo_floorplan.recon.photos_config import PhotoOverlapConfig


def extract_photo_feature_ensemble(
    path: Path, config: PhotoOverlapConfig
) -> tuple[PhotoFeatures, ...]:
    """Return deterministic feature variants in preference order."""

    variants = [extract_photo_features(path, config)]
    if config.enable_sift_fallback:
        variants.append(extract_sift_photo_features(path, config))
    return tuple(variants)
