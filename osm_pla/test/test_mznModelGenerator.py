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
import datetime
import logging
# import unittest
from unittest import TestCase
# import random
# from operator import itemgetter
import re

from jinja2 import Template

from osm_pla.placement.mznplacement import MznModelGenerator

test_ns_placement_data_str = {
    'vim_accounts': ['vim' + vim_account.replace('-', '_') for vim_account in ['aaaaaaaa-38f5-438d-b8ee-3f93b3531f87',
                                                                               'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87',
                                                                               'cccccccc-ed84-4e49-b5df-a9d117bd731f',
                                                                               'dddddddd-ed84-4e49-b5df-a9d117bd731f',
                                                                               'eeeeeeee-38f5-438d-b8ee-3f93b3531f87']],
    'trp_link_latency': [[0, 50, 100, 150, 200], [0, 0, 100, 150, 200], [0, 0, 0, 150, 200], [0, 0, 0, 0, 200],
                         [0, 0, 0, 0, 0]],
    'trp_link_jitter': [[0, 5, 10, 15, 20], [0, 0, 10, 15, 20], [0, 0, 0, 15, 20], [0, 0, 0, 0, 20],
                        [0, 0, 0, 0, 0]],
    'trp_link_price_list': [[0, 5, 6, 6, 7], [0, 0, 6, 6, 7], [0, 0, 0, 6, 7], [0, 0, 0, 0, 7], [0, 0, 0, 0, 0]],
    'ns_desc': [
        {'vnf_id': 'one', 'vnf_price_per_vim': [50, 51, 52, 53, 54]},
        {'vnf_id': 'two', 'vnf_price_per_vim': [20, 21, 22, 23, 24]},
        {'vnf_id': 'three', 'vnf_price_per_vim': [70, 71, 72, 73, 74]},
        {'vnf_id': 'four', 'vnf_price_per_vim': [40, 41, 42, 43, 44]}],
    'vld_desc': [{'cp_refs': ['one', 'two'], 'latency': 150, 'jitter': 30},
                 {'cp_refs': ['two', 'three'], 'latency': 140, 'jitter': 30},
                 {'cp_refs': ['three', 'four'], 'latency': 130, 'jitter': 30}],
    'generator_data': {'file': __file__, 'time': datetime.datetime.now()}
}

test_ns_placement_data_str_no_vld_constraints = {
    'vim_accounts': ['vim' + vim_account.replace('-', '_') for vim_account in ['aaaaaaaa-38f5-438d-b8ee-3f93b3531f87',
                                                                               'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87',
                                                                               'cccccccc-ed84-4e49-b5df-a9d117bd731f',
                                                                               'dddddddd-ed84-4e49-b5df-a9d117bd731f',
                                                                               'eeeeeeee-38f5-438d-b8ee-3f93b3531f87']],
    'trp_link_latency': [[0, 50, 100, 150, 200], [0, 0, 100, 150, 200], [0, 0, 0, 150, 200], [0, 0, 0, 0, 200],
                         [0, 0, 0, 0, 0]],
    'trp_link_jitter': [[0, 5, 10, 15, 20], [0, 0, 10, 15, 20], [0, 0, 0, 15, 20], [0, 0, 0, 0, 20],
                        [0, 0, 0, 0, 0]],
    'trp_link_price_list': [[0, 5, 6, 6, 7], [0, 0, 6, 6, 7], [0, 0, 0, 6, 7], [0, 0, 0, 0, 7], [0, 0, 0, 0, 0]],
    'ns_desc': [
        {'vnf_id': 'one', 'vnf_price_per_vim': [50, 51, 52, 53, 54]},
        {'vnf_id': 'two', 'vnf_price_per_vim': [20, 21, 22, 23, 24]},
        {'vnf_id': 'three', 'vnf_price_per_vim': [70, 71, 72, 73, 74]},
        {'vnf_id': 'four', 'vnf_price_per_vim': [40, 41, 42, 43, 44]}],
    'vld_desc': [{'cp_refs': ['one', 'two']},
                 {'cp_refs': ['two', 'three']},
                 {'cp_refs': ['three', 'four']}],
    'generator_data': {'file': __file__, 'time': datetime.datetime.now()}
}

