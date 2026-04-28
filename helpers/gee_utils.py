"""
Google Earth Engine utilities for FHNW GBSV MC2.

Provides helper functions to initialise GEE, create Sentinel-2 composites,
and download imagery as NumPy arrays or GeoTIFF files.

GEE is only needed for the *initial* download.  Once the satellite images
are saved locally the notebooks work without any GEE dependency.

Security
--------
The GEE project ID is read from the environment variable ``GEE_PROJECT``.
No credentials or project IDs are ever hard-coded.

Before first use, authenticate once in a terminal::

    earthengine authenticate
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np


# ---------------------------------------------------------------------------
# Initialisation  (lazy – only when actually needed)
# ---------------------------------------------------------------------------

def init_gee(project: str | None = None) -> None:
    """Initialise Google Earth Engine.

    Parameters
    ----------
    project : str, optional
        Google Cloud project ID.  Falls back to the ``GEE_PROJECT``
        environment variable if not provided.

    Raises
    ------
    EnvironmentError
        If no project ID is available.
    """
    import ee

    project_id = project or os.environ.get("GEE_PROJECT")
    if not project_id:
        raise EnvironmentError(
            "Pass your Google Cloud project ID to init_gee(), or set the "
            "GEE_PROJECT environment variable.\n"
            "Example:  init_gee('my-gee-project')"
        )
    try:
        ee.Initialize(project=project_id)
    except Exception:
        print(
            "GEE authentication required. Run the following once in a "
            "terminal:\n  earthengine authenticate",
            file=sys.stderr,
        )
        raise


# ---------------------------------------------------------------------------
# Region definitions (plain coordinate tuples – no ee dependency)
# ---------------------------------------------------------------------------

ALETSCH_JUNGFRAUFIRN_BBOX = [8.01, 46.52, 8.08, 46.56]
ALETSCH_TONGUE_BBOX = [8.04, 46.38, 8.12, 46.44]
ALETSCH_REGION_BBOX = [8.00, 46.42, 8.12, 46.52]


# ---------------------------------------------------------------------------
# Sentinel-2 composite helpers  (require ee – imported lazily)
# ---------------------------------------------------------------------------

def _mask_s2_clouds(image):
    """Apply Sentinel-2 QA60 cloud mask."""
    qa = image.select("QA60")
    cloud_bit = 1 << 10
    cirrus_bit = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit).eq(0).And(qa.bitwiseAnd(cirrus_bit).eq(0))
    return image.updateMask(mask)


def get_sentinel2_composite(
    bbox: list[float],
    date_start: str = "2023-06-01",
    date_end: str = "2023-09-30",
    max_cloud_pct: int = 15,
):
    """Create a cloud-free Sentinel-2 median composite.

    Parameters
    ----------
    bbox : list[float]
        ``[west, south, east, north]`` in EPSG:4326.
    date_start, date_end : str
        Date range in ``YYYY-MM-DD`` format.
    max_cloud_pct : int
        Maximum scene-level cloud cover percentage.

    Returns
    -------
    ee.Image
        Median composite clipped to the bounding box.
    """
    import ee

    region = ee.Geometry.Rectangle(bbox)
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(date_start, date_end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud_pct))
        .map(_mask_s2_clouds)
    )
    return collection.median().clip(region)


def download_sentinel2(
    image,
    bbox: list[float],
    filepath: str | Path,
    bands: list[str] | None = None,
    scale: int = 10,
) -> Path:
    """Download a GEE image as GeoTIFF, with local caching.

    If *filepath* already exists the download is skipped.

    Parameters
    ----------
    image : ee.Image
        Earth Engine image to export.
    bbox : list[float]
        ``[west, south, east, north]`` in EPSG:4326.
    filepath : str or Path
        Local destination path (should end in ``.tif``).
    bands : list[str], optional
        Band names to select.  Defaults to ``["B4", "B3", "B2"]``.
    scale : int
        Spatial resolution in metres.

    Returns
    -------
    Path
        The local file path.
    """
    import ee
    import geemap

    filepath = Path(filepath)
    if filepath.exists():
        print(f"Image already cached: {filepath}")
        return filepath

    if bands is None:
        bands = ["B4", "B3", "B2"]

    region = ee.Geometry.Rectangle(bbox)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {bands} at {scale} m to {filepath} ...")
    geemap.ee_export_image(
        image.select(bands),
        filename=str(filepath),
        scale=scale,
        region=region,
        file_per_band=False,
    )
    print(f"Saved to {filepath}")
    return filepath


# ---------------------------------------------------------------------------
# Loading helpers  (no ee dependency)
# ---------------------------------------------------------------------------

def load_image(filepath: str | Path) -> np.ndarray:
    """Load a GeoTIFF as an RGB uint8 NumPy array.

    Sentinel-2 surface reflectance values (0-10 000) are rescaled to 0-255.

    Parameters
    ----------
    filepath : str or Path
        Path to a ``.tif`` file.

    Returns
    -------
    np.ndarray
        Array with shape ``(H, W, 3)`` and dtype ``uint8``.
    """
    import rasterio

    filepath = Path(filepath)
    with rasterio.open(filepath) as src:
        n_bands = src.count
        bands = []
        for i in range(1, min(n_bands, 3) + 1):
            bands.append(src.read(i))
        img = np.stack(bands, axis=-1).astype(np.float64)

    # Sentinel-2 SR values are typically 0-10000; scale to 0-255
    img = np.clip(img / 10000.0 * 255.0, 0, 255).astype(np.uint8)
    return img
