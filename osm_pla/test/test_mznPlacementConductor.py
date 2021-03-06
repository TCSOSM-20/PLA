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
import logging
# from collections import Counter
from unittest import TestCase, mock

# import osm_pla
from osm_pla.placement.mznplacement import MznPlacementConductor, MznModelGenerator

test_mzn_model = """
% This minizinc model is generated using
% C:/Users/LG/PycharmProjects/dynamic_jijna2_mzn/osm_pla/placement/mznplacement.py
% at 2019-10-24 11:12:02.058905.

%This is the NETWORK RESOURCE MODEL
enum  Vims = {
vimaaaaaaaa_38f5_438d_b8ee_3f93b3531f87,
vimbbbbbbbb_38f5_438d_b8ee_3f93b3531f87,
vimcccccccc_ed84_4e49_b5df_a9d117bd731f,
vimdddddddd_ed84_4e49_b5df_a9d117bd731f,
vimeeeeeeee_38f5_438d_b8ee_3f93b3531f87}; % The vim-accounts
array[Vims, Vims] of int: trp_link_latency = [|0,50,100,150,200,
|0,0,100,150,200,
|0,0,0,150,200,
|0,0,0,0,200,
|0,0,0,0,0,
|]; % Transport link latency between data centers
array[Vims, Vims] of int: trp_link_jitter = [|0,50,100,150,200,
|0,0,100,150,200,
|0,0,0,150,200,
|0,0,0,0,200,
|0,0,0,0,0,
|]; % Transport link jitter between data centers
array[Vims, Vims] of int: trp_link_price_list = [|0,5,6,6,7,
|0,0,6,6,7,
|0,0,0,6,7,
|0,0,0,0,7,
|0,0,0,0,0,
|]; % Transport link price list
array[Vims] of int: vim_price_list_1 = [500,51,52,53,54];
array[Vims] of int: vim_price_list_2 = [20,21,22,23,24];
array[Vims] of int: vim_price_list_3 = [70,71,72,73,74];
array[Vims] of int: vim_price_list_4 = [40,41,42,43,44];


% This is the NETWORK BASIC LOAD MODEL (CONSUMED)
% NOTE. This is not applicable in OSM Release 7

% This is the SERVICE CONSUMPTION MODEL
% These are the variables, i.e. which DC to select for each VNF
var Vims: VNF1;
var Vims: VNF2;
var Vims: VNF3;
var Vims: VNF4;


% These are the set of rules for selecting DCs to VNFs
constraint trp_link_latency[VNF1, VNF2] <= 150;
constraint trp_link_latency[VNF2, VNF3] <= 140;
constraint trp_link_latency[VNF3, VNF4] <= 130;
constraint trp_link_jitter[VNF1, VNF2] <= 30;
constraint trp_link_jitter[VNF2, VNF3] <= 30;
constraint trp_link_jitter[VNF3, VNF4] <= 30;

% Calculate the cost for VNFs and cost for transport link and total cost
var int: used_transport_cost =trp_link_price_list[VNF1, VNF2]+
trp_link_price_list[VNF2, VNF3]+
trp_link_price_list[VNF3, VNF4];

var int: used_vim_cost =vim_price_list_1[VNF1]+
vim_price_list_2[VNF2]+
vim_price_list_3[VNF3]+
vim_price_list_4[VNF4];

var int: total_cost = used_transport_cost + used_vim_cost;

solve minimize total_cost;

"""

