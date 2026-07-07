#!/usr/bin/env python3

from pathlib import Path
import json


def initialise_s3_client(credentials_file: Path):
    import boto3

    with credentials_file.open("r") as f:
        creds = json.load(f)

    session = boto3.Session(
        aws_access_key_id=creds["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=creds["AWS_SECRET_ACCESS_KEY"],
    )

    return session.client("s3", endpoint_url=creds["AWS_URL_ENDPOINT"])



def list_deployments(client, bucket: str):
    """
    Lists top-level prefixes in the bucket (i.e. deployments like dep1234/)
    """
    paginator = client.get_paginator("list_objects_v2")

    deployments = set()

    for page in paginator.paginate(
        Bucket=bucket,
        Delimiter="/",  # IMPORTANT: groups by top-level prefix
    ):
        for prefix in page.get("CommonPrefixes", []):
            name = prefix["Prefix"].strip("/")
            deployments.add(name)

    return sorted(deployments)



def main():
    import argparse

    parser = argparse.ArgumentParser(description="List deployments in JASMIN object store")
    parser.add_argument("--credentials", required=True, type=Path)
    parser.add_argument("--bucket", default="sgp")
    args = parser.parse_args()

    print("[INFO] Connecting to S3 / JASMIN object store...")
    client = initialise_s3_client(args.credentials)

    print("[INFO] Listing deployments...")
    deployments = list_deployments(client, args.bucket)

    print(f"\n[RESULT] Found {len(deployments)} deployments:\n")

    for d in deployments:
        print(f"  {d}")


if __name__ == "__main__":
    main()