test_ns_placement_data = {
    'vim_accounts': ['vim' + vim_account.replace('-', '_') for vim_account in ['aaaaaaaa-38f5-438d-b8ee-3f93b3531f87',
                                                                               'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87',
                                                                               'cccccccc-ed84-4e49-b5df-a9d117bd731f',
                                                                               'dddddddd-ed84-4e49-b5df-a9d117bd731f',
                                                                               'eeeeeeee-38f5-438d-b8ee-3f93b3531f87']],
    'trp_link_latency': [[0, 50, 100, 150, 200], [0, 0, 100, 150, 200], [0, 0, 0, 150, 200], [0, 0, 0, 0, 200],
                         [0, 0, 0, 0, 0]],
    'trp_link_jitter': [[0, 5, 10, 15, 20], [0, 0, 10, 15, 20], [0, 0, 0, 15, 20], [0, 0, 0, 0, 20],
                        [0, 0, 0, 0, 0]],
    'trp_link_price_list': [[0, 5, 6, 6, 7], [0, 0, 6, 6, 7], [0, 0, 0, 6, 7], [0, 0, 0, 0, 7], [0, 0, 0, 0, 0]],
    'ns_desc': [
        {'vnf_id': '1', 'vnf_price_per_vim': [50, 51, 52, 53, 54]},
        {'vnf_id': '2', 'vnf_price_per_vim': [20, 21, 22, 23, 24]},
        {'vnf_id': '3', 'vnf_price_per_vim': [70, 71, 72, 73, 74]},
        {'vnf_id': '4', 'vnf_price_per_vim': [40, 41, 42, 43, 44]}],
    'vld_desc': [{'cp_refs': ['1', '2'], 'latency': 150, 'jitter': 30},
                 {'cp_refs': ['2', '3'], 'latency': 140, 'jitter': 30},
                 {'cp_refs': ['3', '4'], 'latency': 130, 'jitter': 30}],
    'generator_data': {'file': __file__, 'time': datetime.datetime.now()}
}

test_ns_placement_data_w_pinning = {
    'vim_accounts': ['vim' + vim_account.replace('-', '_') for vim_account in ['aaaaaaaa-38f5-438d-b8ee-3f93b3531f87',
                                                                               'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87',
                                                                               'cccccccc-ed84-4e49-b5df-a9d117bd731f',
                                                                               'dddddddd-ed84-4e49-b5df-a9d117bd731f',
                                                                               'eeeeeeee-38f5-438d-b8ee-3f93b3531f87']],
    'trp_link_latency': [[0, 50, 100, 150, 200], [0, 0, 100, 150, 200], [0, 0, 0, 150, 200], [0, 0, 0, 0, 200],
                         [0, 0, 0, 0, 0]],
    'trp_link_jitter': [[0, 5, 10, 15, 20], [0, 0, 10, 15, 20], [0, 0, 0, 15, 20], [0, 0, 0, 0, 20],
                        [0, 0, 0, 0, 0]],
    'trp_link_price_list': [[0, 5, 6, 6, 7], [0, 0, 6, 6, 7], [0, 0, 0, 6, 7], [0, 0, 0, 0, 7], [0, 0, 0, 0, 0]],
    'ns_desc': [
        {'vnf_id': '1', 'vnf_price_per_vim': [50, 51, 52, 53, 54]},
        {'vnf_id': '2', 'vnf_price_per_vim': [20, 21, 22, 23, 24],
         'vim_account': 'vimeeeeeeee_38f5_438d_b8ee_3f93b3531f87'},
        {'vnf_id': '3', 'vnf_price_per_vim': [70, 71, 72, 73, 74]},
        {'vnf_id': '4', 'vnf_price_per_vim': [40, 41, 42, 43, 44],
         'vim_account': 'vimcccccccc_ed84_4e49_b5df_a9d117bd731f'}],
    'vld_desc': [{'cp_refs': ['1', '2'], 'latency': 150, 'jitter': 30},
                 {'cp_refs': ['2', '3'], 'latency': 140, 'jitter': 30},
                 {'cp_refs': ['3', '4'], 'latency': 130, 'jitter': 30}],
    'generator_data': {'file': __file__, 'time': datetime.datetime.now()}
}

