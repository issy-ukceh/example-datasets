#!/usr/bin/env python3

from pathlib import Path
import json
import boto3
import csv
import re
from collections import defaultdict


def initialise_s3_client(credentials_file: Path):
    with credentials_file.open("r") as f:
        creds = json.load(f)

    return boto3.client(
        "s3",
        aws_access_key_id=creds["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=creds["AWS_SECRET_ACCESS_KEY"],
        endpoint_url=creds["AWS_URL_ENDPOINT"],
    )


def count_images_per_deployment(client, bucket: str, max_pages: int | None = None):
    """
    Scan the bucket and count JPG images per deployment.
    Optionally limit number of pages for faster sampling.
    """
    paginator = client.get_paginator("list_objects_v2")

    counts = defaultdict(int)
    pages_scanned = 0

    for page in paginator.paginate(Bucket=bucket):
        pages_scanned += 1

        contents = page.get("Contents", [])
        if not contents:
            break

        for obj in contents:
            key = obj["Key"]

            # Only care about JPG images
            if not key.endswith(".jpg"):
                continue

            # Extract deployment ID (depXXXX)
            match = re.match(r"(dep\d+)", key)
            if match:
                deployment = match.group(1)
                counts[deployment] += 1

        if pages_scanned % 50 == 0:
            total_images = sum(counts.values())
            print(f"[INFO] Pages scanned: {pages_scanned}, images counted: {total_images}")

        if max_pages and pages_scanned >= max_pages:
            print("[INFO] Reached max_pages limit")
            break

    return counts


def write_csv(counts: dict, output_file: Path):
    with output_file.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["deployment_id", "image_count"])

        for dep, count in sorted(counts.items()):
            writer.writerow([dep, count])


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Count images per deployment in a bucket")
    parser.add_argument("--credentials", required=True, type=Path)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max_pages", type=int, default=None,
                        help="Limit pages for faster sampling (optional)")
    args = parser.parse_args()

    print(f"[INFO] Connecting to bucket: {args.bucket}")
    client = initialise_s3_client(args.credentials)

    print("[INFO] Counting images across deployments...\n")

    counts = count_images_per_deployment(
        client,
        bucket=args.bucket,
        max_pages=args.max_pages,
    )

    print("\n[INFO] Writing results to CSV...")
    write_csv(counts, args.output)

    print(f"\n✅ DONE")
    print(f"Deployments found: {len(counts)}")
    print(f"Output file: {args.output}")


if __name__ == "__main__":
    main()
