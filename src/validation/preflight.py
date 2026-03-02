from pathlib import Path
from typing import List

from src.validation.base import Validator, ValidationResult


MIN_IMAGE_COUNT = 5


class PreflightValidator(Validator):
    def __init__(self, min_image_count: int = MIN_IMAGE_COUNT):
        self.min_image_count = min_image_count

    def validate(self, dataset_path: Path) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not dataset_path.exists():
            errors.append(f"Dataset path does not exist: {dataset_path}")
            return ValidationResult(is_valid=False, errors=errors)

        raw_images_dir = dataset_path / "raw_images"
        if not raw_images_dir.exists():
            errors.append(f"raw_images directory not found: {raw_images_dir}")
            return ValidationResult(is_valid=False, errors=errors)

        image_files = self._get_image_files(raw_images_dir)
        if len(image_files) < self.min_image_count:
            errors.append(
                f"Insufficient images: found {len(image_files)}, "
                f"minimum required: {self.min_image_count}"
            )

        if not self._all_unique_filenames(image_files):
            errors.append("Duplicate image filenames found")

        flight_log = dataset_path / "flight_logs" / "log.csv"
        if not flight_log.exists():
            errors.append(f"Flight log not found: {flight_log}")

        metadata_config = dataset_path / "metadata" / "dataset_config.yaml"
        if not metadata_config.exists():
            warnings.append(f"Dataset config not found: {metadata_config}")

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    def _get_image_files(self, raw_images_dir: Path) -> List[Path]:
        extensions = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
        return [
            f
            for f in raw_images_dir.iterdir()
            if f.is_file() and f.suffix.lower() in extensions
        ]

    def _all_unique_filenames(self, files: List[Path]) -> bool:
        names = [f.name for f in files]
        return len(names) == len(set(names))