test_ns_placement_data_w_pinning_str = {
    'vim_accounts': ['vim' + vim_account.replace('-', '_') for vim_account in ['aaaaaaaa-38f5-438d-b8ee-3f93b3531f87',
                                                                               'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87',
                                                                               'cccccccc-ed84-4e49-b5df-a9d117bd731f',
                                                                               'dddddddd-ed84-4e49-b5df-a9d117bd731f',
                                                                               'eeeeeeee-38f5-438d-b8ee-3f93b3531f87']],
    'trp_link_latency': [[0, 50, 100, 150, 200], [0, 0, 100, 150, 200], [0, 0, 0, 150, 200], [0, 0, 0, 0, 200],
                         [0, 0, 0, 0, 0]],
    'trp_link_jitter': [[0, 5, 10, 15, 20], [0, 0, 10, 15, 20], [0, 0, 0, 15, 20], [0, 0, 0, 0, 20],
                        [0, 0, 0, 0, 0]],
    'trp_link_price_list': [[0, 5, 6, 6, 7], [0, 0, 6, 6, 7], [0, 0, 0, 6, 7], [0, 0, 0, 0, 7], [0, 0, 0, 0, 0]],
    'ns_desc': [
        {'vnf_id': 'one', 'vnf_price_per_vim': [50, 51, 52, 53, 54]},
        {'vnf_id': 'two', 'vnf_price_per_vim': [20, 21, 22, 23, 24],
         'vim_account': 'vimeeeeeeee_38f5_438d_b8ee_3f93b3531f87'},
        {'vnf_id': 'three', 'vnf_price_per_vim': [70, 71, 72, 73, 74]},
        {'vnf_id': 'four', 'vnf_price_per_vim': [40, 41, 42, 43, 44],
         'vim_account': 'vimcccccccc_ed84_4e49_b5df_a9d117bd731f'}],
    'vld_desc': [{'cp_refs': ['one', 'two'], 'latency': 150, 'jitter': 30},
                 {'cp_refs': ['two', 'three'], 'latency': 140, 'jitter': 30},
                 {'cp_refs': ['three', 'four'], 'latency': 130, 'jitter': 30}],
    'generator_data': {'file': __file__, 'time': datetime.datetime.now()}
}

test_ns_placement_data_str_no_vld = {
    'vim_accounts': ['vim' + vim_account.replace('-', '_') for vim_account in ['aaaaaaaa-38f5-438d-b8ee-3f93b3531f87',
                                                                               'bbbbbbbb-38f5-438d-b8ee-3f93b3531f87',
                                                                               'cccccccc-ed84-4e49-b5df-a9d117bd731f',
                                                                               'dddddddd-ed84-4e49-b5df-a9d117bd731f',
                                                                               'eeeeeeee-38f5-438d-b8ee-3f93b3531f87']],
    'trp_link_latency': [[0, 50, 100, 150, 200], [0, 0, 100, 150, 200], [0, 0, 0, 150, 200], [0, 0, 0, 0, 200],
                         [0, 0, 0, 0, 0]],
    'trp_link_jitter': [[0, 5, 10, 15, 20], [0, 0, 10, 15, 20], [0, 0, 0, 15, 20], [0, 0, 0, 0, 20],
                        [0, 0, 0, 0, 0]],
    'trp_link_price_list': [[0, 5, 6, 6, 7], [0, 0, 6, 6, 7], [0, 0, 0, 6, 7], [0, 0, 0, 0, 7], [0, 0, 0, 0, 0]],
    'ns_desc': [
        {'vnf_id': 'one', 'vnf_price_per_vim': [50, 51, 52, 53, 54]}],
    'vld_desc': [],
    'generator_data': {'file': __file__, 'time': datetime.datetime.now()}
}

expected_model_fragment = """
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
array[Vims, Vims] of int: trp_link_jitter = [|0,5,10,15,20,
|0,0,10,15,20,
|0,0,0,15,20,
|0,0,0,0,20,
|0,0,0,0,0,
|]; % Transport link jitter between data centers
array[Vims, Vims] of int: trp_link_price_list = [|0,5,6,6,7,
|0,0,6,6,7,
|0,0,0,6,7,
|0,0,0,0,7,
|0,0,0,0,0,
|]; % Transport link price list
array[Vims] of int: vim_price_list_1 = [50,51,52,53,54];
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
expected_model_fragment_str = """
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
array[Vims, Vims] of int: trp_link_jitter = [|0,5,10,15,20,
|0,0,10,15,20,
|0,0,0,15,20,
|0,0,0,0,20,
|0,0,0,0,0,
|]; % Transport link jitter between data centers
array[Vims, Vims] of int: trp_link_price_list = [|0,5,6,6,7,
|0,0,6,6,7,
|0,0,0,6,7,
|0,0,0,0,7,
|0,0,0,0,0,
|]; % Transport link price list
array[Vims] of int: vim_price_list_one = [50,51,52,53,54];
array[Vims] of int: vim_price_list_two = [20,21,22,23,24];
array[Vims] of int: vim_price_list_three = [70,71,72,73,74];
array[Vims] of int: vim_price_list_four = [40,41,42,43,44];


