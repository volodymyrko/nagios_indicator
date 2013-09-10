nagios_applet
=============

Gnome applet for nagios

It adds applet to gnome panel.
This applet automatically check your nagios server and notify all problems using popup messages.

Installation:
1. create config file .nagios_checker in your $HOME directory

[DEFAULT]
url = <url_to_nagios_server> # http://server.com/nagios3/
user = <username> # nagiosadmin, nagios user
passwd = <password> # nagiosadmin password
renotify = false # notify every check (true) or once (false)
show_disabled = false # notify (true) if notification is disabled for service or not (false)

2. run nagios_applet.py


Tested on ubuntu-10.04
