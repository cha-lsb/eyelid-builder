from setuptools import setup, find_packages

setup(
    name="eyelid-builder",
    version="0.2.0",
    description="Maya tool used to build an eyelid rig based on joints and curves",
    author="Charlotte Lerat",
    author_email="charlotte.lerat1991@gmail.com",
    license="BSD 2-clause",
    # package_dir={"": "eyelid_builder"},
    # packages=find_packages(where="eyelid_builder"),
    packages=find_packages(include=["eyelid_builder", "eyelid_builder.*"]),
    install_requires=[
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)