% This is the NETWORK BASIC LOAD MODEL (CONSUMED)
% NOTE. This is not applicable in OSM Release 7

% This is the SERVICE CONSUMPTION MODEL
% These are the variables, i.e. which DC to select for each VNF
var Vims: VNFone;
var Vims: VNFtwo;
var Vims: VNFthree;
var Vims: VNFfour;


% These are the set of rules for selecting DCs to VNFs
constraint trp_link_latency[VNFone, VNFtwo] <= 150;
constraint trp_link_latency[VNFtwo, VNFthree] <= 140;
constraint trp_link_latency[VNFthree, VNFfour] <= 130;
constraint trp_link_jitter[VNFone, VNFtwo] <= 30;
constraint trp_link_jitter[VNFtwo, VNFthree] <= 30;
constraint trp_link_jitter[VNFthree, VNFfour] <= 30;

% Calculate the cost for VNFs and cost for transport link and total cost
var int: used_transport_cost =trp_link_price_list[VNFone, VNFtwo]+
trp_link_price_list[VNFtwo, VNFthree]+
trp_link_price_list[VNFthree, VNFfour];

var int: used_vim_cost =vim_price_list_one[VNFone]+
vim_price_list_two[VNFtwo]+
vim_price_list_three[VNFthree]+
vim_price_list_four[VNFfour];

var int: total_cost = used_transport_cost + used_vim_cost;

solve minimize total_cost;
"""

expected_model_fragment_str_no_vld_constraints = """
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
array[Vims, Vims] of int: trp_link_jitter = [|0,5,10,15,20,
|0,0,10,15,20,
|0,0,0,15,20,
|0,0,0,0,20,
|0,0,0,0,0,
|]; % Transport link jitter between data centers
array[Vims, Vims] of int: trp_link_price_list = [|0,5,6,6,7,
|0,0,6,6,7,
|0,0,0,6,7,
|0,0,0,0,7,
|0,0,0,0,0,
|]; % Transport link price list
array[Vims] of int: vim_price_list_one = [50,51,52,53,54];
array[Vims] of int: vim_price_list_two = [20,21,22,23,24];
array[Vims] of int: vim_price_list_three = [70,71,72,73,74];
array[Vims] of int: vim_price_list_four = [40,41,42,43,44];


% This is the NETWORK BASIC LOAD MODEL (CONSUMED)
% NOTE. This is not applicable in OSM Release 7

% This is the SERVICE CONSUMPTION MODEL
% These are the variables, i.e. which DC to select for each VNF
var Vims: VNFone;
var Vims: VNFtwo;
var Vims: VNFthree;
var Vims: VNFfour;


% These are the set of rules for selecting DCs to VNFs

% Calculate the cost for VNFs and cost for transport link and total cost
var int: used_transport_cost =trp_link_price_list[VNFone, VNFtwo]+
trp_link_price_list[VNFtwo, VNFthree]+
trp_link_price_list[VNFthree, VNFfour];

var int: used_vim_cost =vim_price_list_one[VNFone]+
vim_price_list_two[VNFtwo]+
vim_price_list_three[VNFthree]+
vim_price_list_four[VNFfour];

var int: total_cost = used_transport_cost + used_vim_cost;

solve minimize total_cost;
"""

expected_model_fragment_w_pinning = """
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
array[Vims, Vims] of int: trp_link_jitter = [|0,5,10,15,20,
|0,0,10,15,20,
|0,0,0,15,20,
|0,0,0,0,20,
|0,0,0,0,0,
|]; % Transport link jitter between data centers
array[Vims, Vims] of int: trp_link_price_list = [|0,5,6,6,7,
|0,0,6,6,7,
|0,0,0,6,7,
|0,0,0,0,7,
|0,0,0,0,0,
|]; % Transport link price list
array[Vims] of int: vim_price_list_1 = [50,51,52,53,54];
array[Vims] of int: vim_price_list_2 = [20,21,22,23,24];
array[Vims] of int: vim_price_list_3 = [70,71,72,73,74];
array[Vims] of int: vim_price_list_4 = [40,41,42,43,44];


