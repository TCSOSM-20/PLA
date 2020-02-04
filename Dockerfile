# Copyright 2020 ETSI
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

FROM ubuntu:16.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install git tox make python3 python3-pip python-all && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install python3-all debhelper python3-setuptools apt-utils libgl1-mesa-glx && \
    DEBIAN_FRONTEND=noninteractive pip3 install -U setuptools setuptools-version-command stdeb

ADD https://github.com/MiniZinc/MiniZincIDE/releases/download/2.4.2/MiniZincIDE-2.4.2-bundle-linux-x86_64.tgz /minizinc.tgz

RUN tar -zxf /minizinc.tgz && \
    mv /MiniZincIDE-2.4.2-bundle-linux /minizinc

RUN mkdir /entry_data \
    && mkdir /entry_data/mzn-lib \
    && ln -s /entry_data/mzn-lib /minizinc/share/minizinc/exec

ENV FZNEXEC "/entry_data/fzn-exec"
ENV PATH "/minizinc/bin:${PATH}"

RUN mkdir /placement
COPY ./osm_pla/test/pil_price_list.yaml /placement/.
COPY ./osm_pla/test/vnf_price_list.yaml /placement/.
