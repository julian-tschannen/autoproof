# This script does:
# 1. Generate e4pubs folders
#   for all folders in "code", if they (1) don't start with an underscore and (2) contain at least one .e file, copy all relevant files to publish/e4pubs
# 2. Generate website for examples
#   for all folders in "code", if they (1) don't start with an underscore, collect data and generate website

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
dropbox_target = os.path.abspath("../publish/e4pubs")
website_target = os.path.abspath("../publish/website")
zip_target = os.path.abspath("../publish/zip")

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
# helper functions: file system
# ----------------------------------------------------------------------------

def copy_path(source, target):
	_to_logfile("Copying path")
	_to_logfile("Source: " + source)
	_to_logfile("Target: " + target)
	result = False
	if not os.path.exists(source):
		_as_error("Cannot copy '" + source + "' to '" + target + "'. Source does not exist")
	else:
		if os.path.isfile(source):
			shutil.copy(source, target)
			result = True
		elif os.path.exists(target):
			_as_error("Cannot copy directory '" + source + "' to '" + target + "'. Target already exists")
		else:
			shutil.copytree(source, target)
			result = True
	return result

def delete_path(path):
	_to_logfile("Deleting path")
	_to_logfile("Path: " + path)
	result = False
	if os.path.isdir(path):
		shutil.rmtree(path, ignore_errors=False, onerror=handle_remove_readonly)
	elif os.path.isfile(path):
		os.remove(path)
	if os.path.exists(path):
		_as_error("Unable to delete '" + path + "'")
	else:
		result = True
	return result

def handle_remove_readonly(func, path, exc):
	import stat
	excvalue = exc[1]
	if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
		os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
		func(path)
	else:
		raise

def file_get_contents(filename):
	with open(filename) as f:
		return f.read()

# ----------------------------------------------------------------------------
# core functions
# ----------------------------------------------------------------------------

def publish_all():
	for name in os.listdir(base_directory):
		publish_one(name, os.path.join(base_directory, name))

def publish_one(name, fullpath):
	if not os.path.isdir(fullpath):
		return _to_logfile(fullpath + " is no directory. " + name + " ignored")
	if name.startswith("_") or name.startswith("."):
		return _to_logfile(name + " ignored: starts with underscore or dot")
	if not os.path.isfile(os.path.join(fullpath, "readme.txt")):
		return _to_logfile(name + " ignored: does not have a readme.txt file")
	_to_logfile(name + " publishing")
	target = os.path.join (dropbox_target , name)
	delete_path(target)
	copy_path(fullpath, target)
	# copy autoproof.py on demand
	if not os.path.isfile(os.path.join(target, "autoproof.py")):
		copy_path(os.path.join(base_directory, "_default", "autoproof.py"), os.path.join(target, "autoproof.py"))
	# copy app.ecf on demand
	uses_default_ecf = False
	if not os.path.isfile(os.path.join(target, "app.ecf")):
		uses_default_ecf = True
		copy_path(os.path.join(base_directory, "_default", "app.ecf"), os.path.join(target, "app.ecf"))
	
	# create zip file
	if not os.path.exists(zip_target):
		os.makedirs(zip_target)
	with zipfile.ZipFile(os.path.join(zip_target, name + '.zip'), 'w') as myzip:
		if uses_default_ecf:
			myzip.write(os.path.join(base_directory, "_default", "app.ecf"), "app.ecf")
		for filename in os.listdir(fullpath):
			myzip.write(os.path.join(fullpath, filename), filename)

def build_website():
	if os.path.isdir(website_target):
		delete_path(website_target)
	if not os.path.isdir(website_target):
		os.makedirs(website_target)
	copy_path(zip_target, os.path.join(website_target, 'zip'))
	delete_path(zip_target)
	data = {}
	categories = set([])
	for name in os.listdir(base_directory):
		if not name.startswith("_") and not name.startswith(".") and os.path.isfile(os.path.join(base_directory, name, "readme.txt")):
			fullpath = os.path.join(base_directory, name)
			data[name] = extract_data_one(name, fullpath)
			if "category" in data[name]:
				categories |= set(data[name]["category"])

	sorted_data = sorted(data.itervalues(), key=lambda x: x["title"].lower())
	for index, element in enumerate(sorted_data):
		if index == 0:
			previous = None
		else:
			previous = sorted_data[index - 1]
		if index == len(sorted_data) - 1:
			next = None
		else:
			next = sorted_data[index + 1]
		create_individual_page(element, previous, next)
	create_overview_page(sorted_data, categories)

def extract_data_one(name, fullpath):
	_to_logfile(name + " extract data")
	fname = os.path.join(fullpath, "readme.txt")
	if os.path.isfile(fname):
		result = parse_description(fname)
		if not "title" in result:
			result["title"] = name
	else:
		result = {}
		result["title"] = name
	result["key"] = name
	return result

def parse_description(fname):
	result = {}
	key = None
	text = None
	f = open(fname, "r")
	for line in iter(f):
		ll = line.lower()
		if ll.startswith("title:"):
			result["title"] = line[6:].strip()
		elif ll.startswith("source:"):
			result["source"] = line[7:].strip()
		elif ll.startswith("category:"):
			result["category"] = line[9:].strip().split(",")
		elif ll.startswith("reference:"):
			result["reference"] = line[10:].strip()
		elif ll.startswith("abstract:"):
			if key:
				result[key] = text.strip()
			key = "short"
			text = line[9:].strip()
		elif ll.startswith("description:"):
			if key:
				result[key] = text.strip()
			key = "long"
			text = line[13:].strip()
		elif ll.startswith("solution:"):
			if key:
				result[key] = text.strip()
			key = "solution"
			text = line[9:].strip()
		else:
			if key:
				text = text + line
	if key:
		result[key] = text.strip()
	f.close()
	return result

