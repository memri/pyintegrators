# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/indexers.NoteListIndexer.ipynb (unless otherwise specified).

__all__ = ['NotesListIndexer', 'ListTypePredictor']

# Cell
from .util import *
from .notelist import *
from ..indexer import *
from .parser import *
from ...data.schema import *
from ...data.basic import *
from ...imports import *
from ...pod.client import PodClient

# Cell
import spacy
# from imdb import  IMDb

class NotesListIndexer(Indexer):
    """Extracts lists from notes and categorizes them."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_data(self, client):
        notes  = [d.expand(client) for d in indexer_run.get_data(client)]
        return notes

    def index(self, client, indexer_run, notes):
        """Run indexer"""
        predictor = ListTypePredictor()
        for note in notes:
            parser = HTMLListParser()
            lists = parser.get_lists(note)
            for l in lists:
                cat = l.infer_cat_from_title()
                if cat is not None:
                    l.category = cat
                else:
                    predictor.predict(l, assign=True)

        spans = [l.span for l in lists]

        updates_nodes = notes
        new_nodes = lists + spans

        return updates_nodes, new_nodes

class ListTypePredictor():
    """Predicts one of `LIST_CLASSES` for a list in a note."""

    def __init__(self):
        self.classes = LIST_CLASSES
        self.nlp = spacy.load("en_core_web_md")
#         self.ia  = IMDb()
        self.verb_like_tags = ["VB", "VBP"]


    def predict(self, l, assign=False):
        items = l.get_items(remove_html_=True)
        preds = []

        for item in items:
            preds.append(self.predict_item(item))

        pred = max(set(preds), key=preds.count)

        if assign: l.category = pred

        return pred

    def predict_item(self, item):
        if   self.is_movie(item):   return "towatch"
        elif self.is_toread(item):  return "toread"
        elif self.is_podcast(item): return "tolisten"
        elif self.is_tobuy(item):   return "tobuy"
        elif self.is_todo(item):    return "todo"
        else:                       return "uknown"


    def is_todo(self, item):
        doc = self.nlp(item)
        if doc[0].tag_ in self.verb_like_tags: return True
        else: return False


    def is_movie(self, item):
#         result = self.ia.search_movie(item)
#         print(result)
        return False

    def is_toread(self, item):
        return False

    def is_podcast(self, item):
        return False

    def is_tobuy(self, item):
        return False