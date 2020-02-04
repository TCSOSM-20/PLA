<!--
Copyright 2020 ETSI

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.
See the License for the specific language governing permissions and
limitations under the License
-->
# OSM PLA

The PLA module provides computation of optimal placement of xNFs over VIMs by matching NS specific requirements to infrastructure availability and run-time metrics, while considering cost of compute/network.

## Getting Started

Please refer to the [PLA User's Guide](docs/pla_users_guide.md) for a description on how to enable and configure the placement functionality.


## Running the tests

The preferred method to run the PLA unit test is to use tox.

`$ tox`

Please note that some of the unit test modules have dependencies to Minizinc, e.g. test_mznmodels.py and test_mznPlacementConductor.py.
If these tests are to be performed outside a PLA container context, like .e.g. from CLI or from within an IDE, setup the environment as follows (linux example):

```
$ sudo snap install minizinc --classic
$ sudo mkdir -p /minizinc/bin
$ sudo ln -s /snap/bin/minizinc /minizinc/bin/minizinc 
```

## Deployment

PLA is an optional module in OSM. It is installed together with OSM by adding ``--pla`` to the install script.

`$ ./install_osm.sh --pla`

## Built With

* [Python](www.python.org/) - the primary programming language for OSM
* [Minizinc](www.minizinc.org) - a free and open source constraint modelling language

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://osm.etsi.org/gitweb/?p=osm/PLA.git;a=tags).

## License

This project is licensed under the Apache2 License - see the [LICENSE.md](LICENSE) file for details

## Acknowledgments

* **Paolo Dragone** - *PyMzn, a python library that wraps and enhance Minizinc* - [pymzn](https://github.com/paolodragone/pymzn)
* **Billie Thompson** - *Initial work on README.md* - [PurpleBooth](https://github.com/PurpleBooth)

