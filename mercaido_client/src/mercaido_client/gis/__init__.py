from __future__ import annotations

import logging
from typing import Optional, Any

from osgeo import ogr

from .exception import NoSuchLayerError, ClientError


# By default, the GDAL and OGR Python bindings don't raise exceptions, but return
# an error value (e.g. None) and output a message to stdout.
# This switches it to raise exceptions instead.
# Reference: https://gdal.org/api/python_gotchas.html#python-bindings-do-not-raise-exceptions-unless-you-explicitly-call-useexceptions
ogr.UseExceptions()

logger = logging.getLogger(__name__)


class FeatureServerClient:
    """A utility class to communicate with a WFS-T server."""

    _datasource: ogr.DataSource = None
    _endpoint: str
    _readonly: bool

    def __init__(self, endpoint: str, **kwargs) -> None:
        """Create a new FeatureServer instance

        Arguments:
        endpoint (str): The HTTP(S) endpoint of the WFS-T server
        readonly (bool):  Open the layer in read-only mode"""
        self._endpoint = endpoint
        self._readonly = kwargs.get("readonly") or False
        super().__init__()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc):
        self.close()

    def open(self):
        if self._datasource is not None:
            raise ClientError("already opened")
        self._datasource = ogr.Open(f"WFS:{self._endpoint}", not self._readonly)

    def close(self):
        if self._datasource is None:
            raise ClientError("already closed")
        self._datasource.Close()
        self._datasource = None

    def get_layers(self) -> list[Layer]:
        """Return a list of Layers in this FeatureServer"""
        layers = []

        for layer_num in range(self._datasource.GetLayerCount()):
            layers.append(Layer(self._datasource.GetLayer(layer_num)))

        return layers

    def get_layer(self, name: str) -> Layer | None:
        """Return a layer by name or None if no layer with the specified name
        could be found.
        """
        if layer := self._datasource.GetLayerByName(name):
            return Layer(layer)
        else:
            return None


class LayerManagerInterface:
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def create_layer(self, name: str, feature_type: int, **kwargs) -> Layer:
        raise NotImplementedError

    def delete_layer(self, layer: Layer) -> None:
        raise NotImplementedError


class Layer:
    """Wrapper around WFS-T Layer"""

    _ogr_layer: ogr.Layer
    _feature_definition: ogr.FeatureDefn

    def __init__(self, ogr_layer: ogr.Layer) -> None:
        self._ogr_layer = ogr_layer
        self._feature_definition = ogr_layer.GetLayerDefn()

    @property
    def name(self) -> str:
        """The name of the layer"""
        return self._ogr_layer.GetName()

    @property
    def extent(self) -> tuple[float, float, float, float]:
        """The extent of the layer as a 4-element tuple"""
        return self._ogr_layer.GetExtent()

    @property
    def crs(self) -> str:
        spatial_ref = self._ogr_layer.GetSpatialRef()
        authority_name = spatial_ref.GetAuthorityName(None)
        authority_code = spatial_ref.GetAuthorityCode(None)
        return f"{authority_name}:{authority_code}"

    def get_feature(self, feature_id: int) -> Feature | None:
        """Returns Feature with the specified id

        Args:
            id (int): The ID of the feature to return
        """
        if feature := self._ogr_layer.GetFeature(feature_id):
            return Feature(feature)
        else:
            return None

    def get_features(self) -> list[Feature]:
        """Returns a list of features present on this layer."""
        features = []
        self._ogr_layer.ResetReading()
        while feature := self._ogr_layer.GetNextFeature():
            features.append(Feature(feature))

        self._ogr_layer.ResetReading()
        return features

    def create_point(self, point: Point, props: dict[str, Any] = {}) -> Feature:
        """Construct a Point feature for this layer.

        Args:
            point (Point): The point to create

        Returns:
            Feature: A Point feature with the coordinates in `point`

        Raises:
            TypeError: If the WFS layer does not support Point features
        """
        if self._feature_definition.GetGeomType() is not ogr.wkbPoint:
            raise TypeError("This layer does not accept points")

        ogr_feat = ogr.Feature(feature_def=self._feature_definition)
        ogr_feat.SetGeometry(point.geometry)

        return Feature(ogr_feat, props)

    def create_linestring(
        self, points: list[Point], props: dict[str, Any] = {}
    ) -> Feature:
        """Construct a Linestring feature for this layer.

        Args:
            points (list(Point)): A list of points to create the polyline from

        Returns:
            Feature: A Linestring feature with the coordinates in `points`

        Raises:
            TypeError: If the WFS layer does not support Linestring features
        """
        if self._feature_definition.GetGeomType() is not ogr.wkbLineString:
            raise TypeError("This layer does not accept polylines")

        ogr_feat = ogr.Feature(feature_def=self._feature_definition)

        polyline = Polyline(points)

        ogr_feat.SetGeometry(polyline.geometry)
        return Feature(ogr_feat, props)

    def create_polygon(
        self, points: list[list[Point]], props: dict[str, Any] = {}
    ) -> Feature:
        """Construct a Polygon feature for this layer.

        The OGC standard definition requires a polygon to be topologically
        closed. It also states that if the exterior linear ring of a polygon is
        defined in a counterclockwise direction, then it will be seen from the
        "top". Any interior linear rings should be defined in opposite fashion
        compared to the exterior ring, in this case, clockwise.

        A polygon must be topologically closed, as in the first and last
        coordinate of each ring should be identical. If this is not the case,
        an extra point will be added internally to close the ring.

        The exterior outline should be defined in a counterclockwise direction,
        and any interior rings should be defined in the opposite direction, i.e.
        clockwise. Interior rings that are specified this way are subtracted from
        the polygon.

        Arguments:
        points -- A list of lists of points to create the polygon from
        Args:
            points (list(list(Point))): A list of lists of points to create the
                polygon from. Each list is a

        Returns:
            Feature: A Polygon feature with the coordinates in `points`

        Raises:
            TypeError: If the WFS layer does not support Polygon features
        """
        if self._feature_definition.GetGeomType() not in [
            ogr.wkbPolygon,
            ogr.wkbCurvePolygon,
        ]:
            raise TypeError(
                f"This layer does not accept polygons. Expected GeomType: {self._feature_definition.GetGeomType()}"
            )

        ogr_feat = ogr.Feature(feature_def=self._feature_definition)
        polygon = Polygon(points)
        ogr_feat.SetGeometry(polygon.geometry)

        return Feature(ogr_feat, props)

    def add_feature(self, feature: Feature) -> None:
        """Add a feature to the layer.

        The feature type needs to be compatible with the layer feature
        definition.

        Arguments:
            feature (Feature): A Feature to add to the layer.
        """
        self._ogr_layer.CreateFeature(feature._ogr_feature)

    def update_feature(self, feature: Feature) -> None:
        """Update an existing feature.

        The feature type needs to be compatible with the layer feature definition
        and the feature ID needs to exist on this layer.

        Arguments:
            feature (Feature): The Feature to update
        """
        self._ogr_layer.SetFeature(feature)

    def delete_feature(self, feature: Feature) -> None:
        """Delete a feature.

        The feature ID needs to exist on this layer.

        Arguments:
            feature (Feature): The Feature to update
        """
        self._ogr_layer.DeleteFeature(feature)


