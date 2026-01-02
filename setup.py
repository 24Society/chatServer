from os import makedirs, path

makedirs('files\\public', exist_ok=True)
makedirs('groups', exist_ok=True)
makedirs('userData', exist_ok=True)
makedirs('votes', exist_ok=True)
open('groups\\default', 'w').write(''''created_date':'2025-08-13',
'members':[],
'pwd':'',''')
open('groups\\public.dat', 'w').write(''''created_date':'2025-08-13',
'members':'all',
'pwd':'',''')
open('groups\\public.grp', 'w').write('')
open('userData\\default', 'w').write(''''username':'guest',
'pwd':'',
'user_type':'guest',
'remember_me':False,
'show_uid':True,
'create_group':0,''')
open('votes\\default', 'w').write(''''title':'',
'start_time':0,
'For':[],
'against':[],
'last_result':[],''')
if not path.exists('encrypt.py'):
    open('encrypt.py', 'w').write('''def encrypt(orig, ext):
    return orig+ext
''')
