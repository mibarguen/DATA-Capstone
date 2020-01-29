import os
import spectra_generator.spectra_generator

"""
This is a utility to install matlab.engine in your python virtual environment
"""

# In matlab command window, enter '`matlabroot`' and copy to this variable:
MATLABROOT = "/Applications/MATLAB_R2019b.app/extern/engines/python"
VENV_DIRNAME = "venv"

project_root = os.path.dirname(os.path.realpath(__file__))

print("\nPlease confirm the following: ")
print("   MATLABROOT = '%s'" % MATLABROOT)
print("   Virtual Env Dir = '%s'" % VENV_DIRNAME)

ans = input("\nAre these correct? (y/n) ")
if ans.lower() != 'y':
    print("Please edit these values in 'setup_virtual_env.py'")
    exit(0)

# First run matlab setup
os.chdir(MATLABROOT)
os.system('python3 setup.py install --prefix="%s"' % os.path.join(project_root, VENV_DIRNAME))


# Copy this into venv/activate
add_import = 'export PYTHONPATH="%s"' % project_root

os.chdir(project_root)
found = False
with open(os.path.join(VENV_DIRNAME, "bin", "activate"), "r") as f:
    for line in f.readlines():
        if add_import in line:
            found = True

if not found:
    with open(os.path.join(VENV_DIRNAME, "bin", "activate"), "a") as f:
        f.write("\n\n# Automatically added by 'setup_virtual_env.py'\n")
        f.write("%s\n" % add_import)
    print("\nWrote to %s" % os.path.join(VENV_DIRNAME, "bin", "activate"))
else:
    print("\n\nMake sure this is in your './venv/bin/activate' file:")
    print(add_import)
