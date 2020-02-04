#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
import logging
# import platform
from pathlib import Path

# import pkg_resources
import yaml
from osm_common import dbmemory, dbmongo, msglocal, msgkafka

from osm_pla.config.config import Config
from osm_pla.placement.mznplacement import MznPlacementConductor
from osm_pla.placement.mznplacement import NsPlacementDataFactory


class Server:
    pil_price_list_file = Path('/placement/pil_price_list.yaml')
    vnf_price_list_file = Path('/placement/vnf_price_list.yaml')

    def __init__(self, config: Config, loop=None):
        self.log = logging.getLogger("pla.server")
        self.db = None
        self.msgBus = None
        self.config = config
        self.loop = loop or asyncio.get_event_loop()

        try:
            if config.get('database', 'driver') == "mongo":
                self.db = dbmongo.DbMongo()
                self.db.db_connect(config.get('database'))
            elif config.get('database', 'driver') == "memory":
                self.db = dbmemory.DbMemory()
                self.db.db_connect(config.get('database'))
            else:
                raise Exception("Invalid configuration param '{}' at '[database]':'driver'".format(
                    config.get('database', 'driver')))

            if config.get('message', 'driver') == "local":
                self.msgBus = msglocal.MsgLocal()
            elif config.get('message', 'driver') == "kafka":
                self.msgBus = msgkafka.MsgKafka()
            else:
                raise Exception("Invalid message bus driver {}".format(
                    config.get('message', 'driver')))
            self.msgBus.loop = loop
            self.msgBus.connect(config.get('message'))

        except Exception as e:
            self.log.exception("kafka setup error. Exception: {}".format(e))

    def _get_nslcmop(self, nsdlcmop_id):
        """
        :param nsdlcmop_id:
        :return: nslcmop from database corresponding to nslcmop_id
        """
        db_filter = {"_id": nsdlcmop_id}
        nslcmop = self.db.get_one("nslcmops", db_filter)
        return nslcmop

    def _get_nsd(self, nsd_id):
        """
        :param nsd_id:
        :return: nsd from database corresponding to nsd_id
        """
        db_filter = {"_id": nsd_id}
        return self.db.get_one("nsds", db_filter)

    def _get_vim_accounts(self, vim_account_ids):
        """
        :param vim_account_ids: list of VIM account ids
        :return: list of vim account entries from database corresponding to list in vim_accounts_id
        """
        db_filter = {"_id": vim_account_ids}
        return self.db.get_list("vim_accounts", db_filter)

    def _get_vnf_price_list(self, price_list_file_path):
        """
        read vnf price list configuration file and reformat its content

        :param: price_list_file: Path to price list file
        :return: dictionary formatted as {'<vnfd>': {'<vim-url>':'<price>'}}
        """
        with open(str(price_list_file_path)) as pl_fd:
            price_list_data = yaml.safe_load_all(pl_fd)
            return {i['vnfd']: {i1['vim_url']: i1['price'] for i1 in i['prices']} for i in next(price_list_data)}

    def _get_pil_info(self, pil_info_file_path):
        """
        read and return pil information from file
        :param pil_info_file_path: Path to pil_info file
        :return pil configuration file content as Python object
        """
        with open(str(pil_info_file_path)) as pil_fd:
            data = yaml.safe_load_all(pil_fd)
            return next(data)

    async def get_placement(self, nslcmop_id):
        """
        - Collects and prepares placement information.
        - Request placement computation.
        - Formats and distribute placement result

        Note: exceptions result in empty response message

        :param nslcmop_id:
        :return:
        """
        try:
            nslcmop = self._get_nslcmop(nslcmop_id)
            nsd = self._get_nsd(nslcmop['operationParams']['nsdId'])
            self.log.info("nsd: {}".format(nsd))
            valid_vim_accounts = nslcmop['operationParams']['validVimAccounts']
            vim_accounts_data = self._get_vim_accounts(valid_vim_accounts)
            vims_information = {_['vim_url']: _['_id'] for _ in vim_accounts_data}
            price_list = self._get_vnf_price_list(Server.vnf_price_list_file)
            pil_info = self._get_pil_info(Server.pil_price_list_file)
            pinning = nslcmop['operationParams'].get('vnf')
            self.log.info("pinning: {}".format(pinning))
            order_constraints = nslcmop['operationParams'].get('placement-constraints')
            self.log.info("order constraints: {}".format(order_constraints))

            nspd = NsPlacementDataFactory(vims_information,
                                          price_list,
                                          nsd,
                                          pil_info,
                                          pinning, order_constraints).create_ns_placement_data()

            vnf_placement = MznPlacementConductor(self.log).do_placement_computation(nspd)

        except Exception as e:
            # Note: there is no cure for failure so we have a catch-all clause here
            self.log.exception("PLA fault. Exception: {}".format(e))
            vnf_placement = []
        finally:
            await self.msgBus.aiowrite("pla", "placement",
                                       {'placement': {'vnf': vnf_placement, 'nslcmopId': nslcmop_id}})

    def handle_kafka_command(self, topic, command, params):
        self.log.info("Kafka msg arrived: {} {} {}".format(topic, command, params))
        if topic == "pla" and command == "get_placement":
            nslcmop_id = params.get('nslcmopId')
            self.loop.create_task(self.get_placement(nslcmop_id))

    async def kafka_read(self):
        self.log.info("Task kafka_read start")
        while True:
            try:
                topics = "pla"
                await self.msgBus.aioread(topics, self.loop, self.handle_kafka_command)
            except Exception as e:
                self.log.error("kafka read error. Exception: {}".format(e))
                await asyncio.sleep(5, loop=self.loop)

    def run(self):
        self.loop.run_until_complete(self.kafka_read())
        self.loop.close()
        self.loop = None
        if self.msgBus:
            self.msgBus.disconnect()
