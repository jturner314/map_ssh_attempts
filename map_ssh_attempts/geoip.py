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

from pygeoip import GeoIPError
import gzip
import collections
import os
import os.path
import pygeoip
import urllib.request


Coordinate = collections.namedtuple('Coordinate', ('longitude', 'latitude'))


class GeoIPMultiversion(object):

    versions = [4, 6]
    db_names = {4: 'GeoLiteCity.dat',
                6: 'GeoLiteCityv6.dat'}
    db_sources = {4: 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz',
                  6: 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCityv6-beta/GeoLiteCityv6.dat.gz'}

    def __init__(self, cache_dir='~/.cache/map_ssh_attempts'):
        """Create an object to lookup GeoIP information regardless of IP version.

        :param cache_dir: directory in which to place the GeoIP databases
        """
        self.cache_dir = os.path.expanduser(cache_dir)
        self.dbs = {}

    def update_cache(self):
        """Update GeoIP database cache."""
        if not os.path.isdir(self.cache_dir):
            if os.path.lexists(self.cache_dir):
                raise NotADirectoryError('Download location exists but is not a directory.')
            else:
                os.makedirs(self.cache_dir)
        for version in GeoIPMultiversion.versions:
            name = GeoIPMultiversion.db_names[version]
            url = GeoIPMultiversion.db_sources[version]
            with open(os.path.join(self.cache_dir, name), 'wb') as f:
                print("Updating {}... ".format(name), end='')
                db_gz = urllib.request.urlopen(url).read()
                db = gzip.decompress(db_gz)
                f.write(db)
                print("100%")

    def check_cache(self):
        """Check if GeoIP database files exist in cache."""
        for version in GeoIPMultiversion.versions:
            name = GeoIPMultiversion.db_names[version]
            if not os.path.isfile(os.path.join(self.cache_dir, name)):
                return False
        else:
            return True

    def load_dbs(self):
        """Load GeoIP objects from database files."""
        if not self.check_cache():
            self.update_cache()
        self.dbs = {}
        for version in GeoIPMultiversion.versions:
            name = GeoIPMultiversion.db_names[version]
            print("Loading {}... ".format(name), end='')
            self.dbs[version] = pygeoip.GeoIP(os.path.join(self.cache_dir, name))
            print("100%")

    def check_loaded(self):
        """Check if GeoIP databases have been loaded."""
        for version in GeoIPMultiversion.versions:
            if not version in self.dbs:
                return False
        else:
            return True

    def coord_by_addr(self, addr):
        """Given an IPv4Address or IPv6Address, return a location Coordinate.

        :param addr: IPv4Address or IPv6Address object with address of host
        :return: Coordinate object
        """
        if not self.check_loaded():
            self.load_dbs()
        record = self.dbs[addr.version].record_by_addr(str(addr))
        if record:
            return Coordinate(record['longitude'], record['latitude'])
        else:
            raise GeoIPError("Unable to determine coordinates.")

    def __getattr__(self, name):
        if name.endswith('_by_addr'):
            def f(addr):
                if not self.check_loaded():
                    self.load_dbs()
                return getattr(self.dbs[addr.version], name)(str(addr))
            return f
        else:
            raise AttributeError("'GeoIPMultiversion' has no attribute '{}'".format(name))
