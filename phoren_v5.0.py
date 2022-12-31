#! /usr/bin/env python
# Renomme et rotate image selon leur métadata
#
# DEPENDANCES: PIL exifread
# 
# CHANGELOG
# ---------
# todo: revoir logging des etapes
# 2022-31-12 Nouveau repo juste pour version PYTHON
# 2022-11-25 Réécriture "propre" en vue publication gitlab
#
# -----------------------------
# CODES EXIT
#    0 : OK
#    1 : Pas assez d'argument
#    2 : Trop d'arguments
#    3 : Mauvais argument(s)
#    4 : Extension non supportée
#    5 : Dépendances manquantes
#    6 : Argument 1 n'est pas un dossier
#    7 : Action annulée
#    8 : Aucun fichier trouvé avec extension(s) donnée(s)
# -----------------------------

#########################
#   I M P O R T S       #
#########################

import os, sys
import fnmatch, time
import exifread
from PIL import Image


#########################
#   V A R I A B L E S   #
#########################
MYFNAME   = 'phoren'
MYVERSION = 'v5.0'

DEBUG    = False
SLASH    = os.sep
NL       = os.linesep
MYPATH   = os.path.dirname(os.path.abspath(__file__))
MYFILE   = os.path.abspath(__file__)
DEST_DIR = os.path.join(MYPATH, 'test')
AUTOEXEC = os.path.join(MYPATH, '%s_%s_autoexec.bat' % (MYFNAME, MYVERSION))

# Check si des arguments ont été passés au script

