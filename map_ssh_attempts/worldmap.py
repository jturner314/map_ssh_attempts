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

import mpl_toolkits.basemap
import numpy as np
from . import geoip
from . import tor


def plot_attempt_locations(basemap, attempts, *, highlight_tor=False):
    """Plot the attempt locations on `basemap`.

    :param basemap: Basemap object
    :param attempts: list of Attempt objects
    :param highlight_tor: highlight Tor exit nodes in a different color
    """
    normal_lons = []
    normal_lats = []
    tor_lons = []
    tor_lats = []
    geoipmv = geoip.GeoIPMultiversion()
    tordb = tor.TorExitNodeDatabase()
    for attempt in attempts:
        try:
            coord = geoipmv.coord_by_addr(attempt.ip_address)
        except geoip.GeoIPError:
            print("Warning: unable to find coordinates for {}".format(
                attempt.ip_address))
            continue
        if tordb.is_tor_exit_node(attempt.ip_address):
            tor_lons.append(coord.longitude)
            tor_lats.append(coord.latitude)
        else:
            normal_lons.append(coord.longitude)
            normal_lats.append(coord.latitude)
    normal_x, normal_y = basemap(normal_lons, normal_lats)
    tor_x, tor_y = basemap(tor_lons, tor_lats)
    basemap.plot(normal_x, normal_y, 'ro')
    tor_color = 'bo' if highlight_tor else 'ro'
    basemap.plot(tor_x, tor_y, tor_color)


def setup_map():
    """Setup the projections and background image for the map and return it.

    :return: Basemap object
    """
    m = mpl_toolkits.basemap.Basemap(projection='kav7', lon_0=0, resolution='l')
    m.drawcoastlines()
    m.drawcountries()
    m.fillcontinents(color='lightgreen', lake_color='lightblue')
    m.drawparallels(np.arange(-90, 120, 30))
    m.drawmeridians(np.arange(0, 360, 60))
    m.drawmapboundary(fill_color='lightblue')
    return m
