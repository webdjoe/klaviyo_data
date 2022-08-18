import setuptools
from setuptools import find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="klaviyo_data",
    version="0.0.5",
    author="Joseph Trabulsy",
    author_email="webdjoe@gmail.com",
    keywords="Klaviyo, sql, data, python, analytics, marketing",
    description="Easy klaviyo data analytics for email\
        flow and campaign marketing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/klaviyo_data",
    project_urls={
        "Bug Tracker": "https://github.com/klaviyo_data/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'click>=8.0.1',
        'pandas>=1.2.4',
        'python-dateutil',
        'requests>=2.20',
        'six',
        'sqlalchemy>=1.4',
        'klaviyo'
    ],
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=["test"]),
    python_requires=">=3.9",
    entry_points={
        'console_scripts': [
            'klaviyo_cli = klaviyo_data.cli:cli_runner',
            'build_klaviyo = klaviyo_data.cli:klaviyo_db_builder'
        ],
    }
)
