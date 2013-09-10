# -*- coding: utf-8 -*-

import urllib2
from urllib import urlencode
from BeautifulSoup import BeautifulSoup


URL_PREFIX = 'cgi-bin/nagios3/status.cgi?'
GET_PARAMS = {
    'host': 'all',
    'servicestatustypes': 28,
    'hoststatustypes': 15,
}
DISABLE_NOTIFICATION_IMG = '/nagios3/images/ndisabled.gif'


def get_new_nagios_status(url, user, passwd,
    show_disabled=False):

    if not url.endswith('/'):
        url += '/'
    full_url = url + URL_PREFIX
    full_url = full_url + urlencode(GET_PARAMS)
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password('Nagios Access', full_url, user, passwd)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)
    response = urllib2.urlopen(full_url).read()

    soup = BeautifulSoup(response)
    status_table = soup.find('table', {'class': 'status'})

    nagios = {}
    tr = status_table.findNext()
    while tr:
        notification = True
        tds = (tr.findAll('td', recursive=False))
        if len(tds) == 7:
            try:
                host_name = tds[0].find('table').find('table').find('td').find('a').string
            except AttributeError:
                pass
            service_name = tds[1].find('table').find('table').find('td').find('a').string
            if tds[1].find('table').find('img', {'src': DISABLE_NOTIFICATION_IMG}):
                notification = False
            status = tds[2].string

            if notification or show_disabled:
                if not host_name in nagios:
                    nagios[host_name] = {}
                nagios[host_name][service_name] = status

        tr = tr.findNextSibling()

    return nagios
