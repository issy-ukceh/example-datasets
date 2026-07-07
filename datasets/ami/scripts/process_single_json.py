import argparse
from pathlib import Path

from camtrap_functions import (
    build_media_tbl,
    build_detections_tbl,
    build_observations_tbl,
)


def main():

    parser = argparse.ArgumentParser(
        description="Convert a Mothbot JSON file to Camtrap-DP CSVs."
    )

    parser.add_argument(
        "--json-path",
        required=True,
        help="Path to Mothbot JSON file",
    )

    parser.add_argument(
        "--deployment-uuid",
        required=True,
        help="Deployment UUID",
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory for output CSVs",
    )

    args = parser.parse_args()

    media_df, media_uuid = build_media_tbl(
        args.json_path,
        args.deployment_uuid,
    )

    detections_df = build_detections_tbl(
        args.json_path,
        args.deployment_uuid,
        media_uuid,
    )

    observations_df = build_observations_tbl(
        detections_df,
        args.deployment_uuid,
        media_uuid,
    )
    
    output_dir = Path(args.output_dir)

    media_df.to_csv(
        output_dir / "media.csv",
        index=False,
    )

    detections_df.to_csv(
        output_dir / "detections.csv",
        index=False,
    )

    observations_df.to_csv(
        output_dir / "observations.csv",
        index=False,
    )
    
    print("Conversion complete.")


if __name__ == "__main__":
    main()