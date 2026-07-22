import json
import pandas as pd
import uuid
import datetime
from pathlib import Path
import requests

CACHE_PATH = Path("../configs/gbif_taxonomy_cache.json")

# ============================================================================
# Camtrap-DP schemas
# ============================================================================

DEPLOYMENT_FIELDNAMES = [
    "deploymentID",
    "locationID",
    "locationName",
    "latitude",
    "longitude",
    "coordinateUncertainty",
    "deploymentStart",
    "deploymentEnd",
    "setupBy",
    "cameraID",
    "cameraModel",
    "cameraDelay",
    "cameraHeight",
    "cameraDepth",
    "cameraTilt",
    "cameraHeading",
    "detectionDistance",
    "timestampIssues",
    "attractantUse",
    "attractantType",
    "featureType",
    "habitat",
    "deploymentGroups",
    "deploymentTags",
    "deploymentComments",
    "relatedIdentifier",
]

MEDIA_FIELDNAMES = [
    "mediaID",
    "deploymentID",
    "captureMethod", 
    "timestamp",
    "filePath",
    "filePublic",
    "fileName",
    "fileMediatype",
    "exifData",
    "favorite",
    "mediaComments",
]

DETECTION_FIELDNAMES = [
    "detectionID",
    "deploymentID",
    "mediaID",
    "eventID",
    "eventStart",
    "eventEnd",
    "sourceDetectionID",
    "detectionLevel",
    "detectionType",
    "cameraSetupType",
    "scientificName",
    "taxonRank",
    "count",
    "lifeStage",
    "sex",
    "behavior",
    "individualID",
    "individualLength",
    "individualBiomass",
    "individualPositionRadius",
    "individualPositionAngle",
    "individualSpeed",
    "bboxX",
    "bboxY",
    "bboxWidth",
    "bboxHeight",
    "modelID",
    "classificationMethod",
    "classifiedBy",
    "classificationTimestamp",
    "classificationProbability",
    "consensusProtocolRule",
    "detectionTags",
    "detectionComments",
]

OBSERVATION_FIELDNAMES = [
    "observationID",
    "deploymentID",
    "mediaID",
    "eventID",
    "eventStart",
    "eventEnd",
    "observationLevel",
    "observationType",
    "cameraSetupType",
    "scientificName",
    "count",
    "lifeStage",
    "sex",
    "behavior",
    "individualID",
    "individualLength",
    "individualBiomass",
    "individualPositionRadius",
    "individualPositionAngle",
    "individualSpeed",
    "bboxX",
    "bboxY",
    "bboxWidth",
    "bboxHeight",
    "classificationMethod",
    "classifiedBy",
    "classificationTimestamp",
    "classificationProbability",
    "consensusProtocolRule",
    "observationTags",
    "observationComments",
]

# ============================================================================
# Helper functions
# ============================================================================

def infer_deployment_dates(
    json_dir: Path | str,
) -> tuple[str | None, str | None]:
    """
    Infer deployment start and end dates, based on the timestamps
    contained in the Mothbot JSON file names.
    """
    datetimes = []

    for json_file in Path(json_dir).rglob("*.json"):

        with open(json_file, "r") as f:
            data = json.load(f)


        photo_base = data.get("photoBase", "")

        # Extract timestamp part
        try:
            dt_str = photo_base.split("-")[0]
            dt = datetime.datetime.strptime(
                dt_str,
                "%Y%m%d%H%M%S"
            )
            datetimes.append(dt)
        except Exception:
            continue

    if not datetimes:
        return None, None

    start = min(datetimes)
    end = max(datetimes)

    # Return ISO format
    return start.isoformat(), end.isoformat()
    
def choose_date_with_flag(manual, inferred):
    """
    Choose a manually supplied date if available; otherwise use the
    inferred date and flag it as inferred.

    Returns
    -------
    tuple
        Selected date and a boolean indicating whether it was inferred.
    """

    if manual is not None and pd.notna(manual):
        return manual, False

    return inferred, True


def generate_deployment_uuid(bucket_name, deployment_id):
    """
    Create a bucket-specific namespace, then generate a deployment UUID
    within that namespace.
    """
    BUCKET_NAMESPACE = uuid.uuid5(
        uuid.NAMESPACE_URL,
        bucket_name
    )
    
    deployment_uuid = str(uuid.uuid5(
        BUCKET_NAMESPACE,
        deployment_id
    ))
    
    return deployment_uuid

