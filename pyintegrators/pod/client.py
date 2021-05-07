# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/pod.client.ipynb (unless otherwise specified).

__all__ = ['DEFAULT_POD_ADDRESS', 'POD_VERSION', 'PodClient']

# Cell
from ..data.itembase import Edge, ItemBase
from ..indexers.facerecognition.photo import resize
from ..data.schema import *
from ..imports import *
from hashlib import sha256

# Cell
DEFAULT_POD_ADDRESS = "http://localhost:3030"
POD_VERSION = "v3"

# Cell
class PodClient:

    def __init__(self, url=DEFAULT_POD_ADDRESS, version=POD_VERSION, database_key=None, owner_key=None):
        self.url = url
        self.version = POD_VERSION
        self.test_connection(verbose=False)
        self.database_key=database_key if database_key is not None else self.generate_random_key()
        self.owner_key=owner_key if owner_key is not None else self.generate_random_key()
        self.base_url = f"{url}/{version}/{self.owner_key}"
        self.auth_json = {"type":"ClientAuth", "databaseKey": self.database_key}


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
        if isinstance(node, Photo) and not self.create_photo_file(node): return False

        try:
            properties = self.get_properties_json(node)
            properties = {k:v for k, v in properties.items() if v != []}
            print(properties)
            body = {"auth": self.auth_json, "payload":properties}

            result = requests.post(f"{self.base_url}/create_item", json=body)
            if result.status_code != 200:
                print(result, result.content)
                return False
            else:
                id = int(result.json())
                node.id = id
                ItemBase.add_to_db(node)
                return True
        except requests.exceptions.RequestException as e:
            print(e)
            return False

    def add_to_schema(self, node):
        attributes = self.get_properties_json(node)
        for k, v in attributes.items():
            if not isinstance(v, list) and k != "type":
                if isinstance(v, str):
                    value_type = "Text"
                elif isinstance(v, int):
                    value_type = "Integer"

                payload = {"type": "ItemPropertySchema", "itemType": attributes["type"],
                           "propertyName": k, "valueType": value_type}

                body = {"auth": self.auth_json, "payload": payload }

                try:
                    result = requests.post(f"{self.base_url}/create_item", json=body)

                    if result.status_code != 200:
                        print(result, result.content)
                        return False
                    else:
                        id = int(result.json())
                        node.id = id
                        ItemBase.add_to_db(node)

                except requests.exceptions.RequestException as e:
                    print(e)
                    return False
        return True

    def create_photo_file(self, photo):
        file = photo.file[0]
        self.create(file)
        return self.upload_photo(photo.data)

    def upload_photo(self, arr):
        return self.upload_file(arr.tobytes())

    def upload_file(self, file):
        # TODO: currently this only works for numpy images
        try:
            sha = sha256(file).hexdigest()
            result = requests.post(f"{self.base_url}/upload_file/{self.database_key}/{sha}", data=file)
            if result.status_code != 200:
                print(result, result.content)
                return False
            else:
                return True
        except requests.exceptions.RequestException as e:
            print(e)
            return False

    def get_file(self, sha):
        # TODO: currently this only works for numpy images
        try:
            body= {"databaseKey": self.database_key, "payload": {"sha256": sha}}
            result = requests.post(f"{self.base_url}/get_file", json=body)
            if result.status_code != 200:
                print(result, result.content)
                return None
            else:
                return result.content
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def get_photo(self, id, size=640):
        photo = self.get(id)
        self._load_photo_data(photo, size=size)
        return photo

    def _load_photo_data(self, photo, size=None):
        if len(photo.file) > 0 and photo.data is None:
            file = self.get_file(photo.file[0].sha256)
            if file is None:
                print(f"Could not load data of {photo} attached file item does not have data in pod")
                return
            data = np.frombuffer(file, dtype=np.uint8)
            c = photo.channels
            shape = (photo.height,photo.width, c) if c is not None and c > 1 else (photo.height, photo.width)
            data = data.reshape(shape)
            if size is not None: data = resize(data, size)
            photo.data = data
            return
        print(f"could not load data of {photo}, no file attached")

    def create_if_external_id_not_exists(self, node):
        if not self.external_id_exists(node):
            self.create(node)

    def external_id_exists(self, node):
        if node.externalId is None: return False
        existing = self.search_by_fields({"externalId": node.externalId})
        return len(existing) > 0

    def create_edges(self, edges):
        """Create edges between nodes, edges should be of format [{"_type": "friend", "_source": 1, "_target": 2}]"""
        create_edges = []
        for e in edges:
            src, target = e.source.id, e.target.id

            if src is None or target is None:
                print(f"Could not create edge {e} missing source or target id")
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
        ids = [i.id for i in items]
        return self.bulk_action(delete_items=ids)

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

    def get(self, id, expanded=True):
        if not expanded:
            res = self._get_item_with_properties(id)
        else:
            res = self._get_item_expanded(id)
        if res is None:
            return None

        elif res.deleted == True:
            print(f"Item with id {id} does not exist anymore")
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

    def _get_item_expanded(self, id):
        body = {"payload": [id],
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

    def _get_item_with_properties(self, id):
        try:
            body = {"auth": self.auth_json,
                    "payload": str(id)}
#             print(f"{self.base_url}/get_item")
#             print(body)
            result = requests.post(f"{self.base_url}/get_item", json=body)
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
        private = getattr(node, "private", [])
        for k, v in node.__dict__.items():
#             if k[:1] != '_' and k != "private" and k not in private and not (isinstance(v, list)\
#                             and len(v)>0 and isinstance(v[0], Edge)) and v is not None:
            if k[:1] != '_' and k != "private" and k != "id" and k not in private and not (isinstance(v, list)) \
                            and v is not None:
                res[k] = v
        res["type"] = self._get_schema_type(node)
        return res

    @staticmethod
    def _get_schema_type(node):
        for cls in node.__class__.mro():
            if cls.__module__ == "pyintegrators.data.schema" and cls.__name__ != "ItemBase":
                return cls.__name__
        raise ValueError

    def update_item(self, node):
        data = self.get_properties_json(node)
        id = data["id"]
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
            result = requests.post(f"{self.base_url}/search_by_fields", json=body)
            json =  result.json()
            res = [self.item_from_json(item) for item in json]
            return self.filter_deleted(res)
        except requests.exceptions.RequestException as e:
            return None

    def item_from_json(self, json):
        indexer_class = json.get("indexerClass", None)
        constructor = get_constructor(json["_type"], indexer_class)
        new_item = constructor.from_json(json)
        existing = ItemBase.global_db.get(new_item.id)
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

    def run_importer(self, id, servicePayload):

        body = dict()
        body["databaseKey"] = servicePayload["databaseKey"]
        body["payload"] = {"id": id, "servicePayload": servicePayload}

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