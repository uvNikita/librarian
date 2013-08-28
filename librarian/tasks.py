#  coding: utf-8

from functools import wraps
from zipfile import ZipFile

from lxml import etree
from celery import Celery

from librarian import app
from librarian.models import db, Book


celery = Celery(__name__)
celery.conf.update(app.config)


def with_context(task):
    @wraps(task)
    def wrapper(*args, **kwargs):
        with app.test_request_context():
            return task(*args, **kwargs)
    return wrapper


@celery.task
@with_context
def add_books_from_inp(path):
    print "Hello from add_books_from_inp"


@celery.task
@with_context
def add_books_from_inpx(path):
    pass


FB2_NS = 'http://www.gribuser.ru/xml/fictionbook/2.0'
EMPTY_LINE_TAG = '{%s}empty-line' % FB2_NS
ANNOTATION_TAG = '{%s}annotation' % FB2_NS


@celery.task
@with_context
def fill_annotations(zip_path):
    with ZipFile(zip_path, 'r') as zip_file:
        for fb2_filename in zip_file.namelist():
            fb2_file = zip_file.open(fb2_filename)
            id_ = int(fb2_filename.split('.')[0])
            annotation = None
            try:
                annotation = extract_annotation(fb2_file)
            except etree.XMLSyntaxError:
                print 'error in', fb2_filename

            if annotation:
                book = Book.query.get(id_)
                if book:
                    book.annotation = annotation
                    print book.id
                    db.session.flush()
    db.session.commit()


def extract_annotation(fb2_file):
    def _trace_tree(tag):
        if tag.text:
            return tag.text
        if tag.tag == EMPTY_LINE_TAG:
            return '\n'
        text = ' '.join(_trace_tree(child) for child in tag.iterchildren())
        return text

    fb2_tree = etree.parse(fb2_file)
    elems = fb2_tree.findall('.//%s' % ANNOTATION_TAG)
    root_elem = elems[0] if elems else None
    if root_elem is not None:
        return _trace_tree(root_elem)
    return None

