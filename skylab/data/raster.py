from dataclasses import dataclass
from affine import Affine
from pyproj.crs import CRS
import numpy as np

from .vector import Feature

@dataclass(frozen=True)
class RasterMetadata:
    
    """
    RasterMetadata needs only to store the CRS information properly (setter?)
    """
    
    driver: str
    dtype: str
    nodata: float
    width: int
    height: int
    count: int
    crs: CRS
    transform: Affine
    mapping_unit: tuple    

@dataclass(frozen=True)
class Raster:
    """
    TODO: Enforce integrity between array and meta through validators/setters
    TODO: make CRS transformation methods, resampling, reprojection, padding
    TODO: Include methods for rotation, scaling, resampling
    TODO: Verify if it is possible to limit how numpy arrays can shape
    TODO: Verify if it is better to use Block
    
    Properties are for locating raster in time and spectrum (band name)
    Also, what is the source of data
    
    this is intended to be as free as possible
    """
    array: np.ndarray
    meta: RasterMetadata
    properties: dict
    # name: Optional[str] = None
    
@dataclass(frozen=True)
class Crop:
    
    """
    TODO: Create method for rasterized interior
    TODO: Create method for burning outside vector
    TODO: Add *idempotent* CRS transformation in crop creation
    """
    
    raster: Raster
    feature: Feature
    properties: dict
    
# class CropBlock(Block):
#     """
#     A Block of Crops that shares same bounds
#     """
    
#     def __init__()