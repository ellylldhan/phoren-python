#!/usr/bin/env python2
#-*-coding: utf-8 -*-
#NOM......phoren
#EXT.......py
#MAJOR....4
#MINOR....6
#DESCR....photo rename v3 python edition
#USAGE....phoren.py
MYFNAME   = 'phoren'
MYVERSION = 'v4.6'

'''
CHANGELOG: !!! PENSER A CHANGER  `MYVERSION`  !!!
2019-04-10 v4.6   python2 dans shebang
2018-02-27 v4.5   Reecriture script nettoyage logs dans main()
2017-12-10 v4.4   Ajout clean video name
2017-08-23 v4.3   Update CLEAN_LIST
2017-07-21 v4.2   Changement ecriture COMMENT LINES dans scripts produits 
2017-07-18 v4.1   Correction script antidote, toutes extensions
2017-07-18 v4.0   Prend DIR en ligne de commande
2017-07-18 v3.13  Gestion des fichiers doublons (mkdir, move) py script uniquement
'''

import os, sys
import fnmatch, time
import exifread
from PIL import Image

DEBUG    = False
SLASH    = os.sep
NL       = os.linesep
MYPATH   = os.path.dirname(os.path.abspath(__file__))
MYFILE   = os.path.abspath(__file__)
DEST_DIR = os.path.join(MYPATH, 'test')
AUTOEXEC = os.path.join(MYPATH, '%s_%s_autoexec.bat' % (MYFNAME, MYVERSION))

if len(sys.argv) > 1 :
	arg = sys.argv[1].upper()
	if arg.upper().startswith("T:\\"):
		MYPATH = arg
	elif arg.upper().startswith('.\\'):
		MYPATH = os.path.join(MYPATH, arg.split(SLASH)[1:])
	else:
		MYPATH = MYPATH


search_fname = ['File Name', 'Opening']
search_date  = ['Media Create Date ', 'Create Date', 'Date/Time Original', \
				'EXIF DateTimeOriginal', 'Image DateTime', \
				'EXIF DateTimeDigitized']
search_ext   = ['File Type Extension', 'Opening']
search_model = ['Camera Model Name', 'Image Model']
search_dim   = ['Image Size']
search_rotation = ['Image Orientation', 'Orientation']

search_h = ['EXIF ExifImageLength','Image ImageLength', 'Exif Image Height']
search_w = ['EXIF ExifImageWidth', 'Image ImageWidth', 'Exif Image Width']

CLEAN_LIST = [\
	('-WA0', '_WA0'), 
	('IMG-', ''),
	('IMG_', ''),
	('SP800UZ                ', 'SP800UZ'),
	('WhatsApp Image ', ''),
	(' at ', ' '),
	('NIKON ', 'NIKON-')]

###################################################

def tee_autoexec():
	""" Creer le fichier .bat qui permet d'executer le script en loggant stderr/out """
	global AUTOEXEC, MYPATH
	if not os.path.isfile(AUTOEXEC) and os.name == "nt":
		with open(AUTOEXEC, 'w') as f:
			f.write('rem cd /d "%s"\n' % MYPATH)
			f.write('{fn}_{vn}.py 1>{fn}_{vn}_stdout.log 2>{fn}_{vn}_stderr.log\n'.format(fn=MYFNAME,vn=MYVERSION))
			f.close()

def get_filelist(root, patterns='*', single_level=False, yield_folders=False):
	'''
	List files and directories
		usage: lstdir = list(get_filelist(str_path, "*.jpg;*.png")
	''' 
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

def get_exif_date_exif(jpegfn):
	"""return EXIF datetime using exifread (formerly EXIF)"""
	dt_value = None
	f = open(jpegfn, 'rb')
	try:
		tags = exifread.process_file(f)
		if DEBUG:
			print('tags cnt: %d' % len(tags))
			print('\n'.join(tags))
		for dt_tag in DT_TAGS:
			try:
				dt_value = '%s' % tags[dt_tag]
				if DEBUG:
					print('%s: %s' % (dt_tag, dt_value))
				break
			except:
				continue
		if dt_value:
			exif_time = exif_info2time(dt_value)
			return exif_time
	finally:
		f.close()
	return None

