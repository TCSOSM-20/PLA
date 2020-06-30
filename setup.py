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
from setuptools import setup


def parse_requirements(requirements):
    with open(requirements) as f:
        return [req.strip('\n') for req in f if req.strip('\n') and not req.startswith('#') and '://' not in req]


_name = 'osm_pla'
#  _version_command = ('git describe --match v* --tags --long --dirty', 'pep440-git-full') FIXME we have no tags yet
_version = '0.0.1'  # FIXME temporary workaround for _version_command
_description = 'OSM Placement Module'
_author = "Lars Goran Magnusson"
_author_email = 'lars-goran.magnusson@arctoslabs.com'
_maintainer = 'Lars Goran Magnusson'
_maintainer_email = 'lars-goran.magnusson@arctoslabs.com'
_license = 'Apache 2.0'
_url = 'https://osm.etsi.org/gitweb?p=osm/PLA.git;a=tree'


setup(
    name=_name,
    # version_command=_version_command, FIXME temporary fix
    version=_version,
    description=_description,
    long_description=open('README.md', encoding='utf-8').read(),
    author=_author,
    author_email=_author_email,
    maintainer=_maintainer,
    maintainer_email=_maintainer_email,
    url=_url,
    license=_license,
    packages=[_name],
    package_dir={_name: _name},
    install_requires=[
        'osm-common',
        'jinja2==2.10.3',
        'pymzn==0.18.*',
        'pyyaml==5.1.2'
    ],
    dependency_links=[
        'git+https://osm.etsi.org/gerrit/osm/common.git#egg=osm-common',
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "osm-pla-server = osm_pla.cmd.pla_server:main",
        ]
    },
    setup_requires=['setuptools-version-command']
)
