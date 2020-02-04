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
import asyncio
# import platform
# import random
import os
import sys
# import unittest
from unittest import TestCase, mock
from unittest.mock import Mock

# import pkg_resources
import yaml

from osm_pla.placement.mznplacement import NsPlacementDataFactory, MznPlacementConductor
from pathlib import Path

# need to Mock the imports from osm_common made in Server and Config beforehand
sys.modules['osm_common'] = Mock()
from osm_pla.server.server import Server  # noqa: E402
from osm_pla.config.config import Config  # noqa: E402

nslcmop_record_wo_pinning = {'statusEnteredTime': 1574625718.8280587, 'startTime': 1574625718.8280587,
                             '_admin': {'created': 1574625718.8286533,
                                        'projects_write': ['61e4bbab-9659-4abc-a01d-ba3a307becf9'],
                                        'worker': 'e5121e773e8b', 'modified': 1574625718.8286533,
                                        'projects_read': ['61e4bbab-9659-4abc-a01d-ba3a307becf9']},
                             'operationState': 'PROCESSING', 'nsInstanceId': '45f588bd-5bf4-4181-b13b-f16a55a23be4',
                             'lcmOperationType': 'instantiate', 'isCancelPending': False,
                             'id': 'a571b1de-19e5-48bd-b252-ba0ad7d540c9',
                             '_id': 'a571b1de-19e5-48bd-b252-ba0ad7d540c9',
                             'isAutomaticInvocation': False,
                             'links': {'nsInstance': '/osm/nslcm/v1/ns_instances/45f588bd-5bf4-4181-b13b-f16a55a23be4',
                                       'self': '/osm/nslcm/v1/ns_lcm_op_occs/a571b1de-19e5-48bd-b252-ba0ad7d540c9'},
                             'operationParams': {'vimAccountId': 'eb553051-5b6c-4ad6-939b-2ad23bd82e57',
                                                 'lcmOperationType': 'instantiate', 'nsDescription': 'just a test',
                                                 'nsdId': '0f4e658f-62a6-4f73-8623-270e8f0a18bc',
                                                 'nsName': 'ThreeNsd plain placement', 'ssh_keys': [],
                                                 'validVimAccounts': ['eb553051-5b6c-4ad6-939b-2ad23bd82e57',
                                                                      '576bbe0a-b95d-4ced-a63e-f387f8e6e2ce',
                                                                      '3d1ffc5d-b36d-4f69-8356-7f59c740ca2f',
                                                                      'db54dcd4-9fc4-441c-8820-17bce0aef2c3'],
                                                 'nsr_id': '45f588bd-5bf4-4181-b13b-f16a55a23be4',
                                                 'placement-engine': 'PLA',
                                                 'nsInstanceId': '45f588bd-5bf4-4181-b13b-f16a55a23be4'}}

nslcmop_record_w_pinning = {'statusEnteredTime': 1574627411.420499, 'startTime': 1574627411.420499,
                            '_admin': {'created': 1574627411.4209971,
                                       'projects_write': ['61e4bbab-9659-4abc-a01d-ba3a307becf9'],
                                       'worker': 'e5121e773e8b', 'modified': 1574627411.4209971,
                                       'projects_read': ['61e4bbab-9659-4abc-a01d-ba3a307becf9']},
                            'operationState': 'PROCESSING',
                            'nsInstanceId': '61587478-ea25-44eb-9f13-7005046ddb08', 'lcmOperationType': 'instantiate',
                            'isCancelPending': False, 'id': '80f95a17-6fa7-408d-930f-40aa4589d074',
                            '_id': '80f95a17-6fa7-408d-930f-40aa4589d074',
                            'isAutomaticInvocation': False,
                            'links': {
                                'nsInstance': '/osm/nslcm/v1/ns_instances/61587478-ea25-44eb-9f13-7005046ddb08',
                                'self': '/osm/nslcm/v1/ns_lcm_op_occs/80f95a17-6fa7-408d-930f-40aa4589d074'},
                            'operationParams': {
                                'vimAccountId': '576bbe0a-b95d-4ced-a63e-f387f8e6e2ce',
                                'nsr_id': '61587478-ea25-44eb-9f13-7005046ddb08',
                                'nsDescription': 'default description', 'nsdId': '0f4e658f-62a6-4f73-8623-270e8f0a18bc',
                                'validVimAccounts': [
                                    'eb553051-5b6c-4ad6-939b-2ad23bd82e57', '576bbe0a-b95d-4ced-a63e-f387f8e6e2ce',
                                    '3d1ffc5d-b36d-4f69-8356-7f59c740ca2f',
                                    'db54dcd4-9fc4-441c-8820-17bce0aef2c3'], 'nsName': 'ThreeVnfTest2',
                                'wimAccountId': False, 'vnf': [
                                    {'vimAccountId': '3d1ffc5d-b36d-4f69-8356-7f59c740ca2f', 'member-vnf-index': '1'}],
                                'placementEngine': 'PLA',
                                'nsInstanceId': '61587478-ea25-44eb-9f13-7005046ddb08',
                                'lcmOperationType': 'instantiate'}}

