nagios_indicator
=============

Gnome indicator for nagios

It adds icon indicator to gnome panel.
This applet automatically check your nagios server and notify all problems using popup messages.

Installation:
1. create config file .nagios_checker in your $HOME directory

[DEFAULT]
url = <url_to_nagios_server> # http://server.com/nagios3/
user = <username> # nagiosadmin, nagios user
passwd = <password> # nagiosadmin password
renotify = false # notify every check (true) or once (false), (optional)
show_disabled = false # notify (true) if notification is disabled for service or not (false), (optional)
interval = 300 # check interval in second (default 300sec = 5min),  (optional)  

2. run:
    a) python nagios_applet.py
    b) create startup scirpt, for example

    #cat ~/.config/autostart/nagios.desktop 
    [Desktop Entry]
    Name=Nagios Indicator
    GenericName=Nagios Indicator
    Comment=Nagios Indicator
    Exec=python /path/to/nagios_indicator/nagios_indicator.py
    Terminal=false
    Type=Application




Tested on ubuntu 10.04, 12.04
