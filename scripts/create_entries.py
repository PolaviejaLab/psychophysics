
from config import config
from template import Template

import StringIO
import base64
import ldap
import ldif


def build_modlist(old, new):
    # Find keys that exist in both
    intersect = [item for item in new.keys() if old.has_key(item)]

    # Add keys that only exist in new
    add = [item for item in new.keys() if not item in intersect]

    # Remove keys that only exist in old
    remove = [item for item in old.keys() if not item in intersect]

    # Modify only if value is different
    modify = [item for item in intersect if old[item] != new[item]]

    modlist = []

    for item in add:
        modlist.append((ldap.MOD_ADD, item, new[item]))
    for item in modify:
        modlist.append((ldap.MOD_REPLACE, item, new[item]))
    for item in remove:
        modlist.append((ldap.MOD_DELETE, item, old[item]))

    return modlist


def insert_ldif(ldap_server, ldif_string):
    ldif_parser = ldif.LDIFRecordList(StringIO.StringIO(ldif_string))
    ldif_parser.parse()

    total = len(ldif_parser.all_records)
    skipped = 0

    for record in ldif_parser.all_records:
        # Find record
        result_id = ldap_server.search(record[0], ldap.SCOPE_BASE)
        result_type, result_data = ldap_server.result(result_id)

        # Record not found, insert
        if result_data == []:
            print "Adding {}".format(record[0])
            l.add_s(record[0], record[1].items())
            continue

        # Get list of modifications from old to new
        modlist = build_modlist(record[1], result_data[0][1])

        # Not changed, continue
        if len(modlist) == 0:
            skipped += 1
            continue

        # Save changes to server
        print "Updating {}".format(record[0])
        l.modify_s(record[0], modlist)

    print "Updated {} of {} records".format(total - skipped, total)


# Connect to LDAP server
l = ldap.initialize('ldap://localhost')
try:
    l.protocol_version = ldap.VERSION3
    l.simple_bind_s(config['ADMIN_USERNAME'], config['ADMIN_PASSWORD'])
except ldap.INVALID_CREDENTIALS:
    print "Username / password is incorrect."
    sys.exit(0)


# Build odconfig for Mac
t = Template("odconfig")
t.replace(config)
odconfig = base64.b64encode(str(t).replace('\n', ''))


for item in ["ou=groups.ldif", "ou=users.ldif", "ou=macosx.ldif"]:
    t = Template(item)
    t.replace(config)
    t.replace({"ODCONFIG": odconfig})
    insert_ldif(l, str(t))


l.unbind_s()
