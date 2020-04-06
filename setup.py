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
    version="0.3",
    url="https://github.com/labeneator/flask-roles",
    license="GPLv3",
    author="Laban Mwangi",
    author_email="support@east36.co.ke",
    description="Flask plugin to add roles to a project",
    long_description=readme,
    packages=["flask_roles"],
    zip_safe=False,
    include_package_data=True,
    install_requires=["Flask-Login>=0.5.0", "Flask-Principal>=0.4.0"],
    extras_require={
        "testing": ["pip-tools == 4.5.1", "mccabe", "pytest-cov", "pytest"]
    },
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
