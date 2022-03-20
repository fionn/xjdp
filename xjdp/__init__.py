#!/usr/bin/env python3
"""Object-oriented features in Xinjiang"""

import os
import enum
import random
import tempfile
from functools import lru_cache
from typing import Any, NamedTuple, Iterator, IO, cast

import requests  # type: ignore

name = "xjdp"  # pylint: disable=invalid-name

__title__ = name
__version__ = "0.0.1"

DOMAIN = os.environ.get("XJDP_DOMAIN") or "xjdp.aspi.org.au"
PROTOCOL = os.environ.get("XJDP_PROTOCOL") or "https"
BASE_URL = f"{PROTOCOL}://{DOMAIN}/data/"
CANONICAL_BASE_URL = "https://xjdp.aspi.org.au/data/"

Coordinates = NamedTuple("Coordinates", [("lat", float), ("long", float)])

class FType(enum.Enum):
    """Allowed feature types"""
    CAMP = "camp"
    CULTURAL = "cultural"
    MOSQUE = "cultural"  # Mosque is classified as cultural

# pylint: disable=too-few-public-methods,too-many-instance-attributes
class Feature:
    """Geographical Feature"""

    def __init__(self, data: dict) -> None:
        self.data = data
        self.id = data["ID"]  # pylint: disable=invalid-name
        self.original_id = data["originalID"]
        self.title = data["title"]
        self.geo = Coordinates(*data["coords"])
        self.prefecture = data["prefecture"]
        self.county = data["county"]
        self.type = data["type"]
        self.url = f"{CANONICAL_BASE_URL}?marker={self.id}&tab=data"

        try:
            self.image_url = data["gallery"][0]["url"]
        except TypeError:
            self.image_url = None

        try:
            self.text = self._text()
        except TypeError:
            self.text = ""

    def __repr__(self) -> str:
        return f"<XJDP {self.id} {self.title}>"

    def _text(self) -> str:
        text = self.data["text"]
        if text[-3:] == ". .":
            text = text[:-2]
        return text.replace("  ", " ")

    @lru_cache
    def image_file(self) -> IO[bytes]:
        """Get the satellite image"""
        response = requests.get(self.image_url)
        response.raise_for_status()
        image_file = tempfile.NamedTemporaryFile(suffix=".jpg")  # pylint: disable=consider-using-with
        image_file.write(response.content)
        image_file.seek(0)
        return image_file

class XJDP:
    """Interface for the XJDP API"""

    def __init__(self) -> None:
        self.base_url = BASE_URL
        self.session = requests.Session()

    def get(self, path: str) -> dict:
        """HTTP GET"""
        response = self.session.get(self.base_url + path)
        response.raise_for_status()
        return response.json()

    def get_timeline(self) -> list[dict]:
        """Get timeline data"""
        return cast(list, self.get("timeline.json"))

    def get_global(self) -> dict[str, Any]:
        """Get global data"""
        return self.get("global.json")

    @lru_cache
    def markers(self, ftype: FType = FType.CAMP) -> list[dict[str, Any]]:
        """Grab all the datapoints, filtering by feature type"""
        markers = self.get("map/markers.geo.json")["features"]
        return [x for x in markers if x["properties"]["type"] == ftype.value]

    @lru_cache
    def _get_data_by_id(self, feature_id: int, ftype: FType) -> dict[str, Any]:
        """Return detailed information for a given camp"""
        return self.get(f"map/{ftype.value}/{feature_id}.json")

    def get_feature_by_id(self, feature_id: int, ftype: FType) -> Feature:
        """Instantiate a Feature object for a given marker"""
        return Feature(self._get_data_by_id(feature_id, ftype))

    def get_features(self, ftype: FType = FType.CAMP) -> Iterator[Feature]:
        """Like get_markers, but returns an iterator of Features"""
        for marker in self.markers(ftype):
            yield self.get_feature_by_id(marker["properties"]["ID"], ftype)

    def random(self, ftype: FType = FType.CAMP) -> Feature:
        """Get a random feature"""
        choice = random.choice(self.markers(ftype))
        return self.get_feature_by_id(choice["properties"]["ID"], ftype)

def main() -> None:
    """Entry point"""
    xjdp = XJDP()
    features = xjdp.get_features()
    for camp in features:
        print(camp)

if __name__ == "__main__":
    main()
