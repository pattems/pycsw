# =================================================================
#
# Authors: Ricardo Garcia Silva <ricardo.garcia.silva@gmail.com>
#
# Copyright (c) 2017 Ricardo Garcia Silva
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================
"""Unit tests for pycsw.core.metadata"""

import pytest

from pycsw.core import metadata
from pycsw.core.config import StaticContext
from pycsw.core.etree import etree

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("bboxes, expected", [
    (
        [
            "POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))",
            "POLYGON ((2 2, 2 3, 3 3, 3 2, 2 2))",
        ],
        "POLYGON((0.00 0.00, 0.00 3.00, 3.00 3.00, 3.00 0.00, 0.00 0.00))"
    ),
])
def test_bbox_from_polygons(bboxes, expected):
    result = metadata.bbox_from_polygons(bboxes)
    assert result == expected


def test_bbox_from_polygons_invalid():
    bboxes = "stuff"
    with pytest.raises(RuntimeError):
        metadata.bbox_from_polygons(bboxes)


class _Dataset:
    pass


class _Repository:
    dataset = _Dataset


@pytest.mark.parametrize("record", [
    b'<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd" '
    b'xmlns:gco="http://www.isotc211.org/2005/gco">'
    b'<gmd:fileIdentifier><gco:CharacterString>no-identification'
    b'</gco:CharacterString></gmd:fileIdentifier></gmd:MD_Metadata>',
    b'<mdb:MD_Metadata xmlns:mdb="http://standards.iso.org/iso/19115/-3/mdb/2.0" '
    b'xmlns:mcc="http://standards.iso.org/iso/19115/-3/mcc/1.0" '
    b'xmlns:gco="http://standards.iso.org/iso/19115/-3/gco/1.0">'
    b'<mdb:metadataIdentifier><mcc:MD_Identifier><mcc:code>'
    b'<gco:CharacterString>no-identification</gco:CharacterString>'
    b'</mcc:code></mcc:MD_Identifier></mdb:metadataIdentifier>'
    b'</mdb:MD_Metadata>',
])
def test_parse_iso_no_identification(record):
    context = StaticContext()
    exml = etree.fromstring(record, context.parser)
    recobj = metadata._parse_iso(context, _Repository(), exml)
    mappings = context.md_core_model['mappings']
    assert getattr(recobj, mappings['pycsw:Identifier']) == 'no-identification'
    assert getattr(recobj, mappings['pycsw:BoundingBox']) is None
