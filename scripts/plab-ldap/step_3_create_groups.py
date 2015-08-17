#
# Creates user and admin groups
#

import sys
sys.path.append("..")

from config import config
from template import Template
from ldap_utils import init_ldap, insert_ldif, add_to_group, find_user, find_group

import uuid

l = init_ldap(config)

group = {}
group['GROUP_NAME'] = 'admin'
group['GROUP_ID'] = '1000'
group['GROUP_LONGNAME'] = 'Administrators'
group['GROUP_UID'] = str(uuid.uuid4())

t = Template("../../config/plab-ldap/templates/group.ldif")
t.replace(config)
t.replace(group)
insert_ldif(l, str(t))


group = {}
group['GROUP_NAME'] = 'user'
group['GROUP_ID'] = '1001'
group['GROUP_LONGNAME'] = 'Users'
group['GROUP_UID'] = str(uuid.uuid4())

t = Template("../../config/plab-ldap/templates/group.ldif")
t.replace(config)
t.replace(group)
insert_ldif(l, str(t))