def get_all_exif(jpegfn, list_tags):
	"""return EXIF datetime using exifread (formerly EXIF)"""
	dt_value = []

	f = open(jpegfn, 'rb')
	try:
		tags = exifread.process_file(f)
		for dt_tag in list_tags:
			try:
				dt_value.append('%s' % tags[dt_tag])
				if DEBUG:
					print('%s: %s' % (dt_tag, dt_value))
				break
			except:
				continue
		dt_value = anti_doublons(dt_value)
		if len(dt_value) == 1:
			return dt_value[0]
		else:
			print('tag est trop long: %s %s %s') % (dt_tag, len(dt_value), dt_value)
	finally:
		f.close()
	return None

def exif_info2time(ts):
	"""changes EXIF date ('2005:10:20 23:22:28') to number of seconds since 1970-01-01"""
	tpl = time.strptime(ts + 'UTC', '%Y:%m:%d %H:%M:%S%Z')
	return time.mktime(tpl)

def show_fdt(fdt):
	"""human readable format of file modification datetime"""
	return time.strftime("%Y-%m-%d_%H%M%S", time.gmtime(fdt))

def get_exif_date_pil(jpegfn):
	"""return EXIF datetime using PIL"""
	im = Image.open(jpegfn)
	ext = jpegfn.split(SLASH)[-1].split('.')[-1]
	if hasattr(im, '_getexif'):
		try :
			exifdata = im._getexif()
			#print exifdata[0x9291]  # orientation
			dt_value = exifdata[0x9003]
			model  = exifdata[0x0110]
			height = exifdata[0xA003]
			width  = exifdata[0xA002]
			orientation = exifdata[0x0112]
			#exif_time = exif_info2time(dt_value)
			#exif_time = show_fdt(exif_time)
			if orientation != 1:
				tmp = height
				height = width
				width  = tmp

			tpl = time.strptime(dt_value + 'UTC', '%Y:%m:%d %H:%M:%S%Z')
			fdt = time.mktime(tpl)
			exif_time = time.strftime("%Y-%m-%d_%H%M%S", time.gmtime(fdt))
			return '%s_%sx%s_%s.%s' % (exif_time, width, height, model, ext)
		except:
			return jpegfn
	return jpegfn

def anti_doublons(liste, sort=False):
	'''
	tri les doublons et elimine les elements nuls
	'''
	if DEBUG : print '--- --> Anti-doublons'
	temp = []
	for element in liste:
		if element not in temp and element:
			temp.append(element)
	if sort:
		temp.sort()
	return temp

def get_time():
	'''
	import time
	data   : [2017, 3, 27, 22, 15, 52, 0, 86, 1]
	return : sNow
	'''
	if DEBUG: print '--- --> Get time'
	temps = [x for x in time.localtime()]
	yyyy  = '%04i' % temps[0]
	mm    = '%02i' % temps[1]
	dd    = '%02i' % temps[2]
	HH    = '%02i' % temps[3]
	MM    = '%02i' % temps[4]
	SS    = '%02i' % temps[5]
	return '%s-%s-%s_%s%s%s' % (yyyy,mm,dd,HH,MM,SS)

def methode_1(file):
	global search_rotation
	try:
		newfname = get_exif_date_pil(file)
	except:
		newfname = file
	try:
		orientation = get_all_exif(file, search_rotation)
	except:
		orientation = 1
	return newfname, orientation

def methode_2(file):
	global search_date, search_h, search_model
	global search_rotation, search_w, MYPATH
	# methode 2
	ext = file.split(SLASH)[-1].split('.')[-1]
	try:
		time_raw = get_all_exif(file, search_date)
		tpl = time.strptime(time_raw + 'UTC', '%Y:%m:%d %H:%M:%S%Z')
		fdt = time.mktime(tpl)
		exif_time = time.strftime("%Y-%m-%d_%H%M%S", time.gmtime(fdt))
		height = get_all_exif(file, search_h)
		width  = get_all_exif(file, search_w)
		model  = get_all_exif(file, search_model)
	except:
		return file
	try:
		orientation = get_all_exif(file, search_rotation)
		if 'Rotated' in orientation:
			tmp = height
			height = width
			width  = tmp
	except:
		pass
	fname = '%s_%sx%s_%s.%s' % (exif_time, width, height, model, ext)
	newfname = os.path.join(MYPATH, fname)
	return newfname

