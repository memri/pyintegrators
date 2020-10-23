# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/indexers.NoteListIndexer.NoteList.ipynb (unless otherwise specified).

__all__ = ['LIST_CLASSES', 'INote', 'INoteList', 'ULNoteList', 'ISpan', 'get_span']

# Cell
from ...data.schema import *
from .util import *

# Cell
TODO, TOWATCH, TOREAD, TOLISTEN, TOBUY, UNKOWN = "todo","towatch", "toread", "tolisten", "tobuy", "unknown"
LIST_CLASSES = [TODO, TOWATCH, TOREAD, TOLISTEN, TOBUY, UNKOWN]

# Cell
class INote(Note):

    def __repr__(self):
        content = self.content[:50] + " ..." if len(self.content) > 20 else self.content
        return f"INote (#{self.uid}) {content}"

    def show(self):
        print(f"INote (#{self.uid}) {self.content}")


# Cell
class INoteList(NoteList):
    def __str__(self):
        return str(self.content)

    def infer_cat_from_title(self):
        if self.title is None: return None
        if contains(self.title, "do"): return TODO
        if contains(self.title, "read"): return TOREAD
        if contains(self.title, "watch"): return TOWATCH
        if contains(self.title, "listen"): return TOLISTEN
        if contains(self.title, "buy"): return TOBUY
        else: return None

    def get_items(self, remove_html_=False, skip_nested=True):

        if self.itemSpan is not None:
            return [str(self.note.content)[s.startIdx:s.endIdx] for s in self.itemSpan]

        else:
            return []

    def __repr__(self):
        cat_str = f"({self.category})" if self.category   is not None else ""
        title = remove_html(self.title) if self.title is not None else "Untitled"
        return f"(INoteList) # {title} {cat_str}\n{self.content}\n\n"

    def __eq__(self, other):
        return self.uid == other.uid


# Cell
class ULNoteList(INoteList):
    '''A <ul> </ul> list extracted from a note. '''

    def get_items(self, remove_html_=False, skip_nested=False):

        if self.content is None: return [self.textContent]

        result = [i for i in get_toplevel_elements(str(self.content), "li")
                  if len(i("ul")) == 0]

        if remove_html_: result = [remove_html(str(x)) for x in result]
        result = [str(x) for x in result if x != ""]
        return result

    def __repr__(self):
        items = "\n".join(self.get_items(remove_html_=True))
        cat_str = f"({self.category})" if self.category is not None else ""
        title = remove_html(self.title) if self.title is not None else "Untitled"
        return f"ULNoteList # {title} {cat_str}\n{items}\n\n"

# Cell
class ISpan(Span):
    '''A span of an element in a piece of text'''

    def __eq__(self, other):
        return self.startIdx == other.startIdx and self.endIdx == other.endIdx

    def __repr__(self):
        return f"ISpan [{self.startIdx}, {self.endIdx}]"

# Cell
def get_span(note, elem, parsed):
    e_str = str(elem)
    parsed_str = str(parsed)

    begin = parsed_str.find(e_str)
    end = begin + len(e_str)

    return ISpan.from_data(startIdx=begin, endIdx=end)