# Stress Granule Segmentation Pipeline

This repository contains a microscopy image analysis pipeline for segmenting nuclei, cells, and stress granules (SGs) from multi-channel ND2 image stacks, then extracting object-level measurements for downstream analysis.

The main workflow is implemented in `sg_pipeline.py` and calls helper functions stored in the `src/` directory.

## Overview

The pipeline processes ND2 files in a user-selected directory, and for each image it:

- reads the nuclear channel (`c=0`)
- segments nuclei
- reads the cytoplasmic/membrane channel (`c=1`)
- segments individual cells using the nuclear labels as seeds
- segments stress granules inside cells
- computes region properties for nuclei, cells, and SGs
- merges the datasets by field of view, time point, and cell label
- saves output tables and overlay arrays to the source directory

This project is designed for experiments where each field contains multiple time points and several imaging channels, and where stress granule counts or morphology are tracked per cell.

## Repository structure

- `sg_pipeline.py` — main pipeline entry point
- `src/` — segmentation and analysis utilities
  - `nuclear_segmentation.py` — nuclei detection and watershed-based splitting
  - `cell_segmentation.py` — cell segmentation using cytoplasmic signal and nuclear seeds
  - `sg_segmentation.py` — stress granule detection using blob detection
  - `matching_features.py` — matches SGs to parent cells
  - `regions_prop.py` — calculates region properties from labeled masks
  - `size_filter.py` — removes objects below/above size thresholds
  - `bit_depth.py` — intensity normalization utility
- `cell_conditions.py` — assigns protein identity and treatment labels from image index ranges

## Workflow in the main script

`sg_pipeline.py` performs the following steps:

1. Opens a folder picker and selects ND2 files matching the pattern `20x*`.
2. Loads each image using `nd2reader`.
3. Iterates through time points and field-of-view indices.
4. Segments nuclei from the nuclear channel.
5. Segments cells from the cytoplasmic signal using watershed with nuclei as markers.
6. Maps cells to their corresponding nuclei.
7. Segments stress granules using a Gaussian/blobs-based detection algorithm.
8. Matches SGs to the parent cell.
9. Calculates morphology/intensity properties with `regionprops_table`.
10. Merges cell and nuclear data and adds SG counts per cell.
11. Saves CSV output and overlay `.npy` files in the same directory.

## Data assumptions

This pipeline is tailored to image data with:

- ND2 format input
- a nuclear stain or channel in `c=0`
- a cytoplasmic or membrane channel in `c=1`
- multiple fields of view and time points
- a stress granule signal in the cytoplasmic channel

The code also uses image index ranges to annotate protein and treatment conditions through `cell_conditions.py`.

## Dependencies

Install the following Python packages before running the pipeline:

- `numpy`
- `pandas`
- `scipy`
- `scikit-image`
- `nd2reader`
- `napari-segment-blobs-and-things-with-membranes`

A typical environment can be created with:

```bash
pip install numpy pandas scipy scikit-image nd2reader napari-segment-blobs-and-things-with-membranes
```

## Running the pipeline

From the repository root, run:

```bash
python sg_pipeline.py
```

A folder selection dialog will appear. Select the directory containing your ND2 images.

## Output files

The pipeline writes the following files into the selected directory:

- `cell_properties.csv` — merged cell-level properties, including per-cell match to nucleus and SG count
- `sg_properties.csv` — stress granule-level measurements
- `cell_overlays.npy` — RGB overlays for segmented cells
- `sg_overlays.npy` — RGB overlays for detected stress granules
- `nuclear_overlays_array` — RGB overlays for detected nuclei

## Important notes

- The script currently uses a graphical file chooser (`tkinter`) and is intended to run interactively.
- The code hardcodes several segmentation parameters such as nucleus size, cell size thresholds, Gaussian sigma, and SG blob detection settings. These may need tuning for different imaging conditions.
- The pipeline assumes the selected directory contains images matching the naming pattern `20x*`.
- Protein and treatment labeling are based on field index ranges, so image ordering must match the experiment design used by the code.

## Example of the analysis logic

The final merged output is constructed as follows:

- nuclei properties and cell properties are merged by `label`, `field_view`, and `time`
- stress granule counts are aggregated per cell using `label_cell`, `field_view`, `time`, `protein`, and `treatment`
- the count is merged back into the cell-level table for downstream statistical analysis

## License

This project does not currently include a formal license file. If you intend to share or publish this work, add an appropriate open-source license before distribution.

## Suggested next improvements

- add a proper configuration file for segmentation parameters
- support command-line arguments instead of interactive folder selection
- include quality-control plots for segmentation results
- add a requirements file such as `requirements.txt`
- package the workflow as a reusable module or command-line tool

## Contact and maintenance

This repository appears to be a research pipeline and is best treated as a customized analysis workflow for a specific microscopy dataset. Parameters and assumptions may need to be adapted for new imaging conditions or experiments. 

