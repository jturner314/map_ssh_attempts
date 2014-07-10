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
from . import plot
from . import worldmap


def main():
    parser = argparse.ArgumentParser(
        description="Plot failed SSH attempts on a map.")
    subparsers = parser.add_subparsers(dest='action', help="action to perform")

    # Subparser update
    parser_update = subparsers.add_parser(
        'update', description="Update the GeoIP database cache.")

    # Subparser map
    parser_map = subparsers.add_parser(
        'map', description="Plot data on a world map.")
    parser_map.add_argument('property', type=str, choices=['coords'],
                            help="property to map")
    parser_map.add_argument('hostname', type=str,
                            help="hostname of remote server to analyze")

    # Subparser bar
    parser_bar = subparsers.add_parser(
        'bar', description="Show bar plot of data.")
    parser_bar.add_argument('property', type=str,
                            choices=['username', 'country'],
                            help="property to plot")
    parser_bar.add_argument('hostname', type=str,
                            help="hostname of remote server to analyze")

    args = parser.parse_args()

    if args.action == 'update':
        geoipmv = geoip.GeoIPMultiversion()
        geoipmv.update_cache()
    elif args.action == 'map':
        basemap = worldmap.setup_map()
        if args.property == 'coords':
            worldmap.plot_attempt_locations(basemap, getdata.get_data(args.hostname))
        plt.show()
    elif args.action == 'bar':
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        plot.bar_plot(ax, args.property, getdata.get_data(args.hostname))
        fig.tight_layout()
        plt.show()


if __name__ == '__main__':
    main()
