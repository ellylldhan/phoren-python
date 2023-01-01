#! /usr/bin/sh
# Déplace les fichiers générés par phoren
echo "Rangement des logs et des scripts ..."
mkdir logs 2>/dev/null
mv -v *.log logs 2>/dev/null
mv -v *script*.py logs 2>/dev/null
mv -v *script*.bat logs 2>/dev/null
mv -v *SCRIPT*.py logs 2>/dev/null
mv -v *SCRIPT*.bat logs 2>/dev/null