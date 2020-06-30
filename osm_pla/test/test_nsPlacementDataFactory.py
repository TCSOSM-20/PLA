# Copyright 2020 ArctosLabs Scandinavia AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import unittest
from collections import Counter
from pathlib import Path
from unittest import TestCase, mock
from unittest.mock import call

import yaml

from osm_pla.placement.mznplacement import NsPlacementDataFactory


class TestNsPlacementDataFactory(TestCase):
    vim_accounts = [{"vim_password": "FxtnynxBCnouzAT4Hkerhg==", "config": {},
                     "_admin": {"modified": 1564579854.0480285, "created": 1564579854.0480285,
                                "operationalState": "ENABLED",
                                "projects_read": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                "deployed": {"RO-account": "6beb4e2e-b397-11e9-a7a3-02420aff0008",
                                             "RO": "6bcfc3fc-b397-11e9-a7a3-02420aff0008"},
                                "projects_write": ["69915588-e5e2-46d3-96b0-a29bedef6f73"], "detailed-status": "Done"},
                     "name": "OpenStack1", "vim_type": "openstack", "_id": "92b056a7-38f5-438d-b8ee-3f93b3531f87",
                     "schema_version": "1.1", "vim_user": "admin", "vim_url": "http://10.234.12.47:5000/v3",
                     "vim_tenant_name": "admin"},
                    {"config": {}, "vim_tenant_name": "osm_demo", "schema_version": "1.1", "name": "OpenStack2",
                     "vim_password": "gK5v4Gh2Pl41o6Skwp6RCw==", "vim_type": "openstack",
                     "_admin": {"modified": 1567148372.2490237, "created": 1567148372.2490237,
                                "operationalState": "ENABLED",
                                "projects_read": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                "deployed": {"RO-account": "b7fb0034-caf3-11e9-9388-02420aff000a",
                                             "RO": "b7f129ce-caf3-11e9-9388-02420aff000a"},
                                "projects_write": ["69915588-e5e2-46d3-96b0-a29bedef6f73"], "detailed-status": "Done"},
                     "vim_user": "admin", "vim_url": "http://10.234.12.44:5000/v3",
                     "_id": "6618d412-d7fc-4eb0-a6f8-d2c258e0e900"},
                    {"config": {}, "schema_version": "1.1", "name": "OpenStack3",
                     "vim_password": "1R2FoMQnaL6rNSosoRP2hw==", "vim_type": "openstack", "vim_tenant_name": "osm_demo",
                     "_admin": {"modified": 1567599746.689582, "created": 1567599746.689582,
                                "operationalState": "ENABLED",
                                "projects_read": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                "deployed": {"RO-account": "a8161f54-cf0e-11e9-9388-02420aff000a",
                                             "RO": "a80b6280-cf0e-11e9-9388-02420aff000a"},
                                "projects_write": ["69915588-e5e2-46d3-96b0-a29bedef6f73"], "detailed-status": "Done"},
                     "vim_user": "admin", "vim_url": "http://10.234.12.46:5000/v3",
                     "_id": "331ffdec-44a8-4707-94a1-af7a292d9735"},
                    {"config": {}, "schema_version": "1.1", "name": "OpenStack4",
                     "vim_password": "6LScyPeMq3QFh3GRb/xwZw==", "vim_type": "openstack", "vim_tenant_name": "osm_demo",
                     "_admin": {"modified": 1567599911.5108898, "created": 1567599911.5108898,
                                "operationalState": "ENABLED",
                                "projects_read": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                "deployed": {"RO-account": "0a651200-cf0f-11e9-9388-02420aff000a",
                                             "RO": "0a4defc6-cf0f-11e9-9388-02420aff000a"},
                                "projects_write": ["69915588-e5e2-46d3-96b0-a29bedef6f73"], "detailed-status": "Done"},
                     "vim_user": "admin", "vim_url": "http://10.234.12.43:5000/v3",
                     "_id": "eda92f47-29b9-4007-9709-c1833dbfbe31"}]

    vim_accounts_fewer_vims = [{"vim_password": "FxtnynxBCnouzAT4Hkerhg==", "config": {},
                                "_admin": {"modified": 1564579854.0480285, "created": 1564579854.0480285,
                                           "operationalState": "ENABLED",
                                           "projects_read": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                           "deployed": {"RO-account": "6beb4e2e-b397-11e9-a7a3-02420aff0008",
                                                        "RO": "6bcfc3fc-b397-11e9-a7a3-02420aff0008"},
                                           "projects_write": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                           "detailed-status": "Done"},
                                "name": "OpenStack1", "vim_type": "openstack",
                                "_id": "92b056a7-38f5-438d-b8ee-3f93b3531f87",
                                "schema_version": "1.1", "vim_user": "admin", "vim_url": "http://10.234.12.47:5000/v3",
                                "vim_tenant_name": "admin"},
                               {"config": {}, "vim_tenant_name": "osm_demo", "schema_version": "1.1",
                                "name": "OpenStack2",
                                "vim_password": "gK5v4Gh2Pl41o6Skwp6RCw==", "vim_type": "openstack",
                                "_admin": {"modified": 1567148372.2490237, "created": 1567148372.2490237,
                                           "operationalState": "ENABLED",
                                           "projects_read": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                           "deployed": {"RO-account": "b7fb0034-caf3-11e9-9388-02420aff000a",
                                                        "RO": "b7f129ce-caf3-11e9-9388-02420aff000a"},
                                           "projects_write": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                           "detailed-status": "Done"},
                                "vim_user": "admin", "vim_url": "http://10.234.12.44:5000/v3",
                                "_id": "6618d412-d7fc-4eb0-a6f8-d2c258e0e900"},
                               {"config": {}, "schema_version": "1.1", "name": "OpenStack4",
                                "vim_password": "6LScyPeMq3QFh3GRb/xwZw==", "vim_type": "openstack",
                                "vim_tenant_name": "osm_demo",
                                "_admin": {"modified": 1567599911.5108898, "created": 1567599911.5108898,
                                           "operationalState": "ENABLED",
                                           "projects_read": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                           "deployed": {"RO-account": "0a651200-cf0f-11e9-9388-02420aff000a",
                                                        "RO": "0a4defc6-cf0f-11e9-9388-02420aff000a"},
                                           "projects_write": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                           "detailed-status": "Done"},
                                "vim_user": "admin", "vim_url": "http://10.234.12.43:5000/v3",
                                "_id": "eda92f47-29b9-4007-9709-c1833dbfbe31"}]

    vim_accounts_more_vims = [{"vim_password": "FxtnynxBCnouzAT4Hkerhg==", "config": {},
                               "_admin": {"modified": 1564579854.0480285, "created": 1564579854.0480285,
                                          "operationalState": "ENABLED",
                                          "projects_read": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                          "deployed": {"RO-account": "6beb4e2e-b397-11e9-a7a3-02420aff0008",
                                                       "RO": "6bcfc3fc-b397-11e9-a7a3-02420aff0008"},
                                          "projects_write": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                          "detailed-status": "Done"},
                               "name": "OpenStack1", "vim_type": "openstack",
                               "_id": "92b056a7-38f5-438d-b8ee-3f93b3531f87",
                               "schema_version": "1.1", "vim_user": "admin", "vim_url": "http://10.234.12.47:5000/v3",
                               "vim_tenant_name": "admin"},
                              {"config": {}, "vim_tenant_name": "osm_demo", "schema_version": "1.1",
                               "name": "OpenStack2",
                               "vim_password": "gK5v4Gh2Pl41o6Skwp6RCw==", "vim_type": "openstack",
                               "_admin": {"modified": 1567148372.2490237, "created": 1567148372.2490237,
                                          "operationalState": "ENABLED",
                                          "projects_read": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                          "deployed": {"RO-account": "b7fb0034-caf3-11e9-9388-02420aff000a",
                                                       "RO": "b7f129ce-caf3-11e9-9388-02420aff000a"},
                                          "projects_write": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                          "detailed-status": "Done"},
                               "vim_user": "admin", "vim_url": "http://10.234.12.44:5000/v3",
                               "_id": "6618d412-d7fc-4eb0-a6f8-d2c258e0e900"},
                              {"config": {}, "schema_version": "1.1", "name": "OpenStack4",
                               "vim_password": "6LScyPeMq3QFh3GRb/xwZw==", "vim_type": "openstack",
                               "vim_tenant_name": "osm_demo",
                               "_admin": {"modified": 1567599911.5108898, "created": 1567599911.5108898,
                                          "operationalState": "ENABLED",
                                          "projects_read": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                          "deployed": {"RO-account": "0a651200-cf0f-11e9-9388-02420aff000a",
                                                       "RO": "0a4defc6-cf0f-11e9-9388-02420aff000a"},
                                          "projects_write": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                          "detailed-status": "Done"},
                               "vim_user": "admin", "vim_url": "http://10.234.12.43:5000/v3",
                               "_id": "eda92f47-29b9-4007-9709-c1833dbfbe31"},
                              {"config": {}, "schema_version": "1.1", "name": "OpenStack3",
                               "vim_password": "6LScyPeMq3QFh3GRb/xwZw==", "vim_type": "openstack",
                               "vim_tenant_name": "osm_demo",
                               "_admin": {"modified": 1567599911.5108898, "created": 1567599911.5108898,
                                          "operationalState": "ENABLED",
                                          "projects_read": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                          "deployed": {"RO-account": "0a651200-cf0f-11e9-9388-02420aff000a",
                                                       "RO": "0a4defc6-cf0f-11e9-9388-02420aff000a"},
                                          "projects_write": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                          "detailed-status": "Done"},
                               "vim_user": "admin", "vim_url": "http://10.234.12.46:5000/v3",
                               "_id": "eda92f47-29b9-4007-9709-c1833dbfbe31"},
                              {"config": {}, "schema_version": "1.1", "name": "OpenStack5",
                               "vim_password": "6LScyPeMq3QFh3GRb/xwZw==", "vim_type": "openstack",
                               "vim_tenant_name": "osm_demo",
                               "_admin": {"modified": 1567599911.5108898, "created": 1567599911.5108898,
                                          "operationalState": "ENABLED",
                                          "projects_read": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                          "deployed": {"RO-account": "0a651200-cf0f-11e9-9388-02420aff000a",
                                                       "RO": "0a4defc6-cf0f-11e9-9388-02420aff000a"},
                                          "projects_write": ["69915588-e5e2-46d3-96b0-a29bedef6f73"],
                                          "detailed-status": "Done"},
                               "vim_user": "admin", "vim_url": "http://1.1.1.1:5000/v3",
                               "_id": "ffffffff-29b9-4007-9709-c1833dbfbe31"}]

    def _produce_ut_vim_accounts_info(self, vim_accounts):
        """
        FIXME temporary, we will need more control over vim_urls and _id for test purpose - make a generator
        :return: vim_url and _id as dict, i.e. extract these from vim_accounts data
        """
        return {_['name']: _['_id'] for _ in vim_accounts}

    def _adjust_path(self, file):
        """In case we are not running from test directory,
        then assume we are in top level directory (e.g. running from tox) and adjust file path accordingly"""
        path_component = '/osm_pla/test/'
        real_path = os.path.realpath(file)
        if path_component not in real_path:
            return os.path.dirname(real_path) + path_component + os.path.basename(real_path)
        else:
            return real_path

    def _populate_pil_info(self, file):
        """
        Note str(Path()) is a 3.5 thing
        """
        with open(str(Path(self._adjust_path(file)))) as pp_fd:
            test_data = yaml.safe_load_all(pp_fd)
            return next(test_data)

    def _get_ut_nsd_from_file(self, nsd_file_name):
        """
        creates the structure representing the nsd.

        IMPORTANT NOTE: If using .yaml files from the NS packages for the unit tests (which we do),
        then the files must be modified with respect to the way booleans are processed at on-boarding in OSM.
        The following construct in the NS package yaml file:
        mgmt-network: 'false'
        will become a boolean in the MongoDB, and therefore the yaml used in these unit test must use yaml
        tag as follows:
        mgmt-network: !!bool False
        The modification also applies to 'true' => !!bool True
        This will ensure that the object returned from this function is as expected by PLA.
        """
        with open(str(Path(self._adjust_path(nsd_file_name)))) as nsd_fd:
            test_data = yaml.safe_load_all(nsd_fd)
            return next(test_data)

    def _produce_ut_vnf_price_list(self):
        price_list_file = "vnf_price_list.yaml"
        with open(str(Path(self._adjust_path(price_list_file)))) as pl_fd:
            price_list_data = yaml.safe_load_all(pl_fd)
            return {i['vnfd']: {i1['vim_name']: i1['price'] for i1 in i['prices']} for i in next(price_list_data)}

    def _produce_ut_vnf_test_price_list(self, price_list):
        price_list_file = price_list
        with open(str(Path(self._adjust_path(price_list_file)))) as pl_fd:
            price_list_data = yaml.safe_load_all(pl_fd)
            return {i['vnfd']: {i1['vim_name']: i1['price'] for i1 in i['prices']} for i in next(price_list_data)}

    def test__produce_trp_link_characteristics_link_latency_with_more_vims(self):
        """
         -test with more(other) vims compared to pil
         """
        content_expected = [0, 0, 0, 0, 0, 120, 120, 130, 130, 140, 140, 230, 230, 240, 240,
                            340, 340, 32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767]
        nspdf = NsPlacementDataFactory(
            self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts_more_vims),
            self._produce_ut_vnf_price_list(),
            nsd=None,
            pil_info=self._populate_pil_info('pil_unittest1_keys.yaml'),
            pinning=None)
        pil_latencies = nspdf._produce_trp_link_characteristics_data('pil_latency')
        content_produced = [i for row in pil_latencies for i in row]
        self.assertEqual(Counter(content_expected), Counter(content_produced), 'trp_link_latency incorrect')

    def test__produce_trp_link_characteristics_link_latency_with_fewer_vims(self):
        """
        -test with fewer vims compared to pil
        :return:
        """
        content_expected = [0, 0, 0, 120, 120, 140, 140, 240, 240]
        nspdf = NsPlacementDataFactory(
            self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts_fewer_vims),
            self._produce_ut_vnf_price_list(),
            nsd=None,
            pil_info=self._populate_pil_info('pil_unittest1_keys.yaml'),
            pinning=None)
        pil_latencies = nspdf._produce_trp_link_characteristics_data('pil_latency')
        content_produced = [i for row in pil_latencies for i in row]
        self.assertEqual(Counter(content_expected), Counter(content_produced), 'trp_link_latency incorrect')

    def test__produce_trp_link_characteristic_not_supported(self):
        """
        - test with non-supported characteristic
        """
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=None,
                                       pil_info=self._populate_pil_info('pil_unittest1.yaml'), pinning=None)

        with self.assertRaises(Exception) as e:
            nspdf._produce_trp_link_characteristics_data('test_no_support')
        self.assertRegex(str(e.exception), r'characteristic.*not supported', "invalid exception content")

    def test__produce_trp_link_characteristics_link_latency(self):
        """
        -test with full set of vims as in pil
        -test with fewer vims compared to pil
        -test with more(other) vims compared to pil
        -test with invalid/corrupt pil configuration file (e.g. missing endpoint), empty file, not yaml conformant
        - test with non-supported characteristic

        :return:
        """
        content_expected = [0, 0, 0, 0, 120, 120, 130, 130, 140, 140, 230, 230, 240, 240, 340, 340]

        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=None,
                                       pil_info=self._populate_pil_info('pil_unittest1_keys.yaml'), pinning=None)
        pil_latencies = nspdf._produce_trp_link_characteristics_data('pil_latency')
        content_produced = [i for row in pil_latencies for i in row]
        self.assertEqual(Counter(content_expected), Counter(content_produced), 'trp_link_latency incorrect')

    def test__produce_trp_link_characteristics_link_jitter(self):
        """
        -test with full set of vims as in pil
        """
        content_expected = [0, 0, 0, 0, 1200, 1200, 1300, 1300, 1400, 1400, 2300, 2300, 2400, 2400, 3400, 3400]

        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=None,
                                       pil_info=self._populate_pil_info('pil_unittest1_keys.yaml'), pinning=None)
        pil_jitter = nspdf._produce_trp_link_characteristics_data('pil_jitter')
        content_produced = [i for row in pil_jitter for i in row]
        self.assertEqual(Counter(content_expected), Counter(content_produced), 'trp_link_jitter incorrect')

    def test__produce_trp_link_characteristics_link_jitter_with_fewer_vims(self):
        """
        -test with fewer vims compared to pil, link jitter
        """
        content_expected = [0, 0, 0, 1200, 1200, 1400, 1400, 2400, 2400]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(self.vim_accounts_fewer_vims),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=None,
                                       pil_info=self._populate_pil_info('pil_unittest1_keys.yaml'), pinning=None)
        pil_latencies = nspdf._produce_trp_link_characteristics_data('pil_jitter')
        content_produced = [i for row in pil_latencies for i in row]
        self.assertEqual(Counter(content_expected), Counter(content_produced), 'trp_link_jitter incorrect')

    def test__produce_trp_link_characteristics_link_jitter_with_more_vims(self):
        """
        -test with more vims compared to pil, link jitter
        """
        content_expected = [0, 0, 0, 0, 0, 1200, 1200, 1300, 1300, 1400, 1400, 2300,
                            2300, 2400, 2400, 3400, 3400, 32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(self.vim_accounts_more_vims),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=None,
                                       pil_info=self._populate_pil_info('pil_unittest1_keys.yaml'), pinning=None)
        pil_latencies = nspdf._produce_trp_link_characteristics_data('pil_jitter')
        content_produced = [i for row in pil_latencies for i in row]
        self.assertEqual(Counter(content_expected), Counter(content_produced), 'trp_link_jitter incorrect')

    def test__produce_trp_link_characteristics_link_price(self):
        """
        -test with full set of vims as in pil
        """
        content_expected = [0, 0, 0, 0, 12, 12, 13, 13, 14, 14, 23, 23, 24, 24, 34, 34]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=None,
                                       pil_info=self._populate_pil_info('pil_unittest1_keys.yaml'), pinning=None)
        pil_prices = nspdf._produce_trp_link_characteristics_data('pil_price')
        content_produced = [i for row in pil_prices for i in row]
        self.assertEqual(Counter(content_expected), Counter(content_produced), 'invalid trp link prices')

    def test__produce_trp_link_characteristics_link_price_with_fewer_vims(self):
        """
        -test with fewer vims compared to pil
        """
        content_expected = [0, 0, 0, 12, 12, 14, 14, 24, 24]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(self.vim_accounts_fewer_vims),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=None,
                                       pil_info=self._populate_pil_info('pil_unittest1_keys.yaml'), pinning=None)
        pil_prices = nspdf._produce_trp_link_characteristics_data('pil_price')
        content_produced = [i for row in pil_prices for i in row]
        self.assertEqual(Counter(content_expected), Counter(content_produced), 'invalid trp link prices')

    def test__produce_trp_link_characteristics_partly_constrained(self):
        content_expected = [0, 0, 0, 0, 32767, 32767, 32767, 32767, 1200, 1200, 1400, 1400, 2400, 2400, 3400, 3400]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=None,
                                       pil_info=self._populate_pil_info('pil_unittest2_keys.yaml'), pinning=None)
        pil_jitter = nspdf._produce_trp_link_characteristics_data('pil_jitter')
        content_produced = [i for row in pil_jitter for i in row]
        self.assertEqual(Counter(content_expected), Counter(content_produced),
                         'invalid trp link jitter, partly constrained')

    def test__produce_vld_desc_partly_constrained(self):
        vld_desc_expected = [{'cp_refs': ['one', 'two'], 'jitter': 30},
                             {'cp_refs': ['two', 'three'], 'latency': 120}]

        nsd = self._get_ut_nsd_from_file('nsd_unittest2.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None, pinning=None)
        self.assertEqual(vld_desc_expected, nspdf._produce_vld_desc(),
                         "vld_desc incorrect")

    def test__produce_trp_link_characteristics_link_latency_not_yaml_conformant(self):
        """
        -test with invalid/corrupt pil configuration file (not yaml conformant)
        """
        with self.assertRaises(Exception) as e:
            _ = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=None,
                                       pil_info=self._populate_pil_info('not_yaml_conformant.yaml'),
                                       pinning=None)
        self.assertRegex(str(e.exception), r'mapping values are not allowed here.*', "invalid exception content")

    def test__produce_trp_link_characteristics_with_invalid_pil_config(self):
        """
        -test with invalid/corrupt pil configuration file (missing endpoint)
        """
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=None,
                                       pil_info=self._populate_pil_info('corrupt_pil_endpoints_config_unittest1.yaml'),
                                       pinning=None)
        with self.assertRaises(Exception) as e:
            _ = nspdf._produce_trp_link_characteristics_data('pil_latency')
        self.assertEqual('list index out of range', str(e.exception), "unexpected exception")

    def test__produce_vld_desc_w_instantiate_override(self):

        vld_desc_expected = [{'cp_refs': ['one', 'two'], 'latency': 150, 'jitter': 30},
                             {'cp_refs': ['two', 'three'], 'latency': 90, 'jitter': 30}]

        nsd = self._get_ut_nsd_from_file('nsd_unittest_no_vld_constraints.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None, pinning=None,
                                       order_constraints=None)

        self.assertNotEqual(nspdf._produce_vld_desc(),
                            vld_desc_expected, "vld_desc incorrect")

    def test__produce_vld_desc_nsd_w_instantiate_wo(self):
        """
        nsd w/ constraints, instantiate w/o constraints
        :return:
        """
        vld_desc_expected = [{'cp_refs': ['one', 'two'], 'latency': 150, 'jitter': 30},
                             {'cp_refs': ['two', 'three'], 'latency': 90, 'jitter': 30}]

        nsd = self._get_ut_nsd_from_file('nsd_unittest3.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None, pinning=None,
                                       order_constraints=None)

        self.assertEqual(vld_desc_expected, nspdf._produce_vld_desc(),
                         "vld_desc incorrect")

    def test__produce_vld_desc_nsd_w_instantiate_w(self):
        """
        nsd w/ constraints, instantiate w/ constraints => override
        :return:
        """
        vld_desc_expected = [{'cp_refs': ['one', 'two'], 'latency': 120, 'jitter': 21},
                             {'cp_refs': ['two', 'three'], 'latency': 121, 'jitter': 22}]

        nsd = self._get_ut_nsd_from_file('nsd_unittest3.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None, pinning=None,
                                       order_constraints={
                                           'vld-constraints': [{'id': 'three_vnf_constrained_nsd_vld1',
                                                                'link-constraints': {'latency': 120,
                                                                                     'jitter': 21}},
                                                               {'id': 'three_vnf_constrained_nsd_vld2',
                                                                'link-constraints': {'latency': 121,
                                                                                     'jitter': 22}}]})

        self.assertEqual(vld_desc_expected, nspdf._produce_vld_desc(),
                         "vld_desc incorrect")

    def test__produce_vld_desc_nsd_wo_instantiate_wo(self):
        """
        nsd w/o constraints, instantiate w/o constraints = no constraints in model
        :return:
        """
        vld_desc_expected = [{'cp_refs': ['one', 'two']},
                             {'cp_refs': ['two', 'three']}]

        nsd = self._get_ut_nsd_from_file('nsd_unittest_no_vld_constraints.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None, pinning=None,
                                       order_constraints=None)

        self.assertEqual(vld_desc_expected, nspdf._produce_vld_desc(),
                         "vld_desc incorrect")

    def test__produce_vld_desc_nsd_wo_instantiate_w(self):
        """
        nsd w/o constraints, instantiate w/ constraints => add constraints
        :return:
        """
        vld_desc_expected = [{'cp_refs': ['one', 'two'], 'latency': 140, 'jitter': 41},
                             {'cp_refs': ['two', 'three'], 'latency': 141, 'jitter': 42}]

        nsd = self._get_ut_nsd_from_file('nsd_unittest_no_vld_constraints.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None, pinning=None,
                                       order_constraints={
                                           'vld-constraints': [{'id': 'three_vnf_constrained_nsd_vld1',
                                                                'link-constraints': {'latency': 140,
                                                                                     'jitter': 41}},
                                                               {'id': 'three_vnf_constrained_nsd_vld2',
                                                                'link-constraints': {'latency': 141,
                                                                                     'jitter': 42}}]})

        self.assertEqual(vld_desc_expected, nspdf._produce_vld_desc(),
                         "vld_desc incorrect")

    def test__produce_vld_desc_nsd_wo_instantiate_w_faulty_input(self):
        """
        nsd w/o constraints, instantiate w/ constraints => add constraints that can be parsed
        :return:
        """
        vld_desc_expected = [{'cp_refs': ['one', 'two']},
                             {'cp_refs': ['two', 'three'], 'latency': 151}]

        nsd = self._get_ut_nsd_from_file('nsd_unittest_no_vld_constraints.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None, pinning=None,
                                       order_constraints={'vld-constraints': [{'id': 'not_included_vld',
                                                                               'misspelled-constraints':
                                                                                   {'latency': 120,
                                                                                    'jitter': 20}},
                                                                              {'id': 'three_vnf_constrained_nsd_vld2',
                                                                               'link-constraints': {
                                                                                   'latency': 151}}]})

        self.assertEqual(vld_desc_expected, nspdf._produce_vld_desc(),
                         "vld_desc incorrect")

    def test__produce_vld_desc_nsd_wo_instantiate_w_faulty_input_again(self):
        """
        nsd w/o constraints, instantiate w/ faulty constraints => add constraints that can be parsed
        :return:
        """
        vld_desc_expected = [{'cp_refs': ['one', 'two'], 'jitter': 21},
                             {'cp_refs': ['two', 'three']}]

        nsd = self._get_ut_nsd_from_file('nsd_unittest_no_vld_constraints.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None, pinning=None,
                                       order_constraints={
                                           'vld-constraints': [{'id': 'three_vnf_constrained_nsd_vld1',
                                                                'link-constraints': {'delay': 120,
                                                                                     'jitter': 21}},
                                                               {'id': 'three_vnf_constrained_nsd_vld2',
                                                                'misspelled-constraints': {'latency': 121,
                                                                                           'jitter': 22}}]})

        self.assertEqual(vld_desc_expected, nspdf._produce_vld_desc(),
                         "vld_desc incorrect")

    def test__produce_vld_desc_mgmt_network(self):
        vld_desc_expected = [{'cp_refs': ['1', '2'], 'latency': 120, 'jitter': 20},
                             {'cp_refs': ['2', '4'], 'latency': 50, 'jitter': 10},
                             {'cp_refs': ['2', '3'], 'latency': 20, 'jitter': 10}, ]

        nsd = self._get_ut_nsd_from_file('test_five_nsd.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None, pinning=None,
                                       order_constraints=None)

        self.assertEqual(vld_desc_expected, nspdf._produce_vld_desc(), "vld_desc incorrect")

    def test__produce_vld_desc_single_vnf_nsd(self):
        vld_desc_expected = []

        nsd = self._get_ut_nsd_from_file('nsd_unittest4.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None, pinning=None,
                                       order_constraints=None)

        self.assertEqual(vld_desc_expected, nspdf._produce_vld_desc(), "vld_desc_incorrect")

    def test__produce_vld_desc_slice_nsd(self):
        vld_desc_expected = []
        nsd = self._get_ut_nsd_from_file('slice_hackfest_middle_nsd.yaml')
        nsd = nsd['nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None, pinning=None,
                                       order_constraints=None)

        self.assertEqual(vld_desc_expected, nspdf._produce_vld_desc(), "vld_desc_incorrect")

    def test__produce_vld_desc(self):
        """

        :return:
        """
        vld_desc_expected = [{'cp_refs': ['one', 'two'], 'latency': 150, 'jitter': 30},
                             {'cp_refs': ['two', 'three'], 'latency': 90, 'jitter': 30}]

        nsd = self._get_ut_nsd_from_file('nsd_unittest3.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None, pinning=None,
                                       order_constraints=None)

        self.assertEqual(vld_desc_expected, nspdf._produce_vld_desc(), "vld_desc incorrect")

    def test__produce_ns_desc(self):
        """
        ToDo
        - price list sheet with more vims than associated with session
        - price list sheet with fewer vims than associated with session
        - nsd with different vndfd-id-refs
        - fault case scenarios with non-existing vims, non-existing vnfds
        """
        nsd = self._get_ut_nsd_from_file('nsd_unittest3.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None,
                                       pinning=None)

        ns_desc = nspdf._produce_ns_desc()
        # check that all expected member-vnf-index are present
        vnfs = [e['vnf_id'] for e in ns_desc]
        self.assertEqual(Counter(['one', 'two', 'three']), Counter(vnfs), 'vnf_id invalid')

        expected_keys = ['vnf_id', 'vnf_price_per_vim']
        for e in ns_desc:
            # check that vnf_price_per_vim has proper values
            self.assertEqual(Counter([5, 10, 30, 30]), Counter(e['vnf_price_per_vim']), 'vnf_price_per_vim invalid')
            # check that no pinning directives included
            self.assertEqual(Counter(expected_keys), Counter(e.keys()), 'pinning directive misplaced')

    def test__produce_ns_desc_with_more_vims(self):
        nsd = self._get_ut_nsd_from_file('nsd_unittest1.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(self.vim_accounts_more_vims),
                                       self._produce_ut_vnf_test_price_list('vnf_price_list_more_vims.yaml'),
                                       nsd=nsd,
                                       pil_info=None,
                                       pinning=None)

        ns_desc = nspdf._produce_ns_desc()
        # check that all expected member-vnf-index are present
        vnfs = [e['vnf_id'] for e in ns_desc]
        self.assertEqual(Counter([1, 3, 2]), Counter(vnfs), 'vnf_id invalid')

        expected_keys = ['vnf_id', 'vnf_price_per_vim']
        for e in ns_desc:
            # check that vnf_price_per_vim has proper values
            self.assertEqual(Counter([5, 10, 30, 30, 3]), Counter(e['vnf_price_per_vim']), 'vnf_price_per_vim invalid')
            # check that no pinning directives included
            self.assertEqual(Counter(expected_keys), Counter(e.keys()), 'pinning directive misplaced')

    def test__produce_ns_desc_with_fewer_vims(self):
        nsd = self._get_ut_nsd_from_file('nsd_unittest1.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(self.vim_accounts_fewer_vims),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None,
                                       pinning=None)

        ns_desc = nspdf._produce_ns_desc()
        # check that all expected member-vnf-index are present
        vnfs = [e['vnf_id'] for e in ns_desc]
        self.assertEqual(Counter([1, 3, 2]), Counter(vnfs), 'vnf_id invalid')

        expected_keys = ['vnf_id', 'vnf_price_per_vim']
        for e in ns_desc:
            # check that vnf_price_per_vim has proper values
            self.assertEqual(Counter([5, 10, 30]), Counter(e['vnf_price_per_vim']), 'vnf_price_per_vim invalid')
            # check that no pinning directives included
            self.assertEqual(Counter(expected_keys), Counter(e.keys()), 'pinning directive misplaced')

    def test__produce_ns_desc_w_pinning(self):
        nsd = self._get_ut_nsd_from_file('nsd_unittest3.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        pinning = [{'member-vnf-index': 'two', 'vimAccountId': '331ffdec-44a8-4707-94a1-af7a292d9735'}]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=None,
                                       pinning=pinning)
        ns_desc = nspdf._produce_ns_desc()
        # check that all expected member-vnf-index are present
        vnfs = [e['vnf_id'] for e in ns_desc]
        self.assertEqual(Counter(['one', 'three', 'two']), Counter(vnfs), 'vnf_id invalid')

        for e in ns_desc:
            # check that vnf_price_per_vim has proper values
            self.assertEqual(Counter([5, 10, 30, 30]), Counter(e['vnf_price_per_vim']), 'vnf_price_per_vim invalid')
            # check that member-vnf-index 2 is pinned correctly
            if e['vnf_id'] == 'two':
                self.assertTrue('vim_account' in e.keys(), 'missing pinning directive')
                self.assertTrue(pinning[0]['vimAccountId'] == e['vim_account'][3:].replace('_', '-'),
                                'invalid pinning vim-account')
            else:
                self.assertTrue('vim-account' not in e.keys(), 'pinning directive misplaced')

    @mock.patch.object(NsPlacementDataFactory, '_produce_trp_link_characteristics_data')
    @mock.patch.object(NsPlacementDataFactory, '_produce_vld_desc')
    @mock.patch.object(NsPlacementDataFactory, '_produce_ns_desc')
    def test_create_ns_placement_data_wo_order(self, mock_prd_ns_desc, mock_prd_vld_desc, mock_prd_trp_link_char):
        """
        :return:
        """
        vim_accounts_expected = [v.replace('-', '_') for v in ['vim92b056a7-38f5-438d-b8ee-3f93b3531f87',
                                                               'vim6618d412-d7fc-4eb0-a6f8-d2c258e0e900',
                                                               'vim331ffdec-44a8-4707-94a1-af7a292d9735',
                                                               'vimeda92f47-29b9-4007-9709-c1833dbfbe31']]

        nsd = self._get_ut_nsd_from_file('nsd_unittest3.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=self._populate_pil_info('pil_unittest1.yaml'),
                                       pinning=None,
                                       order_constraints=None)
        nspd = nspdf.create_ns_placement_data()
        self.assertEqual(Counter(vim_accounts_expected), Counter(nspd['vim_accounts']),
                         "vim_accounts incorrect")
        # mock1.assert_called_once() Note for python > 3.5
        self.assertTrue(mock_prd_ns_desc.called, '_produce_ns_desc not called')
        # mock2.assert_called_once() Note for python > 3.5
        self.assertTrue(mock_prd_vld_desc.called, ' _produce_vld_desc not called')
        mock_prd_trp_link_char.assert_has_calls([call('pil_latency'), call('pil_jitter'), call('pil_price')])

        regexps = [r"\{.*\}", r".*'file':.*mznplacement.py", r".*'time':.*datetime.datetime\(.*\)"]
        generator_data = str(nspd['generator_data'])
        for regex in regexps:
            self.assertRegex(generator_data, regex, "generator data invalid")

    @mock.patch.object(NsPlacementDataFactory, '_produce_trp_link_characteristics_data')
    @mock.patch.object(NsPlacementDataFactory, '_produce_vld_desc')
    @mock.patch.object(NsPlacementDataFactory, '_produce_ns_desc')
    def test_create_ns_placement_data_w_order(self, mock_prd_ns_desc, mock_prd_vld_desc,
                                              mock_prd_trp_link_char):
        """
        :return:
        """
        vim_accounts_expected = [v.replace('-', '_') for v in ['vim92b056a7-38f5-438d-b8ee-3f93b3531f87',
                                                               'vim6618d412-d7fc-4eb0-a6f8-d2c258e0e900',
                                                               'vim331ffdec-44a8-4707-94a1-af7a292d9735',
                                                               'vimeda92f47-29b9-4007-9709-c1833dbfbe31']]

        nsd = self._get_ut_nsd_from_file('nsd_unittest3.yaml')
        nsd = nsd['nsd:nsd-catalog']['nsd'][0]
        nspdf = NsPlacementDataFactory(self._produce_ut_vim_accounts_info(TestNsPlacementDataFactory.vim_accounts),
                                       self._produce_ut_vnf_price_list(),
                                       nsd=nsd,
                                       pil_info=self._populate_pil_info('pil_unittest1.yaml'),
                                       pinning=None,
                                       order_constraints={
                                           'vld-constraints': [{'id': 'three_vnf_constrained_nsd_vld1',
                                                                'link-constraints': {'latency': 120,
                                                                                     'jitter': 21}},
                                                               {'id': 'three_vnf_constrained_nsd_vld2',
                                                                'link-constraints': {'latency': 121,
                                                                                     'jitter': 22}}]}
                                       )
        nspd = nspdf.create_ns_placement_data()
        self.assertEqual(Counter(vim_accounts_expected), Counter(nspd['vim_accounts']),
                         "vim_accounts incorrect")
        # mock1.assert_called_once() Note for python > 3.5
        self.assertTrue(mock_prd_ns_desc.called, '_produce_ns_desc not called')
        # mock2.assert_called_once() Note for python > 3.5
        self.assertTrue(mock_prd_vld_desc.called, ' _produce_vld_desc not called')
        mock_prd_trp_link_char.assert_has_calls([call('pil_latency'), call('pil_jitter'), call('pil_price')])

        regexps = [r"\{.*\}", r".*'file':.*mznplacement.py", r".*'time':.*datetime.datetime\(.*\)"]
        generator_data = str(nspd['generator_data'])
        for regex in regexps:
            self.assertRegex(generator_data, regex, "generator data invalid")


if __name__ == "__main__":
    if __name__ == '__main__':
        unittest.main()
