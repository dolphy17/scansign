#!/usr/bin/python

import argparse
import re
import gzip
from datetime import datetime
    
parser = argparse.ArgumentParser(description='OpenVPN usage statistics')
parser.add_argument('logfile', type=str, help='OpenVPN logfile (syslog format)')
parser.add_argument('username', type=str, help='Name of the user to create usage statistics')

args = parser.parse_args()

login_pattern = re.compile("^([A-Z][a-z]{{2}} +\d{{1,2}} \d+:\d+:\d+).*openvpn.*\[{username}\].*Connection Initiated".format(username = args.username))
logout_pattern = re.compile("^([A-Z][a-z]{{2}} +\d{{1,2}} \d+:\d+:\d+).*openvpn.*\[{username}\].*Inactivity timeout".format(username = args.username))

if args.logfile.endswith("gz"):
    log = gzip.open(args.logfile, 'rb')
else:
    log = open(args.logfile, 'r')

user_logins = dict()
user_logouts = dict()

for line in log:
    login = login_pattern.search(line)                  
    if login:
        login_datetime = datetime.strptime(login.group(1), '%b %d %H:%M:%S')
        lid = login_datetime.date()
        lit = login_datetime.time()
        if lid not in user_logins or lit < user_logins[lid]:
            user_logins[lid] = lit
    logout = logout_pattern.search(line)
    if logout:
        logout_datetime = datetime.strptime(logout.group(1), '%b %d %H:%M:%S')
        lod = logout_datetime.date()
        lot = logout_datetime.time()
        if lod not in user_logouts or lot > user_logouts[lod]:
            user_logouts[lod] = lot

log.close()

for ld, lt in user_logins.iteritems():
    print "{date} - {time}".format(date=ld.strftime('%b %d'), time=lt.strftime('%H:%M:%S'))

for ld, lt in user_logouts.iteritems():
    print "{date} - {time}".format(date=ld.strftime('%b %d'), time=lt.strftime('%H:%M:%S'))

