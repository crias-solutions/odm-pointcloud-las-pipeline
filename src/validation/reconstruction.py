from pathlib import Path
from typing import List

from src.validation.base import Validator, ValidationResult


MIN_POINT_COUNT = 10000


class ReconstructionValidator(Validator):
    def __init__(self, min_point_count: int = MIN_POINT_COUNT):
        self.min_point_count = min_point_count

    def validate(self, dataset_path: Path) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        odm_dir = dataset_path / "processing" / "odm"
        if not odm_dir.exists():
            errors.append(f"ODM output directory not found: {odm_dir}")
            return ValidationResult(is_valid=False, errors=errors)

        pointcloud = odm_dir / "point_cloud.ply"
        if not pointcloud.exists():
            errors.append(f"Point cloud not found: {pointcloud}")
            return ValidationResult(is_valid=False, errors=errors)

        point_count = self._count_points(pointcloud)
        if point_count < self.min_point_count:
            errors.append(
                f"Insufficient points: {point_count}, "
                f"minimum required: {self.min_point_count}"
            )

        report = dataset_path / "outputs" / "reconstruction_report.json"
        if not report.exists():
            warnings.append(f"Reconstruction report not found: {report}")

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    def _count_points(self, pointcloud: Path) -> int:
        try:
            with open(pointcloud, "r") as f:
                for line in f:
                    if line.startswith("element vertex"):
                        return int(line.split()[-1])
        except Exception:
            pass
        return 0
