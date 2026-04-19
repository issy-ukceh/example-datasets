# Flower visitors minidataset

Subset of dataset from https://doi.org/10.5281/zenodo.15096610

## File layout

- `raw/`                       full-frame smartphone images, one per acquisition
- `cropped/`                   ROI-cropped images around the target flower
- `backgrounds/`               frames without flower visitors
- `annotations_subset.tsv`     subset of annotations_full_frames.txt

## Scope

- Sampled plants:
  - Trifolium pratense
  - Daucus carota
  - Achillea millefolium
- Full-frame images: 25
- Cropped ROI images: 25
- Background images (negatives without flower visitors): 5
- Bounding boxes (detections): 25
- Individual insect sequences: 9

## Taxonomic order counts

```
order
hymenoptera    12
diptera        10
araneae         3
```

## Deepest populated taxonomic rank per detection

```
deepest_rank
species          6
family           6
genus            4
morphospecies    3
order            3
clustergenera    3
```

## Deepest rank by order (the rank heterogeneity story)

```
deepest_rank  clustergenera  family  genus  morphospecies  order  species
order                                                                    
araneae                   0       0      0              0      3        0
diptera                   3       0      1              0      0        6
hymenoptera               0       6      3              3      0        0
```

## What this subset is designed to stress-test

1. Mixed taxonomic rank. Bees and flies are identified to fine ranks (genus, species, morphospecies, clustergenera); other orders to order only.
2. Sequence structure. `seq_id` groups multiple frames of the same individual, so the "what counts as an event" question is visible in the data.
3. Confidence levels. Columns `conf_order`, `conf_family`, `conf_species`, etc. record human annotator confidence and are preserved in the subset.
4. Multi-insect frames. At least one frame has `n_boxes >= 2`.
5. Multiple deployments. 3 plant_folders on different plant species.

## Original dataset

Ştefan, V., Workman, A., Cobain, J. C., Rakosy, D., Wild Stoykova, B., Cyranka, E., Urrego Álvarez, R., & Knight, T. (2025). Dataset of arthropod flower visits captured via smartphone time-lapse photography [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15096610

Licence: CC BY-NC-SA 4.0, with commercial AI training use reserved by the copyright holder (see the Zenodo record for full terms).
