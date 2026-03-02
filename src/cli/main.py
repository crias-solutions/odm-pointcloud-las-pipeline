import logging
import os
from pathlib import Path

import typer

from src.pipeline.runner import PipelineRunner

app = typer.Typer(help="ODM Point Cloud LAS Pipeline")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@app.command()
def run(
    dataset_path: str = typer.Argument(..., help="Path to dataset directory"),
    strategy: str = typer.Option("odm", help="Reconstruction strategy (odm)"),
) -> None:
    """Run the full pipeline on a dataset."""
    logger.info(f"Starting pipeline for dataset: {dataset_path}")
    runner = PipelineRunner(strategy=strategy)
    runner.run(dataset_path)


@app.command()
def validate(
    dataset_path: str = typer.Argument(..., help="Path to dataset directory"),
    stage: str = typer.Option(
        "all",
        help="Validation stage: preflight, geospatial, reconstruction, las, all",
    ),
) -> None:
    """Run validation on a dataset."""
    from src.validation.preflight import PreflightValidator
    from src.validation.geospatial import GeospatialValidator
    from src.validation.reconstruction import ReconstructionValidator
    from src.validation.las_integrity import LasIntegrityValidator

    dataset_path = Path(dataset_path)
    validators = {
        "preflight": PreflightValidator(),
        "geospatial": GeospatialValidator(),
        "reconstruction": ReconstructionValidator(),
        "las": LasIntegrityValidator(),
    }

    if stage == "all":
        for name, validator in validators.items():
            logger.info(f"Running {name} validation...")
            result = validator.validate(dataset_path)
            if not result.is_valid:
                logger.error(f"{name} validation failed: {result.errors}")
                raise typer.Exit(code=1)
        logger.info("All validations passed!")
    else:
        if stage not in validators:
            raise typer.BadParameter(f"Unknown stage: {stage}")
        validator = validators[stage]
        result = validator.validate(dataset_path)
        if not result.is_valid:
            logger.error(f"{stage} validation failed: {result.errors}")
            raise typer.Exit(code=1)
        logger.info(f"{stage} validation passed!")


@app.command()
def geotxt(
    dataset_path: str = typer.Argument(..., help="Path to dataset directory"),
) -> None:
    """Generate geo.txt from flight log."""
    from src.geotxt.generator import GeoTxtGenerator

    logger.info(f"Generating geo.txt for: {dataset_path}")
    generator = GeoTxtGenerator()
    generator.generate(dataset_path)
    logger.info("geo.txt generated successfully!")


@app.command()
def reconstruct(
    dataset_path: str = typer.Argument(..., help="Path to dataset directory"),
    strategy: str = typer.Option("odm", help="Reconstruction strategy"),
) -> None:
    """Run reconstruction on a dataset."""
    from src.reconstruction.odm import ODMStrategy

    logger.info(f"Running {strategy} reconstruction on: {dataset_path}")
    if strategy == "odm":
        strategy_obj = ODMStrategy()
    else:
        raise typer.BadParameter(f"Unknown strategy: {strategy}")
    strategy_obj.run(dataset_path)
    logger.info("Reconstruction completed!")


if __name__ == "__main__":
    app()
