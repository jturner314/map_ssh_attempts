#!/usr/bin/python3

# Copyright (C) 2014  Jim Turner

# This file is part of map_ssh_attempts.

# map_ssh_attempts is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option) any
# later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

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
                          'matplotlib',
                          'numpy',
                          'paramiko >= 1.7.4',
                          'pygeoip'],
        package_data={},
        url="https://github.com/jturner314/map_ssh_attempts",
        version="0.1.0")
