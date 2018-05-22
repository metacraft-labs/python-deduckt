from setuptools import setup, find_packages

description = "python-deduckt infers the concrete types used inside a python program and creates an AST database with static types. "

setup(
    name='python-deduckt',
    author='Metacraft Labs',
    author_email='python@metacraft-labs.com',
    version="0.1",
    license="MIT",
    url='https://www.metacraft-labs.com',
    packages=find_packages(),
    description=description,
    # long_description=open('README.rst').read(),
    install_requires=open('requirements.txt').read(),
    entry_points={
      'console_scripts': [
        'python-deduckt=deduckt.main:main',
      ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
