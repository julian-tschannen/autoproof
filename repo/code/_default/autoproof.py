import sys
import os, os.path
import shutil
import time
from subprocess import call

# EXAMPLE SPECIFIC
ap_options = [
	'-ownership', 
	'-timeout', '120']

# GENERAL (changes here have to be copied to all other autoproof.py files)

# environment variables
os.environ['ISE_PLATFORM'] = 'win64'
os.environ['ISE_C_COMPILER'] = 'msc'
os.environ['ISE_EIFFEL'] = "C:\\Eiffel\\eve"
os.environ['ISE_LIBRARY'] = os.getenv("ISE_EIFFEL")
os.environ['ISE_PRECOMP'] = os.path.join(os.getenv("ISE_EIFFEL"), 'precomp', 'spec', 'win64')
os.environ['PATH'] = os.path.join(os.getenv("ISE_EIFFEL"), 'studio', 'tools', 'boogie') + os.pathsep + os.path.join(os.getenv("ISE_EIFFEL"), 'studio', 'spec', os.getenv("ISE_PLATFORM"), 'bin') + os.pathsep + os.environ['PATH']

# change to specific directory
path = sys.argv[-1]
dir, fn = os.path.split(os.path.abspath(path))
os.chdir(dir)

# check for default ecf, target and options
if not 'ecf_name' in locals():
	for f in os.listdir('.'):
		base = os.path.basename(f)
		file, ext = os.path.splitext(base)
		if ext == '.ecf':
			ecf_name = base
			target_name = file

# ec options
args = ['-batch', 
	'-output_file', 'out.txt', 
	'-project', ecf_name, 
	'-target', target_name, 
	'-batch', 
	'-boogie', '-html'] + ap_options

# call eve
call(["ec.exe"] + args)
