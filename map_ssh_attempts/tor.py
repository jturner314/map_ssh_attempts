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

import ipaddress
import os.path
import urllib.request


class TorExitNodeDatabase(object):

    db_name = 'Tor_ip_list_EXIT.csv'
    db_source = 'http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv'

    def __init__(self, cache_dir='~/.cache/map_ssh_attempts'):
        """Create an object to lookup Tor exit nodes.

        :param cache_dir: directory in which to place the database
        """
        self.cache_dir = os.path.expanduser(cache_dir)
        self.db = None

    def update_cache(self):
        """Update Tor exit node cache."""
        if not os.path.isdir(self.cache_dir):
            if os.path.lexists(self.cache_dir):
                raise NotADirectoryError('Download location exists but is not a directory.')
            else:
                os.makedirs(self.cache_dir)
        name = TorExitNodeDatabase.db_name
        url = TorExitNodeDatabase.db_source
        with open(os.path.join(self.cache_dir, name), 'wb') as f:
            print("Updating {}... ".format(name), end='')
            f.write(urllib.request.urlopen(url).read())
            print("100%")

    def check_cache(self):
        """Check if Tor database file exists in cache."""
        return os.path.isfile(os.path.join(
            self.cache_dir, TorExitNodeDatabase.db_name))

    def check_loaded(self):
        """Check if Tor database has been loaded."""
        return self.db is not None

    def load_dbs(self):
        """Load Tor info from database file."""
        if not self.check_cache():
            self.update_cache()
        name = TorExitNodeDatabase.db_name
        print("Loading {}... ".format(name), end='')
        with open(os.path.join(self.cache_dir, name), 'r') as f:
            self.db = {ipaddress.ip_address(address) for address in f.read().split()}
        print("100%")

    def is_tor_exit_node(self, addr):
        """Given an IPv4Address or IPv6Address, return if it's a Tor exit node.

        :param addr: IPv4Address or IPv6Address object with address of host
        :return: if the address for a Tor exit node
        """
        if not self.check_loaded():
            self.load_dbs()
        return addr in self.db
