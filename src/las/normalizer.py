import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class LasNormalizer:
    def __init__(self, target_crs: str = "EPSG:4326"):
        self.target_crs = target_crs

    def normalize(self, input_las: str) -> str:
        input_path = Path(input_las)
        output_path = input_path.parent / "pointcloud_normalized.las"

        pipeline = self._build_pipeline(str(input_path), str(output_path))
        pipeline_path = input_path.parent / "normalize_pipeline.json"

        with open(pipeline_path, "w") as f:
            json.dump(pipeline, f, indent=2)

        cmd = ["pdal", "pipeline", str(pipeline_path)]
        logger.info(f"Running PDAL normalization: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"PDAL failed: {result.stderr}")
            raise RuntimeError(f"LAS normalization failed: {result.stderr}")

        logger.info(f"Normalized LAS saved: {output_path}")
        return str(output_path)

    def _build_pipeline(self, input_file: str, output_file: str) -> dict:
        return {
            "pipeline": [
                {
                    "type": "readers.las",
                    "filename": input_file,
                },
                {
                    "type": "filters.reprojection",
                    "out_srs": self.target_crs,
                },
                {
                    "type": "writers.las",
                    "filename": output_file,
                    "version": "1.4",
                    "point_format": 7,
                },
            ]
        }
