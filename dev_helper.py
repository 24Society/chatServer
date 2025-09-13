from os import listdir

tmp_dict = {}


def to_dict(s: str) -> dict:
    cmd = 'global tmp_dict\ntmp_dict='
    if not s.startswith('{'):
        cmd += '{'
    cmd += s
    if not s.endswith('}'):
        cmd += '}'
    exec(cmd)
    return tmp_dict


def to_str(**config):
    t = ''
    for i in config.keys():
        if type(config[i]) is str:
            t += f"'{i}':'{config[i]}',\n"
        else:
            t += f"'{i}':{config[i]},\n"
    return t[:-1]


def update_default(c_type):
    if c_type == 'user':
        default_user = open("userData\\default", "r").read()
        for usr in listdir('userData'):
            if not usr.endswith('.usr'):
                continue
            tmp = to_dict(default_user)
            tmp1 = to_dict(open(f"userData\\{usr}").read())
            for i in tmp1.keys():
                tmp[i] = tmp1[i]
            open(f'userData\\{usr}', 'w').write(to_str(**tmp))
    elif c_type == 'group':
        default_group = open('groups\\default', 'r').read()
        for grp in listdir('groups'):
            if not grp.endswith('.dat'):
                continue
            tmp = to_dict(default_group)
            tmp1 = to_dict(open(f'groups\\{grp}').read())
            for i in tmp1.keys():
                tmp[i] = tmp1[i]
            open(f'groups\\{grp}', 'w').write(to_str(**tmp))
    elif c_type == 'votes':
        default_votes = open('votes\\default', 'r').read()
        for vote in listdir('votes'):
            if not vote.endswith('.vot'):
                continue
            tmp = to_dict(default_votes)
            tmp1 = to_dict(open(f'votes\\{vote}').read())
            for i in tmp1.keys():
                tmp[i] = tmp1[i]
            open(f'votes\\{vote}', 'w').write(to_str(**tmp))


def get_color(r, g, b):
    return f'#{hex(r)[2:].rjust(2, '2')}{hex(g)[2:].rjust(2, '2')}{hex(b)[2:].rjust(2, '2')}'.upper()


if __name__ == '__main__':
    update_default('votes')
