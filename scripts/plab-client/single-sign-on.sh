
# Main packages
apt-get install ldap-auth-client libpam-krb5 krb5-user libpam-foreground libsasl2-modules-gssapi-mit ldap-utils

# Cached credentials
apt-get install nss-updatedb libnss-db libpam-cracklib libpam-ccreds

cat <<EOF > /etc/ldap/ldap.conf
BASE		dc=plab-ldap,dc=champalimaud,dc=pt
URI		ldap://plab-ldap.champalimaud.pt

TLS_CACERT      /etc/ssl/certs/ca-certificates.crt
TLS_REQCERT	allow
EOF


cat << EOF > /etc/ldap.conf
bind_policy soft
EOF


cat << EOF > /etc/auth-client-config/profile.d/krb-auth-config
[krb5ldap]
nss_passwd=passwd: files ldap
nss_group=group: files ldap
nss_shadow=shadow: files ldap
nss_netgroup=netgroup: files ldap

pam_auth=auth sufficient pam_krb5.so
	 auth required pam_unix.so nullok_secure use_first_pass

pam_account=account sufficient pam_krb5.so
	    account required pam_unix.so

pam_password=password sufficient pam_krb5.so
	     password required pam_unix.so nullok obscure min=4 max=8 md5

pam_session=session required pam_unix.so
 	    session required pam_mkhomedir.so skel=/etc/skel
	    session optional pam_krb5.so
	    session optional pam_foreground.so

[krb5ldap.cached]
nss_passwd=passwd: files ldap [NOTFOUND=return] db
nss_group=group: files ldap [NOTFOUND=return] db
nss_shadow=shadow: files ldap
nss_netgroup=netgroup: files ldap

pam_auth=auth required 		pam_env.so
	 auth sufficient 	pam_unix.so likeauth nullok
	 auth [default=ignore success=1 service_err=reset] pam_krb5.so use_first_pass
	 auth [default=die success=done] pam_ccreds.so action=validate use_first_pass
	 auth sufficient	pam_ccreds.so action=store use_first_pass
	 auth required		pam_deny.so

pam_account=account sufficient	pam_krb5.so
	    account required    pam_unix.so

pam_password=password sufficient pam_krb5.so
             password required pam_unix.so nullok obscure min=4 max=8 md5

pam_session=session required pam_unix.so
            session required pam_mkhomedir.so skel=/etc/skel
            session optional pam_krb5.so
            session optional pam_foreground.so
EOF

nss_updatedb ldap
auth-client-config -a -p krb5ldap.cached
