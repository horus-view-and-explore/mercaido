from __future__ import annotations

import json
import logging
from enum import Enum
from itertools import takewhile
from typing import Optional
from urllib.parse import urlsplit, urlunsplit, SplitResult

import httpx
from osgeo import ogr, osr

from . import FeatureServerClient, LayerManagerInterface, Layer


logger = logging.getLogger(__name__)

GEOM_TYPE_PREFIX: str = "org.locationtech.jts.geom"


class GeoServerClient(FeatureServerClient, LayerManagerInterface):
    """GeoServer Client

    This class implements two API calls of the GeoServer REST API to:
    - create a layer
    - delete a layer
    """

    _api_endpoint: str
    _workspace: str
    _datastore: str

    def __init__(self, wfs_endpoint: str, workspace: str, datastore: str) -> None:
        url = urlsplit(wfs_endpoint)._asdict()
        url["path"] = "/".join(
            [cmp for cmp in takewhile(lambda c: c != workspace, url["path"].split("/"))]
        )
        url["path"] += "/rest"
        url["query"] = ""
        url["fragment"] = ""

        self._api_endpoint = urlunsplit(SplitResult(**url))
        self._workspace = workspace
        self._datastore = datastore
        super().__init__(endpoint=wfs_endpoint)

    @property
    def api_endpoint(self) -> str:
        return self._api_endpoint

    @property
    def workspace(self) -> str:
        return self._workspace

    @property
    def datastore(self) -> str:
        return self._datastore

    def get_layer(self, name: str) -> Layer | None:
        return super().get_layer(f"{self.workspace}:{name}")

    def create_layer(self, name: str, feature_type: FeatureType, **kwargs) -> Layer:
        """Create a new layer

        Arguments:
            name (str): The name of the new layer
            feature_type (FeatureType): The feature type this layer needs to
                contain
            **kwargs: Additional options

        Keyword arguments:
            srs (str): The SRS for this layer. Default: EPSG:4326
            attributes (list[GeoServerAttribute]):
                List of additional attributes for features. The geometry is
                always added automatically.

        Returns:
            The newly created layer, or None in case of an error

        Raises:
            httpx.HTTPError: If an error occurs with the API request
        """
        logger.info(f"Creating layer {name} in {self.workspace}")
        srs = kwargs.get("srs") or "epsg:4326"
        attributes = kwargs.get("attributes") or []

        attributes.append(GeoServerAttribute("geom", feature_type))

        layer = GeoServerLayer(name, srs, attributes, **kwargs)
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        url = f"{self.api_endpoint}/workspaces/{self.workspace}/datastores/{self.datastore}/featuretypes"

        logger.debug(f"POST {url}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Data: {json.dumps(layer.as_dict(), indent=2)}")

        response = httpx.post(url, headers=headers, json=layer.as_dict())

        response.raise_for_status()

        super().close()
        super().open()

        return super().get_layer(f"{self.workspace}:{name}")

    def delete_layer(self, layer: Layer) -> None:
        """Deletes a layer

        Arguments:
            layer (Layer): The layer to delete

        Raises:
            httpx.HTTPError: If an error occurs with the API request
        """
        logger.info(f"Deleting layer {layer.name} from {self.workspace}")
        (workspace, layer_name) = layer.name.split(":", maxsplit=2)
        url = f"{self.api_endpoint}/workspaces/{self.workspace}/datastores/{self.datastore}/featuretypes/{layer_name}"
        params = {"recurse": True}
        response = httpx.delete(url, params=params)
        response.raise_for_status()

        super().close()
        super().open()


class GeoServerLayer:
    _name: str
    _srs: str
    _attributes: list[GeoServerAttribute]
    _title: str

    def __init__(
        self,
        name: str,
        srs: str,
        attributes: list[GeoServerAttribute],
        title: Optional[str] = None,
    ) -> None:
        self._name = name
        self._srs = srs
        self._attributes = attributes
        self._title = title or name

    @property
    def name(self) -> str:
        return self._name

    @property
    def title(self) -> str:
        return self._title

    @property
    def srs(self) -> str:
        return self._srs

    @property
    def attributes(self) -> list[GeoServerAttribute]:
        return self._attributes

    def as_dict(self) -> dict[str, Any]:
        srs = osr.SpatialReference()
        (_, epsg_num) = self.srs.split(":", 1)
        srs.ImportFromEPSG(int(epsg_num))
        area = srs.GetAreaOfUse()

        return {
            "featureType": {
                "name": self.name,
                "title": self.title,
                "srs": self.srs,
                "enabled": True,
                "attributes": {
                    "attribute": [
                        dict(name=attr.name, binding=attr.datatype)
                        for attr in self.attributes
                    ],
                },
                "latLonBoundingBox": {
                    "crs": self.srs,
                    "minx": area.west_lon_degree,
                    "maxx": area.east_lon_degree,
                    "miny": area.south_lat_degree,
                    "maxy": area.north_lat_degree,
                },
            }
        }


class GeoServerAttribute:
    _name: str
    _datatype: str

    def __init__(self, name: str, datatype: str | FeatureType) -> None:
        self._name = name
        if isinstance(datatype, FeatureType):
            self._datatype = ogr_featuretype_to_geoserver(datatype.value)
        else:
            self._datatype = datatype_to_geoserver(datatype)

    @property
    def name(self) -> str:
        return self._name

    @property
    def datatype(self) -> str:
        return self._datatype


class FeatureType(Enum):
    Point = ogr.wkbPoint
    LineString = ogr.wkbLineString
    Polygon = ogr.wkbPolygon


def datatype_to_geoserver(datatype: str) -> str:
    gs_typename = None
    match datatype:
        case "integer":
            gs_typename = "java.lang.Integer"
        case "float":
            gs_typename = "java.lang.Float"
        case "double":
            gs_typename = "java.lang.Double"
        case "string":
            gs_typename = "java.lang.String"
        case "bool":
            gs_typename = "java.lang.Boolean"
        case _:
            raise TypeError(f"Datatype '{datatype}' is not supported")

    return gs_typename


def ogr_featuretype_to_geoserver(wkb_feature_type: int) -> str:
    gs_typename = None
    match wkb_feature_type:
        case ogr.wkbPoint:
            gs_typename = "Point"
        case ogr.wkbLineString:
            gs_typename = "LineString"
        case ogr.wkbPolygon | ogr.wkbCurvePolygon:
            gs_typename = "Polygon"
        case _:
            raise TypeError("Feature type not supported")

    return f"{GEOM_TYPE_PREFIX}.{gs_typename}"