nslcmop_record_w_pinning_and_order_constraints = {
    'links': {'nsInstance': '/osm/nslcm/v1/ns_instances/7c4c3d94-ebb2-44e8-b236-d876b118434e',
              'self': '/osm/nslcm/v1/ns_lcm_op_occs/fd7c9e15-38aa-4fc5-913c-417b26859fb0'},
    'id': 'fd7c9e15-38aa-4fc5-913c-417b26859fb0', 'operationState': 'PROCESSING', 'isAutomaticInvocation': False,
    'nsInstanceId': '7c4c3d94-ebb2-44e8-b236-d876b118434e', '_id': 'fd7c9e15-38aa-4fc5-913c-417b26859fb0',
    'isCancelPending': False, 'startTime': 1574772631.6932728, 'statusEnteredTime': 1574772631.6932728,
    'lcmOperationType': 'instantiate',
    'operationParams': {'placementEngine': 'PLA',
                        'placement-constraints': {
                            'vld-constraints': [{
                                'id': 'three_vnf_constrained_vld_1',
                                'link-constraints': {
                                    'latency': 120,
                                    'jitter': 20}},
                                {
                                    'link_constraints': {
                                        'latency': 120,
                                        'jitter': 20},
                                    'id': 'three_vnf_constrained_nsd_vld_2'}]},
                        'nsName': 'ThreeVnfTest2',
                        'nsDescription': 'default description',
                        'nsr_id': '7c4c3d94-ebb2-44e8-b236-d876b118434e',
                        'nsdId': '0f4e658f-62a6-4f73-8623-270e8f0a18bc',
                        'validVimAccounts': ['eb553051-5b6c-4ad6-939b-2ad23bd82e57',
                                             '576bbe0a-b95d-4ced-a63e-f387f8e6e2ce',
                                             '3d1ffc5d-b36d-4f69-8356-7f59c740ca2f',
                                             'db54dcd4-9fc4-441c-8820-17bce0aef2c3'],
                        'wimAccountId': False,
                        'vnf': [{'member-vnf-index': '3', 'vimAccountId': '3d1ffc5d-b36d-4f69-8356-7f59c740ca2f'}],
                        'nsInstanceId': '7c4c3d94-ebb2-44e8-b236-d876b118434e',
                        'lcmOperationType': 'instantiate',
                        'vimAccountId': '576bbe0a-b95d-4ced-a63e-f387f8e6e2ce'},
    '_admin': {'projects_read': ['61e4bbab-9659-4abc-a01d-ba3a307becf9'], 'modified': 1574772631.693885,
               'projects_write': ['61e4bbab-9659-4abc-a01d-ba3a307becf9'], 'created': 1574772631.693885,
               'worker': 'e5121e773e8b'}}

