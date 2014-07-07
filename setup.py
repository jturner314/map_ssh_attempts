#!/usr/bin/python3

from setuptools import setup, find_packages

if __name__ == '__main__':
    packages = find_packages()
    setup(
        author="Jim Turner",
        description="Plot failed SSH attempts on a map",
        license="GNU GPLv2+",
        classifiers=[
            "Environment :: Console",
            "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
            "Programming Language :: Python"],
        name="map_ssh_attempts",
        packages=packages,
        entry_points={'console_scripts': ['map_ssh_attempts = map_ssh_attempts:main']},
        test_suite='map_ssh_attempts.testsuite',
        install_requires=['basemap',
                          'paramiko >= 1.7.4',
                          'pygeoip'],
        package_data={},
        url="https://github.com/jturner314/map_ssh_attempts",
        version="0.1.0")
