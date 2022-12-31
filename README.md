# phoren-python

Renomme photo selon leur metadata - version PYTHON

Voir `./phoren.py --usage` pour plus d'infos.

[TOC]

## Pré-requis

- Python > v2.7
- Module PIL
- Module exifread

### Installation

**Python**

- Sur Windows, ouvrir un terminal
- executer `python` pour ouvrir une fenêtre Windows Store
- Installer Python > v2.7

- Sur Linux

```sh
$ sudo apt install python3.10
```

**Modules Python**

- Sur Windows/Linux, ouvrir un terminal
- Installer les modules via `pip`

```sh
$ pip install Image
$ pip install exifread
```

**Permissions Linux**

Facultatif. 

```sh
$ chmod u+x phoren.py
```

## Utilisation

### Syntaxe

```sh
python phoren.py /chemin/vers/dossier $extension_sans_point
./phoren.py /chemin/vers/dossier $extension_sans_point
```

### Exemples

```sh
phoren.py . JPG
phoren.py
```
