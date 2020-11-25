# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/itembase.ipynb (unless otherwise specified).

__all__ = ['ALL_EDGES', 'DB', 'parse_base_item_json', 'Edge', 'ItemBase']

# Cell
# hide
from ..imports import *

ALL_EDGES = "allEdges"
SOURCE, TARGET, TYPE, EDGE_TYPE, LABEL, SEQUENCE = "_source", "_target", "_type", "_type", "label", "sequence"

# Cell
# hide
class DB():
    def __init__(self):
        self.nodes = dict()

    def add(self, node):
        uid = node.uid
        if uid in self.nodes:
            print(f"Error trying to add node, but node with with UID: {uid} is already in database")
        self.nodes[uid] = node

    def get(self, uid):
        res = self.nodes.get(uid, None)
        return res

    def contains(node):
        uid = node.get_property("uid")
        return uid in self.nodes

    def create(self, node):
        existing = self.get(node.properties.get("uid", None))

        if existing is not None:
            if not existing._expanded:
                existing.edges = node.edges
                existing._expanded = node.edges is not None
            return existing
        else:
            self.add(node)
            return node

def parse_base_item_json(json):
    uid = json.get("uid", None)
    dateAccessed = json.get("dateAccessed", None)
    dateCreated = json.get("dateCreated", None)
    dateModified = json.get("dateModified", None)
    deleted = json.get("deleted", None)
    externalId = json.get("externalId", None)
    itemDescription = json.get("itemDescription", None)
    starred = json.get("starred", None)
    version = json.get("version", None)

    return uid, dateAccessed, dateCreated, dateModified, deleted, externalId, itemDescription, starred, version, None, None

# Cell
class Edge():
    """Makes a link between two `ItemBase` Items"""
    def __init__(self, source, target, _type, label=None, sequence=None, created=False, reverse=True):
        self.source   = source
        self.target   = target
        self._type    = _type
        self.label    = label
        self.sequence = sequence
        self.created  = created
        self.reverse  = reverse

    @classmethod
    def from_json(cls, json):
        from .schema import get_constructor
        # we only set the target here
        _type = json[EDGE_TYPE]
        json_target = json[TARGET]
        target_type = json_target["_type"]
        indexer_class = json_target.get("indexerClass", None)
        target_constructor = get_constructor(target_type, indexer_class)
        target = target_constructor.from_json(json_target)
        return cls(source=None, target=target, _type=_type)

    def __repr__(self):
        return f"{self.source} --{self._type}-> {self.target}"

    def update(self, api):
        if self.created:
            api.create_edges([self])

    def __eq__(self, other):
        return self.source is other.source and self.target is other.target \
         and self._type == other._type

    def traverse(self, start):
        """traverse an edge starting from the source to the target or vice versa."""
        if start == self.source:
            return self.target
        elif start == self.target:
            return self.source
        else:
            raise ValueError

# Cell

class ItemBase():
    """Provides a base class for all items. All items in the schema inherit from this class, and it provides some
    basic functionality for consistency and to enable easier usage."""
    global_db = DB()

    def __init__(self, uid=None):
        self.uid=uid
        self.add_to_db(self)

    @classmethod
    def add_to_db(cls, node):
        existing = cls.global_db.get(node.uid)
        if existing is None and node.uid is not None:
            cls.global_db.add(node)

    def replace_self(self, other):
        self.__dict__.update(other.__dict__)

    def __getattribute__(self, name):
        val = object.__getattribute__(self, name)
        if isinstance(val, Edge):
            edge = val
            return edge.traverse(start=self)
        if isinstance(val, list) and len(val) > 0 and isinstance(val[0], Edge):
            edges = val
            return [edge.traverse(start=self) for edge in edges]
        else:
            return val

    def add_edge(self, name, val):
        """Creates an edge of type name and makes it point to val"""
        val = Edge(self, val, name, created=True)
        if name not in self.__dict__:
            raise NameError(f"object {self} does not have edge with name {name}")
        existing = object.__getattribute__(self, name)
        res = existing + [val]
        self.__setattr__(name, res)

    def is_expanded(self):
        """returns whether the node is expanded. An expanded node retrieved nodes that are
        *directly* connected to it
        from the pod, and stored their values via edges in the object."""
        return len(self.get_all_edges()) > 0

    def get_edges(self, name):
        return object.__getattribute__(self, name)

    def get_all_edges(self):
        return [e for attr in self.__dict__.values() if self.attr_is_edge(attr) for e in attr]

    def get_all_edge_names(self):
        return [k for k,v in self.__dict__.items() if self.attr_is_edge(v)]

    def get_property_names(self):
        return [k for k, v in self.__dict__.items() if not type(v) == list]

    @staticmethod
    def attr_is_edge(attr):
        return isinstance(attr, list) and len(attr)>0 and isinstance(attr[0], Edge)

    def update(self, api, edges=True, create_if_not_exists=True, skip_nodes=False):

        if not self.exists(api):
            print(f"creating {self}")
            api.create(self)
        else:
            print(f"updating {self}")
            api.update_item(self)

        if edges:
            for e in self.get_all_edges():
                e.update(api)

    def exists(self, api):
        res = api.search_by_fields({"uid": self.uid})
        if res is None: return False
        return len(res) == 1

    def expand(self, api):
        """Expands a node (retrieves all directly connected nodes ands adds to object)."""
        self._expanded = True
        res = api.get(self.uid, expanded=True)
        for edge_name in res.get_all_edge_names():
            edges = res.get_edges(edge_name)
            for e in edges:
                e.source = self
            self.__setattr__(edge_name, edges)

        # self.edges = res.edges
        return self

    def __repr__(self):
        uid = self.uid
        _type = self.__class__.__name__
        return f"{_type} (#{uid})"

    @classmethod
    def from_data(cls, *args, **kwargs):
        edges = dict()
        new_kwargs = dict()
        for k, v in kwargs.items():
            if isinstance(v, ItemBase):
                edge = Edge(None, v, k)
                edges[k] = edge
                new_kwargs[k] = edge
            else:
                new_kwargs[k] = v

        res = cls(*args, **new_kwargs)

        for v in edges.values():
            v.source = res
        return res

    def inherit_funcs(self, other):
        """This function can be used to inherit new functionalities from a subclass. This is a patch to solve
        the fact that python does provide extensions of classes that are defined in a different file that are
        dynamic enough for our use case."""
        assert issubclass(other, self.__class__)
        self.__class__ = other