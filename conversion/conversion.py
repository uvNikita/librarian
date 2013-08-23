# coding: utf-8

import os
import pkgutil
import zipfile
import tempfile
import shutil
from StringIO import StringIO

from lxml import etree

__all__ = ("fb2_2_epub", )


container_xml_content = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf"
     media-type="application/oebps-package+xml" />
  </rootfiles>
</container>
"""


def _convert_fb2(fb2_tree, format):
    xsl = pkgutil.get_data('conversion', 'res/fb2_2_%s.xsl' % format)
    if not xsl:
        raise RuntimeError("No res/fb2_2_%s.xsl found" % format)
    convertor = etree.XSLT(etree.XML(xsl))
    return convertor(fb2_tree)


def _create_opf(fb2_tree, dest_dir, filename='content.opf'):
    opf_tree = _convert_fb2(fb2_tree, 'opf')
    dest_path = os.path.join(dest_dir, filename)
    with open(dest_path, 'w') as opf_file:
        opf_tree.write(opf_file)
    return dest_path


def _create_html(fb2_tree, dest_dir, filename='index.html'):
    html_tree = _convert_fb2(fb2_tree, 'html')
    dest_path = os.path.join(dest_dir, filename)
    with open(dest_path, 'w') as html_file:
        html_tree.write(html_file)
    return dest_path


def _create_ncx(fb2_tree, dest_dir, filename='book.ncx'):
    ncx_tree = _convert_fb2(fb2_tree, 'ncx')
    dest_path = os.path.join(dest_dir, filename)
    with open(dest_path, 'w') as ncx_file:
        ncx_tree.write(ncx_file)
    return dest_path


def _create_mimetype(dest_dir):
    dest_path = os.path.join(dest_dir, 'mimetype')
    with open(dest_path, 'w') as mime_file:
        mime_file.write('application/epub+zip')
    return dest_path


def _create_container_xml(dest_dir):
    dest_path = os.path.join(dest_dir, 'container.xml')
    with open(dest_path, 'w') as container_file:
        container_file.write(container_xml_content)
    return dest_path


def fb2_2_epub(fb2_file, filename):
    fb2_tree = etree.parse(fb2_file)
    tmp_path = tempfile.mkdtemp(prefix='librarian.', suffix=filename)

    mime_file = _create_mimetype(tmp_path)
    container_file = _create_container_xml(tmp_path)
    opf_file = _create_opf(fb2_tree, tmp_path)
    html_file = _create_html(fb2_tree, tmp_path)
    ncx_file = _create_ncx(fb2_tree, tmp_path)

    epub_file = StringIO()
    with zipfile.ZipFile(epub_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(mime_file, 'metadata', zipfile.ZIP_STORED)
        zip_file.write(container_file, 'META-INF/container.xml')
        zip_file.write(opf_file, 'OEBPS/content.opf')
        zip_file.write(html_file, 'OEBPS/index.html')
        zip_file.write(ncx_file, 'OEBPS/book.ncx')
    shutil.rmtree(tmp_path)

    return epub_file
