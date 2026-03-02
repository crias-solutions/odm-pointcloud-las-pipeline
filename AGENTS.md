# AGENTS.md

> This file provides context to OpenCode and other AI coding assistants about this project.

---

## Project Overview

**Name:** ODM Point Cloud LAS Pipeline

**Description:** A modular Python-orchestrated photogrammetry processing pipeline that converts drone RGB imagery to georeferenced LAS/LAZ point clouds using OpenDroneMap (ODM), with AWS S3 storage and strict validation.

**Type:** Python Application (Dockerized, CLI-controlled)

---

## Tech Stack

- **Language:** Python 3.12
- **Package Manager:** pip
- **Testing:** pytest
- **Linting:** Ruff
- **Formatting:** Ruff / Black
- **Container Runtime:** Docker

### Key Dependencies

- **Geospatial:** PDAL, Open3D
- **CLI:** typer
- **Data Validation:** pydantic, jsonschema
- **Data Processing:** numpy, pandas

---

## Project Structure

```
project-root/
├── src/                              # Source code
│   ├── __init__.py
│   ├── cli/                          # CLI interface
│   │   ├── __init__.py
│   │   └── main.py
│   ├── pipeline/                     # Pipeline orchestration
│   │   ├── __init__.py
│   │   └── runner.py
│   ├── reconstruction/               # Reconstruction engines
│   │   ├── __init__.py
│   │   ├── base.py                    # ReconstructionStrategy base class
│   │   └── odm.py                     # ODM strategy implementation
│   ├── geotxt/                        # geo.txt generation
│   │   ├── __init__.py
│   │   ├── parser.py                  # Flight log parser
│   │   └── generator.py               # geo.txt generator
│   ├── las/                           # LAS/LAZ processing
│   │   ├── __init__.py
│   │   ├── normalizer.py             # PDAL normalization
│   │   └── converter.py               # LAS to LAZ conversion
│   ├── validation/                    # Validation layer
│   │   ├── __init__.py
│   │   ├── preflight.py               # Preflight validation
│   │   ├── geospatial.py             # Geospatial validation
│   │   ├── reconstruction.py          # Reconstruction validation
│   │   └── las_integrity.py           # LAS integrity validation
│   └── metadata                      # Reproducibility metadata
│       ├── __init__.py
│       └── recorder.py                # Metadata logging
├── tests/                             # Test files
│   ├── __init__.py
│   ├── test_geotxt/
│   ├── test_validation/
│   └── test_pipeline/
├── docker/                            # Docker configuration
│   └── Dockerfile
├── Makefile                           # Build automation
├── .devcontainer/                     # Codespaces config
├── AGENTS.md
├── README.md
├── requirements.txt
└── LICENSE
```

---

## Dataset Structure (Mandatory)

The pipeline processes datasets with this structure:

```
dataset_id/
├── raw_images/                        # Original drone images (NEVER MODIFY)
├── flight_logs/
│   └── log.csv                        # Flight log with timestamps/GPS
├── metadata/
│   └── dataset_config.yaml            # Dataset configuration
├── processing/
│   ├── geo.txt                        # Generated geo.txt for ODM
│   ├── odm/                           # ODM output
│   └── logs/                          # Processing logs
├── outputs/
│   ├── pointcloud.las                 # Normalized LAS
│   ├── pointcloud.laz                 # Compressed LAZ
│   ├── reconstruction_report.json    # ODM execution report
│   └── validation_report.json        # Validation results
```

---

## Coding Standards

### Style

- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 88 characters
- Use docstrings for public functions and classes

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `dataset_path` |
| Functions | snake_case | `generate_geo_txt()` |
| Classes | PascalCase | `ODMStrategy` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Private | _prefix | `_internal_method()` |

### Imports

```python
# Standard library
import os
import subprocess
import json

# Third-party
import pandas as pd
import boto3
from pydantic import BaseModel
from typer import Typer

# Local
from src.geotxt.generator import GeoTxtGenerator
from src.validation.preflight import PreflightValidator
```

### Architecture

- Use Strategy pattern for reconstruction engines
- Separate orchestration from engine logic
- Clean architecture: CLI → Pipeline → Strategies/Modules → Data/Validation

---

## Testing

### Run Tests

```bash
pytest
```

### With Coverage

```bash
pytest --cov=src --cov-report=term-missing
```

### Test Naming

- Files: `test_<module>.py`
- Functions: `test_<function>_<scenario>()`

---

## Common Tasks

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Add New Dependency

```bash
pip install <package>
pip freeze > requirements.txt
```

### Run Linter

```bash
ruff check .
```

### Format Code

```bash
ruff format .
```

### Build Docker Image

```bash
docker build -t odm-pipeline -f docker/Dockerfile .
```

### Run Pipeline

```bash
pipeline run /path/to/dataset_id --strategy odm
```

---

## CLI Commands

```bash
# Full pipeline run
pipeline run dataset_path --strategy odm

# Individual steps
pipeline ingest dataset_path
pipeline geotxt generate dataset_path
pipeline reconstruct dataset_path --strategy odm
pipeline validate dataset_path
pipeline upload dataset_path

# Help
pipeline --help
```

---

## AI Assistant Guidelines

### Do

- Write clean, readable code
- Include type hints
- Add docstrings to public functions
- Write unit tests for new features
- Follow existing patterns in the codebase
- Use Strategy pattern for extensible components
- Always validate at each pipeline stage

### Don't

- Remove existing tests without explanation
- Change coding style mid-project
- Add dependencies without justification
- Leave commented-out code
- Hardcode ODM-specific assumptions (use strategy pattern)
- Modify raw_images directory

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ODM_DOCKER_IMAGE` | ODM Docker image (default: opendronemap/odm) | No |
| `LOG_LEVEL` | Logging level (default: INFO) | No |

*AWS S3 integration planned for Phase 2

---

## Notes

### Key Design Decisions

- **geo.txt over EXIF:** Uses ODM-compatible geo.txt for GPS georeferencing instead of EXIF injection
- **EPSG:4326:** All point clouds are reprojected to WGS84
- **PDAL Normalization:** Enforce LAS 1.4, Point Format 7 (RGB), proper scaling
- **Validation-First:** Each stage must pass validation before proceeding

### Validation Stages

1. **Preflight:** Image count, unique filenames, flight log integrity
2. **Geospatial:** Complete geo.txt coverage, CRS bounds
3. **Reconstruction:** Non-zero point cloud, no bounding box anomalies
4. **LAS Integrity:** Header version, point format, RGB preserved

### Reconstruction Strategy Pattern

```python
class ReconstructionStrategy(ABC):
    @abstractmethod
    def run(self, dataset_path: str) -> None:
        pass
```

Implementations: `ODMStrategy` (Phase 1), placeholders for `ColmapStrategy`, `OpenMVGStrategy`

### Docker Orchestration

ODM runs as an external Docker container, not inside the main environment:

```bash
docker run --rm -v dataset_path:/datasets/project opendronemap/odm --project-path /datasets project
```
