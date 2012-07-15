#!/usr/bin/env python
import os
import sys
import re
import MySQLdb
import datetime


def get_db_from_file():
    dbdata = {}
    with open("/etc/postfix/mysql/virtual_alias_maps.cf", "r") as f:
        for line in f.readlines():
            m = re.match(r"(.*?) *= *(.*)", line)
            if m:
                dbdata[m.groups()[0]] = m.groups()[1]
    return dbdata


def showalias(c):
    c.execute("SELECT * FROM alias")
    for i in c.fetchall():
        print i

def build_insert(tbl, newdata):
    names = []
    val_qs = []
    vals = []
    for k, v in newdata.iteritems():
        names.append(k)
        val_qs.append('%s')
        vals.append(v)
    ret = "INSERT INTO %s (%s) VALUES (%s)"%(tbl, ','.join(names), ','.join(val_qs))
    return (ret, vals)

def addalias(c, newdata):
    stmt, vals = build_insert('alias', newdata)
    c.execute(stmt, vals)

def rmalias(c, addr):
    c.execute('DELETE FROM alias WHERE address = %s', [addr])

def main(argv):
    dbdata = get_db_from_file()

    import MySQLdb
    db = MySQLdb.connect(user=dbdata['user'], passwd=dbdata['password'], db=dbdata['dbname'])
    c = db.cursor()
    if len(argv) < 2:
        return showalias(c)
    if argv[1] == 'show':
        return showalias(c)
    if argv[1] == 'add':
        now = datetime.datetime.now()
        new = {
            'address': argv[2],
            'goto': argv[3],
            'name': '',
            'moderators': '',
            'accesspolicy': 'public',
            'domain': argv[2].partition('@')[2],
            'created': now,
            'modified': now,
            'active': 1
        }
        addalias(c, new)
        c.execute('COMMIT;')
        return
    if argv[1] == 'add-mm':
        now = datetime.datetime.now()
        prefix = argv[2]
        domain_from = argv[3]
        domain_to = argv[4]
        for name in ['%s', '%s-admin', '%s-bounces', '%s-confirm', '%s-join', '%s-leave', '%s-owner', '%s-request', '%s-subscribe', '%s-unsubscribe']:
            name = name%(prefix)
            new = {
                'address': '%s@%s'%(name,domain_from),
                'goto': '%s@%s'%(name,domain_to),
                'name': '',
                'moderators': '',
                'accesspolicy': 'public',
                'domain': domain_from,
                'created': now,
                'modified': now,
                'active': 1
            }
            addalias(c, new)
        c.execute('COMMIT;')
        return

    if argv[1] == 'rm-mm':
        now = datetime.datetime.now()
        prefix = argv[2]
        domain = argv[3]
        for name in ['%s', '%s-admin', '%s-bounces', '%s-confirm', '%s-join', '%s-leave', '%s-owner', '%s-request', '%s-subscribe', '%s-unsubscribe']:
            name = name%(prefix)
            rmalias(c, '%s@%s'%(name, domain))
        c.execute('COMMIT;')
        return

    if argv[1] == 'rm':
        addr = argv[2]
        rmalias(c, addr)
        c.execute('COMMIT;')
        return
    sys.stderr.write("Unknown command (use one of 'show', 'add', 'rm', 'add-mm', 'rm-mm')\n")

if __name__ == '__main__':
    sys.exit(main(sys.argv))
