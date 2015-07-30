
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

