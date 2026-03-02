# MASTER AI ASSISTANT PROMPT

## Drone RGB → ODM (geo.txt) → LAS/LAZ → S3

### Research PoC \| Modular \| Dockerized \| Python-Orchestrated

------------------------------------------------------------------------

## PROJECT CONTEXT

You are designing a **research-grade, modular photogrammetry processing
pipeline** for land drone RGB imagery.

The goal is to build a **Python-orchestrated, Dockerized, modular
system** that:

-   Uses OpenDroneMap (ODM) as the initial reconstruction engine
-   Uses `geo.txt` (not EXIF injection) for GPS georeferencing
-   Outputs LAS and LAZ point clouds
-   Uses EPSG:4326 (WGS84)
-   Stores datasets in AWS S3
-   Is CLI-controlled
-   Is fully Dockerized with Conda
-   Is modular to allow additional reconstruction engines later
-   Processes one dataset at a time
-   Includes strict validation per step
-   Is built for research reproducibility

This is a **Proof of Concept (PoC)** but must be architecturally robust
and extensible.

------------------------------------------------------------------------

# IMPLEMENTATION PHASES

## Phase 1 --- Core Pipeline (ODM Only)

Deliverables:

-   Dataset ingestion structure
-   Flight log parser
-   geo.txt generator
-   ODM Docker orchestration
-   LAS normalization via PDAL
-   LAZ compression
-   Validation layer
-   S3 upload
-   CLI interface
-   Reproducibility metadata logging

------------------------------------------------------------------------

## Phase 2 --- Modular Reconstruction Strategy

Abstract reconstruction engine:

``` python
class ReconstructionStrategy:
    def run(self, dataset_path: str) -> None:
        pass
```

Implement:

-   ODMStrategy (Phase 1)
-   Placeholder for ColmapStrategy
-   Placeholder for OpenMVGStrategy

Ensure no tight coupling to ODM.

------------------------------------------------------------------------

## Phase 3 --- Advanced Features (Architectural Preparation)

Prepare architecture for:

-   GCP integration
-   Scale refinement
-   Multi-dataset batch processing
-   Parallel execution
-   Automated AWS compute triggering
-   Additional CRS exports
-   Point cloud postprocessing modules

------------------------------------------------------------------------

# DATASET STRUCTURE (MANDATORY)

    dataset_id/
    │
    ├── raw_images/
    │
    ├── flight_logs/
    │   └── log.csv
    │
    ├── metadata/
    │   ├── dataset_config.yaml
    │
    ├── processing/
    │   ├── geo.txt
    │   ├── odm/
    │   └── logs/
    │
    ├── outputs/
    │   ├── pointcloud.las
    │   ├── pointcloud.laz
    │   ├── reconstruction_report.json
    │   └── validation_report.json

Never modify raw_images.

------------------------------------------------------------------------

# GEO.TXT GENERATION

Design a Python module that:

1.  Parses flight log
2.  Extracts:
    -   Timestamp
    -   Latitude
    -   Longitude
    -   Altitude
3.  Matches images to timestamps
4.  Handles:
    -   Interpolation
    -   Time offset
    -   Missing matches
5.  Generates ODM-compatible `geo.txt`

Validation must include:

-   100% image coverage
-   No missing coordinates
-   Latitude/Longitude bounds valid
-   Altitude numeric

Log:

-   Time alignment offset
-   Interpolation method
-   Number of interpolated points

------------------------------------------------------------------------

# RECONSTRUCTION LAYER

ODM must run inside Docker via Python `subprocess`.

Conceptual execution:

    docker run --rm   -v dataset_path:/datasets/project   opendronemap/odm   --project-path /datasets project

Capture:

-   Logs
-   Exit code
-   Runtime
-   Version info

Store in `reconstruction_report.json`.

------------------------------------------------------------------------

# LAS NORMALIZATION

Even if ODM outputs LAS, enforce normalization using PDAL:

-   Reproject to EPSG:4326
-   Enforce LAS 1.4
-   Use Point Format 7 (RGB)
-   Set scale_x/y/z appropriately
-   Convert to LAZ

Generate PDAL pipeline dynamically.

Validate:

-   CRS correct
-   No NaN coordinates
-   Reasonable bounding box
-   Point count \> minimum threshold

------------------------------------------------------------------------

# VALIDATION LAYER

Validation modules required:

### Preflight

-   Image count threshold
-   Unique filenames
-   Flight log integrity

### Geospatial

-   Complete geo.txt coverage
-   CRS bounds

### Reconstruction

-   Non-zero point cloud
-   No extreme bounding box anomalies

### LAS Integrity

-   Header version correct
-   Point format correct
-   RGB preserved

Each validation produces structured JSON. Failure must halt pipeline.

------------------------------------------------------------------------

# AWS S3 INTEGRATION

Design:

-   Separate raw and processed prefixes
-   Versioned bucket
-   Structured upload:

```{=html}
<!-- -->
```
    s3://bucket/dataset_id/raw/
    s3://bucket/dataset_id/processed/

Upload:

-   LAS
-   LAZ
-   Reports
-   Metadata

Use boto3. Include multipart upload support and retry logic.

------------------------------------------------------------------------

# CLI DESIGN

Use `typer` or `click`.

Example:

    pipeline ingest dataset_path
    pipeline reconstruct dataset_path --strategy odm
    pipeline validate dataset_path
    pipeline upload dataset_path
    pipeline run dataset_path --strategy odm

CLI must:

-   Be modular
-   Be extensible
-   Log cleanly

------------------------------------------------------------------------

# DOCKER + CONDA ENVIRONMENT

Dockerfile must include:

-   Miniconda
-   Python 3.11
-   PDAL
-   Open3D
-   boto3
-   typer
-   pydantic
-   jsonschema
-   numpy
-   pandas

ODM must run as external container, not installed inside main
environment.

Provide:

-   environment.yml
-   Dockerfile
-   Makefile

------------------------------------------------------------------------

# REPRODUCIBILITY METADATA

For each dataset generate:

``` json
{
  "dataset_id": "...",
  "reconstruction_strategy": "ODM",
  "odm_version": "...",
  "docker_image_hash": "...",
  "parameters": {},
  "crs": "EPSG:4326",
  "las_version": "1.4",
  "processing_timestamp": "2026-03-02T19:35:03.889598Z",
  "git_commit": "...",
  "geo_alignment_offset_seconds": 0
}
```

Mandatory for research integrity.

------------------------------------------------------------------------

# ARCHITECTURAL REQUIREMENTS

The system must:

-   Follow clean architecture principles
-   Separate orchestration from engine logic
-   Use strategy pattern for reconstruction
-   Avoid hardcoding ODM-specific assumptions
-   Be easily extendable
-   Support future parallelism
-   Be testable
-   Support CI/CD
-   Be fully containerized

------------------------------------------------------------------------

# OUTPUT REQUIRED FROM AI

Produce:

1.  Full modular architecture diagram (textual)
2.  Folder structure
3.  Python module layout
4.  CLI design
5.  Dockerfile
6.  environment.yml
7.  Example PDAL pipeline
8.  Example geo.txt generator structure
9.  Validation architecture
10. AWS upload module
11. Risk analysis
12. Extension roadmap

Be detailed and explicit. No vague descriptions.
