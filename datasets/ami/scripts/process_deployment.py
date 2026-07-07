import argparse
import csv
from pathlib import Path
import pandas as pd
import logging

from camtrap_functions import (
    infer_deployment_dates,
    generate_deployment_uuid,
    build_deployment_row,
    build_media_row,
    build_detection_rows,
    build_observation_rows,
    MEDIA_FIELDNAMES,
    DETECTION_FIELDNAMES,
    OBSERVATION_FIELDNAMES,
)

def setup_logging(log_dir, deployment_id):
    logger = logging.getLogger("camtrap")
    
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    out_handler = logging.FileHandler(
        log_dir / "process.out"
    )

    err_handler = logging.FileHandler(
        log_dir / "process.err"
    )

    out_handler.setLevel(logging.INFO)
    err_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    out_handler.setFormatter(formatter)
    err_handler.setFormatter(formatter)

    logger.addHandler(out_handler)
    logger.addHandler(err_handler)

    return logger


def write_deployment_csv(
    deployment_row,
    output_dir,
):
    """
    Write Camtrap DP formatted deployment metadata to deployments.csv.
    """

    pd.DataFrame([deployment_row]).to_csv(
        output_dir / "deployments.csv",
        index=False,
    )

def main():

    parser = argparse.ArgumentParser(
        description="Convert a deployment of Mothbot JSON files to Camtrap-DP CSVs."
    )

    parser.add_argument(
        "--bucket_name",
        help="Bucket name, e.g. aia",
    )

    parser.add_argument(
        "--deployment_id",
        help="Deployment identifier, e.g. dep000099",
    )

    args = parser.parse_args()

    bucket_name = args.bucket_name
    deployment_id = args.deployment_id

    # Set up logging
    log_dir = Path("../logs")
    
    log_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    
    logger = setup_logging(log_dir, deployment_id)
    
    logger.info(
        f"Starting deployment {deployment_id}"
    )

    # Specify input/output file paths
    input_dir = Path(
        f"../mothbot/{bucket_name}/{deployment_id}"
    )
    
    if not input_dir.exists():
        raise FileNotFoundError(
            f"Input directory not found: {input_dir}"
        )

    output_dir = Path(
        f"../outputs/{bucket_name}/{deployment_id}"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Load deployment info lookup
    lookup_df = pd.read_csv(
            "../configs/deployment_lookup.csv"
    )

    # Find deployment
    matches = lookup_df.loc[
        lookup_df["deployment_id"] == deployment_id
    ]
    
    if matches.empty:
        raise ValueError(
            f"No deployment metadata found for {deployment_id}"
        )
    
    deployment_lookup = matches.iloc[0].to_dict()
    
    # Infer deployment dates in case manual dates are missing
    start_inferred, end_inferred = infer_deployment_dates(
        input_dir
    )
    
    deployment_lookup["deployment_start_inferred"] = start_inferred
    deployment_lookup["deployment_end_inferred"] = end_inferred
    
    # Generate deployment UUID
    deployment_uuid = generate_deployment_uuid(
        bucket_name,
        deployment_id
    )
    
    # Write deployment metadata to deployments.csv
    deployment_row = build_deployment_row(
        deployment_lookup,
        deployment_id,
        deployment_uuid,
        bucket_name,
    )

    write_deployment_csv(
        deployment_row,
        output_dir,
    )
    
    json_files = sorted(
        input_dir.rglob("*.json")
    )
    
    if not json_files:
        raise ValueError(
            f"No JSON files found in {input_dir}"
        )

    logger.info(
        f"Found {len(json_files):,} JSON files"
    )
    
    # Process all files in deployment, streaming to csv throughout
    with (
        open(output_dir / "media.csv", "w", newline="") as media_file,
        open(output_dir / "detections.csv", "w", newline="") as detection_file,
        open(output_dir / "observations.csv", "w", newline="") as observation_file,
    ):
    
        media_writer = csv.DictWriter(
            media_file,
            fieldnames=MEDIA_FIELDNAMES,
        )
    
        detection_writer = csv.DictWriter(
            detection_file,
            fieldnames=DETECTION_FIELDNAMES,
        )
    
        observation_writer = csv.DictWriter(
            observation_file,
            fieldnames=OBSERVATION_FIELDNAMES,
        )
    
        media_writer.writeheader()
        detection_writer.writeheader()
        observation_writer.writeheader()
    
        for i, json_path in enumerate(json_files, start=1):
        
            try:
    
                media_row, media_uuid = build_media_row(
                    json_path,
                    deployment_uuid,
                )
                
                media_writer.writerow(media_row)
                
                detection_rows = build_detection_rows(
                    json_path,
                    deployment_uuid,
                    media_uuid,
                )
        
                if detection_rows:
                
                    detection_writer.writerows(detection_rows)
        
                observation_rows = build_observation_rows(
                    detection_rows,
                    deployment_uuid,
                    media_uuid,
                )
                
                if observation_rows:
                
                    observation_writer.writerows(observation_rows)
        
                if i % 1000 == 0:
                    logger.info(f"Processed {i:,} files")
                
            except Exception:
            
                logger.exception(
                    f"Failed processing {json_path}"
                )
        
                continue

    logger.info(
        f"Finished deployment {deployment_id}"
    )            
        
if __name__ == "__main__":
    main()
