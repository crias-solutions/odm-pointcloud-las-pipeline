import pytest
from pathlib import Path
from src.validation.preflight import PreflightValidator


def test_preflight_validator_valid_dataset(tmp_path):
    raw_images = tmp_path / "raw_images"
    raw_images.mkdir()
    for i in range(5):
        (raw_images / f"image_{i:03d}.jpg").touch()

    flight_logs = tmp_path / "flight_logs"
    flight_logs.mkdir()
    (flight_logs / "log.csv").touch()

    metadata = tmp_path / "metadata"
    metadata.mkdir()
    (metadata / "dataset_config.yaml").touch()

    validator = PreflightValidator()
    result = validator.validate(tmp_path)

    assert result.is_valid
    assert len(result.errors) == 0


def test_preflight_validator_missing_images(tmp_path):
    raw_images = tmp_path / "raw_images"
    raw_images.mkdir()

    flight_logs = tmp_path / "flight_logs"
    flight_logs.mkdir()

    validator = PreflightValidator(min_image_count=5)
    result = validator.validate(tmp_path)

    assert not result.is_valid
    assert any("Insufficient images" in e for e in result.errors)


def test_preflight_validator_missing_flight_log(tmp_path):
    raw_images = tmp_path / "raw_images"
    raw_images.mkdir()
    for i in range(5):
        (raw_images / f"image_{i:03d}.jpg").touch()

    validator = PreflightValidator()
    result = validator.validate(tmp_path)

    assert not result.is_valid
    assert any("Flight log not found" in e for e in result.errors)
