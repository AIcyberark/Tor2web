"""

:mod:`Tor2Web`
=====================================================

.. automodule:: Tor2Web
   :synopsis: Configuration component

.. moduleauthor:: Arturo Filasto' <art@globaleaks.org>
.. moduleauthor:: Giovanni Pellerano <evilaliv3@globaleaks.org>

"""

# -*- coding: utf-8 -*-

import configparser
import os
import re
import sys
from optparse import OptionParser

from .storage import Storage

listpattern = re.compile(r'\s*("[^"]*"|.*?)\s*,')


class Config(Storage):
    """
    A Storage-like class which loads each attribute into a portable conf file.
    """

    def __init__(self):
        Storage.__init__(self)
        self._section = 'main'
        self._parser = configparser.ConfigParser()

        parser = OptionParser()
        parser.add_option("-c", "--configfile", dest="configfile", default="/etc/tor2web.conf")
        parser.add_option("-p", "--pidfile", dest="pidfile", default='/var/run/tor2web/t2w.pid')
        parser.add_option("-u", "--uid", dest="uid", default='')
        parser.add_option("-g", "--gid", dest="gid", default='')
        parser.add_option("-n", "--nodaemon", dest="nodaemon", default=False, action="store_true")
        parser.add_option("-d", "--rundir", dest="rundir", default='/var/run/tor2web/')
        parser.add_option("-x", "--command", dest="command", default='start')
        options, _ = parser.parse_args()

        self._file = options.configfile

        self.__dict__['configfile'] = options.configfile
        self.__dict__['pidfile'] = options.pidfile
        self.__dict__['uid'] = options.uid
        self.__dict__['gid'] = options.gid
        self.__dict__['nodaemon'] = options.nodaemon
        self.__dict__['command'] = options.command
        self.__dict__['nodename'] = 'tor2web'
        self.__dict__['datadir'] = '/home/tor2web'
        self.__dict__['sysdatadir'] = '/usr/share/tor2web/data'
        self.__dict__['ssl_key'] = None
        self.__dict__['ssl_cert'] = None
        self.__dict__['ssl_intermediate'] = None
        self.__dict__['ssl_dh'] = None
        self.__dict__['rundir'] = options.rundir
        self.__dict__['logreqs'] = False
        self.__dict__['debugmode'] = True
        self.__dict__['debugtostdout'] = True
        self.__dict__['processes'] = 1
        self.__dict__['requests_per_process'] = 1000000
        self.__dict__['transport'] = 'BOTH'
        self.__dict__['listen_ipv4'] = '127.0.0.1'
        self.__dict__['listen_ipv6'] = None
        self.__dict__['listen_port_http'] = 80
        self.__dict__['listen_port_https'] = 443
        self.__dict__['basehost'] = 'AUTO'
        self.__dict__['sockshost'] = '127.0.0.1'
        self.__dict__['socksport'] = 9050
        self.__dict__['sockmaxpersistentperhost'] = 5
        self.__dict__['sockcachedconnectiontimeout'] = 240
        self.__dict__['sockretryautomatically'] = True
        self.__dict__['cipher_list'] = 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:' \
                                       'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:' \
                                       'ECDHE-RSA-AES256-SHA:DHE-DSS-AES256-SHA:DHE-RSA-AES128-SHA:'
        self.__dict__['mode'] = 'BLOCKLIST'
        self.__dict__['onion'] = None
        self.__dict__['blockhotlinking'] = True
        self.__dict__['blockhotlinking_exts'] = ['jpg', 'png', 'gif']
        self.__dict__['extra_http_response_headers'] = None
        self.__dict__['disable_disclaimer'] = False
        self.__dict__['disable_banner'] = False
        self.__dict__['disable_tor_redirection'] = False
        self.__dict__['disable_gettor'] = False
        self.__dict__['avoid_rewriting_visible_content'] = False
        self.__dict__['smtpuser'] = 'globaleaks'
        self.__dict__['smtppass'] = 'globaleaks'
        self.__dict__['smtpmail'] = 'notification@demo.globaleaks.org'
        self.__dict__['smtpmailto_exceptions'] = 'stackexception@lists.tor2web.org'
        self.__dict__['smtpmailto_notifications'] = 'tor2web-abuse@lists.tor2web.org'
        self.__dict__['smtpdomain'] = 'mail.globaleaks.org'
        self.__dict__['smtpport'] = 9267
        self.__dict__['smtpsecurity'] = 'TLS'
        self.__dict__['exit_node_list_refresh'] = 600
        self.__dict__['automatic_blocklist_updates_source'] = ''
        self.__dict__['automatic_blocklist_updates_refresh'] = 600
        self.__dict__['automatic_blocklist_updates_mode'] = "MERGE"
        self.__dict__['publish_blocklist'] = False
        self.__dict__['mirror'] = []
        self.__dict__['dummyproxy'] = None
        self.__dict__['proto'] = 'http://' if self.__dict__['transport'] == 'HTTP' else 'https://'
        self.__dict__['bufsize'] = 4096

        # Development VS. Production
        localpath = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "..", "data"))
        if os.path.exists(localpath):
            self.__dict__['sysdatadir'] = localpath

        self.load()

        if self.__dict__['ssl_key'] is None:
            self.__dict__['ssl_key'] = os.path.join(self.__dict__['datadir'], "certs/tor2web-key.pem")

        if self.__dict__['ssl_cert'] is None:
            self.__dict__['ssl_cert'] = os.path.join(self.__dict__['datadir'], "certs/tor2web-cert.pem")

        if self.__dict__['ssl_intermediate'] is None:
            self.__dict__['ssl_intermediate'] = os.path.join(self.__dict__['datadir'], "certs/tor2web-intermediate.pem")

        if self.__dict__['ssl_dh'] is None:
            self.__dict__['ssl_dh'] = os.path.join(self.__dict__['datadir'], "certs/tor2web-dh.pem")

    def load(self):
        try:
            if (not os.path.exists(self._file) or
                    not os.path.isfile(self._file) or
                    not os.access(self._file, os.R_OK)):
                print(("Tor2web Startup Failure: cannot open config file (%s)" % self._file))
                exit(1)
        except Exception:
            print(("Tor2web Startup Failure: error while accessing config file (%s)" % self._file))
            exit(1)

        try:
            self._parser.read([self._file])

            for name in self._parser.options(self._section):
                self.__dict__[name] = self.parse(name)

            # set any http headers to raw ascii
            if self.extra_http_response_headers:
                for key, value in list(self.extra_http_response_headers.items()):
                    # delete the old key
                    del self.extra_http_response_headers[key]
                    #make the ascii equivalents, and save those.
                    key, value = key.encode('ascii', 'ignore'), value.encode('ascii','ignore')
                    self.extra_http_response_headers[key] = value

        except Exception as e:
            raise Exception("Tor2web Error: invalid config file (%s): %s" % (self._file, e))

        self.verify_config_is_sane()

    def verify_config_is_sane(self):
        '''Checks that the specified config values are allowed.'''
        self.verify_values('transport', ['HTTP', 'HTTPS', 'BOTH'])
        self.verify_values('logreqs', [True, False])
        self.verify_values('debugmode', [True, False])
        self.verify_values('debugtostdout', [True, False])
        self.verify_values('blockhotlinking', [True, False])
        self.verify_values('disable_banner', [True, False])
        self.verify_values('disable_gettor', [True, False])
        self.verify_values('disable_tor_redirection', [True, False])
        self.verify_values('proto', ['http://', 'https://'])

        # TODO: Add a bunch more here to ensure sane config file


    def verify_values(self, key, allowed_values ):
        '''asserts that the key is one of the allowed values.  If not, spits out an error message.'''

        # if key is not in the dict, don't bother.
        if key not in self.__dict__:
            return

        value = self.__dict__[key]
        allowed_values_string = '{' + ', '.join([ "'" + str(x) + "'" for x in allowed_values]) + '}'
        assert self.__dict__[key] in allowed_values, "config.%s='%s' (%s) is invalid.  Allowed values: %s" % (key, value, type(value), allowed_values_string)

    def splitlist(self, line):
        return [x[1:-1] if x[:1] == x[-1:] == '"' else x
                for x in listpattern.findall(line.rstrip(',') + ',')]

    def parse(self, name):
        try:
            value = self._parser.get(self._section, name)
            
            # strip any boundry whitespace just in case
            value = value.strip()

            if value.isdigit():
                return int(value)
            if value.lower() in ['true', 'false']:
                return value.lower() == 'true'
            if value.lower() in ['','none']:
                return None
            if value[0] == "[" and value[-1] == "]":
                return self.splitlist(value[1:-1])

            return value

        except configparser.NoOptionError:
            # if option doesn't exists returns None
            return None

    def __getattr__(self, name):
        return self.__dict__.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__[name] = value

        # keep an open port with private attributes
        if name.startswith("_"):
            return

        try:
            # XXX: Automagically discover variable type
            self._parser.set(self._section, name, value)

        except configparser.NoOptionError:
            raise NameError(name)

    def t2w_file_path(self, path):
        local_path = os.path.join(self.datadir, path)
        global_path = os.path.join(self.sysdatadir, path)

        if os.path.exists(local_path):
            return local_path
        elif os.path.exists(global_path):
            return global_path
        else:
            return local_path
