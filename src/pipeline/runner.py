import logging
from pathlib import Path

from src.geotxt.generator import GeoTxtGenerator
from src.reconstruction.odm import ODMStrategy
from src.las.normalizer import LasNormalizer
from src.las.converter import LazConverter
from src.validation.preflight import PreflightValidator
from src.validation.geospatial import GeospatialValidator
from src.validation.reconstruction import ReconstructionValidator
from src.validation.las_integrity import LasIntegrityValidator
from src.metadata.recorder import MetadataRecorder

logger = logging.getLogger(__name__)


class PipelineRunner:
    def __init__(self, strategy: str = "odm"):
        self.strategy = strategy
        self.validators = {
            "preflight": PreflightValidator(),
            "geospatial": GeospatialValidator(),
            "reconstruction": ReconstructionValidator(),
            "las": LasIntegrityValidator(),
        }

    def run(self, dataset_path: str) -> None:
        dataset_path = Path(dataset_path)
        logger.info(f"Starting pipeline for dataset: {dataset_path}")

        self._validate_stage("preflight", dataset_path)

        logger.info("Generating geo.txt...")
        generator = GeoTxtGenerator()
        generator.generate(str(dataset_path))

        self._validate_stage("geospatial", dataset_path)

        logger.info(f"Running {self.strategy} reconstruction...")
        if self.strategy == "odm":
            strategy = ODMStrategy()
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        strategy.run(str(dataset_path))

        self._validate_stage("reconstruction", dataset_path)

        logger.info("Normalizing LAS...")
        normalizer = LasNormalizer()
        las_path = dataset_path / "outputs" / "pointcloud.las"
        normalized_las = normalizer.normalize(str(las_path))

        logger.info("Converting to LAZ...")
        converter = LazConverter()
        laz_path = converter.convert(normalized_las)

        self._validate_stage("las", dataset_path)

        logger.info("Recording metadata...")
        recorder = MetadataRecorder()
        recorder.record(
            dataset_path=str(dataset_path),
            strategy=self.strategy,
            las_path=str(laz_path),
        )

        logger.info("Pipeline completed successfully!")

    def _validate_stage(self, stage: str, dataset_path: Path) -> None:
        validator = self.validators.get(stage)
        if not validator:
            return
        logger.info(f"Running {stage} validation...")
        result = validator.validate(dataset_path)
        if not result.is_valid:
            raise RuntimeError(f"{stage} validation failed: {result.errors}")
        logger.info(f"{stage} validation passed!")
