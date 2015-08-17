import StringIO
import ldif
import ldap


def init_ldap(config):
    # Connect to LDAP server
    l = ldap.initialize('ldap://localhost')
    try:
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(config['ADMIN_USERNAME'], config['ADMIN_PASSWORD'])
    except ldap.INVALID_CREDENTIALS:
        print "Username / password is incorrect."
        sys.exit(0)
    return l


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
        try:
            result_id = ldap_server.search(record[0], ldap.SCOPE_BASE)
            result_type, result_data = ldap_server.result(result_id)
        except:
            result_data = None

        # Record not found, insert
        if result_data == [] or result_data is None:
            print "Adding {}".format(record[0])
            ldap_server.add_s(record[0], record[1].items())
            continue

        # Get list of modifications from old to new
        modlist = build_modlist(result_data[0][1], record[1])

        # Not changed, continue
        if len(modlist) == 0:
            skipped += 1
            continue

        print modlist

        # Save changes to server
        print "Updating {}".format(record[0])
        ldap_server.modify_s(record[0], modlist)

    print "Updated {} of {} records".format(total - skipped, total)


def find_user(ldap_server, config, name):
    try:
        result_id = ldap_server.search("uid=" + name + ", ou=users, " + config['ROOT_DN'], ldap.SCOPE_BASE)
        result_type, result_data = ldap_server.result(result_id)
    except:
        return None

    if result_data == []:
        return None

    return result_data[0][1]


def find_group(ldap_server, config, name):
    result_id = ldap_server.search("cn=" + name + ", ou=groups, " + config['ROOT_DN'], ldap.SCOPE_BASE)
    result_type, result_data = ldap_server.result(result_id)

    if result_data == []:
        return None

    return result_data[0][1]


def find_group_by_gid(ldap_server, config, gid):
    result_id = ldap_server.search("ou=groups, " + config['ROOT_DN'], ldap.SCOPE_ONELEVEL, "gidNumber=" + gid, [])
    result_type, result_data = ldap_server.result(result_id)

    if result_data == []:
        return None

    return result_data[0][1]


def add_to_group(l, config, username, groupname):
    user = find_user(l, config, username)
    group = find_group(l, config, groupname)

    if user == []:
        raise Exception("Invalid user: " + username)
    if group == []:
        raise Exception("Invalid group: " + groupname)

    dn = "cn={}, ou=groups, {}\n".format(group['cn'][0], config['ROOT_DN'])

    if not user['uid'][0] in group['memberUid']:
        modlist = [(ldap.MOD_ADD, "memberUid", user['uid'][0])]
        l.modify_s(dn, modlist)

    apple_uid = user['apple-generateduid'][0]
    if not apple_uid in group['apple-group-memberguid']:
        modlist = [(ldap.MOD_ADD, "apple-group-memberguid", apple_uid)]
        l.modify_s(dn, modlist)
