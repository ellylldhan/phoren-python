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

import os
import logging
import fnmatch
import sys

#########################
#   C L A S S E S       #
#########################
import exifread


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    BOLDRED = '\033[1;91m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class Erreur:
    OK = {
        "code": 0,
        "msg" : Color.BOLD + "==> Pas d'erreur." + Color.END
    }
    PAS_ASSEZ_ARGUMENT = {
        "code": 1,
        "msg" : Color.BOLDRED + "==> ERREUR : Pas assez d'arguments." + Color.END
    }
    TROP_ARGUMENT = {
        "code": 2,
        "msg" : Color.BOLDRED + "==> ERREUR : Trop d'arguments." + Color.END
    }
    MAUVAIS_ARGUMENT = {
        "code": 3,
        "msg" : Color.BOLDRED + "==> ERREUR : Argument invalide." + Color.END
    }
    EXTENSION_NON_SUPPORTEE = {
        "code": 4,
        "msg" : Color.BOLDRED + "==> ERREUR : Extension non supportée." + Color.END
    }
    DEPENDANCES_MANQUANTES = {
        "code": 5,
        "msg" : Color.BOLDRED + "==> ERREUR : Dépendances manquante." + Color.END
    }
    ARG_N_EST_PAS_UN_DOSSIER = {
        "code": 6,
        "msg" : Color.BOLDRED + "==> ERREUR : Argument invalide (n'est pas un dossier)." + Color.END
    }
    ACTION_ANNULEE = {
        "code": 7,
        "msg" : Color.BOLDRED + "==> ERREUR : Action annulée." + Color.END
    }
    AUCUN_FICHIER_TROUVE = {
        "code": 8,
        "msg" : Color.BOLDRED + "==> ERREUR : Aucun fichier trouvé." + Color.END
    }


#########################
#   V A R I A B L E S   #
#########################
MYFNAME = 'phoren'
MYVERSION = 'v5.0'
DESCRIPTION = "Renomme et retourne des images selon leur métadata - Version Python3"
USAGE = """
\033[1mNOM\033[0m
    \033[1m{myfn}\033[0m version \033[1m{ver}\033[0m (Python)

\033[1mDESCRIPTION\033[0m
    {descr}

\033[1mUSAGE\033[0m
    $ \033[1;92m{myfn} /chemin/vers/dossier/origine EXTENSION\033[0m

\033[1mEXEMPLES\033[0m
    $ phoren . jpg 
    $ phoren /mnt/sdcard-420/DCIM JPG
    $ phoren '/c/Users/Moi/Mes Photos/Vacances 2023' jpg

\033[1;91mDEPENDANCES\033[0m
    \033[1mexifread\033[0m   permet de lire les métadata d'une image.
    \033[1mImage\033[0m      permet de modifier la rotation d'une image (module PIL).
    
    Installation des dépendances :
    
    $ python pip install exifread
    $ python pip install Image

\033[1mREMARQUES\033[0m
    - nom d'extension sans point en préfixe (ex. \033[1mJPG\033[0m et non pas \033[1m.JPG\033[0m)
    - nom d'extension est sensible à la casse (ex. \033[1mJPG\033[0m != \033[1mjpg\033[0m)
""".format(myfn=MYFNAME, descr=DESCRIPTION, ver=MYVERSION)

DEBUG = False
# SLASH = os.sep
# NL = os.linesep
MYPATH = os.path.dirname(os.path.abspath(__file__))
# MYFILE = os.path.abspath(__file__)
# DEST_DIR = os.path.join(MYPATH, 'test')
# AUTOEXEC = os.path.join(MYPATH, '%s_%s_autoexec.bat' % (MYFNAME, MYVERSION))

# TAGS_ORIENTATION = ['Image Orientation', 'Orientation']
# TAGS_DATE = [
#     'Media Create Date ', 'Create Date', 'DateTimeOriginal',
#     'Date/Time Original', 'EXIF DateTimeOriginal',
#     'Image DateTime', 'EXIF DateTimeDigitized']
# TAGS_MODELE = ['Camera Model Name', 'Image Model', 'Model']
# TAGS_DIM_LENGTH = ['ExifImageLength', 'ImageLength', 'EXIF ExifImageLength', 'Image ImageLength', 'Exif Image Height']
# TAGS_DIM_WIDTH = ['ExifImageWidth', 'ImageWidth', 'EXIF ExifImageWidth', 'Image ImageWidth', 'Exif Image Width']
TAGS_ORIENTATION = ['Image Orientation']
TAGS_DATE = ['Media Create Date ', 'Create Date', 'DateTimeOriginal', 'Image DateTime']
TAGS_MODELE = ['Camera Model Name', 'Image Model', 'Model']
TAGS_DIM_LENGTH = ['ImageLength', 'Image ImageLength']
TAGS_DIM_WIDTH = ['ImageWidth', 'Image ImageWidth']

CLEAN_LIST = [
    ('-WA0', '_WA0'),
    ('IMG-', ''),
    ('IMG_', ''),
    ('SP800UZ                ', 'SP800UZ'),
    ('WhatsApp Image ', ''),
    (' at ', ' '),
    ('NIKON ', 'NIKON-')]

logging.basicConfig(filename='%s_%s_logs.log' % (MYFNAME, MYVERSION),
                    filemode="a",
                    level=logging.DEBUG,
                    format='%(asctime)s | %(levelname)s | %(message)s')


#######################
# M A I N             #
#######################

