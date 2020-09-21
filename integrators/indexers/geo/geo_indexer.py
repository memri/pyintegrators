# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/indexers.GeoIndexer.ipynb (unless otherwise specified).

__all__ = ['GeoIndexer', 'LOCATION_EDGE']

# Cell
from ...data.schema import *
from ...data.itembase import *
from ...pod.client import PodClient
from ..indexer import IndexerBase, get_indexer_run_data, IndexerData, test_registration
from .. import *
import pycountry, requests
import reverse_geocoder as rg

# Cell

LOCATION_EDGE = "hasLocation"

class GeoIndexer(IndexerBase):
    """Adds Countries and Cities to items with a location."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def latlong2citycountry(self, latlong):
        geo_result = rg.search([latlong])[0]
        city_name = geo_result["name"]
        country_name = pycountry.countries.get(alpha_2=geo_result["cc"]).name
        return city_name, country_name

    def get_country_by_name(self, client, name):
        data = client.search_by_fields({"_type": "Country", "name": name})
        if data == None or data == []: return None
        else:
            return data[0]

    def get_lat_long(self, item):
        locations = item.location
        if len(locations) != 1:
            print(f"skipping item {item}, found {len(locations)} locations")
            return None, True

        latlong = locations[0].latitude, locations[0].longitude

        if None in latlong:
            print(f"skipping item {item}, incomplete latlong")
            None, True

        return latlong, False

    def get_data(self, client, indexer_run):
        items_expanded      = [d.expand(client) for d in get_indexer_run_data(client, indexer_run)]
        items_with_location = [x for x in items_expanded if any([loc.latitude is not None for loc in x.location])]
        print(f"{len(items_with_location)} items found to index")
        return IndexerData(items_with_location=items_with_location)

    def index(self, data, indexer_run, client=None):
        items_with_location = data.items_with_location
        print(f"indexing {len(items_with_location)} items")

        new_nodes = []
        for n, item in enumerate(items_with_location):

            latlong, skip = self.get_lat_long(item)
            if skip: continue

            # get geo info
            city_name, country_name = self.latlong2citycountry(latlong)

            # add information to indexer objects
            item.city = city_name
            # item.add_property("city", city_name)
            country = self.get_country_by_name(client, country_name) if client is not None else None

            if country is None:
                country = Country(name=country_name)
                new_nodes.append(country)

            item.add_edge("country", country)
            # item.country=country/
            # edge = Edge(item, country, "country", created=True)
            # item.add_edge(edge)

            progress = int(n+1 / len(items_with_location) * 100)

            indexer_run.progress=progress
            if client is not None: indexer_run.update(client, edges=False)

            # indexer_run.set_progress(client, progress)

        return items_with_location, new_nodes