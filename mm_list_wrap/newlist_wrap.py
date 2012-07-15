#!/usr/bin/env python
import os
import sys
import subprocess
if len(sys.argv) < 2:
    sys.stderr.write("%s listname@domain.com lists.domain.com admin@email.com admin_pw\n"%(sys.argv[0]))
    sys.exit(1)

list_email = sys.argv[1]
redir_domain = sys.argv[2]
admin_email = sys.argv[3]
admin_pw = sys.argv[4]

list_name, _, domain = list_email.partition('@')

p = subprocess.Popen(['newlist', '-q', list_name, admin_email, admin_pw, '--emailhost=%s'%(domain)], stdout=subprocess.PIPE)
p.communicate()
subprocess.check_call(['pf_alias_mgr.py', 'add-mm', list_name, domain, redir_domain])
