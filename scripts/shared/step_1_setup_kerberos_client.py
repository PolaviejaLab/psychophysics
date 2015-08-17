#
# This script sets up Kerberos on the client and joins
# the active directory domain to obtain a keytab file.
#

import sys
sys.path.append("..")

from config import config
from template import Template

import os

print "Installing Kerberos client configuration"

template = Template("../../config/shared/krb5.conf")
template.replace(config)
template.write("/etc/krb5.conf")

template = Template("../../config/shared/ad.conf")
template.replace(config)
template.write("/etc/ad.conf")

print "Joining system to Active Directory domain"

os.system("net ads join -s /etc/ad.conf -U " + config['AD_USERNAME'])
