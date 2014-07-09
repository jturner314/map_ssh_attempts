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

import argparse
import matplotlib.pyplot as plt
from . import geoip
from . import getdata
from . import worldmap


def main():
    parser = argparse.ArgumentParser(description="Plot failed SSH attempts on a map.")
    parser.add_argument('action', type=str, choices=['plot', 'update'],
                        help="action to perform")
    parser.add_argument('hostname', type=str, nargs='?',
                        help="hostname of remote server with auth.log")
    args = parser.parse_args()

    if args.action == 'plot':
        basemap = worldmap.setup_map()
        worldmap.plot_attempt_locations(getdata.get_data(args.hostname), basemap)
        plt.show()
    elif args.action == 'update':
        geoipmv = geoip.GeoIPMultiversion()
        geoipmv.update_cache()


if __name__ == '__main__':
    main()
