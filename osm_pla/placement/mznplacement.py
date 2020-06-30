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
import platform
import itertools

import pymzn
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader


class MznPlacementConductor(object):
    """
    Knows how to process placement req using minizinc
    """
    if platform.system() == 'Windows':
        default_mzn_path = 'C:\\Program Files\\MiniZinc IDE (bundled)\\minizinc.exe'
    else:
        default_mzn_path = '/minizinc/bin/minizinc'

    def __init__(self, log, mzn_path=default_mzn_path):
        pymzn.config['minizinc'] = mzn_path
        self.log = log  # FIXME what to log (besides forwarding it to MznModelGenerator) here?

    def _run_placement_model(self, mzn_model, ns_desc, mzn_model_data={}):
        """
        Runs the minizinc placement model and post process the result
        Note: in this revision we use the 'item' output mode from pymzn.minizinc since it ease
        post processing of the solutions when we use enumerations in mzn_model
        Note: minizinc does not support '-' in identifiers and therefore we convert back from use of '_' when we
        process the result
        Note: minizinc does not support identifiers starting with numbers and therefore we skip the leading 'vim_'
        when we process the result

        :param mzn_model: a minizinc model as str (note: may also be path to .mzn file)
        :param ns_desc: network service descriptor, carries information about pinned VNFs so those can be included in
         the result
        :param mzn_model_data: minizinc model data dictionary (typically not used with our models)
        :return: list of dicts formatted as {'vimAccountId': '<account id>', 'member-vnf-index': <'index'>}
        or formatted as [{}] if unsatisfiable model
        """
        solns = pymzn.minizinc(mzn_model, data=mzn_model_data, output_mode='item')

        if 'UNSATISFIABLE' in str(solns):
            return [{}]

        solns_as_str = str(solns[0])

        # make it easier to extract the desired information by cleaning from newline, whitespace etc.
        solns_as_str = solns_as_str.replace('\n', '').replace(' ', '').rstrip(';')

        vnf_vim_mapping = (e.split('=') for e in solns_as_str.split(';'))

        res = [{'vimAccountId': e[1][3:].replace('_', '-'), 'member-vnf-index': e[0][3:]} for e in
               vnf_vim_mapping]
        # add any pinned VNFs
        pinned = [{'vimAccountId': e['vim_account'][3:].replace('_', '-'), 'member-vnf-index': e['vnf_id']} for e in
                  ns_desc if 'vim_account' in e.keys()]

        return res + pinned

    def do_placement_computation(self, nspd):
        """
        Orchestrates the placement computation

        :param nspd: placement data
        :return: see _run_placement_model
        """
        mzn_model = MznModelGenerator(self.log).create_model(nspd)
        return self._run_placement_model(mzn_model, nspd['ns_desc'])


class MznModelGenerator(object):
    '''
    Has the capability to generate minizinc models from information contained in
    NsPlacementData objects. Uses jinja2 as templating language for the model
    '''
    default_j2_template = "osm_pla_dynamic_template.j2"
    template_search_path = ['osm_pla/placement', '../placement', '/pla/osm_pla/placement']

    def __init__(self, log):
        '''
        Constructor
        '''
        self.log = log  # FIXME we do not log anything so far

    def create_model(self, ns_placement_data):
        '''
        Creates a minizinc model according to the content of nspd
        nspd - NSPlacementData
        return MZNModel
        '''
        self.log.info('ns_desc: {}'.format(ns_placement_data['ns_desc']))
        self.log.info('vld_desc: {}'.format(ns_placement_data['vld_desc']))
        mzn_model_template = self._load_jinja_template()
        mzn_model = mzn_model_template.render(ns_placement_data)
        self.log.info('Minizinc model: {}'.format(mzn_model))
        return mzn_model

    def _load_jinja_template(self, template_name=default_j2_template):
        """loads the jinja template used for model generation"""
        env = Environment(loader=FileSystemLoader(MznModelGenerator.template_search_path))
        return env.get_template(template_name)


