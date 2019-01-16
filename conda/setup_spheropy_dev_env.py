"""
"""
import os, sys
import argparse
import subprocess
import shutil

def main():
    script_args = parse_args()
    if not is_conda_available():
        print('\"conda\" is not available in this context. Are you sure you have minconda or anaconda installed and are running this from a conda environment?')

    add_conda_forge()

    install_deps()

def parse_args():
    parser = argparse.ArgumentParser()
    return parser.parse_args()

def is_conda_available():
    try:
        subprocess.check_call(
            ['conda', '--help'],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False

def install_deps():
    subprocess.check_call(['conda', 'install', '--yes',
        'python=3.6',
        'pylint',
        'git',
        'pexpect']
    )
    subprocess.check_call(['pip', 'install',
        # install pybluez. If running on windows we need to install irvinec's fork that has a patch for windows.
        'git+https://github.com/irvinec/pybluez' if is_running_on_windows() else 'git+https://github.com/pybluez/pybluez',
        # install pygatt
        'git+https://github.com/peplin/pygatt'])
    # TODO: let's see if we can use pygatt for the ble communication since it x-plat and installed fine here.

def add_conda_forge():
    subprocess.check_call(['conda', 'config', '--add', 'channels', 'conda-forge'])

def is_running_on_windows():
    return os.name == 'nt'

def is_running_on_linux():
    return os.name == 'posix'

def is_running_on_mac():
    return os.name == 'mac'

class TempDir(object):
    """
    """

    def __init__(self):
        self.parent_path = os.path.realpath(os.path.curdir)
        self.path = os.path.join(self.parent_path, '.tmp')

    def __enter__(self):
        os.makedirs(self.path)
        os.chdir(self.path)

    def __exit__(self, a, b, c):
        os.chdir(self.parent_path)
        shutil.rmtree(self.path)


if __name__ == '__main__': main()