def nettoyage_fname(file):
	""" 
	clean fname: "20170712" > "2017-07-12", etc. 
	@arg   file full path & name
	@ret   file full path & (new) name
	""" 
	global CLEAN_LIST, SLASH
	# 258 file Z:\GoogleDrive\Google Photos\JAN\2016\20160510_164422.jpg
	newfname = file.split(SLASH)[-1].replace('VID-', '').replace('VID_', '')
	# 260 newfname 20160729_125521873.jpg
	reste    = SLASH.join(file.split(SLASH)[:-1])
	for y in range(2000, 2020):
			for m in range(1, 13):
				for d in range(1, 32):
					if newfname.startswith('%i%02i%02i' % (y, m, d)):
						newfname = newfname.replace('%i%02i%02i' % (y, m, d), '%i-%02i-%02i' % (y, m, d))
						break
	
	for x in CLEAN_LIST:
		newfname = newfname.replace(x[0], x[1])
	# 271 return (fullpath)2016-07-26_WA0006.jpg
	return os.path.join(reste, newfname)

def build_phoren_bat(results, temps):
	global MYVERSION
	msg = ['REM phoren_%s_SCRIPT_%s.bat\n' % (MYVERSION,temps)]
	anti= ['REM phoren_%s_ANTIDOTE_%s.bat\n' % (MYVERSION,temps)]

	tmp, pmt = [], []
	for r in results:
		if not os.path.isfile(r[1]):
			tmp.append('MOVE /-Y "%s" "%s"' % (r[0], r[1]))
			pmt.append('MOVE /-Y "%s" "%s"' % (r[1], r[0]))

	if tmp and pmt:
		tmp.sort()
		pmt.sort()
		msg  += tmp
		anti += pmt
		return msg, anti
	else:
		return None, None

def build_phoren_sh(results, temps):
	msg = [\
		'#!/bin/bash',
		'# phoren_%s_SCRIPT_%s.sh\n' % (MYVERSION,temps)]
	anti = [\
		'#!/bin/bash',
		'# phoren_%s_ANTIDOTE_%s.sh\n' % (MYVERSION,temps)]

	tmp, pmt = [], []
	for r in results:
		if not os.path.isfile(r[1]):
			tmp.append('mv -nv "%s" "%s"' % (r[0], r[1]))
			pmt.append('mv -nv "%s" "%s"' % (r[1], r[0]))

	if tmp and pmt:
		tmp.sort()
		pmt.sort()
		msg  += tmp
		anti += pmt
		return msg, anti
	else:
		return None, None

def build_phoren_py1(results, temps):
	global SLASH
	msg = [\
		'#! python2',
		'# -*- coding: UTF-8 -*-',
		'# phoren_%s_SCRIPT_%s.py\n' % (MYVERSION,temps),
		'import os, shutil\n',
		'SLASH  = os.sep',
		'MYPATH = os.path.dirname(os.path.abspath(__file__))\n']
	anti = [\
		'#! python2',
		'# -*- coding: UTF-8 -*-',
		'# phoren_%s_ANTIDOTE_%s.py\n' % (MYVERSION,temps),
		'import os, shutil\n',
		'SLASH  = os.sep',
		'MYPATH = os.path.dirname(os.path.abspath(__file__))\n']

	tmp, pmt = [], []
	for r in results:
		#path0 = os.path.join(MYPATH, r[0])
		#path1 = os.path.join(MYPATH, r[1])
		path0 = r[0].replace('\\', '\\\\')
		path1 = r[1].replace('\\', '\\\\')
		if not os.path.isfile(path1):

			msg_tmp  = 'if not os.path.isfile("%s"):\n'     % path1
			msg_tmp += '\tos.rename("%s", "%s")\n'      % (r[0], r[1].split(SLASH)[-1])
			msg_tmp += '\tprint("Moved %s --> %s")\n\n' % (r[0], r[1].split(SLASH)[-1])
			msg_tmp += 'else:\n'
			msg_tmp += '\ttry:\n'
			msg_tmp += '\t\tos.makedirs(os.path.join(MYPATH, "xxDOUBLONSxx")\n'
			msg_tmp += '\texcept:\n'
			msg_tmp += '\t\tpass\n'
			msg_tmp += '\tshutil.move("%s", "%s")\n' % (r[0], os.path.join(MYPATH, "xxDOUBLONSxx", os.path.basename(r[1]))) 
			msg_tmp += '\tprint("DOUBLONS %s --> .\\xxDOUBLONSxx\\%s")\n' % (r[0], r[1].split(SLASH)[-1])
			tmp.append(msg_tmp)

			msg_pmt  = 'if not os.path.isfile("%s"):\n'     % path0
			msg_pmt += '\tos.rename("%s", "%s")\n'        % (r[1], r[0].split(SLASH)[-1])
			msg_pmt += '\tprint("Moved %s" --> "%s")\n\n' % (r[1], r[0].split(SLASH)[-1])

			pmt.append(msg_pmt)
		else:
			print '# FILE EXISTS : %s' % path1
	
	if tmp and pmt:
		tmp.sort()
		pmt.sort()
		msg  += tmp
		anti += pmt
		return msg, anti
	else:
		return None, None

