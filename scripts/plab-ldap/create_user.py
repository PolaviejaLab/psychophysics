#
# This script creates an LDAP user, the specifics are currently hardcoded
#

from config import config
from template import Template
from ldap_utils import init_ldap, insert_ldif, add_to_group, find_user, find_group

import sha
import StringIO
import ldif
import ldap
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

l = init_ldap(config)

user = {}
user['USER_NAME'] = 'ivar.clemens'
user['USER_GIVENNAME'] = 'Ivar'
user['USER_SURNAME'] = 'Clemens'
user['USER_FULLNAME'] = user['USER_GIVENNAME'] + " " + user['USER_SURNAME']
user['USER_GROUP_NAME'] = 'admin'
user['USER_PASSWORD'] = '{SASL} ivar.clemens'
user['USER_TITLE'] = 'None'
user['USER_HOME'] = '/home/' + user['USER_NAME']

old_user = find_user(l, config, user['USER_NAME'])

if old_user is None:
    user['USER_ID'] = '1000'
    user['USER_UID'] = str(uuid.uuid4())
else:
    user['USER_ID'] = old_user['uidNumber'][0]
    user['USER_UID'] = old_user['apple-generateduid'][0]

group = find_group(l, config, user['USER_GROUP_NAME'])
user['USER_GROUP_ID'] = group['gidNumber'][0]

user['USER_PASSWORD_HASH'] = "{KERBEROS} " + user['USER_NAME']
 #hash_password(user['USER_PASSWORD'])

t = Template("user.ldif")
t.replace(config)
t.replace(user)
insert_ldif(l, str(t))

add_to_group(l, config, user['USER_NAME'], user['USER_GROUP_NAME'])

# Get user and show details
group = find_group(l, config, user['USER_GROUP_NAME'])
user = find_user(l, config, user['USER_NAME'])

pp = pprint.PrettyPrinter(indent = 4)

print "User added:"
pp.pprint(user)
pp.pprint(group)

l.unbind_s()
