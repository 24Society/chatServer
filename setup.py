from os import makedirs, path

dirs = ['files\\public', 'groups', 'userData', 'votes']
default = {
    'groups\\default': ''''created_date':'2025-08-13',
'members':[],
'pwd':'',''',
    'groups\\public.dat': ''''created_date':'2025-08-13',
'members':'all',
'pwd':'',''',
    'groups\\public.grp': '',
    'userData\\default': ''''username':'guest',
'pwd':'',
'user_type':'guest',
'remember_me':False,
'show_uid':True,
'create_group':0,''',
    'votes\\default': ''''title':'',
'start_time':0,
'For':[],
'against':[],
'last_result':[],''',
    'votes\\public.vot': ''''title':'',
'start_time':0,
'For':[],
'against':[],
'last_result':[],''',
}

for d in dirs:
    makedirs(d, exist_ok=True)
for file, content in default:
    if not path.exists(file):
        open(file, 'w').write(content)
if not path.exists('encrypt.py'):
    open('encrypt.py', 'w').write('''def encrypt(orig, ext):
    return orig+ext
''')