def build_phoren_py2(results, temps):
	global SLASH
	
	DSLASH = SLASH+SLASH
	
	msg = [\
		'#! python2',
		'# -*- coding: UTF-8 -*-',
		'# phoren_%s_SCRIPT_%s.py\n' % (MYVERSION,temps),
		'import os, shutil\n',
		'SLASH  = os.sep',
		'MYPATH = os.path.dirname(os.path.abspath(__file__))\n']
	anti = [\
		'#! python2',
		'# -*- coding: UTF-8 -*-',
		'# phoren_%s_ANTIDOTE_%s.py\n' % (MYVERSION,temps),
		'import os, shutil\n',
		'SLASH  = os.sep',
		'MYPATH = os.path.dirname(os.path.abspath(__file__))\n']

	tmp, pmt = [], []
	for r in results:
		#path0 = os.path.join(MYPATH, r[0])
		#path1 = os.path.join(MYPATH, r[1])
		path0 = r[0].replace('\\', '\\\\')
		path1 = r[1].replace('\\', '\\\\')

		msg_tmp  = 'if not os.path.isfile("%s"):\n'     % path1
		msg_tmp += '\tos.rename("%s", "%s")\n'      % (r[0], r[1].split(SLASH)[-1])
		msg_tmp += '\tprint("Moved %s --> %s")\n\n' % (r[0], r[1].split(SLASH)[-1])
		msg_tmp += 'else:\n'
		msg_tmp += '\ttry:\n'
		msg_tmp += '\t\tos.makedirs(os.path.join(MYPATH, "xxDOUBLONSxx"))\n'
		msg_tmp += '\texcept:\n'
		msg_tmp += '\t\tpass\n'
		msg_tmp += '\tshutil.move("%s", "%s")\n' % (r[0], DSLASH.join([".", "xxDOUBLONSxx", os.path.basename(r[1])])) 
		msg_tmp += '\tprint("DOUBLONS %s --> %s")\n' % (r[0], DSLASH.join([".", "xxDOUBLONS", os.path.basename(r[1])]))
		tmp.append(msg_tmp)

		msg_pmt  = 'if not os.path.isfile("%s"):\n'     % path0
		msg_pmt += '\tos.rename("%s", "%s")\n'        % (r[1], r[0].split(SLASH)[-1])
		msg_pmt += '\tprint("Moved %s" --> "%s")\n\n' % (r[1], r[0].split(SLASH)[-1])

		pmt.append(msg_pmt)
	
	if tmp and pmt:
		tmp.sort()
		pmt.sort()
		msg  += tmp
		anti += pmt
		return msg, anti
	else:
		return None, None

