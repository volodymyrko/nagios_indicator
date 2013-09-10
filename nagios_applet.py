# -*- coding: utf-8 -*-

import sys
import gobject
import gtk
import appindicator
import pynotify
import os
import ConfigParser
from nagios_checker import get_new_nagios_status


CHECK_INTERVAL = 60 * 5 * 1000 # mls
CHECK_INTERVAL = 30 * 1000 # mls

CUSTOM_ICON = 'indicator-messages'
BAD_AUTH_ICON = 'new-messages-red'
NAGIOS_MSG_ICON = 'indicator-messages-new'

#ICON_PATH = '?'
#ICON_NAME = '?'
#def menuitem_response(w, buf, i):
#    print buf, i
#    if i == 1:
#        ind.set_status(appindicator.STATUS_ATTENTION)
#        ind.set_attention_icon("skype")
#    elif i == 2:
#        ind.set_status(appindicator.STATUS_ACTIVE)
#import pdb; pdb.set_trace()


class NagiosApplet(object):
    """ Nagios checker applet
    """

    def __init__(self):
        pynotify.init("Init")
        self.ind = appindicator.Indicator("nagios-checker",
            CUSTOM_ICON,
            appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.build_menu()
        self.nagios_status = {}
        self.renotify = False
        self.show_disabled = False
        self.auth = {}

    def build_menu(self):
        """Create applet menu
        """
        menu = gtk.Menu()
        item = gtk.MenuItem("Check nagios status now")
        menu.append(item)
        item.connect("activate", self.check_now)
        item.show()
        #item = gtk.MenuItem("Stop monitoring")
        #menu.append(item)
        #item.connect("activate", stop_monitor)
        #item.show()
        #item = gtk.MenuItem("Start monitoring")
        #menu.append(item)
        #item.connect("activate", start_monitor)
        #item.show()
        item = gtk.MenuItem("Relaod config")
        menu.append(item)
        item.connect("activate", self.get_config)
        item.show()
        item = gtk.MenuItem("Quit")
        menu.append(item)
        item.connect("activate", self.quit)
        item.show()
        self.ind.set_menu(menu)

    def check_status(self):
        # try get auth info in not
        if not self.auth:
            self.get_config()
            self.ind.set_status(appindicator.STATUS_ATTENTION)
            self.ind.set_attention_icon(BAD_AUTH_ICON)
        # do job if auth info exists
        if self.auth:
            if self.ind.get_attention_icon() == BAD_AUTH_ICON:
                self.ind.set_status(appindicator.STATUS_ACTIVE)
            new_nagios_status = get_new_nagios_status(
                show_disabled=self.show_disabled, **self.auth)
            for host in new_nagios_status:
                for service, new_value in new_nagios_status[host].items():
                    try:
                        old_value = self.nagios_status[host].pop(service)
                        if new_value != old_value or self.renotify:
                            self.notify(header=host,
                                body='{0} {1}'.format(service, new_value))
                    except KeyError:
                        self.notify(header=host,
                            body='{0} {1}'.format(service, new_value))
            for host in self.nagios_status:
                for service in self.nagios_status[host]:
                    self.notify(header=host,
                        body='{0} {1}'.format(service, 'OK'))
            self.nagios_status = new_nagios_status

            if self.nagios_status:
                self.ind.set_status(appindicator.STATUS_ATTENTION)
                self.ind.set_attention_icon(NAGIOS_MSG_ICON)
            else:
                self.ind.set_status(appindicator.STATUS_ACTIVE)
        else:
            self.notify(header='CONFIG ERROR',
                body='please, check config file')
        return True

    def run(self):
        self.get_config()
        self.check_status()
        self.timeout_id = gobject.timeout_add(CHECK_INTERVAL,
            self.check_status)
        gtk.main()

    def quit(self, menu_item):
        sys.exit(0)

    def check_now(self, menu_item):
        gobject.source_remove(self.timeout_id)
        self.check_status()
        self.timeout_id = gobject.timeout_add(CHECK_INTERVAL,
            self.check_status)

    def get_config(self, menu_item=None):
        self.auth = {}
        home_dir = os.path.expanduser("~")
        conf_file = os.path.join(home_dir, '.nagios_checker')
        if os.path.isfile(conf_file):
            conf = ConfigParser.ConfigParser()
            conf.read(conf_file)
            params = conf.defaults()
            if conf.has_option('DEFAULT', 'renotify'):
                self.renotify = conf.getboolean('DEFAULT', 'renotify')
            if conf.has_option('DEFAULT', 'show_disabled'):
                self.show_disabled = conf.getboolean('DEFAULT',
                    'show_disabled')
            cred_fields = ['url', 'user', 'passwd']
            if all(f in params for f in cred_fields):
                self.auth.update({
                    'url': params['url'],
                    'user': params['user'],
                    'passwd': params['passwd'],
                    })

    def notify(self, header, body=None, type='info'):
        msg = pynotify.Notification(header, body)
        msg.set_timeout(10)
        msg.show()
        msg.close()

if __name__ == "__main__":
    applet = NagiosApplet()
    applet.run()
