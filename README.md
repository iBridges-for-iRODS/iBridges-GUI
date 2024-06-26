# iBridges <img src="ibridgesgui/icons/logo.png" width="150" align="right">  

<p align="center">
  <p align="center">
    <a href="https://chstaiger.github.io/iBridges-Gui/"><strong> Documentation »</strong></a> .
    <a href="https://github.com/chStaiger/iBridges-Gui/issues">Report Bug or Request Feature</a>
    .
  </p>
</p>

[![Python package](https://github.com/chStaiger/iBridges-Gui/actions/workflows/linter.yml/badge.svg)](https://github.com/chStaiger/iBridges-Gui/actions/workflows/linter.yml)
[![Quarto Publish](https://github.com/chStaiger/iBridges-Gui/actions/workflows/publish.yml/badge.svg)](https://github.com/chStaiger/iBridges-Gui/actions/workflows/publish.yml)

## About

The git repository contains a generic *iRODS* graphical user interface.  The iRODS functionality is based on [ibridges](https://github.com/UtrechtUniversity/iBridges) and works with any *iRODS* instance.  


![](docs/screenshots/metadata.png)
  
## Highlights

- Works on Windows, Mac OS and Linux
- Runs on Python 3.9 or higher.
- Supported iRODS server versions: 4.2.11 or higher and 4.3.0 or higher.
- **Upload** and **Download** your data.
- Manipulate the **metadata** on the iRODS server.
- **Synchronize** your data between your local computer and the iRODS server.
- **Search** through all metadata for your dataset or collection.
- Safe default options when working with your data.

## Installation
- The python package 

  ```bash
  pip install ibridgesgui
  ```
  
- A specific branch of the git repository (testers, developers)

  ```bash
  pip install git+https://github.com/chStaiger/iBridges-Gui.git@branch-name
  ```
  
- Locally from code (for developers)

  ```bash
  git clone git@github.com:chStaiger/iBridges-Gui.git
  cd iBridges-Gui
  pip install .
  ```
  
## Start the GUI
- From a pip python package

  ```bash
  ibridges-gui
  ```
- From code (for developers)

  ```bash
  python ibridgesgui/__main__.py
  ```
 
 

## Authors
**Christine Staiger (Maintainer) [ORCID](https://orcid.org/0000-0002-6754-7647)**

- *Wageningen University & Research* 2021 - 2022
- *Utrecht University* 2022

**Tim van Daalen**, *Wageningen University & Research* 2021

**Maarten Schermer (Maintainer) [ORCID](https://orcid.org/my-orcid?orcid=0000-0001-6770-3155)**, *Utrecht University* 2023

**Raoul Schram (Maintainer) [ORCID](https://orcid.org/my-orcid?orcid=0000-0001-6616-230X)**. 
*Utrecht University* 2023

## Contributors

**J.P. Mc Farland**,
*University of Groningen, Center for Information Technology*, 2022
    
## Contributing
### Code
Instructions on how to extend the GUI or contribute to the code base can be found in the [documentation](https://chstaiger.github.io/iBridges-Gui/).

## License
This project is licensed under the GPL-v3 license.
The full license can be found in [LICENSE](LICENSE).
