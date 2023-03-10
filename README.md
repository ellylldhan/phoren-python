# phoren-python

Renomme photo selon leur metadata - version PYTHON

[TOC]

## Pré-requis

- Python > v2.7
- Module Image (ou PIL)
- Module exifread

### Installation

**Installation de Python (Windows)**

1. Sur Windows, ouvrir le Windows Store
2. Chercher 'python'
3. Installer Python > v2.7

**Installation de Python (Debian)**

```sh
$ sudo apt install python3.10
```

**Installation des Modules Python**

1. Sur Windows/Linux, ouvrir un terminal
2. Installer les modules via `pip`

```sh
$ pip install Image
$ pip install exifread
```

- **Image** permet de modifier la rotation d'une image (module **PIL**).
- **exifread** permet de lire les métadata d'une image.

**Permissions Linux**

Facultatif. Pour attribuer les droits d'exécution à l'utilisateur courant :

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
phoren.py /tmp/mesPhotos/ jpeg
```