def build_phoren_py(results, temps):
	global SLASH
	
	DSLASH = SLASH+SLASH
	
	msg = [\
		'#! python2',
		'# -*- coding: UTF-8 -*-',
		'# phoren_%s_SCRIPT_%s.py\n' % (MYVERSION,temps),
		'import os, shutil\n',
		'SLASH  = os.sep',
		'MYPATH = os.path.dirname(os.path.abspath(__file__))\n']
	anti = [\
		'#! python2',
		'# -*- coding: UTF-8 -*-',
		'# phoren_%s_ANTIDOTE_%s.py\n' % (MYVERSION,temps),
		'import os, shutil\n',
		'SLASH  = os.sep',
		'MYPATH = os.path.dirname(os.path.abspath(__file__))\n']

	tmp, pmt = [], []
	for r in results:
		path0 = os.path.join(MYPATH, r[0]).replace('\\', '\\\\')
		path1 = os.path.join(MYPATH, r[1]).replace('\\', '\\\\')
		#path0 = r[0].replace('\\', '\\\\')
		#path1 = r[1].replace('\\', '\\\\')

		msg_tmp  = 'if not os.path.isfile("%s"):\n' % path1
		msg_tmp += '\tshutil.move("%s", "%s")\n'    % (path0, path1)
		msg_tmp += '\tprint("Moved %s --> %s")\n\n' % (r[0], r[1])
		msg_tmp += 'else:\n'
		msg_tmp += '\ttry:\n'
		msg_tmp += '\t\tos.makedirs(os.path.join(MYPATH, "xxDOUBLONSxx"))\n'
		msg_tmp += '\texcept:\n'
		msg_tmp += '\t\tpass\n'
		msg_tmp += '\tshutil.move("%s", "%s")\n'     % (path0, DSLASH.join([".", "xxDOUBLONSxx", os.path.basename(r[1])])) 
		msg_tmp += '\tprint("DOUBLONS %s --> %s")\n' % (r[0], DSLASH.join([".", "xxDOUBLONS", os.path.basename(r[1])]))
		tmp.append(msg_tmp)

		msg_pmt  = 'if not os.path.isfile("%s"):\n'     % path0
		msg_pmt += '\ttry:\n'
		msg_pmt += '\t\tos.rename("%s", "%s")\n'        % (r[1], r[0].split(SLASH)[-1])
		msg_pmt += '\t\tprint("Moved %s" --> "%s")\n' % (r[1], r[0].split(SLASH)[-1])
		msg_pmt += '\texcept:\n'
		msg_pmt += '\t\tpass\n\n'
		pmt.append(msg_pmt)
	
	if tmp and pmt:
		tmp.sort()
		pmt.sort()
		msg  += tmp
		anti += pmt
		return msg, anti
	else:
		return None, None


def write_scripts(type, extension, msg1, msg2=[], msg3=[]):
	global NOW, MYFNAME, MYVERSION
	if extension in ['py', 'py.log']:
		intro_comment = end_comment = '"""'
	if extension in ['bat', 'bat.log']:
		intro_comment = 'GOTO comment'
		end_comment = ':comment'
	if extension in ['sh', 'sh.log']:
		intro_comment = ": '"
		end_comment = "'"
	
	with open('%s_%s_%s_%s.%s' % (MYFNAME, MYVERSION, type, NOW, extension) , 'w') as f:
		f.write('\n'.join(msg1) )
		f.write('\n\n%s\nAUTRES SCRIPTS' % intro_comment)
		f.write('\n--------------\n' )
		f.write('\n'.join(msg2) )
		f.write('\n--------------\n' )
		f.write('\n'.join(msg3))
		f.write('\n--------------\n\n' )
		f.write(end_comment + '\n')
		f.close()

