from pathlib import Path
from typing import List

from src.validation.base import Validator, ValidationResult


class LasIntegrityValidator(Validator):
    def validate(self, dataset_path: Path) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        las_file = dataset_path / "outputs" / "pointcloud.las"
        laz_file = dataset_path / "outputs" / "pointcloud.laz"

        if not las_file.exists():
            errors.append(f"LAS file not found: {las_file}")

        if not laz_file.exists():
            errors.append(f"LAZ file not found: {laz_file}")

        if las_file.exists():
            if not self._validate_las_header(las_file):
                errors.append("LAS header validation failed")

            if not self._has_rgb(las_file):
                errors.append("LAS file missing RGB data")

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    def _validate_las_header(self, las_file: Path) -> bool:
        try:
            with open(las_file, "rb") as f:
                magic = f.read(4)
                if magic != b"LASF":
                    return False
                f.seek(24)
                version = f.read(2).decode("ascii")
                if version not in ("1.4", "1.3", "1.2", "1.1", "1.0"):
                    return False
            return True
        except Exception:
            return False

    def _has_rgb(self, las_file: Path) -> bool:
        try:
            with open(las_file, "rb") as f:
                f.seek(104)
                point_format = ord(f.read(1))
                return point_format >= 2
        except Exception:
            return False
