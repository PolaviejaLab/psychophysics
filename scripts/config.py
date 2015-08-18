
config = dict()
config['SERVER'] = 'plab-ldap'
config['ROOT_DN'] = 'dc=plab-ldap,dc=champalimaud,dc=pt'

config['ADMIN_USERNAME'] = "cn=admin," + config['ROOT_DN']
config['ADMIN_PASSWORD'] = 'jooChoo9'

config['AD_USERNAME'] = "teste.neuro"
