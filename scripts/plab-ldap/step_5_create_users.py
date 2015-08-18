import sys
sys.path.append("..")

from config import config
from template import Template
from ldap_utils import init_ldap, insert_ldif, add_to_group, find_user, find_group

import sha
import StringIO
import ldif
import ldap
import ldap.sasl
import base64
import uuid
import os
import hashlib
import pprint

def hash_password(password):
    salt = os.urandom(4)
    h = hashlib.sha1(password)
    h.update(salt)
    return "{SSHA}" + base64.b64encode(h.digest() + salt).replace("\n", "")


def get_free_user_id(ldap_server):
    result_id = ldap_server.search("ou=users, " + config['ROOT_DN'], ldap.SCOPE_ONELEVEL)
    result_type, result_data = ldap_server.result(result_id)

    next_number = 1000

    for result in result_data:
        current_number = int(result[1]['uidNumber'][0])
        if(current_number >= next_number):
            next_number = current_number + 1

    return next_number


def create_user(ldap_server, user):
    old_user = find_user(ldap_server, config, user['USER_NAME'])

    if old_user is None:
        user['USER_ID'] = str(get_free_user_id(ldap_server))
        user['USER_UID'] = str(uuid.uuid4())
    else:
        user['USER_ID'] = old_user['uidNumber'][0]
        user['USER_UID'] = old_user['apple-generateduid'][0]

    group = find_group(l, config, user['USER_GROUP_NAME'])
    user['USER_GROUP_ID'] = group['gidNumber'][0]

    user['USER_PASSWORD_HASH'] = "{KERBEROS} " + user['USER_NAME']

    t = Template("../../config/plab-ldap/templates/user.ldif")
    t.replace(config)
    t.replace(user)
    insert_ldif(ldap_server, str(t))

    add_to_group(ldap_server, config, user['USER_NAME'], user['USER_GROUP_NAME'])

    # Get user and show details
    group = find_group(ldap_server, config, user['USER_GROUP_NAME'])
    user = find_user(ldap_server, config, user['USER_NAME'])

    pp = pprint.PrettyPrinter(indent = 4)

    print "Added user (" + user['uid'][0] + ") with id (" + str(user['uidNumber']) + ")"


l = init_ldap(config)

# Read list of users
users_file = open("../../data/users.ldif")
users_ldif = users_file.read()

ldif_parser = ldif.LDIFRecordList(StringIO.StringIO(users_ldif))
ldif_parser.parse()

admins = ['ivar.clemens', 'eric.dewitt', 'nico.bonacchi']

for record in ldif_parser.all_records:
    if not 'objectClass' in record[1]:
        continue

    classes = record[1]['objectClass']

    if not 'person' in classes:
        continue

    if not 'sn' in record[1] or not 'givenName' in record[1]:
        print "Details missing for user " + record[0]
        continue

    try:
        user = {}

        user['USER_GIVENNAME'] = record[1]['givenName'][0]
        user['USER_SURNAME'] = record[1]['sn'][0]

        if 'userPrincipalName' in record[1]:
            user['USER_NAME'] = record[1]['userPrincipalName'][0].split('@')[0]
        else:
            user['USER_NAME'] = user['USER_GIVENNAME'].lower() + "." + user['USER_SURNAME'].lower()

        user['USER_FULLNAME'] = record[1]['displayName'][0]

        if user['USER_NAME'] in admins:
            user['USER_GROUP_NAME'] = 'admin'
        else:
            user['USER_GROUP_NAME'] = 'user'

            user['USER_TITLE'] = 'None'
            user['USER_HOME'] = '/home/' + user['USER_NAME']
    except:
        print "There was a problem parsing user " + record[0]
        pp = pprint.PrettyPrinter(indent = 4)
        pp.pprint(record[1])
        continue

    create_user(l, user)

l.unbind_s()
