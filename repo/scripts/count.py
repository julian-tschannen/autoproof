# This script does:
# 1. count lines of code for several categories

import os
import time
import shutil
import glob
import markdown
import zipfile

# ----------------------------------------------------------------------------
# paths
# ----------------------------------------------------------------------------

base_directory = os.path.abspath("../code")

# ----------------------------------------------------------------------------
# helper functions: log and printing
# ----------------------------------------------------------------------------

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
# core functions
# ----------------------------------------------------------------------------

def count_all():
	for name in os.listdir(base_directory):
		count_one(name, os.path.join(base_directory, name))

def count_one(name, fullpath):
	if not os.path.isdir(fullpath):
		return _to_logfile(fullpath + " is no directory. " + name + " ignored")
	if name.startswith("_") or name.startswith("."):
		return _to_logfile(name + " ignored: starts with underscore or dot")
	if not os.path.isfile(os.path.join(fullpath, "readme.txt")):
		return _to_logfile(name + " ignored: does not have a readme.txt file")
	_to_logfile(name + " counting")
	loc_eiffel = 0
	loc_spec = 0
	loc_pre = 0
	loc_post = 0
	loc_frame = 0
	loc_var = 0
	loc_assert = 0
	for filename in os.listdir(fullpath):
		if filename.endswith(".e"):
			le, ls, lpre, lpost, lframe, lvar, la = count_file(os.path.join(fullpath, filename))
			loc_eiffel += le
			loc_spec += ls
			loc_pre += lpre
			loc_post += lpost
			loc_frame += lframe
			loc_var += lvar
			loc_assert += la
	print name, loc_eiffel, loc_spec, loc_pre, loc_post, loc_frame, loc_var, loc_assert

def count_file(filename):
	_to_logfile(filename + " counting")
	f = open(filename, "r")
	loc_eiffel = 0
	loc_spec = 0
	loc_pre = 0
	loc_post = 0
	loc_frame = 0
	loc_l_inv = 0
	loc_var = 0
	loc_c_inv = 0
	loc_assert = 0
	in_spec = False
	in_pre = False
	in_post = False
	in_assert = False
	in_var = False
	for line in iter(f):
		ll = line.lower().strip()
		if ll == "" or ll.startswith("--"):
			pass
		elif ll.startswith("description"):
			if in_spec:
				loc_spec -= 1
		else:
			if in_spec:
				loc_spec += 1
				in_spec = not (ll == "end" or ll == "until" or ll == "do" or ll.startswith("deferred") or ll == "attribute" or ll.startswith("once") or ll == "local" or ll.startswith("class") or ll.startswith("frozen"))
				if in_pre:
					if ll.startswith("modify"):
						loc_frame += 1
					elif ll.startswith("decreases"):
						loc_var += 1
					else:
						loc_pre += 1
					in_pre = in_spec
				elif in_post:
					loc_post += 1
					in_post = in_spec
				elif in_var:
					loc_var += 1
					in_var = in_spec
				elif in_assert:
					loc_assert += 1
					in_assert = in_spec
				else:
					in_pre = ll.startswith("require")
					in_post = ll.startswith("ensure")
			elif ll.startswith("check"):
				loc_spec += 1
				loc_assert += 1
				in_spec = not ll.endswith("end")
				in_assert = in_spec
			else:
				loc_eiffel += 1
				in_spec = (ll.startswith("require") or ll.startswith("ensure") or ll == "invariant" or ll == "variant" or ll == "note")
				in_pre = ll.startswith("require")
				in_post = ll.startswith("ensure")
				in_var = ll.startswith("variant")

	f.close()
	return (loc_eiffel, loc_spec, loc_pre, loc_post, loc_frame, loc_var, loc_assert)

print "name", "eiffel", "spec", "pre", "post", "frame", "var", "assert"
count_all()