class Feature:
    _ogr_feature: ogr.Feature

    def __init__(self, ogr_feature: ogr.Feature, props: dict[str, Any] = {}) -> None:
        self._ogr_feature = ogr_feature
        for field, value in props:
            self._ogr_feature[field] = value

    def __getitem__(self, field: str) -> Any:
        return self._ogr_feature[field]

    def __setitem__(self, field: str, value: Any) -> None:
        self._ogr_feature[field] = value

    @property
    def id(self) -> int:
        return self._ogr_feature.GetFID()

    @property
    def geometry(self) -> ogr.Geometry:
        return self._ogr_feature.GetGeomFieldRef()

    @geometry.setter
    def geometry(self, new_geometry: ogr.Geometry) -> None:
        self._ogr_feature.SetGeometry(new_geometry)


class Point:
    _latitude: float
    _longitude: float
    _altitude: Optional[float]
    _ogr_geometry: ogr.Geometry

    def __init__(
        self, latitude: float, longitude: float, altitude: Optional[float] = None
    ) -> None:
        self._latitude = latitude
        self._longitude = longitude
        self._altitude = altitude
        self._ogr_geometry = ogr.Geometry(ogr.wkbPoint)
        if altitude:
            self._ogr_geometry.AddPoint(longitude, latitude, altitude)
        else:
            self._ogr_geometry.AddPoint_2D(longitude, latitude)

    @property
    def latitude(self) -> float:
        return self._latitude

    @latitude.setter
    def latitude(self, value: float) -> None:
        self._latitude = value

    @property
    def longitude(self) -> float:
        return self._longitude

    @longitude.setter
    def longitude(self, value: float) -> None:
        self._longitude = value

    @property
    def altitude(self) -> float:
        return self._altitude

    @altitude.setter
    def altitude(self, value: float) -> None:
        self._altitude = value

    @property
    def geometry(self) -> ogr.Geometry:
        return self._ogr_geometry

    def wkt(self) -> str:
        return self._ogr_geometry.ExportToWkt()


class Polyline:
    _points: list[Point]
    _ogr_geometry: ogr.Geometry

    def __init__(self, points: list[Point]) -> None:
        self.points = points

    @property
    def points(self) -> list[Point]:
        return self._points

    @points.setter
    def points(self, points: list[Point]) -> None:
        self._points = points
        geometry = ogr.Geometry(ogr.wkbLineString)
        for point in points:
            if point.altitude:
                geometry.AddPoint(point.longitude, point.latitude, point.altitude)
            else:
                geometry.AddPoint_2D(point.longitude, point.latitude)
        self._ogr_geometry = geometry

    @property
    def geometry(self) -> ogr.Geometry:
        return self._ogr_geometry

    def wkt(self) -> str:
        return self._ogr_geometry.ExportToWkt()


class Polygon:
    _points: list[list[Point]]
    _ogr_geometry: ogr.Geometry

    def __init__(self, points: list[list[Point]]) -> None:
        self.points = points

    @property
    def points(self) -> list[list[Point]]:
        return self._points

    @points.setter
    def points(self, points: list[list[Point]]) -> None:
        if len(points) < 1:
            raise ValueError("A polygon needs at least one ring of points")
        for i, ring in enumerate(points):
            if len(ring) < 3:
                raise ValueError(
                    f"Polygon ring {i} has too few points, found {len(points)}, need at least 3 to create a polygon"
                )

        self._points = points
        geometry = ogr.Geometry(ogr.wkbPolygon)
        for ring in points:
            ring_geom = ogr.Geometry(ogr.wkbLinearRing)

            for point in ring:
                if point.altitude:
                    ring_geom.AddPoint(point.longitude, point.latitude, point.altitude)
                else:
                    ring_geom.AddPoint_2D(point.longitude, point.latitude)

            ring_geom.CloseRings()
            geometry.AddGeometry(ring_geom)

        self._ogr_geometry = geometry

    @property
    def geometry(self) -> ogr.Geometry:
        return self._ogr_geometry

    def wkt(self) -> str:
        return self._ogr_geometry.ExportToWkt()
