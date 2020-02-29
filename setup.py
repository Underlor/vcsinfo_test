from setuptools import find_packages, setup


setup(
    name="vcs-info-test",
    version="1.0.1",
    author="Aleksandr Popov",
    author_email="admin@alexue4.ru",
    url="https://github.com/Underlor/vcsinfo_test",
    description="This script collects data about user repositories from working directories.",
    license="MIT",
    packages=find_packages(),
    entry_points={"console_scripts": ["vcsinfo = vcsinfo_src.vcs_info:main"]},
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=["paramiko"],
)
