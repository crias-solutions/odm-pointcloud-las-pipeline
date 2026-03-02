import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.geotxt.parser import FlightLogParser, FlightLogEntry

logger = logging.getLogger(__name__)


class GeoTxtGenerator:
    def __init__(self, time_offset_seconds: float = 0.0):
        self.time_offset_seconds = time_offset_seconds

    def generate(self, dataset_path: str) -> None:
        dataset_path = Path(dataset_path)

        flight_log_path = dataset_path / "flight_logs" / "log.csv"
        if not flight_log_path.exists():
            raise FileNotFoundError(f"Flight log not found: {flight_log_path}")

        parser = FlightLogParser(time_offset_seconds=self.time_offset_seconds)
        log_entries = parser.parse(flight_log_path)
        logger.info(f"Parsed {len(log_entries)} flight log entries")

        raw_images_dir = dataset_path / "raw_images"
        image_files = self._get_image_files(raw_images_dir)
        logger.info(f"Found {len(image_files)} images")

        geo_entries = self._match_images_to_gps(image_files, log_entries, parser)

        output_path = dataset_path / "processing" / "geo.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._write_geo_txt(geo_entries, output_path)
        logger.info(f"Generated geo.txt with {len(geo_entries)} entries: {output_path}")

    def _get_image_files(self, raw_images_dir: Path) -> List[Path]:
        extensions = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
        return sorted(
            [
                f
                for f in raw_images_dir.iterdir()
                if f.is_file() and f.suffix.lower() in extensions
            ]
        )

    def _match_images_to_gps(
        self,
        image_files: List[Path],
        log_entries: List[FlightLogEntry],
        parser: FlightLogParser,
    ) -> List[Dict]:
        geo_entries: List[Dict] = []

        for image_file in image_files:
            timestamp = self._extract_timestamp(image_file.name)
            if timestamp:
                entry = parser.find_closest_entry(log_entries, timestamp)
                if entry:
                    geo_entries.append(
                        {
                            "filename": image_file.name,
                            "longitude": entry.longitude,
                            "latitude": entry.latitude,
                            "altitude": entry.altitude,
                        }
                    )
                    continue

            if log_entries:
                geo_entries.append(
                    {
                        "filename": image_file.name,
                        "longitude": log_entries[0].longitude,
                        "latitude": log_entries[0].latitude,
                        "altitude": log_entries[0].altitude,
                    }
                )

        return geo_entries

    def _extract_timestamp(self, filename: str) -> Optional[datetime]:
        patterns = [
            r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})",
            r"(\d{4})-(\d{2})-(\d{2})T(\d{2})-(\d{2})-(\d{2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    dt = datetime(
                        int(match.group(1)),
                        int(match.group(2)),
                        int(match.group(3)),
                        int(match.group(4)),
                        int(match.group(5)),
                        int(match.group(6)),
                    )
                    return dt
                except ValueError:
                    pass
        return None

    def _write_geo_txt(self, entries: List[Dict], output_path: Path) -> None:
        with open(output_path, "w") as f:
            f.write("# filename, longitude, latitude, altitude\n")
            for entry in entries:
                f.write(
                    f"{entry['filename']}, {entry['longitude']}, "
                    f"{entry['latitude']}, {entry['altitude']}\n"
                )
