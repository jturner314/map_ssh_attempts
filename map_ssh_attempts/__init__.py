#!/usr/bin/python3

import argparse
import collections
import datetime
import ipaddress
import matplotlib.pyplot as plt
import mpl_toolkits.basemap
import numpy as np
import os
import os.path
import paramiko.client
import pygeoip
import re
import tempfile
import urllib.request
import gzip


GEOIP_DBS = {4: ('GeoLiteCity.dat', 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'),
             6: ('GeoLiteCityv6.dat', 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCityv6-beta/GeoLiteCityv6.dat.gz')}


Attempt = collections.namedtuple('Attempt', ('datetime', 'username', 'ip_address'))


Coordinate = collections.namedtuple('Coordinate', ('longitude', 'latitude'))


def update_geoip_dbs(cache_dir='~/.cache/map_ssh_attempts'):
    """Update GeoIP database cache.

    :param cache_dir: directory in which to place the GeoIP databases
    """
    cache_dir = os.path.expanduser(cache_dir)
    if not os.path.isdir(cache_dir):
        if os.path.lexists(cache_dir):
            raise NotADirectoryError('Download location exists but is not a directory.')
        else:
            os.makedirs(cache_dir)
    for info in GEOIP_DBS.values():
        name, url = info
        with open(os.path.join(cache_dir, name), 'wb') as f:
            db_gz = urllib.request.urlopen(url).read()
            db = gzip.decompress(db_gz)
            f.write(db)


def open_geoip_dbs(cache_dir='~/.cache/map_ssh_attempts'):
    """Create GeoIP objects from database files.

    :param cache_dir: directory containing the GeoIP databases
    """
    cache_dir = os.path.expanduser(cache_dir)
    dbs = {}
    for version, info in GEOIP_DBS.items():
        name, url = info
        if not os.path.isfile(os.path.join(cache_dir, name)):
            update_geoip_dbs(cache_dir)
        dbs[version] = pygeoip.GeoIP(os.path.join(cache_dir, name))
    return dbs


def print_download_progress(done, todo):
    """Print the progress of a download.

    :param done: portion completed
    :param todo: total amount that needs to be done
    """
    print('Downloading... {:.2%}'.format(done/todo), end='\r')


def open_auth_log(hostname, *args, **kwargs):
    """Open a readonly file-like object that reads /etc/log/auth.log on `hostname`.

    :param hostname: the server to connect to
    :param args: extra args to pass to SSHClient.connect()
    :param kwargs: extra keyword args to pass to SSHClient.connect()
    :return: TemporaryFile object with log file contents
    """
    # Initiate connection
    client = paramiko.client.SSHClient()
    client.load_system_host_keys()
    kwargs['compress'] = kwargs.get('compress', True)
    client.connect(hostname, *args, **kwargs)

    # Copy file
    temp = tempfile.TemporaryFile()
    sftp = client.open_sftp()
    sftp.getfo('/var/log/auth.log', temp, print_download_progress)
    sftp.close()
    print()

    # Seek back to beginning of file for reading
    temp.seek(0)
    return temp


def parse_datetime(string, fmt=None):
    """Parse the string and return a datetime object.

    The default `fmt` is equivalent to '%b %e %H:%M:%S'

    :param string: string to parse
    :param fmt: format usable by `strptime`
    :return: datetime object
    """
    if fmt is None:
        match = re.match('(\S+)\s+(\d+)\s+(.*)', string)
        new_string = '{} {:0} {}'.format(
            match.group(1), int(match.group(2)), match.group(3))
        parsed = datetime.datetime.strptime(new_string, '%b %d %H:%M:%S')
        return datetime.datetime(
            datetime.datetime.now().year, parsed.month, parsed.day,
            parsed.hour, parsed.minute, parsed.second)
    else:
        return datetime.datetime.strptime(string, fmt)


def parse_log(log_file):
    """Generate tuples of SSH attempt events from `log_file` file-like object.

    :param log_file: file-like object with contents of ``/var/log/auth.log``
    :return: list of tuples of the form (datetime, username, ip_address)
    """
    with log_file as f:
        for line in f:
            line = line.decode('UTF-8')
            regexps = ['(?P<datetime>.*) .* sshd\[\d+\]: User (?P<username>\S+) from (?P<ip_address>\S+) not allowed',
                       '(?P<datetime>.*) .* sshd\[\d+\]: Invalid user (?P<username>\S+) from (?P<ip_address>\S+)']
            for regexp in regexps:
                match = re.match(regexp, line)
                if match is not None:
                    yield Attempt(parse_datetime(match.groupdict()['datetime']),
                                  match.groupdict()['username'],
                                  ipaddress.ip_address(match.groupdict()['ip_address']))
                    break


def ip_to_lon_lat(ip_address, geoip_dbs):
    """Given an IPv4Address or IPv6Address, return a GeoIP (lon,lat) coordinate pair.

    :param ip_address: IPv4Address or IPv6Address object with address of host
    :return: (longitude, latitude) tuple
    """
    record = geoip_dbs[ip_address.version].record_by_addr(str(ip_address))
    return Coordinate(record['longitude'], record['latitude'])


def plot_attempt_locations(attempts, basemap):
    """Plot the attempt locations on `basemap`.

    :param attempts: list of Attempt objects
    :param basemap: Basemap object
    """
    lons = []
    lats = []
    geoip_dbs = open_geoip_dbs()
    for attempt in attempts:
        coord = ip_to_lon_lat(attempt.ip_address, geoip_dbs)
        lons.append(coord.longitude)
        lats.append(coord.latitude)
    x, y = basemap(lons, lats)
    basemap.plot(x, y, 'ro')


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


def main():
    parser = argparse.ArgumentParser(description="Plot failed SSH attempts on a map.")
    parser.add_argument('action', type=str, choices=['plot', 'update'],
                        help="action to perform")
    parser.add_argument('hostname', type=str, nargs='?',
                        help="hostname of remote server with auth.log")
    args = parser.parse_args()

    if args.action == 'plot':
        basemap = setup_map()
        plot_attempt_locations(parse_log(open_auth_log(args.hostname)), basemap)
        plt.show()
    elif args.action == 'update':
        update_geoip_dbs()


if __name__ == '__main__':
    main()
