#!/usr/bin/env python3
"""Object-oriented camps in Xinjiang"""

from functools import lru_cache
from typing import cast, NamedTuple, Iterator

import requests

Coordinates = NamedTuple("Coordinates", [("lat", float), ("long", float)])

# pylint: disable=too-few-public-methods,too-many-instance-attributes
class Feature:
    """Geographical Feature"""

    def __init__(self, data: dict) -> None:
        self.data = data
        self.id = data["ID"] # pylint: disable=invalid-name
        self.title = data["title"]
        self.location = Coordinates(data["coords"][0], data["coords"][1])
        self.prefecture = data["prefecture"]
        self.county = data["county"]
        self.text = data["text"]
        self.type = data["type"]
        try:
            self.image_url = data["gallery"][0]["url"]
        except TypeError:
            self.image_url = None

class XJDP:
    """Interface for the XJDP API"""

    def __init__(self) -> None:
        self.base_url = "https://xjdp.aspi.org.au/data/"
        self.session = requests.Session()

    def get(self, path: str) -> dict:
        """HTTP GET"""
        response = self.session.get(self.base_url + path)
        response.raise_for_status()
        return response.json()

    def get_timeline(self) -> list:
        """Get timeline data"""
        return cast(list, self.get("timeline.json"))

    def get_global(self) -> dict:
        """Get global data"""
        return self.get("global.json")

    @lru_cache
    def markers(self, ftype: str = "camp") -> list:
        """Grab all the datapoints, filtering by feature type"""
        markers = self.get("map/markers.geo.json")["features"]
        return [x for x in markers if x["properties"]["type"] == ftype]

    @lru_cache
    def _get_data_by_id(self, feature_id: int) -> dict:
        """Return detailed information for a given camp"""
        return self.get(f"map/camp/{feature_id}.json")

    def get_feature_by_id(self, feature_id: int) -> Feature:
        """Instantiate a Feature object for a given marker"""
        return Feature(self._get_data_by_id(feature_id))

    def get_features(self, ftype: str = "camp") -> Iterator:
        """Like get_markers, but returns an iterator of Features"""
        for marker in self.markers(ftype):
            yield self.get_feature_by_id(marker["properties"]["ID"])

def main() -> None:
    """Entry point"""
    xjdp = XJDP()
    features = xjdp.get_features()
    for camp in features:
        print(camp.id, "\t", camp.title)

if __name__ == "__main__":
    main()
