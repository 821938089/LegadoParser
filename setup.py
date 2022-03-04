from setuptools import setup, find_packages

import sys

__version__ = '1.0.0'

install_requires = []

with open('requirements.txt', 'r') as f:
    t = f.read()
    install_requires = list(filter(None, t.split('\n')))

with open('LegadoParser2/config.py', 'r+', encoding='utf-8') as f:
    # 关闭调试模式
    t = f.read()

    if ~t.find('DEBUG_MODE = True'):
        t = t.replace('DEBUG_MODE = True', 'DEBUG_MODE = False')

        f.truncate(0)
        f.seek(0)

        f.write(t)

extra_ocr = ['fonttools~=4.29.1', 'cnocr~=2.1.0']

extras_require = {'ocr': extra_ocr}

package_data = {'': ['*.dll', '*.pyd', '*.js']}

if sys.platform == 'win32':
    python_requires = '==3.9.*'
else:
    python_requires = '>=3.8, <4'

setup(
    name='LegadoParser',
    version=__version__,

    url='https://github.com/821938089/LegadoParser',
    author='Horis',

    packages=find_packages(include=['LegadoParser2', 'LegadoParser2.*']),

    install_requires=install_requires,

    extras_require=extras_require,

    package_data=package_data,

    python_requires=python_requires
)
