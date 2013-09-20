# -*- coding: utf-8 -*-

import urllib2
from urllib import urlencode
from HTMLParser import HTMLParser


URL_PREFIX = 'cgi-bin/nagios3/status.cgi?'
GET_PARAMS = {
    'host': 'all',
    'servicestatustypes': 28,
    'hoststatustypes': 15,
}
DISABLE_NOTIFY_GIF = 'ndisabled.gif'


class NagiosHTMLParser(HTMLParser):
    """ parse nagios page
    """

    def __init__(self):
        HTMLParser.__init__(self)
        self.problems = {}

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if tag == 'a':
            if 'extinfo' in props['href'] and 'service' in props['href']:
                self.host = props['href'].split('&')[1].split('=')[1]
                self.service = props['href'].split('&')[2].split('=')[1]
                if '+' in self.service:
                        self.service = self.service.replace('+', ' ')
                if '#' in self.service:
                        self.service = self.service.split('#')[0]

                if not self.host in self.problems:
                    self.problems[self.host] = {}
                self.problems[self.host][self.service] = {
                    'notify': True,
                }

        if tag == 'td' and 'class' in props:
            if props['class'] == 'statusWARNING':
                self.problems[self.host][self.service]['status'] = 'WARNING'
            if props['class'] == 'statusCRITICAL':
                self.problems[self.host][self.service]['status'] = 'CRITICAL'
        if tag == 'img' and 'src' in props:
            if DISABLE_NOTIFY_GIF in props['src']:
                self.problems[self.host][self.service]['notify'] = False


def get_new_nagios_status(url, user, passwd):
    """ Output:
    {
    'host_name': {
        'service_name': {
            'status': 'CRITICAL|WARNING',
            'notify': True,
            },
        },
    }
    """
    if not url.endswith('/'):
        url += '/'
    full_url = url + URL_PREFIX
    full_url = full_url + urlencode(GET_PARAMS)
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password('Nagios Access', full_url, user, passwd)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)
    response = urllib2.urlopen(full_url).read()

    parser = NagiosHTMLParser()
    parser.feed(response)

    return parser.problems