def extract_datetime_from_photobase(
    photo_base: str | None,
) -> datetime.datetime | None:
    """
    Extract timestamp from a Mothbot photoBase string.
    """

    if not photo_base:
        return None

    return datetime.datetime.strptime(
        photo_base.split("-")[0],
        "%Y%m%d%H%M%S",
    )

def points_to_bbox(
    points: list,
) -> tuple[float, float, float, float]:
    """
    Convert corner points to bounding-box coordinates.
    """
    
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    return min(xs), min(ys), max(xs), max(ys)

def round_points(
    points: list,
    precision: int = 3,
) -> list:
    """
    Round coordinates for deterministic UUID generation.
    """
    
    return [
        [round(x, precision), round(y, precision)]
        for x, y in points
    ]
    
def get_scientific_name(shape: dict) -> str | None:
    """Return the lowest available scientific name based on taxonRank."""

    taxon_rank = shape.get("taxonRank")

    rank_map = {
        "genus": "genus",
        "family": "family",
        "order": "order",
        "class": "class",
        "phylum": "phylum",
        "kingdom": "kingdom",
    }

    if taxon_rank == "species":
        return " ".join(
            filter(None, [shape.get("genus"), shape.get("species")])
        ) or None

    return shape.get(rank_map.get(taxon_rank, ""))

# ============================================================================
# Standardise taxonomy against GBIF
# ============================================================================

def load_taxonomy_cache():
    """
    Load the GBIF taxonomy cache from disk.

    Returns
    -------
    dict
        Dictionary mapping taxonomic keys to cached GBIF match
        results. Returns an empty dictionary if the cache file
        does not exist.

    Notes
    -----
    Cache entries are keyed using the output of
    ``make_taxon_key()``.

    Example
    -------
    {
        "Animalia|Arthropoda|Insecta|Lepidoptera|Crambidae|"
        "Loxomorpha|flavidissimalis": {
            "scientificName": "Loxomorpha flavidissimalis",
            "taxonRank": "species",
            "gbifKey": "9308930",
            "confidence": 100,
            "matchType": "EXACT"
        }
    }
    """
    if CACHE_PATH.exists():
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return {}
    
def save_taxonomy_cache(cache):
    """
    Save the GBIF taxonomy cache to disk.

    Parameters
    ----------
    cache : dict
        Taxonomy cache dictionary containing GBIF lookup results.

    Notes
    -----
    The cache is written as formatted JSON so that it can be
    inspected or edited manually if necessary.

    Existing cache contents will be overwritten.
    """
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)
        
def make_taxon_key(shape):
    """
    Create a unique cache key from the taxonomy fields of a shape.

    Parameters
    ----------
    shape : dict
        Detection record from a Mothbot JSON file.

    Returns
    -------
    str
        Pipe-delimited string containing the taxonomy hierarchy.

    Notes
    -----
    Missing values are represented as empty strings so that
    records with identical taxonomy generate identical keys.

    Example
    -------
    Animalia|Arthropoda|Insecta|Lepidoptera|Crambidae|
    Loxomorpha|flavidissimalis
    """
    return "|".join([
        str(shape.get("kingdom") or ""),
        str(shape.get("phylum") or ""),
        str(shape.get("class") or ""),
        str(shape.get("order") or ""),
        str(shape.get("family") or ""),
        str(shape.get("genus") or ""),
        str(shape.get("species") or ""),
    ])

