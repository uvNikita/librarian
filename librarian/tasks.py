#  coding: utf-8
import logging
import tempfile
import os
import shutil
from functools import wraps
from zipfile import ZipFile

from lxml import etree
from celery import Celery

from librarian import app
from librarian.models import db, Book, Author, Genre, Sequence


log = logging.getLogger(__name__)

celery = Celery(__name__)
celery.conf.update(app.config)


def with_context(task):
    @wraps(task)
    def wrapper(*args, **kwargs):
        with app.app_context():
            return task(*args, **kwargs)

    return wrapper


@celery.task
@with_context
def add_books_from_inp(path):
    """
    Add books and create all need entities from parsed .inp file
    :type path: str
    :param path: path to .inp file
    """
    log.info("Start to process {file}".format(file=path))
    with open(path) as inp_file:
        for line in inp_file:
            (unparsed_authors, gen_titles, title,
             seq_title, sequence_number, id_) = line.split('\x04')[:6]
            # Do nothing if book already exists in library
            if Book.query.get(id_) is not None:
                continue
            unparsed_authors = unparsed_authors.split(':')[:-1]
            authors = []
            for unparsed_author in unparsed_authors:
                unparsed_author = unparsed_author.split(',')
                last_name = unparsed_author[0]
                first_name = unparsed_author[1] or None
                db_author = Author.query.filter_by(
                    first_name=first_name,
                    last_name=last_name
                ).first()
                if db_author:
                    authors.append(db_author)
                else:
                    authors.append(Author(
                        first_name=first_name,
                        last_name=last_name
                    ))

            gen_titles = gen_titles.split(':')[:-1]
            genres = []
            for gen_title in gen_titles:
                db_genre = Genre.query.filter_by(title=gen_title).first()
                if db_genre:
                    genres.append(db_genre)
                else:
                    genres.append(Genre(title=gen_title))

            if seq_title:
                db_sequence = Sequence.query.filter_by(title=seq_title).first()
                sequence = db_sequence or Sequence(title=seq_title)
            else:
                sequence = None
            sequence_number = int(sequence_number) if sequence_number else None

            id_ = int(id_)
            book = Book(
                id=id_,
                title=title,
                authors=authors,
                genres=genres,
                sequence=sequence,
                sequence_number=sequence_number,
                annotation=None
            )

            db.session.add(book)
            db.session.flush()
        db.session.commit()
    log.info("Finish to process {file}".format(file=path))


@celery.task
@with_context
def add_books_from_inpx(path):
    tmp_path = tempfile.mkdtemp(prefix='librarian.', suffix='-inpx')
    log.info(u"Extracting archive {a} to {d}".format(a=path, d=tmp_path))
    with ZipFile(path) as inpx_file:
        names = inpx_file.namelist()
        names = filter(lambda name: name.endswith('.inp'), names)
        for name in names:
            inpx_file.extract(name, tmp_path)
    log.info("Done")
    log.info(u"Going to process files: {files}".format(files=names))
    try:
        for name in names:
            inp_file_path = os.path.join(tmp_path, name)
            add_books_from_inp(inp_file_path)
    finally:
        shutil.rmtree(tmp_path)


FB2_NS = 'http://www.gribuser.ru/xml/fictionbook/2.0'
EMPTY_LINE_TAG = '{%s}empty-line' % FB2_NS
ANNOTATION_TAG = '{%s}annotation' % FB2_NS


@celery.task
@with_context
def fill_annotations(zip_path):
    total = updated = bad = 0
    with ZipFile(zip_path, 'r') as zip_file:
        for fb2_filename in zip_file.namelist():
            total += 1
            fb2_file = zip_file.open(fb2_filename)
            id_ = int(fb2_filename.split('.')[0])
            annotation = None
            try:
                annotation = extract_annotation(fb2_file)
            except etree.XMLSyntaxError:
                bad += 1
                log.warn(u"Not well-formed xml in %s", fb2_filename)

            if annotation:
                book = Book.query.get(id_)
                if book:
                    updated += 1
                    book.annotation = annotation
                    db.session.flush()
    log.info("Finish parsing annotation from %s: total(%d), updated(%d), bad(%d)",
             zip_path, total, updated, bad)
    db.session.commit()


@celery.task
@with_context
def fill_annotations_from_dir(dir_path):
    log.info(u"Going to parse annotations from {}".format(dir_path))
    for filename in os.listdir(dir_path):
        if filename.endswith('.zip'):
            fill_annotations(os.path.join(dir_path, filename))


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
