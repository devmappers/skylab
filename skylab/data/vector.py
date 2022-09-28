from dataclasses import dataclass, field
from pyproj.crs import CRS
from shapely.geometry import Polygon, MultiPolygon, shape
from shapely.ops import transform as vec_transform
from pyproj import Transformer
from typing import NamedTuple
import fiona

from expression.collections import block, Block

class Bounds(NamedTuple):
    left: float
    bottom: float
    right: float
    top: float

@dataclass(frozen=True, eq=True)
class FeatureCRS:
    # TODO: expose shapely methods
    # index: Option[str]
    properties: dict
    geometry: Polygon
    crs: CRS
    
    def _repr_svg_(self):
        
        return self.geometry._repr_svg_()
    
    def to_crs(self, dest_crs):
        
        """
        If same CRS, returns itself, else use transformer
        """
        
        if self.crs == CRS.from_user_input(dest_crs):
            
            return self
        
        else:
        
            project = Transformer.from_crs(self.crs, dest_crs, always_xy=True).transform
            return FeatureCRS(geometry = vec_transform(project, self.geometry), crs = dest_crs)
        
    # TODO: Do this makes sense to be memoized?
    def bounds(self):
        return self.geometry.bounds
    
    def fetch(self, fetch_function):
        """
        fetch_function (signature FeatureCRS -> Block[Crop])
        
        """
        
        return fetch_function(self)
        
    
@dataclass(frozen=True, eq=True)
class Feature:
    # TODO: expose shapely methods
    # index: Option[str]
    properties: dict = field(hash=True)
    geometry: Polygon = field(hash=True)
    
    def _repr_svg_(self):
        
        return self.geometry._repr_svg_()
    
    def transform(self, transformer):
        
        """
        Applies a crs transformer to the geometry. The transformer has itself the
        information of source and destiny CRS.
        """
        
        return Feature(
            properties = self.properties,
            geometry = vec_transform(transformer.transform, self.geometry)
        )
    
    # TODO: Do this makes sense to be memoized?
    def bounds(self):
        return self.geometry.bounds

@dataclass()
class FeatureCollection:
    # TODO: expose shapely methods
    
    features: Block[Feature]
    crs: CRS
    
    def _repr_svg_(self):
        
        return self.asMultiPolygon()._repr_svg_()
    
    # Memoize!
    def asMultiPolygon(self):
        
        return FeatureCRS(properties={}, geometry = MultiPolygon(self.features.map(lambda x: x.geometry)), crs= self.crs)
    
    def to_crs(self, dest_crs):
        
        if self.crs == CRS.from_user_input(dest_crs):
            
            return self
        
        else:
        
            transformer = Transformer.from_crs(self.crs, dest_crs, always_xy=True)
            feat_transformer = lambda ft: vec_transform(transformer.transform, ft.geometry)
        
            return self.__class__(features = self.features.map(feat_transformer), crs = self.crs)
    
    def explode(self):
        
        """
        returns the block of features
        """
        
        return map(
            (
                lambda crs: (
                    lambda x: FeatureCRS(
                        properties = x.properties,
                        geometry = x.geometry,
                        crs = self.crs
                    )
                )
            )(self.crs)
            ,self.features
        )
    
    # TODO: Do this makes sense to be memoized?
    def bounds(self):
        
        
        
#         xyz = tuple(zip(*list(self.features)))
#         return min(xyz[0]), min(xyz[1]), max(xyz[0]), max(xyz[1])
        
#         map(
#         self.explode,
            
#         )
        return self.asMultiPolygon().bounds()

    # TODO: def to_GeoDataFrame(self):
    
    
class GDALVectorOpener:
    
    """
    Context does not work properly inside class without the "with" keyword
    TODO: see if contextmanager solves the problem
    
    Test if iterators are passed correctly
    """
    
    def __init__(self, filepath):
        
        # self._filepath = PurePosixPath(filepath)
        self._filepath = filepath
        self._src = fiona.open(self._filepath)
        # crs = deepcopy(self._src.crs)
        with fiona.open(self._filepath):
            self.crs = CRS.from_user_input(self._src.crs["init"])
            self._meta = self._src.meta
        # self._iter = map(self._guard,iter(self._src))
        # self._iter = iter(self._src)
        
#     def _guard(self,x):
#         try:
#             return Some(x)
#         except StopIteration:
#         # except Exception:
#             # pass
#             return Nothing

    def cast_feature(self, item):
        
        # feature: dict = yield from item
        feature = item
        
        return Feature(
            # index = feature["id"],
            properties = feature["properties"],
            geometry = shape(feature["geometry"])
        )
    
    def cast_feature_crs(self, item):
        
        # feature: dict = yield from item
        feature = item
        
        return FeatureCRS(
            # index = feature["id"],
            properties = feature["properties"],
            geometry = shape(feature["geometry"]),
            crs = self.crs
        )
    
    def _features(self, src):
        
        return map(
            self.cast_feature, # function
            iter(src)          # iterable
        )
    def collect(self):
        
        with fiona.open(self._filepath) as src:
            
            feats = block.empty
            for feature in self._features(src):
                feats = feats.cons(feature)
            
        return FeatureCollection(features = feats, crs = self.crs)
        # self._iter.