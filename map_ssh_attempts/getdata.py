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

import collections
import datetime
import ipaddress
import paramiko.client
import re
import tempfile


Attempt = collections.namedtuple('Attempt', ('datetime', 'username', 'ip_address'))


def get_data(hostname):
    """Perform all operations necessary to get, parse, and yield attempts.

    :param hostname: the server to connect to
    :return: generator of tuples of the form (datetime, username, ip_address)
    """
    return parse_log(open_auth_log(hostname))


def print_download_progress(done, todo):
    """Print the progress of a download.

    :param done: portion completed
    :param todo: total amount that needs to be done
    """
    print('Downloading auth.log... {:.0%}'.format(done/todo), end='\r')


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
    :return: generator of tuples of the form (datetime, username, ip_address)
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
