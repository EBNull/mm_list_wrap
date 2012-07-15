#!/usr/bin/env python
import os
import sys
import subprocess
if len(sys.argv) < 2:
    sys.stderr.write("%s listname@domain.com\n"%(sys.argv[0]))
    sys.exit(1)

list_email = sys.argv[1]

list_name, _, domain = list_email.partition('@')

assert domain, "You need to specify the full list email address"

p = subprocess.Popen(['rmlist', '-a', list_name], stdout=subprocess.PIPE)
p.communicate()
subprocess.check_call(['pf_alias_mgr.py', 'rm-mm', list_name, domain])
