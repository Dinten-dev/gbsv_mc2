# GBSV Mini-Challenge 2 – Aletsch Glacier Image Analysis

Satellite-based monitoring and analysis of the Aletsch Glacier using classical image processing techniques applied to Sentinel-2 imagery.

## Overview

Three processing blocks are covered across 15 notebooks:

| Block | Days | Topic |
|-------|------|-------|
| Augmentation | 1–5 | Gamma correction, noise injection, SSIM evaluation |
| Pattern Detection | 6–10 | Canny edge detection, parameter sweeps, EPD evaluation |
| Segmentation | 11–15 | Otsu thresholding, morphological operations, connected components |

## Data

All images are Sentinel-2 Level-2A composites (10 m resolution, summer 2023) stored in `data/raw/`. They are included in the repository – no external download needed.

## Setup

```bash
pip install -r requirements.txt
```

## Running

Each notebook is standalone. Open any notebook and run all cells:

```bash
cd notebooks
jupyter notebook day01_data_domain_augmentation.ipynb
```

## Project Structure

```
MC2/
├── notebooks/          # 15 Jupyter notebooks (day01–day15)
├── data/
│   ├── raw/            # Sentinel-2 satellite images (.tif)
│   └── processed/      # (reserved for intermediate data)
├── figures/            # Saved plots from notebook runs
├── helpers/
│   └── gee_utils.py    # Image loading utility
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.9+
- numpy, matplotlib, opencv-python, scikit-image, scikit-learn, pandas, rasterio

## Author

Traver Correvon – FHNW, FS26
