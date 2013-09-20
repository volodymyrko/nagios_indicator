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
HOST_NAME_EVEN = {
    'align': 'left',
    'valign': 'center',
    'class': 'statusEven',
}
HOST_NAME_ODD = {
    'align': 'left',
    'valign': 'center',
    'class': 'statusOdd',
}
SERVICE_WARNING = {
    'align': 'LEFT',
    'valign': 'center',
    'class': 'statusBGWARNING',
}
SERVICE_CRITICAL = {
    'align': 'LEFT',
    'valign': 'center',
    'class': 'statusBGCRITICAL',
}
DISABLE_NOTIFY_GIF = 'ndisabled.gif'


class NagiosHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.problems = {}
        self.get_host_name = False
        self.get_service_name = False
        self.status = None

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if tag == 'td':
            if props == HOST_NAME_EVEN or props == HOST_NAME_ODD:
                self.get_host_name = True
            if props == SERVICE_WARNING or props == SERVICE_CRITICAL:
                self.status = props['class'][8:]
                self.get_service_name = True
        if tag == 'img' and 'src' in props:
            if DISABLE_NOTIFY_GIF in props['src']:
                self.problems[self.host_name][self.service_name][
                'notify'] = False

    def handle_data(self, data):
        if self.get_host_name:
            self.get_host_name = False
            self.host_name = data
            if not self.host_name in self.problems:
                self.problems[self.host_name] = {}
        if self.get_service_name:
            self.get_service_name = False
            self.service_name = data
            self.problems[self.host_name][self.service_name] = {
                'notify': True,
                'status': self.status,
            }


def get_new_nagios_status(url, user, passwd):
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
