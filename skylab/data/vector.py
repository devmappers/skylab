from dataclasses import dataclass
import fiona
# from abc
# from pathlib import PurePosixPath
# from copy import deepcopy
from pyproj.crs import CRS
from shapely.geometry import shape, polygon

@dataclass
class Feature:
    index: str
    properties: dict
    geometry: polygon.Polygon
    crs: CRS

class GDALVectorOpener:
    
    def __init__(self, filepath):
        
        # self._filepath = PurePosixPath(filepath)
        self._filepath = filepath
        self._src = fiona.open(self._filepath)
        # crs = deepcopy(self._src.crs)
        self.crs = CRS.from_user_input(self._src.crs["init"])
        self._meta = self._src.meta
        self._iter = iter(self._src)
        # self._feature_iter = 
    
    def cast_geometry(self, item) -> Feature:
        
        return Feature(
            index = item["id"],
            properties = item["properties"],
            geometry = shape(item["geometry"]),
            crs = self.crs
        )
    
    def features(self):
        
        return map(
            self.cast_geometry, # function
            self._iter          # iterable
        )