% This is the NETWORK BASIC LOAD MODEL (CONSUMED)
% NOTE. This is not applicable in OSM Release 7

% This is the SERVICE CONSUMPTION MODEL
% These are the variables, i.e. which DC to select for each VNF
var Vims: VNF1;
Vims: VNF2 = vimeeeeeeee_38f5_438d_b8ee_3f93b3531f87;
var Vims: VNF3;
Vims: VNF4 = vimcccccccc_ed84_4e49_b5df_a9d117bd731f;


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

expected_model_fragment_w_pinning_str = """
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
array[Vims, Vims] of int: trp_link_jitter = [|0,5,10,15,20,
|0,0,10,15,20,
|0,0,0,15,20,
|0,0,0,0,20,
|0,0,0,0,0,
|]; % Transport link jitter between data centers
array[Vims, Vims] of int: trp_link_price_list = [|0,5,6,6,7,
|0,0,6,6,7,
|0,0,0,6,7,
|0,0,0,0,7,
|0,0,0,0,0,
|]; % Transport link price list
array[Vims] of int: vim_price_list_one = [50,51,52,53,54];
array[Vims] of int: vim_price_list_two = [20,21,22,23,24];
array[Vims] of int: vim_price_list_three = [70,71,72,73,74];
array[Vims] of int: vim_price_list_four = [40,41,42,43,44];


% This is the NETWORK BASIC LOAD MODEL (CONSUMED)
% NOTE. This is not applicable in OSM Release 7

% This is the SERVICE CONSUMPTION MODEL
% These are the variables, i.e. which DC to select for each VNF
var Vims: VNFone;
Vims: VNFtwo = vimeeeeeeee_38f5_438d_b8ee_3f93b3531f87;
var Vims: VNFthree;
Vims: VNFfour = vimcccccccc_ed84_4e49_b5df_a9d117bd731f;


% These are the set of rules for selecting DCs to VNFs
constraint trp_link_latency[VNFone, VNFtwo] <= 150;
constraint trp_link_latency[VNFtwo, VNFthree] <= 140;
constraint trp_link_latency[VNFthree, VNFfour] <= 130;
constraint trp_link_jitter[VNFone, VNFtwo] <= 30;
constraint trp_link_jitter[VNFtwo, VNFthree] <= 30;
constraint trp_link_jitter[VNFthree, VNFfour] <= 30;

% Calculate the cost for VNFs and cost for transport link and total cost
var int: used_transport_cost =trp_link_price_list[VNFone, VNFtwo]+
trp_link_price_list[VNFtwo, VNFthree]+
trp_link_price_list[VNFthree, VNFfour];

var int: used_vim_cost =vim_price_list_one[VNFone]+
vim_price_list_two[VNFtwo]+
vim_price_list_three[VNFthree]+
vim_price_list_four[VNFfour];

var int: total_cost = used_transport_cost + used_vim_cost;

solve minimize total_cost;
"""

expected_model_fragment_str_no_vld = """
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
array[Vims, Vims] of int: trp_link_jitter = [|0,5,10,15,20,
|0,0,10,15,20,
|0,0,0,15,20,
|0,0,0,0,20,
|0,0,0,0,0,
|]; % Transport link jitter between data centers
array[Vims, Vims] of int: trp_link_price_list = [|0,5,6,6,7,
|0,0,6,6,7,
|0,0,0,6,7,
|0,0,0,0,7,
|0,0,0,0,0,
|]; % Transport link price list
array[Vims] of int: vim_price_list_one = [50,51,52,53,54];


% This is the NETWORK BASIC LOAD MODEL (CONSUMED)
% NOTE. This is not applicable in OSM Release 7

% This is the SERVICE CONSUMPTION MODEL
% These are the variables, i.e. which DC to select for each VNF

var Vims: VNFone;

% These are the set of rules for selecting DCs to VNFs

% Calculate the cost for VNFs and cost for transport link and total cost
var int: used_transport_cost =0;

var int: used_vim_cost =vim_price_list_one[VNFone];

var int: total_cost = used_transport_cost + used_vim_cost;

solve minimize total_cost;
"""


