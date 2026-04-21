# Example usage

> [!NOTE]
> Remember to install `uv`!
> 
> [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

## Quick-check

```bash
# All datasets
./.github/scripts/validate_datasets.py --format text
# A specific dataset
./.github/scripts/validate_datasets.py --dataset ias --format text
```

## Create README

```bash
# Validate datasets and save results
./.github/scripts/validate_datasets.py --format json > tmp.json
# Create README
./.github/scripts/sync_issues.py --dry-run --mode readme --test-file tmp.json > tmp.md
```

Open `tmp.md` and inspect the results!