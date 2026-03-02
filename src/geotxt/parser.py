import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class FlightLogEntry:
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: float


class FlightLogParser:
    def __init__(self, time_offset_seconds: float = 0.0):
        self.time_offset_seconds = time_offset_seconds

    def parse(self, log_path: Path) -> List[FlightLogEntry]:
        entries: List[FlightLogEntry] = []
        with open(log_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    timestamp_str = row.get("timestamp", row.get("time", ""))
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    timestamp = timestamp.replace(tzinfo=None)
                    timestamp = timestamp.replace(
                        microsecond=timestamp.microsecond
                        + int(self.time_offset_seconds * 1_000_000)
                    )

                    latitude = float(row["latitude"])
                    longitude = float(row["longitude"])
                    altitude = float(row["altitude"])

                    entries.append(
                        FlightLogEntry(
                            timestamp=timestamp,
                            latitude=latitude,
                            longitude=longitude,
                            altitude=altitude,
                        )
                    )
                except (KeyError, ValueError) as e:
                    logger.warning(f"Skipping invalid row: {e}")
                    continue

        return entries

    def find_closest_entry(
        self, entries: List[FlightLogEntry], target_time: datetime
    ) -> Optional[FlightLogEntry]:
        if not entries:
            return None

        closest = min(
            entries, key=lambda e: abs((e.timestamp - target_time).total_seconds())
        )
        return closest
