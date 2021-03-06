
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m"

function get_schemas()
{
	# Create list of schemas
	ldapsearch -Q -LLL -Y EXTERNAL -H ldapi:/// -b cn=schema,cn=config cn | grep cn: | grep \{ | cut -f 2 -d \}
}


function has_schema()
{
	local schemas=$(get_schemas)

	if [[ $schemas =~ $1 ]]; then
		return 0
	else
		return 1
	fi
}


for schema in core cosine nis inetorgperson misc kerberos samba apple
do
	if has_schema $schema; then
		echo -e ${GREEN}Skipping schema: $schema, already present${NC}
		continue
	fi

	echo -e ${BLUE}Inserting schema: $schema${NC}
	ldapadd -Q -Y EXTERNAL -H ldapi:/// -f ../../config/plab-ldap/schema/$schema.ldif

	if ! has_schema $schema; then
		echo -e "${RED}Failed to install schema: $schema${NC}"
		exit
	fi
done
