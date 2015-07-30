
source config.sh

GREEN="\033[0;32m"
RED="\033[0;31m"
NC="\033[0m"

ADMIN_PASS_HASH=$(slappasswd -h {SSHA} -s $ADMIN_PASS)

cat <<EOF > password-change.ldif
dn: olcDatabase={1}mdb,cn=config
replace: olcRootPW
olcRootPW: $ADMIN_PASS_HASH
EOF


# Create list of schemas
schemas=$(ldapsearch -Q -LLL -Y EXTERNAL -H ldapi:/// -b cn=schema,cn=config cn | grep cn: | grep \{ | cut -f 2 -d \})

echo -e ${RED}Changing password${NC}
ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f password-change.ldif

for schema in core cosine nis inetorgperson misc kerberos samba apple
do
	if [[ $schemas =~ $schema ]]; then
		echo -e ${GREEN}Skipping schema: $schema, already present${NC}
		continue
	fi

	echo -e ${RED}Inserting schema: $schema${NC}
	ldapadd -Q -Y EXTERNAL -H ldapi:/// -f ../schema/$schema.ldif
done

#ldapadd -x -H ldap://$SERVER -D "cn=config" -w $ADMIN_PASS -f ../schema/misc.ldif

