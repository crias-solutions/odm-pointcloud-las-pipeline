import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

from src.reconstruction.base import ReconstructionStrategy

logger = logging.getLogger(__name__)

ODM_DOCKER_IMAGE = os.getenv("ODM_DOCKER_IMAGE", "opendronemap/odm")


class ODMStrategy(ReconstructionStrategy):
    def __init__(self, docker_image: str = ODM_DOCKER_IMAGE):
        self.docker_image = docker_image

    def run(self, dataset_path: str) -> None:
        dataset_path = Path(dataset_path)
        project_name = dataset_path.name
        datasets_dir = dataset_path.parent

        logger.info(f"Running ODM on dataset: {project_name}")
        logger.info(f"Using Docker image: {self.docker_image}")

        self._run_odm_docker(project_name, datasets_dir)
        self._generate_report(dataset_path)

    def _run_odm_docker(self, project_name: str, datasets_dir: Path) -> None:
        cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{datasets_dir.resolve()}:/datasets",
            self.docker_image,
            "--project-path",
            "/datasets",
            project_name,
        ]

        logger.info(f"Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"ODM failed: {result.stderr}")
            raise RuntimeError(f"ODM reconstruction failed: {result.stderr}")

        logger.info("ODM completed successfully")

    def _generate_report(self, dataset_path: Path) -> None:
        odm_dir = dataset_path / "processing" / "odm"

        report = {
            "strategy": "ODM",
            "docker_image": self.docker_image,
            "completed_at": datetime.utcnow().isoformat() + "Z",
            "output_directory": str(odm_dir),
        }

        report_path = dataset_path / "outputs" / "reconstruction_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Reconstruction report saved: {report_path}")
