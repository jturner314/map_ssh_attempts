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

import operator
import numpy as np
from . import geoip

def bar_plot(ax, prop, attempts):
    """Apply bar plot of `prop` from `attempts` on `ax`.

    :param ax: Matplotlib Axes
    :param prop: property to plot
    :param attempts: generator of Attempt tuples
    """
    data = {}
    if prop != 'username':
        geoipmv = geoip.GeoIPMultiversion()
    for attempt in attempts:
        if prop == 'username':
            data[attempt.username] = data.get(attempt.username, 0) + 1
        elif prop == 'country':
            try:
                country = geoipmv.country_name_by_addr(attempt.ip_address)
            except AttributeError:
                print("Warning: unable to find country for {}".format(
                    attempt.ip_address))
                continue
            data[country] = data.get(country, 0) + 1
        else:
            raise ValueError("Unknown `prop` value: {}".format(prop))

    labels, values = zip(*sorted(data.items(), key=operator.itemgetter(1)))
    bottoms = np.arange(len(labels)) + 0.5
    ax.barh(bottoms, values, align='center', color='lightgreen')
    ax.grid(axis='x')
    ax.set_ylabel(prop.capitalize())
    ax.set_xlabel('Number of attempts')
    ax.set_yticks(bottoms)
    ax.set_yticklabels(labels)