def main():
    # Logging start
    logging.info("-" * 48)
    logging.info("... Entrée dans le main")

    # Check Arguments
    chemin, extension = check_args()

    # Récupèration des fichiers à traiter
    flist = [x for x in get_filelist(chemin, '*.' + extension, single_level=True, yield_folders=False)]

    # Traitement des fichiers
    traitement(flist)

    # Création du script de nettoyage, si n'existe pas
    create_clean_file()

    logging.info('... Fin du main')


#######################
# F O N C T I O N S   #
#######################
def anti_doublons(liste):
    result = []
    for l in liste:
        if l and l not in result:
            result.append(l)

    return result


def create_clean_file():
    """Génère les scripts à exécuter pour nettoyer les fichiers générés par l'exécution de phoren"""
    logging.info('... Préparation script nettoyage %s' % os.name)

    # Creation du script de nettoyage si n'existe pas
    clean_file = 'phoren_range_bazar.sh' if os.name == 'posix' else 'phoren_range_bazar.bat'

    if not os.path.isfile(clean_file):
        if os.name == 'posix':
            msg = ['#! /usr/bin/sh']
            msg += ["# Déplace les fichiers générés par phoren"]
            msg += ['echo "Rangement des logs et des scripts ..."']
            msg += ['mkdir logs 2>/dev/null']
            msg += ['mv -v *.log logs 2>/dev/null']
            msg += ['mv -v *script*.py logs 2>/dev/null']
            msg += ['mv -v *script*.bat logs 2>/dev/null']
            msg += ['mv -v *SCRIPT*.py logs 2>/dev/null']
            msg += ['mv -v *SCRIPT*.bat logs 2>/dev/null']
        else:
            msg = ["'Nettoyage des fichiers générés par phoren"]
            msg += ['echo "Rangement des logs et des scripts ..."']
            msg += ['md logs 2>Nul']
            msg += ['move *.log logs 2>Nul']
            msg += ['move *script*.py logs 2>Nul']
            msg += ['move *script*.bat logs 2>Nul']
            msg += ['move *SCRIPT*.py logs 2>Nul']
            msg += ['move *SCRIPT*.bat logs 2>Nul']

        with open(clean_file, 'w') as fw:
            logging.info('... Ecriture script nettoyage')
            fw.write(os.linesep.join(msg))
            fw.close()


def check_args():
    """Check arguments passés à PHOREN"""
    logging.info('... Check arguments passés à PHOREN')
    checkpath = None
    extension = None

    if len(sys.argv) < 3:
        # Check si $2 n'est pas vide
        logging.error("++ L'arg en position 2 n'est pas donné (extension).")
        print(Erreur.PAS_ASSEZ_ARGUMENT.get('msg'))
        print(USAGE)
        exit(Erreur.PAS_ASSEZ_ARGUMENT.get('code'))
    else:
        # Check si DIR existe
        logging.info("... Définition du chemin de recherche.")
        checkpath = MYPATH if sys.argv[1] == '.' else sys.argv[1]

        if not os.path.isdir(checkpath):
            logging.error("++ Le chemin donné n'a pas été trouvé.")
            print(Erreur.MAUVAIS_ARGUMENT.get('msg'))
            print(USAGE)
            exit(Erreur.MAUVAIS_ARGUMENT.get('code'))

        # Définition extension
        logging.info("... Définition de l'extension.")
        extension = sys.argv[2]

    return checkpath, extension


def get_all_exif(jpegfn):
    """Cherche l'orientation d'un fichier dans ses metadata"""
    logging.info("... Cherche orientation dans métadata")

    resultat = []
    f = open(jpegfn, 'rb')
    exifdata = exifread.process_file(f)
    f.close()

    return exifdata


def get_filelist(root, patterns='*', single_level=False, yield_folders=False):
    """List files and directories"""

    logging.info("... Récupération des fichiers/dossiers")

    patterns = patterns.split(';')
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
                    break
        if single_level:
            break


def get_info_from_exif(exifdata, list_tags):
    resultat = []
    for tag in list_tags:
        if tag in exifdata.keys():
            resultat.append(exifdata[tag])

    return resultat

    # def method_1(fichier):
    # newfname = 'pouet'
    # orientation = get_all_exif(fichier, SEARCH_ROTATION)

    # return newfname, orientation
    # try:
    #     # newfname = get_exif_date_pil(fichier)
    #     newfname = 'pouet'
    # except:
    #     newfname = fichier
    # try:
    #     orientation = get_all_exif(fichier, SEARCH_ROTATION)
    # except:
    #     orientation = 1
    # return newfname, orientation


def traitement(flist):
    """Traitement des images."""
    logging.info("... Traitement des images.")

    resultat = []
    for f in flist:
        logging.info("... Traitement de l'image %s" % os.path.basename(f))

        # Nom du fichier courant
        oldfname = os.path.basename(f)

        # get exifdata
        exifdata = get_all_exif(f)

        # get orientation
        orientation = get_info_from_exif(exifdata, TAGS_ORIENTATION)

        # get date
        date = get_info_from_exif(exifdata, TAGS_DATE)

        # get model
        modele = get_info_from_exif(exifdata, TAGS_MODELE)

        # get LxH
        dim_length = get_info_from_exif(exifdata, TAGS_DIM_LENGTH)
        dim_width = get_info_from_exif(exifdata, TAGS_DIM_WIDTH)

        oldfname = os.path.basename(f)
        print("-----------------------------------------------")
        print('file        : %s' % oldfname)
        print("orientation : %s" % orientation)
        print("date        : %s" % date)
        print("modele      : %s" % modele)
        print("dim. length : %s" % dim_length)
        print("dim. width  : %s" % dim_width)
        # print(exifdata)


#######################
# M A I N             #
#######################
main()
