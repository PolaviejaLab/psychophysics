
KERBEROS_HOSTNAME="kerberos"
LDAP_HOSTNAME="ldap"
DOMAIN="psychophysics"
REALM="PSYCHOPHYSICS"

function get_ip()
{
  ifconfig | grep eth0 -A 1 | grep inet | cut -f 2 -d\: | cut -f 1 -d \  #
}

KRB5_CONFIG=/etc/krb5.conf
KRB5_KDC_PROFILE=/etc/krb5kdc/kdc.conf

IP=$(get_ip)

cat <<EOF > /etc/hosts
127.0.0.1 localhost

::1 localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

$IP $KERBEROS_HOSTNAME.$DOMAIN $KERBEROS_HOSTNAME
EOF

apt-get install krb5-{admin-server,kdc,user}

/etc/init.d/krb5-admin-server stop
/etc/init.d/krb5-kdc stop

rm /var/lib/krb5kdc/*

mkdir -p /var/log/kerberos
touch /var/log/kerberos/{krb5kdc,kadmin,krb5lib}.log
chmod -R 750 /var/log/kerberos

cat <<EOF > /etc/krb5.conf
[libdefaults]
  default_realm = $REALM

  krb4_config = /etc/krb.conf
  krb4_realms = /etc/krb.realms
  kdc_timesync = 1
  ccache_type = 4
  forwardable = true
  proxiable = true

[realms]
  CHAMPALIMAUD.PT = {
    kdc = champalimaud.pt
  }

  $REALM = {
    kdc = $KERBEROS_HOSTNAME
    admin_server = $KERBEROS_HOSTNAME
    default_domain = $DOMAIN
  }

[domain_realm]
  .CHAMPALIMAUD.PT = CHAMPALIMAUD.PT
  .$DOMAIN = $REALM

[login]
  krb4_convert = true
  krb4_get_tickets = false

[logging]
  kdc = FILE:/var/log/kerberos/krb5kdc.log
  admin_server = FILE:/var/log/kerberos/kadmin.log
  default = FILE:/var/log/kerberos/krb5lib.log
EOF

echo "*/admin *" > /etc/krb5kdc/kadm5.acl

cat <<EOF > /etc/krb5kdc/kdc.conf
[kdcdefaults]
  kdc_ports = 750,88

[logging]
  kdc = FILE:/var/log/kerberos/krb5kdc.log
  admin_server = FILE:/var/log/kerberos/kadmin.log
  default = FILE:/var/log/kerberos/krb5lib.log

[realms]
  $REALM = {
    database_name = /var/lib/krb5kdc/principal
    admin_keytab = FILE:/etc/krb5kdc/kadm5.keytab
    acl_file = /etc/krb5kdc/kadm5.acl
    key_stash_file = /etc/krb5kdc/stash
    kdc_ports = 750,88
    max_life = 10h 0m 0s
    max_renewable_life = 7d 0h 0m 0s
    master_key_type = des3-hmac-sha1
    supported_enctypes = aes256-cts:normal arcfour-hmac:normal des3-hmac-sha1:normal des-cbc-crc:normal des:normal des:v4 des:norealm des:onlyrealm des:afs3
    default_principal_flags = +preauth
  }
EOF

krb5_newrealm

/etc/init.d/krb5-admin-server start
/etc/init.d/krb5-kdc start

kadmin.local -q "add_policy -minlength 8 -minclasses 3 admin"
kadmin.local -q "add_policy -minlength 8 -minclasses 4 host"
kadmin.local -q "add_policy -minlength 8 -minclasses 4 service"
kadmin.local -q "add_policy -minlength 8 -minclasses 2 user"
kadmin.local -q "addprinc -policy admin root/admin"

kadmin.local -q "addprinc -policy user ivar.clemens"
kadmin.local -q "addprinc -policy host -randkey host/$KERBEROS_HOSTNAME.$DOMAIN"
kadmin.local -q "addprinc -policy host -randkey host/$LDAP_HOSTNAME.$DOMAIN"
kadmin.local -q "addprinc -policy host -randkey ldap/$KERBEROS_HOSTNAME.$DOMAIN"

kadmin.local -q "ktadd -k /etc/krb5.keytab -norandkey host/$KERBEROS_HOSTNAME.$DOMAIN"
kadmin.local -q "ktadd -k /etc/krb5.keytab -norandkey host/$LDAP_HOSTNAME.$DOMAIN"
kadmin.local -q "ktadd -k /etc/krb5.keytab -norandkey ldap/$KERBEROS_HOSTNAME.$DOMAIN"

chmod 644 /etc/krb5.keytab