list_of_vims = [{"_id": "73cd1a1b-333e-4e29-8db2-00d23bd9b644", "vim_user": "admin", "name": "OpenStack1",
                 "vim_url": "http://10.234.12.47:5000/v3", "vim_type": "openstack", "vim_tenant_name": "osm_demo",
                 "vim_password": "O/mHomfXPmCrTvUbYXVoyg==", "schema_version": "1.1",
                 "_admin": {"modified": 1565597984.3155663,
                            "deployed": {"RO": "f0c1b516-bcd9-11e9-bb73-02420aff0030",
                                         "RO-account": "f0d45496-bcd9-11e9-bb73-02420aff0030"},
                            "projects_write": ["admin"], "operationalState": "ENABLED", "detailed-status": "Done",
                            "created": 1565597984.3155663, "projects_read": ["admin"]},
                 "config": {}},
                {"_id": "684165ea-2cf9-4fbd-ac22-8464ca07d1d8", "vim_user": "admin",
                 "name": "OpenStack2", "vim_url": "http://10.234.12.44:5000/v3",
                 "vim_tenant_name": "osm_demo", "vim_password": "Rw7gln9liP4ClMyHd5OFsw==",
                 "description": "Openstack on NUC", "vim_type": "openstack",
                 "admin": {"modified": 1566474766.7288046,
                           "deployed": {"RO": "5bc59656-c4d3-11e9-b1e5-02420aff0006",
                                        "RO-account": "5bd772e0-c4d3-11e9-b1e5-02420aff0006"},
                           "projects_write": ["admin"], "operationalState": "ENABLED",
                           "detailed-status": "Done", "created": 1566474766.7288046,
                           "projects_read": ["admin"]},
                 "config": {}, "schema_version": "1.1"},
                {"_id": "8460b670-31cf-4fae-9f3e-d0dd6c57b61e", "vim_user": "admin", "name": "OpenStack1",
                 "vim_url": "http://10.234.12.47:5000/v3", "vim_type": "openstack",
                 "vim_tenant_name": "osm_demo", "vim_password": "NsgJJDlCdKreX30FQFNz7A==",
                 "description": "Openstack on Dell",
                 "_admin": {"modified": 1566992449.5942867,
                            "deployed": {"RO": "aed94f86-c988-11e9-bb38-02420aff0088",
                                         "RO-account": "aee72fac-c988-11e9-bb38-02420aff0088"},
                            "projects_write": ["0a5d0c5b-7e08-48a1-a686-642a038bbd70"],
                            "operationalState": "ENABLED", "detailed-status": "Done", "created": 1566992449.5942867,
                            "projects_read": ["0a5d0c5b-7e08-48a1-a686-642a038bbd70"]}, "config": {},
                 "schema_version": "1.1"},
                {"_id": "9b8b5268-acb7-4893-b494-a77656b418f2",
                 "vim_user": "admin", "name": "OpenStack2",
                 "vim_url": "http://10.234.12.44:5000/v3",
                 "vim_type": "openstack", "vim_tenant_name": "osm_demo",
                 "vim_password": "AnAV3xtoiwwdnAfv0KahSw==",
                 "description": "Openstack on NUC",
                 "_admin": {"modified": 1566992484.9190753,
                            "deployed": {"RO": "c3d61158-c988-11e9-bb38-02420aff0088",
                                         "RO-account": "c3ec973e-c988-11e9-bb38-02420aff0088"},
                            "projects_write": ["0a5d0c5b-7e08-48a1-a686-642a038bbd70"],
                            "operationalState": "ENABLED", "detailed-status": "Done",
                            "created": 1566992484.9190753,
                            "projects_read": ["0a5d0c5b-7e08-48a1-a686-642a038bbd70"]},
                 "config": {}, "schema_version": "1.1"},
                {"_id": "3645f215-f32d-4355-b5ab-df0a2e2233c3", "vim_user": "admin", "name": "OpenStack3",
                 "vim_url": "http://10.234.12.46:5000/v3", "vim_tenant_name": "osm_demo",
                 "vim_password": "XkG2w8e8/DiuohCFNp0+lQ==", "description": "Openstack on NUC",
                 "vim_type": "openstack",
                 "_admin": {"modified": 1567421247.7016313,
                            "deployed": {"RO": "0e80f6a2-cd6f-11e9-bb50-02420aff00b6",
                                         "RO-account": "0e974524-cd6f-11e9-bb50-02420aff00b6"},
                            "projects_write": ["0a5d0c5b-7e08-48a1-a686-642a038bbd70"],
                            "operationalState": "ENABLED", "detailed-status": "Done",
                            "created": 1567421247.7016313,
                            "projects_read": ["0a5d0c5b-7e08-48a1-a686-642a038bbd70"]},
                 "schema_version": "1.1", "config": {}},
                {"_id": "53f8f2bb-88b5-4bf9-babf-556698b5261f",
                 "vim_user": "admin", "name": "OpenStack4",
                 "vim_url": "http://10.234.12.43:5000/v3",
                 "vim_tenant_name": "osm_demo",
                 "vim_password": "GLrgVn8fMVneXMZq1r4yVA==",
                 "description": "Openstack on NUC",
                 "vim_type": "openstack",
                 "_admin": {"modified": 1567421296.1576457,
                            "deployed": {
                                "RO": "2b43c756-cd6f-11e9-bb50-02420aff00b6",
                                "RO-account": "2b535aea-cd6f-11e9-bb50-02420aff00b6"},
                            "projects_write": [
                                "0a5d0c5b-7e08-48a1-a686-642a038bbd70"],
                            "operationalState": "ENABLED",
                            "detailed-status": "Done",
                            "created": 1567421296.1576457,
                            "projects_read": [
                                "0a5d0c5b-7e08-48a1-a686-642a038bbd70"]},
                 "schema_version": "1.1", "config": {}}]

