import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class MetadataRecorder:
    def __init__(self):
        self.crs = "EPSG:4326"
        self.las_version = "1.4"

    def record(
        self,
        dataset_path: str,
        strategy: str,
        las_path: str,
    ) -> None:
        dataset_path = Path(dataset_path)

        git_commit = self._get_git_commit()

        metadata = {
            "dataset_id": dataset_path.name,
            "reconstruction_strategy": strategy.upper(),
            "odm_version": self._get_odm_version(),
            "docker_image": self._get_docker_image(),
            "parameters": {},
            "crs": self.crs,
            "las_version": self.las_version,
            "processing_timestamp": datetime.utcnow().isoformat() + "Z",
            "git_commit": git_commit,
            "geo_alignment_offset_seconds": 0,
        }

        output_path = dataset_path / "outputs" / "metadata.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Metadata recorded: {output_path}")

    def _get_git_commit(self) -> str:
        import subprocess

        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"

    def _get_odm_version(self) -> str:
        return "unknown"

    def _get_docker_image(self) -> str:
        import os

        return os.getenv("ODM_DOCKER_IMAGE", "opendronemap/odm")
