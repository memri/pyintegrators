# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/indexers.NoteListIndexer.Parser.ipynb (unless otherwise specified).

__all__ = ['HTMLListParser', 'LISTTYPE_VERBS', 'LIST_PREFIXES']

# Cell
import bs4
import random
from .util import *
from .notelist import *
from ...data.schema import *
from ...data.basic import *
from ...imports import *

# Cell

LISTTYPE_VERBS = ["do", "read", "watch", "buy", "listen"]
LIST_PREFIXES = ["to", "to-", "to ", ""]

class HTMLListParser():
    '''Extracts lists from HTML data, generated by an HTML text editor like evernote'''

    def __init__(self):
        self.single_item_list_patterns = [p+v for v in LISTTYPE_VERBS for p in LIST_PREFIXES]

    def get_html_lists(self, note, parsed):
        html_lists = parsed.find_all("ul", recursive=False) + parsed.find_all("ol", recursive=False)
        return [ULNoteList.from_data(title=None, content=str(x), textContent=x.get_text(),
                                     note=note, span=get_span(x, parsed)) for x in html_lists]

    def get_lists(self, note):
        """Extracts lists from a note"""
        parsed = bs4.BeautifulSoup(note.content, 'html.parser')
        note.content=str(parsed)

        all_lists = self.get_html_lists(note, parsed) + \
                    self.get_unformatted_lists(note, parsed)
        for l in all_lists: note.add_edge("noteList", l)

        return all_lists

    def parse(self, x, tag=None):
        if isinstance(x, bs4.BeautifulSoup): return x.find(tag) if tag is not None else x
        elif isinstance(x, bs4.element.Tag): return x
        else:
            res =  bs4.BeautifulSoup(x, 'html.parser')
            return res.find(tag) if tag is not None else res

    def get_single_line_list(self, par):
        """Get single list lists. An example could be: '<strong>read</strong>: great book title'"""
        par = self.parse(par, "p")
        par_html = "".join(mapped(str, par.contents))

        pat = "|".join([f"(<strong>|<em>|<u>)?{v}:? ?(</strong>|</em>|</u>)?:? ?"
                        for v in LISTTYPE_VERBS])
        match = re.search(pat, par_html, re.IGNORECASE)
        if match is None: return None, None

        title_html = match.group() if match is not None else None

        if len(par.get_text()) > len(remove_html(title_html)) + 2:
            title = match.group()
            content = par_html[par_html.index(title) + len(title):]
            return title, content
        else:
            return None, None

    def get_unformatted_lists(self, note, parsed):
        """retrieve lists without <ul></ul> tags. We have two options:
                1) multiline lists prefixed with a title keyword (e.g. "Buy:" "Read:")
                2) single element single line lists"""

        parsed = parsed if parsed is not None else self.parse(note.content)
        toplevel_paragraphs = parsed.find_all("p", recursive=False)
        res = []


        for i, par in enumerate(toplevel_paragraphs):
            if is_title(par):
                # this extracts the lists that have a title and are not on a single line
                items = trim_till_newline(list(toplevel_paragraphs)[i+1:])
                if len(items) == 0: continue
                list_span  = Span.from_data(startIdx=get_span(title, parsed).startIdx,
                                            endIdx=get_span(items[-1], parsed).endIdx)

                l = INoteList.from_data(note=note,span=list_span,
                                        title=str(par.contents[0]),
                                        content="".join(mapped(str,items)),
                                        itemSpan=[get_span(x, parsed) for x in items])
                res.append(l)

            else:
                title, html_content = self.get_single_line_list(par)
                if title is not None:
                    span = get_span(str(par), parsed)
                    itemSpans = [Span.from_data(startIdx=span.startIdx + len(str(title)),
                                                endIdx=span.endIdx)]
                    l = INoteList.from_data(note=note, title=title, content=str(html_content),
                                            itemSpan=itemSpans, span=get_span(par, parsed))
                    res.append(l)
        return res