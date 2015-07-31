
config = dict()
config['SERVER'] = 'psychophysics'
config['ROOT_DN'] = 'dc=psychophysics'

config['ADMIN_USERNAME'] = "cn=admin," + config['ROOT_DN']
config['ADMIN_PASSWORD'] = 'password'
