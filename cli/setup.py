import os
from setuptools import find_packages, setup

with open("wing/version.txt") as ifp:
    VERSION = ifp.read().strip()

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

# eth-brownie should be installed as a library so that it doesn't pin version numbers for all its dependencies
# and wreak havoc on the install.
os.environ["BROWNIE_LIB"] = "1"

setup(
    name="wing",
    version=VERSION,
    packages=find_packages(),
    install_requires=["eth-brownie", "inspector-facet", "moonworm>=0.6.0", "tqdm"],
    extras_require={
        "dev": ["black", "isort"],
    },
    description="Command line interface for Great Wyrm smart contracts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Moonstream DAO",
    author_email="engineering@moonstream.to",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "wing=wing.cli:main",
        ]
    },
    package_data={"wing": ["version.txt"]},
    include_package_data=True,
)
