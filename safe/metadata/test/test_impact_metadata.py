# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Exception Classes.**

Custom exception classes for the IS application.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '12/10/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# DO NOT REMOVE THIS
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

from datetime import datetime, date
from unittest import TestCase

from PyQt4.QtCore import QDate, QUrl

from safe.common.exceptions import MetadataReadError
from safe.common.utilities import unique_filename

from safe.metadata import ImpactLayerMetadata
from safe.metadata.test import (
    TEMP_DIR,
    EXISTING_IMPACT_JSON,
    EXISTING_IMPACT_FILE, INVALID_IMPACT_JSON,
    INCOMPLETE_IMPACT_JSON, EXISTING_IMPACT_XML, TEST_XML_BASEPATH)


class TestImpactMetadata(TestCase):

    def test_metadata_provenance(self):
        metadata = self.generate_test_metadata()
        self.assertEqual(metadata.provenance.count, 3)
        self.assertEqual(metadata.provenance.last.title, 'Title 3')

    def test_metadata_date(self):
        metadata = ImpactLayerMetadata('random_layer_id')
        path = TEST_XML_BASEPATH + 'gco:Date'

        # using QDate
        test_value = QDate(2015, 6, 7)
        metadata.set('ISO19115_TEST', test_value, path)
        self.assertEqual(metadata.get_xml_value('ISO19115_TEST'), '2015-06-07')

        # using datetime
        test_value = datetime(2015, 6, 7)
        metadata.update('ISO19115_TEST', test_value)
        self.assertEqual(metadata.get_xml_value('ISO19115_TEST'), '2015-06-07')

        # using date
        test_value = date(2015, 6, 7)
        metadata.set('ISO19115_TEST', test_value, path)
        self.assertEqual(metadata.get_xml_value('ISO19115_TEST'), '2015-06-07')

        # using str should fail
        test_value = '2015-06-07'
        with self.assertRaises(TypeError):
            metadata.update('ISO19115_TEST', test_value)

    def test_metadata_url(self):
        metadata = ImpactLayerMetadata('random_layer_id')
        path = TEST_XML_BASEPATH + 'gmd:URL'

        # using QUrl
        test_value = QUrl('http://inasafe.org')
        metadata.set('ISO19115_TEST', test_value, path)
        self.assertEqual(
            metadata.get_xml_value('ISO19115_TEST'), 'http://inasafe.org')

        # using str should work as it is casted
        test_value = 'http://inasafe.org'
        metadata.update('ISO19115_TEST', test_value)

        # using invalid QUrl (has a space)
        test_value = QUrl('http://inasafe.org ')
        with self.assertRaises(ValueError):
            metadata.set('ISO19115_TEST', test_value, path)

    def test_metadata_str(self):
        metadata = ImpactLayerMetadata('random_layer_id')
        path = TEST_XML_BASEPATH + 'gco:CharacterString'

        # using str
        test_value = 'Random string'
        metadata.set('ISO19115_TEST', test_value, path)
        self.assertEqual(
            metadata.get_xml_value('ISO19115_TEST'), 'Random string')

        # using int
        test_value = 1234
        metadata.update('ISO19115_TEST', test_value)
        self.assertEqual(metadata.get_xml_value('ISO19115_TEST'), '1234')

        # using float
        test_value = 1234.5678
        metadata.update('ISO19115_TEST', test_value)
        self.assertEqual(metadata.get_xml_value('ISO19115_TEST'), '1234.5678')

        # using invalid QUrl
        test_value = QUrl()
        with self.assertRaises(TypeError):
            metadata.update('ISO19115_TEST', test_value)

    def test_json_write(self):
        metadata = self.generate_test_metadata()
        with open(EXISTING_IMPACT_JSON) as f:
            expected_json = f.read()

        filename = unique_filename(suffix='.json', dir=TEMP_DIR)
        metadata.write_to_file(filename)
        with open(filename) as f:
            written_json = f.read()

        self.assertEquals(expected_json, written_json)

    def test_json_read(self):
        metadata = ImpactLayerMetadata(EXISTING_IMPACT_FILE)
        with open(EXISTING_IMPACT_JSON) as f:
            expected_metadata = f.read()

        self.assertEquals(expected_metadata, metadata.json)

    def test_invalid_json_read(self):
        with self.assertRaises(MetadataReadError):
            ImpactLayerMetadata(
                EXISTING_IMPACT_FILE,
                json_uri=INVALID_IMPACT_JSON)

    def test_incomplete_json_read(self):
        ImpactLayerMetadata(
            EXISTING_IMPACT_FILE,
            json_uri=INCOMPLETE_IMPACT_JSON)

    def test_xml_read(self):
        generated_metadata = ImpactLayerMetadata(
            EXISTING_IMPACT_FILE, xml_uri=EXISTING_IMPACT_XML)

        # TODO (MB): add more checks
        self.assertEquals(generated_metadata.get_xml_value('license'), 'GPLv2')

    def test_xml_to_json_to_xml(self):
        generated_metadata = ImpactLayerMetadata(
            EXISTING_IMPACT_FILE,
            xml_uri=EXISTING_IMPACT_XML)
        with open(EXISTING_IMPACT_XML) as f:
            expected_metadata = f.read()

        json_tmp_file = unique_filename(suffix='.json', dir=TEMP_DIR)
        generated_metadata.write_to_file(json_tmp_file)
        read_tmp_metadata = ImpactLayerMetadata(EXISTING_IMPACT_FILE,
                                                json_uri=json_tmp_file)
        self.assertEquals(expected_metadata, read_tmp_metadata.xml)

    def generate_test_metadata(self):
        # if you change this you need to update IMPACT_TEST_FILE_JSON
        metadata = ImpactLayerMetadata('random_layer_id')
        path = 'gmd:MD_Metadata/gmd:dateStamp/'
        path = TEST_XML_BASEPATH + 'gco:CharacterString'
        # using str
        test_value = 'Random string'
        metadata.set('ISO19115_STR', test_value, path)
        test_value = 1234
        metadata.set('ISO19115_INT', test_value, path)
        test_value = 1234.5678
        metadata.set('ISO19115_FLOAT', test_value, path)

        metadata.report = 'My super report'
        metadata.summary_data = {'res1': 1234, 'res2': 4321}

        metadata.append_provenance_step(
            'Title 1', 'Description of step 1', '2015-06-25T13:14:24.508974')
        metadata.append_provenance_step(
            'Title 2', 'Description of step 2', '2015-06-25T13:14:24.508980')
        metadata.append_provenance_step(
            'Title 3', 'Description of step 3', '2015-06-25T13:14:24.508984')

        return metadata
