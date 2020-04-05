"""
Flask-Roles
-------------

A small plugin to flask to add roles support.

"""
from setuptools import setup

with open("README.rst", "r") as f:
    readme = f.read()

setup(
    name="flask_roles",
    version="0.1",
    url="https://bitbucket.org/east36/python-nifty-client",
    license="GPLv3",
    author="Laban Mwangi",
    author_email="support@east36.co.ke",
    description="Flask plugin to add roles to a project",
    long_description=readme,
    packages=["flask_roles"],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
