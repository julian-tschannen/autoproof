# This script does:
# 1. Verify all examples

import os
import platform
import sys
import time
import shutil
import subprocess
import argparse
import difflib

# ----------------------------------------------------------------------------
# set up environment
# ----------------------------------------------------------------------------

os.environ['ISE_PLATFORM'] = 'win64'
os.environ['ISE_EIFFEL'] = os.path.join("C:\\","Eiffel", "eve_96431")
os.environ['ISE_LIBRARY'] = os.getenv("ISE_EIFFEL")
os.environ['ISE_PRECOMP'] = os.path.join(os.getenv("ISE_EIFFEL"), 'precomp', 'spec', 'win64')
os.environ['PATH'] = os.path.join(os.getenv("ISE_EIFFEL"), 'studio', 'tools', 'boogie') + os.pathsep + os.path.join(os.getenv("ISE_EIFFEL"), 'studio', 'spec', os.getenv("ISE_PLATFORM"), 'bin') + os.pathsep + os.environ['PATH']

# ----------------------------------------------------------------------------
# paths
# ----------------------------------------------------------------------------

base_directory = os.path.abspath("../code")
dropbox_target = os.path.abspath("../publish/e4pubs")
eifgens_directory = 'C:\\Temp\\EIFGENs'
tempfile_name = 'temp.out'

# ----------------------------------------------------------------------------
# helper functions: log and printing
# ----------------------------------------------------------------------------

# open logfile
tempfile = open(tempfile_name, 'w')

# clear log file
open("log.txt", 'w').close()
# open log file
_log_file = open("log.txt", 'w')

_has_colorama = False
try:
	from colorama import init, Fore, Back, Style
	init()
	_has_colorama = True
except ImportError:
	pass

def _to_logfile(text):
	_log_file.write(time.strftime('%H:%M:%S', time.gmtime(time.clock())))
	_log_file.write("  ---  ")
	_log_file.write(text)
	_log_file.write("\n")
	_log_file.flush()

def _as_info(text, pre=''):
	print pre + text
	_to_logfile(pre + text)

def _as_warning(text, pre=''):
	if _has_colorama:
		print pre + Back.YELLOW + Fore.YELLOW + Style.BRIGHT + text + Style.RESET_ALL
	else:
		print pre + text
	_to_logfile(pre + text)

def _as_error(text, pre=''):
	if _has_colorama:
		print pre + Back.RED + Fore.RED + Style.BRIGHT + text + Style.RESET_ALL
	else:
		print pre + text
	_to_logfile(pre + text)

def _as_success(text, pre=''):
	if _has_colorama:
		print pre + Back.GREEN + Fore.GREEN + Style.BRIGHT + text + Style.RESET_ALL
	else:
		print pre + text
	_to_logfile(pre + text)

# ----------------------------------------------------------------------------
# actions
# ----------------------------------------------------------------------------

def clean():
	return True

def verify_all():
	for name in os.listdir(dropbox_target):
		verify_one(name, os.path.join(dropbox_target, name))
	return True

def verify_one(name, path):
	compile(name, path)
	run_autoproof(name, path)
	return True

def compile(name, dir):
	project_path = os.path.join(eifgens_directory, name)
	if not os.path.exists(project_path):
		os.makedirs(project_path)
	args = ['-config', os.path.join(dir, "app.ecf"), 
		'-target', 'app', 
		'-batch',
		'-project_path', project_path
	]
	print name, "compiling", 
	subprocess.call(['ec.exe'] + args, stdout=tempfile, stderr=tempfile)
	#subprocess.call([os.path.join(os.getenv("ISE_LIBRARY"), 'Eiffel', 'Ace', 'EIFGENs', 'bench', 'F_code', 'ec.exe')] + args, stdout=tempfile, stderr=tempfile)
	return True

def run_autoproof(name, dir):
	project_path = os.path.join(eifgens_directory, name)
	if not os.path.exists(project_path):
		os.makedirs(project_path)
	args = ['-config', os.path.join(dir, "app.ecf"), 
		'-target', 'app', 
		'-batch',
		'-project_path', project_path,
		'-autoproof',
	]
	if 'postpredicate' in open(os.path.join(dir, "autoproof.py")).read():
		args += ['-postpredicate']
	if 'overflow' in open(os.path.join(dir, "autoproof.py")).read():
		args += ['-overflow']
	print "verifying", 
	start = time.clock()
	subprocess.call(['ec.exe'] + args, stdout=tempfile, stderr=tempfile)
	#subprocess.call([os.path.join(os.getenv("ISE_LIBRARY"), 'Eiffel', 'Ace', 'EIFGENs', 'bench', 'F_code', 'ec.exe')] + args, stdout=tempfile, stderr=tempfile)
	end = time.clock()
	print str(end - start), 
	
	# measure Boogie file sizes
	f = open("C:\\Temp\\autoproof.bpl")
	bg_theory = 0
	custom_content = -1
	for line in f:
		if line.startswith("// Custom content"):
			custom_content = 0;
		if not (line == "" or line.startswith("//")):
			if custom_content >= 0:
				custom_content = custom_content + 1
			else:
				bg_theory = bg_theory + 1

	print str(bg_theory), str(custom_content)
	
	return True


# ----------------------------------------------------------------------------
# parse arguments and execute actions
# ----------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('--clean', '-c', action='store_true')
parser.add_argument('projects', nargs=argparse.REMAINDER)

arguments = parser.parse_args()

if arguments.clean:
	clean()

if len(arguments.projects) == 0:
	verify_all()
else:
	for t in arguments.projects:
		verify_one(t)

tempfile.close()
