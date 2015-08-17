#
# This script creates the users and groups OUs in your LDAP database.
#

import sys
sys.path.append("..")

from config import config
from template import Template
from ldap_utils import init_ldap, insert_ldif

import ldap
import base64

l = init_ldap(config)

# Build odconfig for Mac
t = Template("../../config/plab-ldap/odconfig")
t.replace({'HOMEDIRECTORY': '#/Users/$uid$'})
t.replace(config)
odconfig = base64.b64encode(str(t).replace('\n', ''))

for item in ["ou=groups.ldif", "ou=users.ldif", "ou=macosx.ldif"]:
    t = Template("../../config/plab-ldap/" + item)
    t.replace(config)
    t.replace({"ODCONFIG": odconfig})
    insert_ldif(l, str(t))

l.unbind_s()
