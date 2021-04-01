from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
        name='wiki-annotate', 
        version='1.0', 
        packages=find_packages()
        python_requires=">=3.8",
        install_requires=required,
        )
