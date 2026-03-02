import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class LazConverter:
    def __init__(self, compression_level: int = 6):
        self.compression_level = compression_level

    def convert(self, input_las: str) -> str:
        input_path = Path(input_las)
        output_path = input_path.with_suffix(".laz")

        cmd = [
            "laszip",
            "-compress",
            "-o",
            str(output_path),
            str(input_path),
        ]

        logger.info(f"Running LAZ conversion: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning(f"laszip not available, using PDAL: {result.stderr}")
            return self._convert_with_pdal(input_path, output_path)

        logger.info(f"Converted to LAZ: {output_path}")
        return str(output_path)

    def _convert_with_pdal(self, input_path: Path, output_path: Path) -> str:
        pipeline = {
            "pipeline": [
                {
                    "type": "readers.las",
                    "filename": str(input_path),
                },
                {
                    "type": "writers.laz",
                    "filename": str(output_path),
                    "compression": "laszip",
                },
            ]
        }

        pipeline_path = input_path.parent / "laz_pipeline.json"
        with open(pipeline_path, "w") as f:
            json.dump(pipeline, f)

        cmd = ["pdal", "pipeline", str(pipeline_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"LAZ conversion failed: {result.stderr}")

        logger.info(f"Converted to LAZ (PDAL): {output_path}")
        return str(output_path)