def main():
	global MYPATH, SLASH, NOW

	# 0. Generate autoexec.bat
	tee_autoexec()
	
	clean_file = 'phoren_range_bazar.bat'if os.name != 'posix' else 'phorange_bazar.sh'	
	
	if os.name == 'posix':
		msg = ['#! /usr/bin/sh']
		msg+= ['echo "Rangement des logs et des scripts ..."']
		msg+= ['mkdir logs 2>/dev/null']
		msg+= ['mv -v *.log logs 2>/dev/null']
		msg+= ['mv -v *script*.py logs 2>/dev/null']
		msg+= ['mv -v *script*.bat logs 2>/dev/null']
		msg+= ['mv -v *SCRIPT*.py logs 2>/dev/null']
		msg+= ['mv -v *SCRIPT*.bat logs 2>/dev/null']
		msg+= ['rm -v *_autoexec.* 2>/dev/null']
	else:
		msg = ['rem cd /d "Z:\\GoogleDrive\\Google Photos"']
		msg+= ['echo "Rangement des logs et des scripts ..."']
		msg+= ['md logs 2>Nul']
		msg+= ['move *.log logs 2>Nul']
		msg+= ['move *script*.py logs 2>Nul']
		msg+= ['move *script*.bat logs 2>Nul']
		msg+= ['move *SCRIPT*.py logs 2>Nul']
		msg+= ['move *SCRIPT*.bat logs 2>Nul']
		msg+= ['del *_autoexec.* 2>Nul']
		
	if not os.path.isfile(clean_file):
		print '[ 0579 ] ... Ecriture du script de nettoyage %s' % clean_file
		with open(clean_file, 'w') as flux:
			flux.write('\n'.join(msg))
			flux.close()

	# 1. Get filelist (jpg, JPG)
	jlist = [x for x in get_filelist(MYPATH, '*.jpg;*.JPG;*.jpeg;*.mp4', True, False)]
	#jlist = [x for x in get_filelist(MYPATH, '*.mp4', True, False)]

	# 2. For each file...
	results = []
	for file in jlist:
		oldfname = file.split(SLASH)[-1]
		
		#print '387', file
		newfname, orientation = methode_1(file)
		
		if oldfname == os.path.basename(newfname):
			newfname = methode_2(file)

			if oldfname == os.path.basename(newfname):
				newfname = file

		#print('%s --> %s') % (oldfname, newfname.split(SLASH)[-1])
		newfname = nettoyage_fname(newfname)
		#r = raw_input('pause %s' % newfname)
		
		if oldfname == os.path.basename(newfname):
			#print('!!! same names %s --> %s') % (oldfname, newfname)
			print 'Processing %s : NO ACTION REQUIRED' % oldfname
			continue
		else:
			print('%s --> %s') % (oldfname, os.path.basename(newfname))
			results.append((oldfname, nettoyage_fname(newfname)))

	if results == []:
		sys.exit("Les fichiers n'ont pas besoin d'etre renommes")
	else:
		# temporary fix
		tmp = []
		for r in results:
			tmp.append((r[0], r[1].split(SLASH)[-1]))
		results = tmp
		
	msg_bat, anti_bat = build_phoren_bat(results, NOW)
	msg_sh,  anti_sh  = build_phoren_sh(results, NOW)
	msg_py,  anti_py  = build_phoren_py(results, NOW)

	# write phoren py
	if msg_py and anti_py:
		write_scripts('script', 'py', msg_py, msg_bat, msg_sh)
		write_scripts('antidote', 'py.log', anti_py, anti_bat, anti_sh)
		write_scripts('SCRIPT', 'bat.log', msg_bat,msg_sh)
		write_scripts('ANTIDOTE', 'bat.log', anti_bat, anti_sh)

	for r in results:
		print('MOVE "%s" "%s"' % (r[0], r[1]))
	

	
###################################################



NOW = get_time()

main()




# TODO
# compare new vs old pour economiser du temps
# log antidote
# check isFile pour eviter overwriting


"""
POUR PLUS TARD (tabs not accurate)
	Image Make (ASCII)        : samsung
	Image Orientation (Short) : Rotated 90 CW
	Image XResolution (Ratio) : 72
	Image YResolution (Ratio) : 72
	EXIF ImageUniqueID (ASCII): F16QLHF01VB

Make                            : samsung
Orientation                     : Horizontal (normal)
X Resolution                    : 72
Y Resolution                    : 72
Image Unique ID                 : F16QLHF01VB

Exif Image Width                : 5312
Exif Image Height               : 2988

*************************************************

File Name                       : 20161130_112837.jpg
File Modification Date/Time     : 2016:11:30 10:28:36+00:00
File Access Date/Time           : 2017:07:07 23:34:01+01:00
File Creation Date/Time         : 2017:07:07 23:34:01+01:00
Create Date                     : 2016:11:30 11:28:37.435
Date/Time Original              : 2016:11:30 11:28:37.435
Modify Date                     : 2016:11:30 11:28:37.435

File Type Extension             : jpg

Make                            : samsung
Camera Model Name               : SM-G900F

Image Width                     : 5312
Image Height                    : 2988
Image Size                      : 5312x2988
Exif Image Width                : 5312
Exif Image Height               : 2988

*************************************************

for file in *.mp4; do exiftool "$file" > "$file.nfo" ;
echo "md5                             : $(echo $file | md5sum | sed 's/\ \ -//')" >> "$file".nfo; done

"""