# FIXME this is not correct re mgmt-network setting.
nsd_from_db = {"_id": "15fc1941-f095-4cd8-af2d-1000bd6d9eaa", "short-name": "three_vnf_constrained_nsd_low",
               "name": "three_vnf_constrained_nsd_low", "version": "1.0",
               "description": "Placement constraints NSD",
               "_admin": {"modified": 1567672251.7531693,
                          "storage": {"pkg-dir": "ns_constrained_nsd", "fs": "local",
                                      "descriptor": "ns_constrained_nsd/ns_constrained_nsd.yaml",
                                      "zipfile": "package.tar.gz",
                                      "folder": "15fc1941-f095-4cd8-af2d-1000bd6d9eaa", "path": "/app/storage/"},
                          "onboardingState": "ONBOARDED", "usageState": "NOT_IN_USE",
                          "projects_write": ["0a5d0c5b-7e08-48a1-a686-642a038bbd70"], "operationalState": "ENABLED",
                          "userDefinedData": {}, "created": 1567672251.7531693,
                          "projects_read": ["0a5d0c5b-7e08-48a1-a686-642a038bbd70"]},
               "constituent-vnfd": [{"vnfd-id-ref": "cirros_vnfd_v2", "member-vnf-index": "one"},
                                    {"vnfd-id-ref": "cirros_vnfd_v2", "member-vnf-index": "two"},
                                    {"vnfd-id-ref": "cirros_vnfd_v2", "member-vnf-index": "three"}],
               "id": "three_vnf_constrained_nsd_low", "vendor": "ArctosLabs",
               "vld": [{"type": "ELAN", "short-name": "ns_constrained_nsd_low_vld1",
                        "link-constraint": [{"constraint-type": "LATENCY", "value": "100"},
                                            {"constraint-type": "JITTER", "value": "30"}],
                        "vim-network-name": "external", "mgmt-network": True,
                        "id": "three_vnf_constrained_nsd_low_vld1",
                        "vnfd-connection-point-ref": [
                            {"vnfd-id-ref": "cirros_vnfd_v2", "member-vnf-index-ref": "one",
                             "vnfd-connection-point-ref": "vnf-cp0"},
                            {"vnfd-id-ref": "cirros_vnfd_v2",
                             "member-vnf-index-ref": "two",
                             "vnfd-connection-point-ref": "vnf-cp0"}],
                        "name": "ns_constrained_nsd_vld1"},
                       {"type": "ELAN", "short-name": "ns_constrained_nsd_low_vld2",
                        "link-constraint": [{"constraint-type": "LATENCY", "value": "50"},
                                            {"constraint-type": "JITTER", "value": "30"}],
                        "vim-network-name": "lanretxe", "mgmt-network": True,
                        "id": "three_vnf_constrained_nsd_low_vld2",
                        "vnfd-connection-point-ref": [
                            {"vnfd-id-ref": "cirros_vnfd_v2", "member-vnf-index-ref": "two",
                             "vnfd-connection-point-ref": "vnf-cp0"},
                            {"vnfd-id-ref": "cirros_vnfd_v2", "member-vnf-index-ref": "three",
                             "vnfd-connection-point-ref": "vnf-cp0"}],
                        "name": "ns_constrained_nsd_vld2"}]}


