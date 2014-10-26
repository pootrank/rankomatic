#! /usr/bin/env python

"""A script to get and start up mongodb from the heroku config variable.
Make sure you call it from the root directory of the app."""

import subprocess
import os
import re

heroku_command = "heroku config:get MONGOHQ_URL"
proc = subprocess.Popen(heroku_command.split(), stdout=subprocess.PIPE)
url = proc.communicate()[0]
pattern = 'mongodb://(.*?):(.*?)@(.*?):(\d*)/(.*)'
m = re.match(pattern, url)
keys = ['username', 'password', 'host', 'port', 'database']
vals = [m.group(i) for i in xrange(1, 6)]
args = dict(zip(keys, vals))
mongo_command = "mongo -u {username} -p {password} --host {host} --port {port} {database}".format(**args)
os.system(mongo_command)