class NsPlacementDataFactory(object):
    """
    process information an network service and applicable network infrastructure resources in order to produce
    information tailored for the minizinc model code generator
    """

    def __init__(self, vim_accounts_info, vnf_prices, nsd, pil_info, pinning=None, order_constraints=None):
        """
        :param vim_accounts_info: a dictionary with vim url as key and id as value, we add a unique index to it for use
        in the mzn array constructs and adjust the value of the id to minizinc acceptable identifier syntax
        :param vnf_prices: a dictionary with 'vnfd-id-ref' as key and a dictionary with vim_urls: cost as value
        :param nsd: the network service descriptor
        :param pil_info: price list and metrics for PoP interconnection links
        :param pinning: list of {'member-vnf-index': '<idx>', 'vim_account': '<vim-account>'}
        :param order_constraints: any constraints provided at instantiation time
        """
        next_idx = itertools.count()
        self._vim_accounts_info = {k: {'id': 'vim' + v.replace('-', '_'), 'idx': next(next_idx)} for k, v in
                                   vim_accounts_info.items()}
        self._vnf_prices = vnf_prices
        self._nsd = nsd
        self._pil_info = pil_info
        self._pinning = pinning
        self._order_constraints = order_constraints

    def _produce_trp_link_characteristics_data(self, characteristics):
        """
        :param characteristics: one of  {pil_latency, pil_price, pil_jitter}
        :return: 2d array of requested trp_link characteristics data
        """
        if characteristics not in {'pil_latency', 'pil_price', 'pil_jitter'}:
            raise Exception('characteristic \'{}\' not supported'.format(characteristics))
        num_vims = len(self._vim_accounts_info)
        trp_link_characteristics = [[0 if col == row else 0x7fff for col in range(num_vims)] for row in range(num_vims)]
        for pil in self._pil_info['pil']:
            if characteristics in pil.keys():
                ep1 = pil['pil_endpoints'][0]
                ep2 = pil['pil_endpoints'][1]
                # only consider links between applicable vims
                if ep1 in self._vim_accounts_info and ep2 in self._vim_accounts_info:
                    idx1 = self._vim_accounts_info[ep1]['idx']
                    idx2 = self._vim_accounts_info[ep2]['idx']
                    trp_link_characteristics[idx1][idx2] = pil[characteristics]
                    trp_link_characteristics[idx2][idx1] = pil[characteristics]

        return trp_link_characteristics

    def _produce_vld_desc(self):
        """
        Creates the expected vlds from the nsd. Includes constraints if part of nsd.
        Overrides constraints with any syntactically correct instantiation parameters
        :return:
        """
        vld_desc = []
        for vld in self._nsd['vld']:
            if vld.get('mgmt-network', False) is False:
                vld_desc_entry = {}
                cp_refs = [ep_ref['member-vnf-index-ref'] for ep_ref in vld['vnfd-connection-point-ref']]
                if len(cp_refs) == 2:
                    vld_desc_entry['cp_refs'] = cp_refs
                    if 'link-constraint' in vld.keys():
                        for constraint in vld['link-constraint']:
                            if constraint['constraint-type'] == 'LATENCY':
                                vld_desc_entry['latency'] = constraint['value']
                            elif constraint['constraint-type'] == 'JITTER':
                                vld_desc_entry['jitter'] = constraint['value']
                    vld_desc.append(vld_desc_entry)

        # create candidates from instantiate params
        if self._order_constraints is not None:
            candidate_vld_desc = []
            # use id to find the endpoints in the nsd
            for entry in self._order_constraints.get('vld-constraints'):
                for vld in self._nsd['vld']:
                    if entry['id'] == vld['id']:
                        vld_desc_instantiate_entry = {}
                        cp_refs = [ep_ref['member-vnf-index-ref'] for ep_ref in vld['vnfd-connection-point-ref']]
                        vld_desc_instantiate_entry['cp_refs'] = cp_refs
                        # add whatever constraints that are provided to the vld_desc_entry
                        # misspelled 'link-constraints' => empty dict
                        # lack (or misspelling) of one or both supported constraints => entry not appended
                        for constraint, value in entry.get('link-constraints', {}).items():
                            if constraint == 'latency':
                                vld_desc_instantiate_entry['latency'] = value
                            elif constraint == 'jitter':
                                vld_desc_instantiate_entry['jitter'] = value
                        if set(['latency', 'jitter']).intersection(vld_desc_instantiate_entry.keys()):
                            candidate_vld_desc.append(vld_desc_instantiate_entry)
            # merge with nsd originated, FIXME log any deviations?
            for vld_d in vld_desc:
                for vld_d_i in candidate_vld_desc:
                    if set(vld_d['cp_refs']) == set(vld_d_i['cp_refs']):
                        if vld_d_i.get('jitter'):
                            vld_d['jitter'] = vld_d_i['jitter']
                        if vld_d_i.get('latency'):
                            vld_d['latency'] = vld_d_i['latency']

        return vld_desc

    def _produce_ns_desc(self):
        """
        collect information for the ns_desc part of the placement data
        for the vim_accounts that are applicable, collect the vnf_price
        """
        ns_desc = []
        for vnfd in self._nsd['constituent-vnfd']:
            vnf_info = {'vnf_id': vnfd['member-vnf-index']}
            # prices
            prices_for_vnfd = self._vnf_prices[vnfd['vnfd-id-ref']]
            # the list of prices must be ordered according to the indexing of the vim_accounts
            price_list = [_ for _ in range(len(self._vim_accounts_info))]
            for k in prices_for_vnfd.keys():
                if k in self._vim_accounts_info.keys():
                    price_list[self._vim_accounts_info[k]['idx']] = prices_for_vnfd[k]
            vnf_info['vnf_price_per_vim'] = price_list

            # pinning to dc
            if self._pinning is not None:
                for pinned_vnf in self._pinning:
                    if vnfd['member-vnf-index'] == pinned_vnf['member-vnf-index']:
                        vnf_info['vim_account'] = 'vim' + pinned_vnf['vimAccountId'].replace('-', '_')

            ns_desc.append(vnf_info)
        return ns_desc

    def create_ns_placement_data(self):
        """populate NsPlacmentData object
        """
        ns_placement_data = {'vim_accounts': [vim_data['id'] for _, vim_data in sorted(self._vim_accounts_info.items(),
                                                                                       key=lambda item: item[1][
                                                                                           'idx'])],
                             'trp_link_latency': self._produce_trp_link_characteristics_data('pil_latency'),
                             'trp_link_jitter': self._produce_trp_link_characteristics_data('pil_jitter'),
                             'trp_link_price_list': self._produce_trp_link_characteristics_data('pil_price'),
                             'ns_desc': self._produce_ns_desc(),
                             'vld_desc': self._produce_vld_desc(),
                             'generator_data': {'file': __file__, 'time': datetime.datetime.now()}}

        return ns_placement_data
