.. Copyright (C) 2014  Jim Turner

   This file is part of map_ssh_attempts.

   map_ssh_attempts is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by the Free
   Software Foundation, either version 2 of the License, or (at your option) any
   later version.

   This program is distributed in the hope that it will be useful, but WITHOUT ANY
   WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
   PARTICULAR PURPOSE.  See the GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along with
   this program.  If not, see <http://www.gnu.org/licenses/>.

#######################
Map Failed SSH Attempts
#######################

This is a script to plot failed attempts to SSH into a remote machine on a
world map showing the sources of those attempts.

.. figure:: doc/example_map.png

Dependencies
============

* Python 3
* basemap
* paramiko
* matplotlib
* numpy
* pygeoip

Installation
============

To install, run::

  # ./setup.py install
