
mkdir -p ../../data

kinit teste.neuro
klist

echo ""
echo "Attempting to download users database..."

dapsearch -l 2 -H ldap://champalimaud.pt -b ou=UsersNeurociencias,dc=champalimaud,dc=pt > ../../data/users.ldif
kdestroy