######################################################
# These are helper functions to handle unittest of asyncio.
# Inspired by: https://blog.miguelgrinberg.com/post/unit-testing-asyncio-code
def _run(co_routine):
    return asyncio.get_event_loop().run_until_complete(co_routine)


def _async_mock(*args, **kwargs):
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


######################################################

class TestServer(TestCase):

    def _produce_ut_vim_accounts_info(self, list_of_vims):
        """
        FIXME temporary, we will need more control over vim_urls and _id for test purpose - make a generator
        :return: vim_url and _id as dict, i.e. extract these from vim_accounts data
        """
        return {_['vim_url']: _['_id'] for _ in list_of_vims}

    def _produce_ut_vnf_price_list(self):
        price_list_file = "vnf_price_list.yaml"
        with open(str(Path(price_list_file))) as pl_fd:
            price_list_data = yaml.safe_load_all(pl_fd)
            return {i['vnfd']: {i1['vim_url']: i1['price'] for i1 in i['prices']} for i in next(price_list_data)}

    def _populate_pil_info(self, file):
        """
        FIXME we need more control over content in pil information - more files or generator and data
        Note str(Path()) is a 3.5 thing
        """
        with open(str(Path(file))) as pp_fd:
            test_data = yaml.safe_load_all(pp_fd)
            return next(test_data)

    @mock.patch.object(Config, '_read_config_file')
    @mock.patch.object(Config, 'get', side_effect=['doesnotmatter', 'memory', 'memory', 'local', 'doesnotmatter'])
    def serverSetup(self, mock_get, mock__read_config_file):
        """
        Helper that returns a Server object
        :return:
        """
        cfg = Config(None)
        return Server(cfg)

    def _adjust_path(self, file):
        """In case we are not running from test directory,
        then assume we are in top level directory (e.g. running from tox) and adjust file path accordingly"""
        path_component = '/osm_pla/test/'
        real_path = os.path.realpath(file)
        if path_component not in real_path:
            return os.path.dirname(real_path) + path_component + os.path.basename(real_path)
        else:
            return real_path

    def test__get_nslcmop(self):
        server = self.serverSetup()
        server.db = Mock()
        _ = server._get_nslcmop(nslcmop_record_wo_pinning["id"])
        server.db.get_one.assert_called_with("nslcmops", {'_id': nslcmop_record_wo_pinning["id"]})

    def test__get_nsd(self):  # OK
        server = self.serverSetup()
        server.db = Mock()
        _ = server._get_nsd(nslcmop_record_wo_pinning['operationParams']['nsdId'])
        server.db.get_one.assert_called_with("nsds", {'_id': nslcmop_record_wo_pinning['operationParams']['nsdId']})

    def test__get_vim_accounts(self):  # OK
        server = self.serverSetup()
        server.db = Mock()
        _ = server._get_vim_accounts(nslcmop_record_wo_pinning['operationParams']['validVimAccounts'])
        server.db.get_list.assert_called_with('vim_accounts',
                                              {'_id': nslcmop_record_wo_pinning['operationParams']['validVimAccounts']})

    def test__get_vnf_price_list(self):
        server = self.serverSetup()
        pl = server._get_vnf_price_list(Path(self._adjust_path('./vnf_price_list.yaml')))
        self.assertIs(type(pl), dict, "price list not a dictionary")
        for k, v in pl.items():
            self.assertIs(type(v), dict, "price list values not a dict")

    def test__get_pil_info(self):
        server = self.serverSetup()
        ppi = server._get_pil_info(Path(self._adjust_path('./pil_price_list.yaml')))
        self.assertIs(type(ppi), dict, "pil is not a dict")
        self.assertIn('pil', ppi.keys(), "pil has no pil key")
        self.assertIs(type(ppi['pil']), list, "pil does not contain a list")
        # check for expected keys
        expected_keys = {'pil_description', 'pil_price', 'pil_latency', 'pil_jitter', 'pil_endpoints'}
        self.assertEqual(expected_keys, ppi['pil'][0].keys(), 'expected keys not found')

    def test_handle_kafka_command(self):  # OK
        server = self.serverSetup()
        server.loop.create_task = Mock()
        server.handle_kafka_command('pli', 'get_placement', {})
        server.loop.create_task.assert_not_called()
        server.loop.create_task.reset_mock()
        server.handle_kafka_command('pla', 'get_placement', {'nslcmopId': nslcmop_record_wo_pinning["id"]})
        self.assertTrue(server.loop.create_task.called, 'create_task not called')
        args, kwargs = server.loop.create_task.call_args
        self.assertIn('Server.get_placement', str(args[0]), 'get_placement not called')

    @mock.patch.object(NsPlacementDataFactory, '__init__', lambda x0, x1, x2, x3, x4, x5, x6: None)
    @mock.patch.object(MznPlacementConductor, 'do_placement_computation')
    @mock.patch.object(NsPlacementDataFactory, 'create_ns_placement_data')
    @mock.patch.object(Server, '_get_vim_accounts')
    @mock.patch.object(Server, '_get_nsd')
    @mock.patch.object(Server, '_get_nslcmop')
    @mock.patch.object(Server, '_get_vnf_price_list')
    @mock.patch.object(Server, '_get_pil_info')
    def test_get_placement(self, mock_get_pil_info, mock_get_vnf_price_list, mock__get_nslcmop, mock__get_nsd,
                           mock__get_vim_accounts,
                           mock_create_ns_placement_data,
                           mock_do_placement_computation):
        """
        run _get_placement and check that things get called as expected
        :return:
        """
        placement_ret_val = [{'vimAccountId': 'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': 'one'},
                             {'vimAccountId': 'aaaaaaaa-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': 'two'},
                             {'vimAccountId': 'aaaaaaaa-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': 'three'}]
        server = self.serverSetup()

        server.msgBus.aiowrite = _async_mock()
        mock__get_nsd.return_value = nsd_from_db
        mock__get_vim_accounts.return_value = list_of_vims

        # FIXME need update to match nslcmop, not for test but for consistency
        mock_do_placement_computation.return_value = placement_ret_val
        _run(server.get_placement(nslcmop_record_wo_pinning['id']))

        self.assertTrue(mock_get_vnf_price_list.called, '_get_vnf_price_list not called as expected')
        self.assertTrue(mock_get_pil_info.called, '_get_pil_info not called as expected')
        self.assertTrue(mock__get_nslcmop.called, '_get_nslcmop not called as expected')
        # mock_get_nsd.assert_called_once() assert_called_once() for python > 3.5
        self.assertTrue(mock__get_nsd.called, 'get_nsd not called as expected')
        # mock_get_enabled_vims.assert_called_once() assert_called_once() for python > 3.5
        self.assertTrue(mock__get_vim_accounts.called, 'get_vim_accounts not called as expected')
        # mock_create_ns_placement_data.assert_called_once() assert_called_once() for python > 3.5
        self.assertTrue(mock_create_ns_placement_data.called, 'create_ns_placement_data not called as expected')
        # mock_do_placement_computation.assert_called_once()  assert_called_once() for python > 3.5
        self.assertTrue(mock_do_placement_computation.called, 'do_placement_computation not called as expected')
        self.assertTrue(server.msgBus.aiowrite.mock.called)

        args, kwargs = server.msgBus.aiowrite.mock.call_args
        self.assertTrue(len(args) == 3, 'invalid format')
        self.assertEqual('pla', args[0], 'topic invalid')
        self.assertEqual('placement', args[1], 'message invalid')
        # extract placement result and check content
        rsp_payload = args[2]

        expected_rsp_keys = {'placement'}
        self.assertEqual(expected_rsp_keys, set(rsp_payload.keys()), "placement response missing keys")
        self.assertIs(type(rsp_payload['placement']), dict, 'placement not a dict')

        expected_placement_keys = {'vnf', 'nslcmopId'}
        self.assertEqual(expected_placement_keys, set(rsp_payload['placement']), "placement keys invalid")

        vim_account_candidates = [e['vimAccountId'] for e in placement_ret_val]

        self.assertEqual(nslcmop_record_wo_pinning['id'], rsp_payload['placement']['nslcmopId'], "nslcmopId invalid")

        self.assertIs(type(rsp_payload['placement']['vnf']), list, 'vnf not a list')
        expected_vnf_keys = {'vimAccountId', 'member-vnf-index'}
        self.assertEqual(expected_vnf_keys, set(rsp_payload['placement']['vnf'][0]), "placement['vnf'] missing keys")
        self.assertIn(rsp_payload['placement']['vnf'][0]['vimAccountId'], vim_account_candidates,
                      "vimAccountId invalid")

    @mock.patch.object(NsPlacementDataFactory, '__init__', lambda x0, x1, x2, x3, x4, x5, x6: None)
    @mock.patch.object(MznPlacementConductor, 'do_placement_computation')
    @mock.patch.object(NsPlacementDataFactory, 'create_ns_placement_data')
    @mock.patch.object(Server, '_get_vim_accounts')
    @mock.patch.object(Server, '_get_nsd')
    @mock.patch.object(Server, '_get_nslcmop')
    @mock.patch.object(Server, '_get_vnf_price_list')
    @mock.patch.object(Server, '_get_pil_info')
    def test_get_placement_with_pinning(self, mock_get_pil_info, mock_get_vnf_price_list, mock__get_nslcmop,
                                        mock__get_nsd, mock__get_vim_accounts,
                                        mock_create_ns_placement_data,
                                        mock_do_placement_computation):
        """
        run _get_placement and check that things get called as expected
        :return:
        """
        placement_ret_val = [{'vimAccountId': 'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': 'one'},
                             {'vimAccountId': 'aaaaaaaa-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': 'two'},
                             {'vimAccountId': 'aaaaaaaa-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': 'three'}]
        server = self.serverSetup()

        server.msgBus.aiowrite = _async_mock()
        mock__get_nsd.return_value = nsd_from_db
        mock__get_vim_accounts.return_value = list_of_vims

        # FIXME need update to match nslcmop, not for test but for consistency
        mock_do_placement_computation.return_value = placement_ret_val
        _run(server.get_placement(nslcmop_record_w_pinning['id']))

        self.assertTrue(mock_get_vnf_price_list.called, '_get_vnf_price_list not called as expected')
        self.assertTrue(mock_get_pil_info.called, '_get_pil_info not called as expected')
        self.assertTrue(mock__get_nslcmop.called, '_get_nslcmop not called as expected')
        # mock_get_nsd.assert_called_once() assert_called_once() for python > 3.5
        self.assertTrue(mock__get_nsd.called, 'get_nsd not called as expected')
        # mock_get_enabled_vims.assert_called_once() assert_called_once() for python > 3.5
        self.assertTrue(mock__get_vim_accounts.called, 'get_vim_accounts not called as expected')
        # mock_create_ns_placement_data.assert_called_once() assert_called_once() for python > 3.5
        self.assertTrue(mock_create_ns_placement_data.called, 'create_ns_placement_data not called as expected')
        # mock_do_placement_computation.assert_called_once()  assert_called_once() for python > 3.5
        self.assertTrue(mock_do_placement_computation.called, 'do_placement_computation not called as expected')
        self.assertTrue(server.msgBus.aiowrite.mock.called)

        args, kwargs = server.msgBus.aiowrite.mock.call_args
        self.assertTrue(len(args) == 3, 'invalid format')
        self.assertEqual('pla', args[0], 'topic invalid')
        self.assertEqual('placement', args[1], 'message invalid')
        # extract placement result and check content
        rsp_payload = args[2]

        expected_rsp_keys = {'placement'}
        self.assertEqual(expected_rsp_keys, set(rsp_payload.keys()), "placement response missing keys")
        self.assertIs(type(rsp_payload['placement']), dict, 'placement not a dict')

        expected_placement_keys = {'vnf', 'nslcmopId'}
        self.assertEqual(expected_placement_keys, set(rsp_payload['placement']), "placement keys invalid")

        vim_account_candidates = [e['vimAccountId'] for e in placement_ret_val]

        self.assertEqual(nslcmop_record_w_pinning['id'], rsp_payload['placement']['nslcmopId'], "nslcmopId invalid")

        self.assertIs(type(rsp_payload['placement']['vnf']), list, 'vnf not a list')
        expected_vnf_keys = {'vimAccountId', 'member-vnf-index'}
        self.assertEqual(expected_vnf_keys, set(rsp_payload['placement']['vnf'][0]), "placement['vnf'] missing keys")
        self.assertIn(rsp_payload['placement']['vnf'][0]['vimAccountId'], vim_account_candidates,
                      "vimAccountId invalid")

    # Note: does not mock reading of price list and pil_info
    @mock.patch.object(NsPlacementDataFactory, '__init__', lambda x0, x1, x2, x3, x4, x5: None)
    @mock.patch.object(MznPlacementConductor, 'do_placement_computation')
    @mock.patch.object(NsPlacementDataFactory, 'create_ns_placement_data')
    @mock.patch.object(Server, '_get_vim_accounts')
    @mock.patch.object(Server, '_get_nsd')
    @mock.patch.object(Server, '_get_nslcmop')
    def test_get_placement_w_exception(self, mock__get_nslcmop,
                                       mock__get_nsd,
                                       mock__get_vim_accounts,
                                       mock_create_ns_placement_data,
                                       mock_do_placement_computation):
        """
        check that raised exceptions are handled and response provided accordingly
        """
        server = self.serverSetup()

        server.msgBus.aiowrite = _async_mock()
        mock__get_nsd.return_value = nsd_from_db
        mock__get_nsd.side_effect = RuntimeError('kaboom!')
        mock__get_vim_accounts.return_value = list_of_vims
        mock_do_placement_computation.return_value = \
            [{'vimAccountId': 'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': '1'},
             {'vimAccountId': 'aaaaaaaa-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': '2'},
             {'vimAccountId': 'aaaaaaaa-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': '3'}]

        _run(server.get_placement(nslcmop_record_w_pinning['id']))
        self.assertTrue(server.msgBus.aiowrite.mock.called)
        args, kwargs = server.msgBus.aiowrite.mock.call_args
        rsp_payload = args[2]
        expected_keys = {'placement'}
        self.assertEqual(expected_keys, set(rsp_payload.keys()), "placement response missing keys")
        self.assertIs(type(rsp_payload['placement']['vnf']), list, 'vnf not a list')
        self.assertEqual([], rsp_payload['placement']['vnf'], 'vnf list not empty')
        self.assertEqual(nslcmop_record_w_pinning['id'], rsp_payload['placement']['nslcmopId'], "nslcmopId invalid")