test_mzn_model_w_pinning = """
% This minizinc model is generated using
% C:/Users/LG/PycharmProjects/dynamic_jijna2_mzn/osm_pla/placement/mznplacement.py
% at 2019-10-24 11:12:02.058905.

%This is the NETWORK RESOURCE MODEL
enum  Vims = {
vimaaaaaaaa_38f5_438d_b8ee_3f93b3531f87,
vimbbbbbbbb_38f5_438d_b8ee_3f93b3531f87,
vimcccccccc_ed84_4e49_b5df_a9d117bd731f,
vimdddddddd_ed84_4e49_b5df_a9d117bd731f,
vimeeeeeeee_38f5_438d_b8ee_3f93b3531f87}; % The vim-accounts
array[Vims, Vims] of int: trp_link_latency = [|0,50,100,150,200,
|0,0,100,150,200,
|0,0,0,150,200,
|0,0,0,0,200,
|0,0,0,0,0,
|]; % Transport link latency between data centers
array[Vims, Vims] of int: trp_link_jitter = [|0,50,100,150,200,
|0,0,100,150,200,
|0,0,0,150,200,
|0,0,0,0,200,
|0,0,0,0,0,
|]; % Transport link jitter between data centers
array[Vims, Vims] of int: trp_link_price_list = [|0,5,6,6,7,
|0,0,6,6,7,
|0,0,0,6,7,
|0,0,0,0,7,
|0,0,0,0,0,
|]; % Transport link price list
array[Vims] of int: vim_price_list_1 = [500,51,52,53,54];
array[Vims] of int: vim_price_list_2 = [20,21,22,23,24];
array[Vims] of int: vim_price_list_3 = [70,71,72,73,74];
array[Vims] of int: vim_price_list_4 = [40,41,42,43,44];


% This is the NETWORK BASIC LOAD MODEL (CONSUMED)
% NOTE. This is not applicable in OSM Release 7

% This is the SERVICE CONSUMPTION MODEL
% These are the variables, i.e. which DC to select for each VNF
Vims: VNF1 = vimbbbbbbbb_38f5_438d_b8ee_3f93b3531f87;
var Vims: VNF2;
Vims: VNF3 = vimbbbbbbbb_38f5_438d_b8ee_3f93b3531f87;
var Vims: VNF4;


% These are the set of rules for selecting DCs to VNFs
constraint trp_link_latency[VNF1, VNF2] <= 150;
constraint trp_link_latency[VNF2, VNF3] <= 140;
constraint trp_link_latency[VNF3, VNF4] <= 130;
constraint trp_link_jitter[VNF1, VNF2] <= 30;
constraint trp_link_jitter[VNF2, VNF3] <= 30;
constraint trp_link_jitter[VNF3, VNF4] <= 30;

% Calculate the cost for VNFs and cost for transport link and total cost
var int: used_transport_cost =trp_link_price_list[VNF1, VNF2]+
trp_link_price_list[VNF2, VNF3]+
trp_link_price_list[VNF3, VNF4];

var int: used_vim_cost =vim_price_list_1[VNF1]+
vim_price_list_2[VNF2]+
vim_price_list_3[VNF3]+
vim_price_list_4[VNF4];

var int: total_cost = used_transport_cost + used_vim_cost;

solve minimize total_cost;

"""

test_mzn_unsatisfiable_model = """
var 1..2: item1;
var 1..2: item2;
constraint item1 + item2 == 5;

solve satisfy;
"""


class TestMznPlacementConductor(TestCase):
    def test__run_placement_model(self):
        expected_result = [{'vimAccountId': 'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': '1'},
                           {'vimAccountId': 'aaaaaaaa-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': '2'},
                           {'vimAccountId': 'aaaaaaaa-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': '3'},
                           {'vimAccountId': 'aaaaaaaa-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': '4'}]

        mpc = MznPlacementConductor(logging.getLogger(__name__))
        placement = mpc._run_placement_model(mzn_model=test_mzn_model, ns_desc={})
        # sort the result to ease assert with expected result
        sorted_placement = sorted(placement, key=lambda k: k['member-vnf-index'])
        self.assertEqual(expected_result, sorted_placement, 'Faulty syntax or content')

    def test__run_placement_model_w_pinning(self):
        expected_result = [{'vimAccountId': 'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': '1'},
                           {'vimAccountId': 'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': '2'},
                           {'vimAccountId': 'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': '3'},
                           {'vimAccountId': 'aaaaaaaa-38f5-438d-b8ee-3f93b3531f87', 'member-vnf-index': '4'}]

        ns_desc = [{'vnf_price_per_vim': [10, 9, 7, 8], 'vnf_id': '2'},
                   {'vim_account': 'vimbbbbbbbb_38f5_438d_b8ee_3f93b3531f87', 'vnf_price_per_vim': [10, 9, 7, 8],
                    'vnf_id': '1'},
                   {'vnf_price_per_vim': [10, 9, 7, 8], 'vnf_id': '4'},
                   {'vim_account': 'vimbbbbbbbb_38f5_438d_b8ee_3f93b3531f87', 'vnf_price_per_vim': [10, 9, 7, 8],
                    'vnf_id': '3'}
                   ]

        mpc = MznPlacementConductor(logging.getLogger(__name__))
        placement = mpc._run_placement_model(mzn_model=test_mzn_model_w_pinning, ns_desc=ns_desc)
        # sort the result to ease assert with expected result
        sorted_placement = sorted(placement, key=lambda k: k['member-vnf-index'])
        self.assertEqual(expected_result, sorted_placement, 'Faulty syntax or content')

    def test__run_placement_model_unsatisfiable(self):
        mpc = MznPlacementConductor(logging.getLogger(__name__))
        self.assertEqual([{}], mpc._run_placement_model(mzn_model=test_mzn_unsatisfiable_model, ns_desc={}),
                         "Faulty syntax or content for unsatisfiable model")

    @mock.patch.object(MznModelGenerator, 'create_model', side_effect=['%model'])
    @mock.patch.object(MznPlacementConductor, '_run_placement_model')
    def test_do_placement_computation(self, mock_run, mock_create):
        mpc = MznPlacementConductor(logging.getLogger(__name__))
        dummy_nspd = {'ns_desc': {}}
        _ = mpc.do_placement_computation(dummy_nspd)
        mock_create.assert_called_with(dummy_nspd)
        mock_run.assert_called_with('%model', {})
