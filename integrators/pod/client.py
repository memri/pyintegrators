# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/pod.client.ipynb (unless otherwise specified).

__all__ = ['DEFAULT_POD_ADDRESS', 'PodClient']

# Cell
from ..data.itembase import Edge, ItemBase
from ..data.schema import *
from ..imports import *

# Cell
DEFAULT_POD_ADDRESS = "http://localhost:3030/v2"

# Cell
class PodClient:

    def __init__(self, url=DEFAULT_POD_ADDRESS, database_key=None, owner_key=None):
        self.url = url
        self.test_connection(verbose=False)
        self.database_key=database_key if database_key is not None else self.generate_random_key()
        self.owner_key=owner_key if owner_key is not None else self.generate_random_key()
        self.base_url = f"{url}/{self.owner_key}"

    @staticmethod
    def generate_random_key():
        return "".join([str(random.randint(0, 9)) for i in range(64)])

    def test_connection(self, verbose=True):
        try:
            res = requests.get(self.url)
            if verbose: print("Succesfully connected to pod")
            return True
        except requests.exceptions.RequestException as e:
            print("Could no connect to backend")
            return False

    def create(self, node):
        try:
            body = {  "databaseKey": self.database_key, "payload":self.get_properties_json(node) }

            result = requests.post(f"{self.base_url}/create_item",
                                   json=body)
            if result.status_code != 200:
                print(result, result.content)
                return False
            else:
                uid = int(result.json())
                node.uid = uid
                ItemBase.add_to_db(node)
                return True
        except requests.exceptions.RequestException as e:
            print(e)
            return False

    def create_edges(self, edges):
        """Create edges between nodes, edges should be of format [{"_type": "friend", "_source": 1, "_target": 2}]"""
        create_edges = []
        for e in edges:
            src, target = e.source.uid, e.target.uid

            if src is None or target is None:
                print(f"Could not create edge {e} missing source or target uid")
                return False
            data = {"_source": src, "_target": target, "_type": e._type}
            if e.label is not None: data[LABEL] = e.label
            if e.sequence is not None: data[SEQUENCE] = e.sequence

            if e.reverse:
                data2 = copy(data)
                data2["_source"] = target
                data2["_target"] = src
                data2["_type"] = "~" + data2["_type"]
                create_edges.append(data2)

            create_edges.append(data)

        return self.bulk_action(create_items=[], update_items=[],create_edges=create_edges)

    def delete_items(self, items):
        uids = [i.uid for i in items]
        return self.bulk_action(delete_items=uids)

    def delete_all(self):
        items = self.get_all_items()
        self.delete_items(items)

    def bulk_action(self, create_items=None, update_items=None, create_edges=None, delete_items=None):
        create_items = create_items if create_items is not None else []
        update_items = update_items if update_items is not None else []
        create_edges = create_edges if create_edges is not None else []
        delete_items = delete_items if delete_items is not None else []
        edges_data = {"databaseKey": self.database_key, "payload": {
                    "createItems": create_items, "updateItems": update_items,
                    "createEdges": create_edges, "deleteItems": delete_items}}
        try:
            result = requests.post(f"{self.base_url}/bulk_action",
                                   json=edges_data)
            if result.status_code != 200:
                if "UNIQUE constraint failed" in str(result.content):
                    print(result.status_code, "Edge already exists")
                else:
                    print(result, result.content)
                return False
            else:
                return True
        except requests.exceptions.RequestException as e:
            print(e)
            return False

    def create_edge(self, edge):
        return self.create_edges([edge])

    def get(self, uid, expanded=True):
        if not expanded:
            res = self._get_item_with_properties(uid)
        else:
            res = self._get_item_expanded(uid)
        if res is None:
            return None

        elif res.deleted == True:
            print(f"Item with uid {uid} does not exist anymore")
            return None
        else:
            return res

    def get_all_items(self):
        try:
            body = {  "databaseKey": self.database_key, "payload":None}
            result = requests.post(f"{self.base_url}/get_all_items", json=body)
            if result.status_code != 200:
                print(result, result.content)
                return None
            else:
                json = result.json()
                res =  [self.item_from_json(x) for x in json]
                return self.filter_deleted(res)

        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def filter_deleted(self, items):
        return [i for i in items if not i.deleted == True]

    def _get_item_expanded(self, uid):
        body = {"payload": [uid],
                "databaseKey": self.database_key}
        try:
            result = requests.post(f"{self.base_url}/get_items_with_edges",
                                    json=body)
            if result.status_code != 200:
                print(result, result.content)
                return None
            else:
                json = result.json()[0]
                res =  self.item_from_json(json)
                return res

        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def _get_item_with_properties(uid):
        try:
            result = requests.get(f"{self.base_url}/items/{uid}")
            if result.status_code != 200:
                print(result, result.content)
                return None
            else:
                json = result.json()
                if json == []:
                    return None
                else:
                    return json
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def get_properties_json(self, node):
        res = dict()
        for k,v in node.__dict__.items():
            if k[:1] != '_' and not (isinstance(v, list) and len(v)>0 and isinstance(v[0], Edge)) and v is not None:
                res[k] = v
        res["_type"] = self._get_schema_type(node)
        return res

    @staticmethod
    def _get_schema_type(node):
        for cls in node.__class__.mro():
            if cls.__module__ == "integrators.data.schema" and cls.__name__ != "ItemBase":
                return cls.__name__
        raise ValueError

    def update_item(self, node):
        data = self.get_properties_json(node)
        uid = data["uid"]
        body = {"payload": data,
                "databaseKey": self.database_key}

        try:
            result = requests.post(f"{self.base_url}/update_item",
                                  json=body)
            if result.status_code != 200:
                print(result, result.content)
        except requests.exceptions.RequestException as e:
            print(e)

    def search_by_fields(self, fields_data):

        body = {"payload": fields_data,
                "databaseKey": self.database_key}
        try:
            result = requests.post(f"{self.base_url}/search_by_fields",
                                   json=body)
            json =  result.json()
            res = [self.item_from_json(item) for item in json]
            return self.filter_deleted(res)
        except requests.exceptions.RequestException as e:
            return None

    def item_from_json(self, json):
        indexer_class = json.get("indexerClass", None)
        constructor = get_constructor(json["_type"], indexer_class)
        new_item = constructor.from_json(json)
        existing = ItemBase.global_db.get(new_item.uid)
        # TODO: cleanup
        if existing is not None:
            if not existing.is_expanded() and new_item.is_expanded():
                for edge_name in new_item.get_all_edge_names():
                    edges = new_item.get_edges(edge_name)
                    for e in edges:
                        e.source = existing
                    existing.__setattr__(edge_name, edges)

            for prop_name in new_item.get_property_names():
                existing.__setattr__(prop_name, new_item.__getattribute__(prop_name))
            return existing
        else:
            return new_item

    def get_properties(self, expanded):
        properties = copy(expanded)
        if ALL_EDGES in properties: del properties[ALL_EDGES]
        return properties

    def run_importer(self, uid, servicePayload):

        body = dict()
        body["databaseKey"] = servicePayload["databaseKey"]
        body["payload"] = {"uid": uid, "servicePayload": servicePayload}

        print(body)

        try:
            res = requests.post(f"{self.base_url}/run_importer", json=body)
            # res = requests.post(self.url)
            if res.status_code != 200:
                print(f"Failed to start importer on {url}:\n{res.status_code}: {res.text}")
            else:
                print("Starting importer")
        except requests.exceptions.RequestException as e:
            print("Error with calling importer {e}")