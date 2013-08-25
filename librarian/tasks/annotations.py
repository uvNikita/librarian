# encoding: utf-8

from lxml import etree

from librarian.models import db, Book


FB2_NS = 'http://www.gribuser.ru/xml/fictionbook/2.0'
EMPTY_LINE_TAG = '{%s}empty-line' % FB2_NS
ANNOTATION_TAG = '{%s}annotation' % FB2_NS


def _trace_tree(tag):
    if tag.text:
        return tag.text
    if tag.tag == EMPTY_LINE_TAG:
        return '\n'
    text = ' '.join(_trace_tree(child) for child in tag.iterchildren())
    return text


def extract_annotation(fb2_file):
    fb2_tree = etree.parse(fb2_file)
    elems = fb2_tree.findall('.//%s' % ANNOTATION_TAG)
    root_elem = elems[0] if elems else None
    if root_elem is not None:
        return _trace_tree(root_elem)
    return None


def fill_annotations(inpx_file):
    for id_, fb2_file in inpx_file:
        annotation = extract_annotation(fb2_file)
        if annotation:
            book = Book.get(id_)
            if book:
                book.annotation = annotation
    db.session.flush()