class TestMznModelGenerator(TestCase):
    def test_create_model(self):
        mg = MznModelGenerator(logging.getLogger(__name__))
        mzn_model = mg.create_model(test_ns_placement_data_str)

        # so asserting exact content is difficult due to the datetime.now(), therefore we ignore the first lines
        self.assertTrue(expected_model_fragment_str.replace('\n', '') in
                        mzn_model.replace('\n', ''), "faulty model generated")

    def test_create_model_no_vld_constraints(self):
        """
        instantiate w/o constraints in nsd or order params has a valid model
        :return:
        """
        mg = MznModelGenerator(logging.getLogger(__name__))
        mzn_model = mg.create_model(test_ns_placement_data_str_no_vld_constraints)

        # so asserting exact content is difficult due to the datetime.now(), therefore we ignore the first lines
        self.assertTrue(expected_model_fragment_str_no_vld_constraints.replace('\n', '') in
                        mzn_model.replace('\n', ''), "faulty model generated")

    def test_create_model_w_pinning(self):
        mg = MznModelGenerator(logging.getLogger(__name__))
        mzn_model = mg.create_model(test_ns_placement_data_w_pinning_str)

        # so asserting exact content is difficult due to the datetime.now(), therefore we ignore the first lines
        self.assertTrue(expected_model_fragment_w_pinning_str.replace('\n', '') in
                        mzn_model.replace('\n', ''), "faulty model generated")

    def test_create_model_no_vld(self):
        mg = MznModelGenerator(logging.getLogger(__name__))
        mzn_model = mg.create_model(test_ns_placement_data_str_no_vld)

        # so asserting exact content is difficult due to the datetime.now(), therefore we ignore the first lines
        self.assertTrue(expected_model_fragment_str_no_vld.replace('\n', '') in
                        mzn_model.replace('\n', ''), "faulty model generated")

    def test__load_jinja_template(self):
        """

        add other test to check exception if template not loaded (e.g. invalid template name,
        perhaps also valid name but invalid content (in case jinja2 detects such things))
        """
        mg = MznModelGenerator(logging.getLogger(__name__))
        template = mg._load_jinja_template()  # Note we use the default template
        self.assertTrue(isinstance(template, Template), "failed to load jinja2 template")

    def test_vim_account_replace(self):
        mg = MznModelGenerator(logging.getLogger(__name__))
        nspd = test_ns_placement_data_str
        mzn_model = mg.create_model(nspd)

        expected = '%This is the NETWORK RESOURCE MODEL' + '\n' + 'enum  Vims = {' + '\n'
        for val in test_ns_placement_data_str['vim_accounts']:
            expected = expected + val.replace('-', '_') + ',\n'
        expected = expected[:-2] + '}; % The vim-accounts'
        res = re.findall(expected, mzn_model)
        self.assertEqual(1, len(res), "vim accounts didnt replace from - to _")

    def test_trp_link_price_list(self):
        mg = MznModelGenerator(logging.getLogger(__name__))
        mzn_model = mg.create_model(test_ns_placement_data_str)

        expected = 'array\\[Vims, Vims\\] of int: trp_link_price_list = \\['
        for price_list in test_ns_placement_data_str['trp_link_price_list']:
            expected = expected + '\\|' + (str(price_list)[1:-1]).replace(" ", "") + ',\n'
        expected = expected + '\\|\\]; % Transport link price list'
        res = re.findall(expected, mzn_model)
        self.assertEqual(1, len(res), "price list is not correct")

    def test_link_latency(self):
        mg = MznModelGenerator(logging.getLogger(__name__))
        mzn_model = mg.create_model(test_ns_placement_data_str)

        expected = 'array\\[Vims, Vims\\] of int: trp_link_latency = \\['
        for link_latency in test_ns_placement_data_str['trp_link_latency']:
            expected = expected + '\\|' + (str(link_latency)[1:-1]).replace(" ", "") + ',\n'
        expected = expected + '\\|\\]; % Transport link latency between data centers'
        res = re.findall(expected, mzn_model)
        self.assertEqual(1, len(res), "trp_link_latency values is not correct")

    def test_link_jitter(self):
        mg = MznModelGenerator(logging.getLogger(__name__))
        mzn_model = mg.create_model(test_ns_placement_data_str)

        expected = 'array\\[Vims, Vims\\] of int: trp_link_jitter = \\['
        for link_jitter in test_ns_placement_data_str['trp_link_jitter']:
            expected = expected + '\\|' + (str(link_jitter)[1:-1]).replace(" ", "") + ',\n'
        expected = expected + '\\|\\]; % Transport link jitter between data centers'

        res = re.findall(expected, mzn_model)

        self.assertEqual(1, len(res), "trp_link_jitter values is not correct")

    def test_price_per_vim(self):
        mg = MznModelGenerator(logging.getLogger(__name__))
        mzn_model = mg.create_model(test_ns_placement_data_w_pinning_str)

        expected = ""
        for price_list in test_ns_placement_data_w_pinning_str['ns_desc']:
            expected += 'array\\[Vims\\] of int: vim_price_list_' + price_list.get('vnf_id') + " = "
            temp = str(price_list.get('vnf_price_per_vim'))[1:-1].replace(" ", "")
            expected += "\\[" + temp + "\\];\n"

        res = re.findall(expected, mzn_model)
        self.assertEqual(1, len(res), "mzn_model contains pinning")

    def test_pinning(self):
        mg = MznModelGenerator(logging.getLogger(__name__))
        mzn_model = mg.create_model(test_ns_placement_data_str)

        expected = ""
        for pin_list in test_ns_placement_data_str['ns_desc']:
            if pin_list.get('vim_account'):
                expected += 'Vims: VNF' + pin_list.get('vnf_id') + ' = ' + pin_list.get('vim_account') + ';\n'
            else:
                expected += 'var Vims: VNF' + pin_list.get('vnf_id') + ';\n'

        res = re.findall(expected, mzn_model)
        self.assertEqual(1, len(res), "mzn_model has no pinning")

    def test__without_pinning(self):
        mg = MznModelGenerator(logging.getLogger(__name__))
        mzn_model = mg.create_model(test_ns_placement_data_w_pinning_str)

        expected = ""
        for pin_list in test_ns_placement_data_w_pinning_str['ns_desc']:
            if pin_list.get('vim_account'):
                expected += 'Vims: VNF' + pin_list.get('vnf_id') + ' = ' + pin_list.get('vim_account') + ';\n'
            else:
                expected += 'var Vims: VNF' + pin_list.get('vnf_id') + ';\n'

        res = re.findall(expected, mzn_model)
        self.assertEqual(1, len(res), "mzn_model contains pinning")

    def test__without_constraints_for_jitter_and_latency(self):
        mg = MznModelGenerator(logging.getLogger(__name__))
        mzn_model = mg.create_model(test_ns_placement_data_str_no_vld_constraints)

        expected_latency = "constraint trp_link_latency"
        expected_jitter = "constraint trp_link_jitter"
        latency_or_jitter_was_found = 0
        for l_o_j in test_ns_placement_data_str_no_vld_constraints['vld_desc']:
            if l_o_j.get('latency') or l_o_j.get('jitter'):
                latency_or_jitter_was_found = 1

        res_latency = re.findall(expected_latency, mzn_model)
        res_jitter = re.findall(expected_jitter, mzn_model)
        self.assertEqual(0, latency_or_jitter_was_found, "Jitter or latency was found in the test input")
        self.assertEqual(0, len(res_latency), "constraint trp_link_latency was found in mzn_model")
        self.assertEqual(0, len(res_jitter), "constraint trp_link_latency was found in mzn_model")

    def test__constraints_for_jitter_and_latency(self):
        mg = MznModelGenerator(logging.getLogger(__name__))
        mzn_model = mg.create_model(test_ns_placement_data_str)

        expected_latency = ""
        expected_jitter = ""
        latency_or_jitter_was_found = 0
        for l_o_j in test_ns_placement_data_str['vld_desc']:
            if not (l_o_j.get('latency') or l_o_j.get('jitter')):
                latency_or_jitter_was_found = 1
            expected_latency += "constraint trp_link_latency" + "\\[VNF" + l_o_j.get('cp_refs')[0] + ", VNF" + \
                                l_o_j.get('cp_refs')[1] + "\\] \\<= " + str(l_o_j.get('latency')) + ";\n\n"

            expected_jitter += "constraint trp_link_jitter" + "\\[VNF" + l_o_j.get('cp_refs')[0] + ", VNF" + \
                               l_o_j.get('cp_refs')[1] + "\\] \\<= " + str(l_o_j.get('jitter')) + ";\n\n"

        res = re.findall(expected_latency + expected_jitter, mzn_model)
        self.assertEqual(0, latency_or_jitter_was_found, "Jitter or latency was not found in the test input")
        self.assertEqual(1, len(res), "faulty model generated")