def create_individual_page(data, previous, next):
	f = open(os.path.join(website_target, data["key"] + ".html"), "w+")

	write_header(f, 'AutoProof Verified Code Repository - ' + data['title'])

	# naviagation
	f.write('<div style="text-align: center;background-color:#ddd;margin-top:10px;padding:5px">')
	if previous:
		f.write('<span style="float:left;text-align:left;width:250px"><a href="' + previous['key'] + '.html">&lt; ' + previous['title'] + '</a></span>')
	else:
		f.write('<span style="float:left;width:250px">&nbsp;</span>')
	f.write(' <a href="index.html">AutoProof Code Repository</a> ')
	if next:
		f.write('<span style="float:right;text-align:right;width:250px"><a href="' + next['key'] + '.html">' + next['title'] + ' &gt;</a></span>')
	else:
		f.write('<span style="float:right;width:250px">&nbsp;</span>')
	f.write("</div>")

	# data
	if "title" in data:
		f.write("<h1>" + data["title"] + "</h1>\n")
	if "category" in data and len(data["category"]) > 0:
		t = "**Category:**"
		for c in data["category"]:
			t += " " + c + ",";
		f.write(format(t[:-1]))
	if "source" in data and data["source"] != '':
		f.write(format("**Source:** " + data["source"]) + "\n")
	if "reference" in data and data["reference"] != '':
		f.write(format("**Reference:** " + data["reference"]) + "</p>\n")
	if "long" in data:
		f.write("<h2>Description</h2>\n" + format(data["long"]) + "\n")
	if "solution" in data:
		f.write("<h2>Solution</h2>\n" + format(data["solution"]) + "\n")
	if "key" in data:
		f.write('<div style="float:right"><a href="./zip/' + data['key'] + '.zip">download source</a></div>')
		f.write("<h2>Code</h2>\n")
		f.write("<iframe width=\"800\" height=\"800\" src=\"http://cloudstudio.ethz.ch/e4pubs/#" + data["key"] + "\" frameborder=\"0\"></iframe>")
	
	write_footer(f)
	f.close()

def format(text):
	return markdown.markdown(text)

def create_overview_page(data, categories):
	f = open(os.path.join(website_target, "index.html"), "w+")
	write_header(f, 'AutoProof Verified Code Repository - Overview')
	
	f.write('<h1>AutoProof Verified Code Repository</h1>\n')
	f.write(format(file_get_contents(os.path.join(base_directory, '_default', 'intro.txt'))))

	f.write('<table class="repo">\n')
	f.write('<thead><tr>\n')
	f.write('<th></th>\n')
	f.write('<th style="width:192px">Name</th>\n')
	f.write('<th>Description</th>\n')
	f.write('<th>Source</th>\n')
	f.write('<th style="width:112px">Category<br/><span style="font-size:0.8em">(<a class="cat" href="#">show all</a>)</span></th>\n')
	f.write('</tr></thead><tbody>\n')
	counter = 0
	for element in data:
		counter += 1
		f.write('<tr class="row">')
		f.write('<td style="text-align: center">' + str(counter) + '</td>')
		f.write("<td>")
		f.write(format('**[' + element['title'] + '](' + element['key'] + '.html)**'))
		f.write("</td>")
		f.write("<td>")
		if 'short' in element and element['short'] != '':
			f.write(format(element['short']))
		f.write("</td>")
		f.write("<td>")
		if 'source' in element and element['source'] != '':
			f.write(format(element['source']))
		f.write("</td>")
		f.write('<td class="filter">')
		if 'category' in element and len(element['category']) > 0:
			first = True
			for c in (sorted(element['category'])):
				if not first:
					f.write(' / ')
				first = False
				f.write('<a class="cat" href="#">' + c.strip() + '</a>')
		f.write("</td>")
		f.write('</tr>\n')
	f.write('</tbody></table>\n')
	f.write(
"""
<script type="text/javascript" src="http://code.jquery.com/jquery-1.8.3.js"></script>
<script type="text/javascript">
	$("a.cat").click(function(e) {
		e.preventDefault();
		var searchTerm = $(this).text();
		if (searchTerm == "show all") {
			$("table.repo .row").show();
		} else {
			$("table.repo .row").hide().filter(function() {
					return $(this).find(".filter").text().indexOf(searchTerm) >= 0;
				}).show();
		}
		$('table.repo tbody tr:visible').removeClass('even').filter(':odd').addClass('even');
	});
	$('table.repo tbody tr:visible').filter(':odd').addClass('even');
</script>
<style type="text/css">
table.repo p { margin: 3px; }
table.repo th { padding: 0.25em; color: #99001d; background-color: #cca5ac; }
table.repo td { padding: 0.25em; font-size: 0.9em; }
table.repo .even { background-color: #dddddd; }
</style>
""")
	write_footer(f)
	f.close()

def write_header(f, title):
	f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
			'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n'
			'"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
			'<html xmlns="http://www.w3.org/1999/xhtml">\n'
			'<head>\n'
			'  <title>' + title + '</title>\n'
			'  <link rel="stylesheet" type="text/css" href="/styles/se_red.css" />\n'
			'  <meta http-equiv="content-type" content="text/html; charset=UTF-8" />\n'
			'</head>\n'
			'\n'
			'<body>\n'
			'<div id="header_section">\n'
			'  <!--#include virtual="/nav_bar.html" -->\n'
			'</div>\n'
			'\n'
			'<div id="main_content">\n')

def write_footer(f):
	f.write('</div>\n'
			'<!--#include virtual="/footer.html" -->\n'
			'</body>\n'
			'</html>\n')

publish_all()
build_website()
