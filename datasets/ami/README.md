# AMI Mothbot Labels to Camtrap DP Converter

## Overview

This repository converts Mothbot-generated manual labels into datasets that follow the Camtrap DP standard, with additional custom tables detections.csv and cameras.csv. It's designed to work with images collected using Automated Monitoring of Insects (AMI) systems.

The processing workflow:

1. Reads a deployment of Mothbot JSON files.
2. Extracts deployment, camera, media, and detection information.
3. Standardises taxonomic classifications against the GBIF Species Match API.
4. Generates Camtrap-DP tables:
   - `deployments.csv`
   - `cameras.csv` (custom table)
   - `media.csv`
   - `detections.csv` (custom table, proposed by InsectAI as an extension to Camtrap DP)
   - `observations.csv`
5. Generates a `datapackage.json` metadata file (work in progress).

---

## Repository Structure

```text
.
├── scripts/
│   ├── process_deployment.py
│   ├── camtrap_functions.py
│   └── create_datapackage_json.py
│
├── configs/
│   ├── camera_lookup.csv
│   ├── deployment_lookup.csv
│   └── gbif_taxonomy_cache.json
│
├── mothbot/
│   └── <bucket_name>/
│       └── <deployment_id>/
│           └── *.json
│
├── outputs/
│   └── <bucket_name>/
│       └── <deployment_id>/
│           ├── deployments.csv
│           ├── cameras.csv
│           ├── media.csv
│           ├── detections.csv
│           ├── observations.csv
│           └── datapackage.json
│
└── logs/
    ├── process.out
    └── process.err
```

---

## Key Dependencies

- Python
- pandas
- requests

See `environments/ami-publishing.yml` for the full reproducible software environment.

---

## Installation

Create the Conda environment:

```bash
conda env create -f environments/ami-publishing.yml
```

Activate it:

```bash
conda activate ami-publishing
```

---

## Input Data

### Mothbot JSON Files

The processing script expects a directory structure of:

```text
mothbot/
└── <bucket_name>/
    └── <deployment_id>/
        ├── file1.json
        ├── file2.json
        └── ...
```

An example Mothbot annotation file is provided at:
```text
examples/mothbot_annotation_example.json
```

Each JSON file should contain Mothbot-generated image annotation data with the following structure.

#### Required Fields

- `photoBase`: source image filename containing the capture datetime
- `shapes`: list of one or more annotated detections
  - `points`: list of four bounding-box corner coordinates in pixel units, formatted as `[x, y]`
  - `kingdom`, `phylum`, `class`, `order`, `family`, `genus`, `species`: taxonomic classifications stored as strings. Lower taxonomic ranks may be `null` if the specimen could not be identified further.

#### Optional Fields

- `identifier_human`: name of the labeller
- `timestamp_ID_human`: timestamp when the annotation was created, stored as a Unix timestamp in milliseconds

Additional fields may be present and will be ignored.

### Deployment Metadata

Deployment-level metadata are supplied through:

```text
configs/deployment_lookup.csv
```

#### Required Fields

- `deployment_id`
- `bucket_name`
- `latitude`
- `longitude`

#### Optional Fields

- `location_name`
- `location_id`
- `deployment_start`
- `deployment_end`
- `camera_id` (If not supplied, no rows will be created in `cameras.csv`)

If `deployment_start` and `deployment_end` are missing, they will be inferred from image timestamps.

### Camera Metadata

Camera-level metadata are supplied through:

```text
configs/camera_lookup.csv
```

The only required field is `camera_id`. All other fields are optional. Since `cameras.csv` is a custom extension and not part of the Camtrap DP standard, deployments can still be processed when additional camera metadata are unavailable.

### Optional Fields

- `camera_model`
- `camera_focal_length_px`
- `distance_from_camera_cm`
- `image_width_px`
- `image_height_px`
- `field_of_view_width_cm`
- `field_of_view_height_cm`

---

## Usage

### Process a Deployment

```bash
python scripts/process_deployment.py \
    --bucket_name <bucket_name> \
    --deployment_id <deployment_id>
```

Example:
```bash
python scripts/process_deployment.py \
    --bucket_name aia \
    --deployment_id dep000099
```

### Outputs

The script creates:

```text
outputs/<bucket_name>/<deployment_id>/
```

containing:

| File | Description |
|--------|--------|
| deployments.csv | Deployment metadata |
| cameras.csv | Camera metadata |
| media.csv | Media records |
| detections.csv | Detection-level records |
| observations.csv | Observation-level records |
| datapackage.json | Dataset metadata package |
| process.out | Processing log |
| process.err | Error log |

---

## Taxonomic Validation

Taxonomic classifications are validated against the GBIF Species Match API.

To reduce repeated API requests, a local cache is maintained:

```text
configs/gbif_taxonomy_cache.json
```

The cache is:

- Loaded at the start of processing.
- Updated during execution.
- Saved periodically and at completion.

---

## Identifiers

The pipeline generates deterministic UUIDs for deployments, cameras, media, detections and observations. This ensures that reprocessing the same deployment produces stable identifiers.

---

## Datapackage Generation

`create_datapackage_json.py` is a work-in-progress for generating a Camtrap-DP `datapackage.json`.

Automatic extraction/generation needs to be added for:

- Spatial extent
- Temporal extent
- Coordinate precision
- Taxonomic coverage
- Dataset identifiers

---

## Logging

Processing logs are written to:

```text
logs/process.out
logs/process.err
```

`process.out` contains:

- Processing progress
- File counts
- Completion messages

`process.err` contains:

- Exceptions
- Failed file processing events

Files that fail processing are logged and skipped, allowing processing of the remaining deployment to continue.

---

## Planned Development

- Finish implementing `datapackage.json` creation.
- Implement coordinate generalisation (probably rounding to nearest 0.1 degree).
- Add tracking details (`eventID`) and event-level observations. Currently we only have media-level rows in observations.csv, but I think mirroring the event + media level structure from the Camtrap DP example dataset should work once we have the tracks.

---

## Contact

**Maintainer:** Issy Russ  
**Organisation:** UK Centre for Ecology & Hydrology (UKCEH)  
**Email:** isorus@ceh.ac.uk

For questions or issues, please contact the maintainer or open an issue in the example-datasets repository.