
source common.sh
source config.sh

for schema in core cosine nis inetorgperson misc kerberos samba apple
do
	if has_schema $schema; then
		echo -e ${GREEN}Skipping schema: $schema, already present${NC}
		continue
	fi

	echo -e ${BLUE}Inserting schema: $schema${NC}
	ldapadd -Q -Y EXTERNAL -H ldapi:/// -f ../schema/$schema.ldif

	if ! has_schema $schema; then 
		echo -e "${RED}Failed to install schema: $schema"
		exit
	fi
done

