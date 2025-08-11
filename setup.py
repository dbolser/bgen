from pathlib import Path
from setuptools import setup
from setuptools.command.build_ext import build_ext
import subprocess

class BuildWaf(build_ext):
    def run(self):
        subprocess.check_call(['./waf', 'configure'])
        subprocess.check_call(['./waf'])
        bin_dir = Path('bgenlib/bin')
        bin_dir.mkdir(parents=True, exist_ok=True)
        (Path('build') / 'apps' / 'bgenix').rename(bin_dir / 'bgenix')
        super().run()

setup(
    name='bgenlib',
    version='1.1.7',
    description='BGEN reference implementation packaged for Python',
    packages=['bgenlib'],
    package_data={'bgenlib': ['bin/bgenix']},
    cmdclass={'build_ext': BuildWaf},
    entry_points={'console_scripts': ['bgenix=bgenlib.runner:run_bgenix']},
)