def get_validated_taxonomy(shape, taxon_cache):
    """
    Validate a taxonomic identification against the GBIF Species
    Match API and return the lowest supported rank.

    Parameters
    ----------
    shape : dict
        Detection record from a Mothbot JSON file containing
        taxonomic fields such as kingdom, phylum, class, order,
        family, genus and species.

    taxon_cache : dict
        Dictionary containing cached GBIF lookup results.

    Returns
    -------
    dict or None
        Dictionary containing validated taxonomy information if
        a sufficiently confident match is found, otherwise None.

        Returned dictionary structure:

        {
            "scientificName": str,
            "taxonRank": str,
            "gbifKey": str,
            "confidence": int,
            "matchType": str
        }
    """
    key = make_taxon_key(shape)

    if key in taxon_cache:
        return taxon_cache[key]

    params = {}

    for field in [
        "kingdom",
        "phylum",
        "class",
        "order",
        "family",
        "genus",
        "species",
    ]:
        value = shape.get(field)

        if value:
            params[field] = value

    try:

        response = requests.get(
            "https://api.gbif.org/v2/species/match",
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        result = response.json()

        diagnostics = result.get("diagnostics", {})

        confidence = diagnostics.get("confidence", 0)
        match_type = diagnostics.get("matchType", "NONE")

        if confidence >= 95 and match_type != "NONE":

            classification = result.get("classification", [])

            if classification:

                lowest = classification[-1]

                usage = result.get("usage", {})

                cache_result = {
                    "scientificName": lowest["name"],
                    "taxonRank": lowest["rank"].lower(),
                    "gbifKey": usage.get("key"),
                    "confidence": confidence,
                    "matchType": match_type,
                }

            else:
                cache_result = None

        else:
            cache_result = None

    except requests.RequestException:
        cache_result = None

    # Cache successful and unsuccessful lookups
    taxon_cache[key] = cache_result

    return cache_result


# ============================================================================
# Build rows for Camtrap DP CSVs
# ============================================================================

def build_deployment_row(
    deployment_lookup: dict,
    deployment_id: str,
    deployment_uuid: str,
    bucket_name: str,
) -> dict:
    """
    Build a Camtrap-DP deployment record.

    Parameters
    ----------
    deployment_lookup : dict
        Deployment metadata.
    deployment_id : str
        Source deployment identifier.
    deployment_uuid : str
        Deployment UUID.
    bucket_name : str
        Country/bucket name.

    Returns
    -------
    dict
        Deployment row.
    """

    deployment_start, start_inferred = choose_date_with_flag(
        deployment_lookup.get("deployment_start"),
        deployment_lookup.get("deployment_start_inferred"),
    )

    deployment_end, end_inferred = choose_date_with_flag(
        deployment_lookup.get("deployment_end"),
        deployment_lookup.get("deployment_end_inferred"),
    )

    deployment_comment = None

    if start_inferred or end_inferred:
        deployment_comment = (
            "Deployment start and/or end dates were not provided "
            "and were inferred from image timestamps."
        )
    
    deployment_row = {
        "deploymentID": deployment_uuid,
        "locationID": deployment_id,
        "locationName": deployment_lookup.get("location_name"),
        "latitude": deployment_lookup.get("latitude"),
        "longitude": deployment_lookup.get("longitude"),
        "coordinateUncertainty": None,
        "deploymentStart": deployment_start, #TODO: Potentially get from Alyssa's deployment info
        "deploymentEnd": deployment_end, #TODO: Potentially get from Alyssa's deployment info
        "setupBy": None,
        "cameraID": None, #TODO: Potentially get from Alyssa's deployment info
        "cameraModel": "UKCEH-AMI", #TODO: Change to camera model from Alyssa's deployment info
        "cameraDelay": None,
        "cameraHeight": None,
        "cameraDepth": None,
        "cameraTilt": None,
        "cameraHeading": None,
        "detectionDistance": None,
        "timestampIssues": None,
        "attractantUse": True,
        "attractantType": "light",
        "featureType": None,
        "habitat": None,
        "deploymentGroups": f"country:{bucket_name}",
        "deploymentTags": None,
        "deploymentComments": deployment_comment,
        "relatedIdentifier": None,
    }

    return deployment_row

def build_media_row(
    json_path: str,
    deployment_uuid: str,
) -> tuple[dict, str]:
    """
    Build a single Camtrap-DP media record from a Mothbot JSON file.

    Parameters
    ----------
    json_path : str
        Path to the input JSON file.
    deployment_uuid : str
        Deployment UUID.

    Returns
    -------
    tuple[dict, str]
        Media row and generated media UUID.
    """

    with open(json_path, "r") as f:
        data = json.load(f)

    photo_base = data.get("photoBase", "")

    media_uuid = str(uuid.uuid5(
        uuid.UUID(deployment_uuid),
        photo_base
    ))

    media_row = {
        "mediaID": media_uuid,
        "deploymentID": deployment_uuid,
        "captureMethod": "timeLapse", 
        "timestamp": extract_datetime_from_photobase(photo_base),
        "filePath": "https://dap.ceda.ac.uk/bodc/deposits01/soc240656/Images/GR7801_CR03_01_307.jpg", #TODO: Link to real image url. Currently a random example image from CEDA
        "filePublic": True,
        "fileName": f"{photo_base}.jpg",
        "fileMediatype": "image/jpeg",
        "exifData": None,
        "favorite": None,
        "mediaComments": None,
    }

    return media_row, media_uuid
       

def build_detection_rows(
    json_path: str,
    deployment_uuid: str,
    media_uuid: str,
    taxon_cache: dict[str, dict | None],
) -> list:
    """
    Build Camtrap-DP detection rows from a Mothbot JSON file.

    Parameters
    ----------
    json_path : str
        Path to the input JSON file.
    deployment_uuid : str
        Deployment UUID.
    media_uuid : str
        Parent media UUID.
        
    taxon_cache : dict[str, dict | None]
        Cache of previously queried GBIF taxonomic matches.
    
    Returns
    -------
    list
        Detection rows.
    """
    
    with open(json_path, "r") as f:
        data = json.load(f)

    shapes = data.get("shapes", [])

    detection_rows = []

    media_namespace = uuid.UUID(media_uuid)

    for shape in shapes:
        points = shape.get("points", [])
        if len(points) != 4:
            continue #TODO: raise some kind of warning/create log?

        x_min, y_min, x_max, y_max = points_to_bbox(points)

        # Round bbox points for consistency
        rounded_points = round_points(points)
        
        detection_id = json.dumps({
            "points": rounded_points,
            "timestamp": shape.get("timestamp_ID_human")
        }, sort_keys=True)
        
        detection_uuid = str(uuid.uuid5(
            media_namespace,
            detection_id
        ))

        validated_taxon = get_validated_taxonomy(
            shape,
            taxon_cache,
        )

        if validated_taxon:
        
            scientific_name = validated_taxon["scientificName"]
            taxon_rank = validated_taxon["taxonRank"]
        
        else:
            taxon_rank = None
            scientific_name = None

        row = {
            "detectionID": detection_uuid,
            "deploymentID": deployment_uuid,
            "mediaID": media_uuid,
            "eventID": None,  # Potentially add eventIDs to manual observations once tracks have been generated
            "eventStart": None,
            "eventEnd": None,
            "sourceDetectionID": None,
            "detectionLevel": "media",
            "detectionType": "animal",
            "cameraSetupType": None,
            "scientificName": scientific_name,
            "taxonRank": taxon_rank,
            "count": None,
            "lifeStage": None,
            "sex": None,
            "behavior": None,
            "individualID": None,
            "individualLength": None,
            "individualBiomass": None,
            "individualPositionRadius": None,
            "individualPositionAngle": None,
            "individualSpeed": None,
            "bboxX": x_min, #TODO: Update bbox to relative (not pixels) and start in top-left
            "bboxY": y_min,
            "bboxWidth": x_max - x_min,
            "bboxHeight": y_max - y_min,
            "modelID": None,
            "classificationMethod": "manual",
            "classifiedBy": shape.get("identifier_human"),
            "classificationTimestamp": datetime.datetime.fromtimestamp(shape.get("timestamp_ID_human") / 1000),
            "classificationProbability": None,
            "consensusProtocolRule": None,
            "detectionTags": None,
            "detectionComments": None,
        }

        detection_rows.append(row)

    return detection_rows


def build_observation_rows(
    detection_rows: list,
    deployment_uuid: str,
    media_uuid: str,
) -> list:
    """
    Build Camtrap-DP observation rows from detection rows.

    Parameters
    ----------
    detection_rows : list
        Detection records.
    deployment_uuid : str
        Deployment UUID.
    media_uuid : str
        Parent media UUID.

    Returns
    -------
    list
        Observation rows.
    """

    observation_rows = []

    for d in detection_rows:

        # Rules for converting detection to observation - may change for machine-labelled detections
        if d["classificationMethod"] != "manual":
            continue
        
        if not d["scientificName"] or not d["taxonRank"]:
            continue

        observation_uuid = str(
            uuid.uuid5(
                uuid.UUID(d["detectionID"]),
                "observation"
            )
        )

        observation_rows.append({
            "observationID": observation_uuid,
            "deploymentID": deployment_uuid,
            "mediaID": media_uuid,
            "eventID": d["eventID"],
            "eventStart": d["eventStart"],
            "eventEnd": d["eventEnd"],
            "observationLevel": d["detectionLevel"],
            "observationType": d["detectionType"],
            "cameraSetupType": d["cameraSetupType"],
            "scientificName": d["scientificName"],
            "count": d["count"],
            "lifeStage": d["lifeStage"],
            "sex": d["sex"],
            "behavior": d["behavior"],
            "individualID": d["individualID"],
            "individualLength": d["individualLength"],
            "individualBiomass": d["individualBiomass"],
            "individualPositionRadius": d["individualPositionRadius"],
            "individualPositionAngle": d["individualPositionAngle"],
            "individualSpeed": d["individualSpeed"],
            "bboxX": d["bboxX"], #TODO: Update bbox to relative (not pixels) and start in top-left
            "bboxY": d["bboxY"],
            "bboxWidth": d["bboxWidth"],
            "bboxHeight": d["bboxHeight"],
            "classificationMethod": d["classificationMethod"],
            "classifiedBy": d["classifiedBy"],
            "classificationTimestamp": d["classificationTimestamp"],
            "classificationProbability": d["classificationProbability"],
            "consensusProtocolRule": d["consensusProtocolRule"],
            "observationTags": None,
            "observationComments": None,
        })

    return observation_rows

# ============================================================================
# Build tables for Camtrap DP CSVs
# ============================================================================

# Wrappers that bring together the rows generated for each csv

def build_deployments_tbl(
    deployment_lookup: dict,
    deployment_id: str,
    deployment_uuid: str,
    bucket_name: str,
) -> pd.DataFrame:
    """
    Build the deployments table.

    Parameters
    ----------
    deployment_lookup : dict
        Deployment metadata.
    deployment_id : str
        Source deployment identifier.
    deployment_uuid : str
        Deployment UUID.
    bucket_name : str
        Country/bucket name.

    Returns
    -------
    pd.DataFrame
        Deployment table.
    """

    deployment_row = build_deployment_row(
        deployment_lookup,
        deployment_id,
        deployment_uuid,
        bucket_name,
    )

    return pd.DataFrame([deployment_row])

def build_media_tbl(
    json_path: str,
    deployment_uuid: str,
) -> tuple[pd.DataFrame, str]:
    """
    Build the media table for a single Mothbot JSON file.

    Parameters
    ----------
    json_path : str
        Path to the input JSON file.
    deployment_uuid : str
        Deployment UUID.

    Returns
    -------
    tuple[pd.DataFrame, str]
        Media table and generated media UUID.
    """

    media_row, media_uuid = build_media_row(
        json_path,
        deployment_uuid,
    )

    return pd.DataFrame([media_row]), media_uuid


def build_detections_tbl(
    json_path: str,
    deployment_uuid: str,
    media_uuid: str,
    taxon_cache: dict[str, dict | None],
) -> pd.DataFrame:
    """
    Build the detections table for a single Mothbot JSON file.

    Parameters
    ----------
    json_path : str
        Path to the input JSON file.
    deployment_uuid : str
        Deployment UUID.
    media_uuid : str
        Media UUID.

    Returns
    -------
    pd.DataFrame
        Detection records.
    """

    detection_rows = build_detection_rows(
        json_path,
        deployment_uuid,
        media_uuid,
        taxon_cache,
    )

    return pd.DataFrame(detection_rows)

    
def build_observations_tbl(
    detections: pd.DataFrame | list[dict],
    deployment_uuid: str,
    media_uuid: str,
) -> pd.DataFrame:
    """
    Build the observations table from detection records.

    Parameters
    ----------
    detections : pd.DataFrame | list[dict]
        Detection records as either:
        - a pandas DataFrame, or
        - a list of detection row dictionaries.
    deployment_uuid : str
        Deployment UUID.
    media_uuid : str
        Media UUID.

    Returns
    -------
    pd.DataFrame
        Observation records.
    """

    if isinstance(detections, pd.DataFrame):
        detection_rows = detections.to_dict("records")
    else:
        detection_rows = detections

    observation_rows = build_observation_rows(
        detection_rows,
        deployment_uuid,
        media_uuid,
    )

    return pd.DataFrame(observation_rows)
