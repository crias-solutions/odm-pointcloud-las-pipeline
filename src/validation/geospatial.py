from pathlib import Path
from typing import List

from src.validation.base import Validator, ValidationResult


LAT_MIN = -90.0
LAT_MAX = 90.0
LON_MIN = -180.0
LON_MAX = 180.0


class GeospatialValidator(Validator):
    def validate(self, dataset_path: Path) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        geo_txt = dataset_path / "processing" / "geo.txt"
        if not geo_txt.exists():
            errors.append(f"geo.txt not found: {geo_txt}")
            return ValidationResult(is_valid=False, errors=errors)

        entries = self._parse_geo_txt(geo_txt)
        if not entries:
            errors.append("geo.txt is empty")
            return ValidationResult(is_valid=False, errors=errors)

        raw_images_dir = dataset_path / "raw_images"
        image_files = self._get_image_files(raw_images_dir)
        image_names = {f.name for f in image_files}

        geo_image_names = {e["filename"] for e in entries}
        missing = image_names - geo_image_names
        if missing:
            errors.append(f"Images missing from geo.txt: {len(missing)} images")

        for entry in entries:
            lat = entry.get("latitude")
            lon = entry.get("longitude")
            alt = entry.get("altitude")

            if lat is None or lon is None or alt is None:
                errors.append(
                    f"Missing coordinates in geo.txt for: {entry.get('filename')}"
                )
                continue

            if not (LAT_MIN <= lat <= LAT_MAX):
                errors.append(f"Invalid latitude {lat} for {entry.get('filename')}")
            if not (LON_MIN <= lon <= LON_MAX):
                errors.append(f"Invalid longitude {lon} for {entry.get('filename')}")
            if not isinstance(alt, (int, float)) or alt < -500 or alt > 10000:
                errors.append(f"Invalid altitude {alt} for {entry.get('filename')}")

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    def _parse_geo_txt(self, geo_txt: Path) -> List[dict]:
        entries = []
        with open(geo_txt, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(",")
                if len(parts) >= 4:
                    entries.append(
                        {
                            "filename": parts[0].strip(),
                            "longitude": float(parts[1].strip()),
                            "latitude": float(parts[2].strip()),
                            "altitude": float(parts[3].strip()),
                        }
                    )
        return entries

    def _get_image_files(self, raw_images_dir: Path) -> List[Path]:
        extensions = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
        return [
            f
            for f in raw_images_dir.iterdir()
            if f.is_file() and f.suffix.lower() in extensions
        ]
