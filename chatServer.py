import threading
from datetime import datetime
from os import remove
from random import randint as rd
from socket import socket, SOL_SOCKET, SO_SNDBUF, AF_INET, SOCK_STREAM
from time import time
from typing import Any

from dev_helper import *
from encrypt import *

minCompatibleClient = to_dict(open('minCompatibleClient.dat').read())
latestClient = to_dict(open('latestClient.dat').read())
default_user = open("userData\\default", "r").read()


class User:
    uid: int
    data: dict[str, Any]
    orig_pwd: str
    user_socket: socket | None

    def __init__(self, uid: int = 0, usr_data: str = to_str(username='guest', pwd='1', user_type='guest',
                                                            remember_me=False, show_uid=True, create_group=0,
                                                            voted=False),
                 user_socket: socket | None = None):
        tmp = to_dict(default_user)
        tmp1 = to_dict(usr_data)
        for i in tmp1.keys():
            tmp[i] = tmp1[i]
        self.uid = uid
        self.data = tmp
        self.orig_pwd = ''
        self.user_socket = user_socket
        self.in_game = 0

    def rename(self, new_name):
        new_pwd = encrypt(self.orig_pwd, new_name)
        orig_data = open(f'userData\\{self.uid}.usr', 'r').read()
        updated_data = orig_data.replace(f"'username':'{self.data['username']}'", f"'username':'{new_name}'")
        updated_data = updated_data.replace(f"'pwd':'{self.data['pwd']}'", f"'pwd':'{new_pwd}'")
        with open(f'userData\\{self.uid}.usr', 'w') as f:
            f.write(updated_data)
        self.data['username'] = new_name
        self.data['pwd'] = new_pwd

    def set_pw(self, new_pwd):
        tmp_pwd = encrypt(new_pwd, self.data['username'])
        orig_data = open(f'userData\\{self.uid}.usr', 'r').read()
        updated_data = orig_data.replace(f"'pwd':'{self.data['pwd']}'", f"'pwd':'{tmp_pwd}'")
        with open(f'userData\\{self.uid}.usr', 'w') as f:
            f.write(updated_data)
        self.orig_pwd = new_pwd
        self.data['pwd'] = tmp_pwd

    def set_remember(self):
        orig_data = open(f'userData\\{self.uid}.usr', 'r').read()
        if self.data['remember_me']:
            updated_data = orig_data.replace("'remember_me':True", "'remember_me':False")
        else:
            updated_data = orig_data.replace("'remember_me':False", "'remember_me':True")
        with open(f'userData\\{self.uid}.usr', 'w') as f:
            f.write(updated_data)
        self.data['remember_me'] = not self.data['remember_me']

    def set_show_uid(self):
        orig_data = open(f'userData\\{self.uid}.usr', 'r').read()
        if self.data['show_uid']:
            updated_data = orig_data.replace("'show_uid':True", "'show_uid':False")
        else:
            updated_data = orig_data.replace("'show_uid':False", "'show_uid':True")
        with open(f'userData\\{self.uid}.usr', 'w') as f:
            f.write(updated_data)
        self.data['show_uid'] = not self.data['show_uid']

    def create_group(self):
        orig_data = open(f'userData\\{self.uid}.usr', 'r').read()
        old_cnt = self.data['create_group']
        self.data['create_group'] += 1
        updated_data = orig_data.replace(f"'create_group':{old_cnt}", f"'create_group':{self.data['create_group']}")
        with open(f'userData\\{self.uid}.usr', 'w') as f:
            f.write(updated_data)

    def vote(self):
        orig_data = open(f'userData\\{self.uid}.usr', 'r').read()
        if self.data['voted']:
            updated_data = orig_data.replace("'voted':True", "'voted':False")
        else:
            updated_data = orig_data.replace("'voted':False", "'voted':True")
        open(f'userData\\{self.uid}.usr', 'w').write(updated_data)
        self.data['voted'] = not self.data['voted']

    def __str__(self):
        tmp = to_dict(default_user)
        tmp1 = to_dict(open(f'userData\\{self.uid}.usr', 'r').read())
        for i in tmp1.keys():
            tmp[i] = tmp1[i]
        return str(tmp)


class Vote:
    data: dict[str, Any]
    group: str

    def __init__(self, group):
        self.data = to_dict(open(f'votes\\{group}.vot').read())
        self.group = group

    def start(self, title):
        self.data['title'] = title
        self.data['start_time'] = time()
        orig_data = open(f'votes\\{self.group}.vot').read()
        updated_data = orig_data.replace("'title':''", f"'title':'{title}'")
        updated_data = updated_data.replace("'start_time':0", f"'start_time':{self.data['start_time']}")
        open(f'votes\\{self.group}.vot', 'w').write(updated_data)

    def end(self):
        tmp = self.data['last_result']
        self.data['last_result'] = [self.data['title'], len(self.data['For']), len(self.data['against'])]
        orig_data = open(f'votes\\{self.group}.vot').read()
        updated_data = orig_data.replace(f"'title':'{self.data['title']}'", "'title':''")
        updated_data = updated_data.replace(f"'start_time':{self.data['start_time']}", "'start_time':0")
        updated_data = updated_data.replace(f"'last_result':{tmp}", f"'last_result':{self.data['last_result']}")
        updated_data = updated_data.replace(f"'For':{self.data['For']}", "'For':[]")
        updated_data = updated_data.replace(f"'against':{self.data['against']}", "'against':[]")
        open(f'votes\\{self.group}.vot', 'w').write(updated_data)
        self.data['title'] = ''
        self.data['start_time'] = 0

    def check(self):
        if time() - self.data['start_time'] >= 24 * 3600:
            self.end()
            return True
        return False

    def vote(self, opt, username):
        orig_data = open(f'votes\\{self.group}.vot').read()
        tmp = self.data[opt].copy()
        self.data[opt].append(username)
        updated_data = orig_data.replace(f"'{opt}':{tmp}", f"'{opt}':{self.data[opt]}")
        open(f'votes\\{self.group}.vot', 'w').write(updated_data)


class Group:
    data: dict[str, Any]
    name: str
    votes: Vote

    def __init__(self, group_data='default'):
        self.name = group_data[:-4]
        self.data = to_dict(open(f'groups\\{group_data}').read())
        self.votes = Vote(self.name)

    def add_member(self, username):
        tmp = self.data['members'].copy()
        self.data['members'].append(username)
        orig_data = open(f'groups\\{self.name}.dat').read()
        updated_data = orig_data.replace(f"'members':{tmp}", f"'members':{self.data['members']}")
        open(f'groups\\{self.name}.dat', 'w').write(updated_data)

    def del_member(self, username):
        tmp = self.data['members'].copy()
        self.data['members'].remove(username)
        orig_data = open(f'groups\\{self.name}.dat').read()
        updated_data = orig_data.replace(f"'members':{tmp}", f"'members':{self.data['members']}")
        open(f'groups\\{self.name}.dat', 'w').write(updated_data)

    def start_vote(self, vote_title):
        self.votes.start(vote_title)

    def end_vote(self):
        self.votes.end()

    def check_date(self):
        return self.votes.check()

    def vote(self, opt, usr: User):
        self.votes.vote(opt, usr.data['username'])


class Game:
    players: dict[str, list]
    length: dict[str, int]
    sockets: list[socket]

    def __init__(self):
        self.players = {}
        self.length = {}
        self.apple = []
        self.dot = []
        self.sockets = []

    def get_pos(self):
        success = False
        x = 0
        y = 0
        while not success:
            x = rd(0, 11)
            y = rd(0, 15)
            for i in self.players.keys():
                for j in i[3:]:
                    if x == j[0] and y == j[1]:
                        break
                else:
                    continue
                break
            else:
                success = True
        return [x, y]

    def join(self, usr, p_socket):
        if usr in self.players.keys():
            return 'refused'
        self.sockets.append(p_socket)
        pos = self.get_pos()
        color = get_color(rd(50, 200), rd(50, 200), rd(50, 200))
        self.players[usr] = [color, usr, 0, pos]
        self.length[usr] = 1
        return ' '.join([str(i) for i in pos])

    def __str__(self):
        dot = self.dot[:2]
        dot.append(max(0, (6 - int(time() - self.dot[2]))))
        tmp = {'apple': self.apple, 'dot': dot}
        for i in self.players.keys():
            tmp[f'p_{i}'] = self.players[i]
        return f'info {tmp}'

    def gen_apple(self):
        self.apple = self.get_pos()

    def gen_dot(self):
        pos: list[int | float] = self.get_pos()
        pos.append(time())
        self.dot = pos

    def update(self, usr, nx, ny):
        if 6 - int(time() - self.dot[2]) < 0:
            self.gen_dot()
        if [nx, ny] == self.apple:
            self.players[usr][2] = 1
            self.length[usr] += 1
            self.gen_apple()
        elif [nx, ny] == self.dot[:2]:
            self.players[usr][2] = (6 - int(time() - self.dot[2])) * 3
            self.gen_dot()
        else:
            for i in self.players.keys():
                for j in self.players[i][3:]:
                    if nx == j[0] and ny == j[1]:
                        self.players[usr][0] = 'gameover'
                        break
                else:
                    continue
                break
            self.players[usr][2] = 0
        self.players[usr].insert(3, [nx, ny])
        try:
            self.players[usr].pop(self.length[usr] + 3)
        except IndexError:
            pass

    def remove(self, usr):
        self.players.pop(usr)
        self.length.pop(usr)


userList: list[User] = []
for u in listdir('userData'):
    if u.endswith('.usr'):
        userList.append(User(int(u[:-4]), open(f'userData\\{u}', 'r').read()))

groupList: dict[str, Group] = {}
for g in listdir('groups'):
    if g.endswith('.dat'):
        tmp_name = g[:-4]
        groupList[tmp_name] = Group(g)

gameList: list[Game] = [Game()]
for gg in range(1, 10):
    gameList.append(Game())
    gameList[gg].gen_apple()
    gameList[gg].gen_dot()


def broadcast(message, group):
    member = groupList[group].data['members']
    public = False
    if member == 'all':
        public = True
        member = []
    for i in userList:
        if (i.data['username'] in member or public) and i.user_socket is not None:
            client = i.user_socket
            try:
                client.send((f"message " + message).encode('utf-8'))
            except ConnectionResetError:
                i.user_socket = None
                client.close()
                client_sockets.remove(client)


def recv_f(_client_socket):
    recv = _client_socket.recv(1024).decode("utf-8")
    try:
        tmp = to_dict(recv)
        return tmp
    except SyntaxError:
        _client_socket.close()
        client_sockets.remove(_client_socket)
        return {}


def handle_client(_client_socket, _addr):
    _client_socket.setsockopt(SOL_SOCKET, SO_SNDBUF, 1024)
    now = User()
    print(f"[新连接] {_addr}")
    recv = _client_socket.recv(1024).decode("utf-8")
    client_data = to_dict(recv)
    if client_data['ver'] < minCompatibleClient['ver']:
        _client_socket.send(
            f'refused 版本{client_data['ver']}过旧\n请至少更新到{minCompatibleClient['ver']}'.encode('utf-8'))
    else:
        _client_socket.send('ok'.encode('utf-8'))
    while True:
        try:
            message = recv_f(_client_socket)
            if now.data['user_type'] != 'player':
                if message['cmd'] == 'log':
                    for i in userList:
                        if i.data['username'] == message['opt'][0]:
                            if not i.data['remember_me']:
                                if message['opt'][1] == '':
                                    _client_socket.send('refused 密码不能为空'.encode('utf-8'))
                                    break
                                elif encrypt(message['opt'][1], message['opt'][0]) != i.data['pwd']:
                                    _client_socket.send('refused 用户名或密码错误'.encode('utf-8'))
                                    break
                            if i.user_socket is not None:
                                _client_socket.send('refused 此用户已在某处登录'.encode('utf-8'))
                                break
                            i.user_socket = _client_socket
                            now = i
                            now.orig_pwd = message['opt'][1]
                            _client_socket.send(('ok ' + str(now)).encode('utf-8'))
                            break
                    else:
                        _client_socket.send('refused 用户名或密码错误'.encode('utf-8'))
                    continue
                if message['cmd'] == 'reg':
                    if len(message['opt'][0]) < 2 or len(message['opt'][0]) > 30:
                        _client_socket.send('refused 用户名长度须在2~30间'.encode('utf-8'))
                        continue
                    if len(message['opt'][1]) < 6 or len(message['opt'][1]) > 16:
                        _client_socket.send('refused 密码长度须在6~16间'.encode('utf-8'))
                        continue
                    for j in userList:
                        if message['opt'][0] == j.data['username']:
                            _client_socket.send('refused 此用户名已被占用'.encode('utf-8'))
                            break
                    else:
                        tmp_id = 1
                        i = 0
                        while i < len(userList):
                            if tmp_id == userList[i].uid:
                                tmp_id += 1
                                i = 0
                            i += 1
                        open(f'userData\\{tmp_id}.usr', 'w').write(
                            to_str(username=message['opt'][0], pwd=encrypt(message['opt'][1], message['opt'][0]),
                                   user_type='user', remember_me=False, show_uid=True, create_group=0))
                        userList.append(User(tmp_id, open(f'userData\\{tmp_id}.usr', 'r').read()))
                        now = userList[-1]
                        now.orig_pwd = message['opt'][1]
                        now.user_socket = _client_socket
                        _client_socket.send(f'ok {tmp_id} {str(now)}'.encode('utf-8'))
                    continue
                if message['cmd'] == 'check':
                    _client_socket.send(f'info {latestClient['ver']}'.encode('utf-8'))
                    continue
                if message['cmd'] == 'history':
                    gp = message['opt'][0]
                    history = open(f'groups\\{gp}.grp', encoding='utf-8').read().split('\n-----\n')[:-1]
                    content = 'history '
                    for i in history:
                        content += f'{i}\n\0'
                    _client_socket.send(content.encode('utf-8'))
                    continue
                if message['cmd'] == 'message':
                    content = f'{now.data['username']} {now.uid} '
                    content += message['msg']
                    broadcast(content, message['opt'][0])
                    with open(f'groups\\{message["opt"][0]}.grp', 'a', encoding='utf-8') as f:
                        f.write(
                            f'[{now.data['username']}(id:{now.uid})] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                        for i in message['msg'].split('\n'):
                            f.write('  ' + i + '\n')
                        f.write('-----\n')
                    continue
                if message['cmd'] == 'name':
                    if len(message['opt'][0]) < 2 or len(message['opt'][0]) > 30:
                        _client_socket.send('refused 用户名长度须在2~30间'.encode('utf-8'))
                        continue
                    for j in userList:
                        if message['opt'][0] == j.data['username']:
                            _client_socket.send('refused 此用户名已被占用'.encode('utf-8'))
                            break
                    else:
                        now.rename(message['opt'][0])
                        _client_socket.send('ok'.encode('utf-8'))
                    continue
                if message['cmd'] == 'pwd':
                    if len(message['opt'][1]) < 6 or len(message['opt'][1]) > 16:
                        _client_socket.send('refused 密码长度须在6~16之间'.encode('utf-8'))
                        continue
                    if encrypt(message['opt'][0], now.data['username']) != now.data['pwd']:
                        _client_socket.send('refused 旧密码输入错误'.encode('utf-8'))
                        continue
                    now.set_pw(message['opt'][1])
                    _client_socket.send('ok'.encode('utf-8'))
                    continue
                if message['cmd'] == 'info':
                    if message['opt'][0] == 'user':
                        _client_socket.send(('info ' + str(now)).encode('utf-8'))
                    elif message['opt'][0] == 'group':
                        _client_socket.send(('info ' + str(groupList[message['opt'][1]].data)).encode('utf-8'))
                    continue
                if message['cmd'] == 'remember':
                    now.set_remember()
                    continue
                if message['cmd'] == 'show_uid':
                    now.set_show_uid()
                    continue
                if message['cmd'] == 'create':
                    if now.data['create_group'] >= 2 and now.data['user_type'] != 'admin':
                        _client_socket.send('refused 创建群聊次数已达上限'.encode('utf-8'))
                        continue
                    for i in listdir('groups'):
                        if i[:-4] == message['opt'][0]:
                            _client_socket.send('refused 此群聊名已被占用'.encode('utf-8'))
                            break
                    else:
                        now.create_group()
                        open(f'groups\\{message['opt'][0]}.dat', 'w').write(
                            to_str(created_date=datetime.now().strftime("%Y-%m-%d"), members=[now.data['username']],
                                   pwd=message['opt'][1]))
                        open(f'votes\\{message['opt'][0]}.vot', 'w').write(to_str(title='', start_time=0, For=[],
                                                                                  against=[], last_result=[]))
                        groupList[message['opt'][0]] = Group(f'{message['opt'][0]}.dat')
                        open(f'groups\\{message['opt'][0]}.grp', 'w').write('')
                        _client_socket.send(f'ok 还可创建{2 - now.data['create_group']}个群聊'.encode('utf-8'))
                    continue
                if message['cmd'] == 'enter':
                    if message['opt'][0] not in groupList.keys():
                        _client_socket.send('refused 群聊不存在'.encode('utf-8'))
                        continue
                    if (message['opt'][0] != 'public' and
                            now.data['username'] not in groupList[message['opt'][0]].data['members']):
                        _client_socket.send('refused 不是此群聊的成员'.encode('utf-8'))
                        continue
                    _client_socket.send('ok'.encode('utf-8'))
                    continue
                if message['cmd'] == 'join':
                    if message['opt'][0] not in groupList.keys():
                        _client_socket.send('refused 群聊不存在'.encode('utf-8'))
                        continue
                    if (message['opt'][0] == 'public' or
                            now.data['username'] in groupList[message['opt'][0]].data['members']):
                        _client_socket.send('refused 已经是此群聊的成员'.encode('utf-8'))
                        continue
                    if message['opt'][1] != groupList[message['opt'][0]].data['pwd']:
                        _client_socket.send('refused 密码错误'.encode('utf-8'))
                        continue
                    groupList[message['opt'][0]].add_member(now.data['username'])
                    _client_socket.send('ok'.encode('utf-8'))
                    continue
                if message['cmd'] == 'withdraw':
                    if message['opt'][0] == 'public':
                        _client_socket.send('refused 不可以退出公屏'.encode('utf-8'))
                        continue
                    groupList[message['opt'][0]].del_member(now.data['username'])
                    _client_socket.send('ok'.encode('utf-8'))
                    continue
                if message['cmd'] == 'cancel':
                    if now.data['user_type'] == 'admin':
                        _client_socket.send('refused 管理员不可注销账号'.encode('utf-8'))
                        continue
                    remove(f'userData\\{now.uid}.usr')
                    userList.remove(now)
                    _client_socket.send('ok'.encode('utf-8'))
                    continue
                if message['cmd'] == 'start':
                    if message['opt'][0] == 'vote':
                        tmp = groupList[message['opt'][1]]
                        if tmp.check_date():
                            tmp.start_vote(message['opt'][2])
                            _client_socket.send('ok'.encode('utf-8'))
                            continue
                        else:
                            _client_socket.send('refused 有其他投票正在进行'.encode('utf-8'))
                            continue
                if message['cmd'] == 'get_title':
                    tmp = groupList[message['opt'][0]]
                    if tmp.check_date():
                        _client_socket.send('refused 没有正在进行的投票'.encode('utf-8'))
                    _client_socket.send(('ok ' + groupList[message['opt'][0]].votes.data['title']).encode('utf-8'))
                    continue
                if message['cmd'] == 'vote':
                    if (now.data['username'] in groupList[message['opt'][0]].votes.data['For']
                            or now.data['username'] in groupList[message['opt'][0]].votes.data['against']):
                        _client_socket.send('refused 已投票过'.encode('utf-8'))
                        continue
                    groupList[message['opt'][0]].vote(message['opt'][1], now)
                    _client_socket.send('ok'.encode('utf-8'))
                    continue
                if message['cmd'] == 'get_result':
                    tmp = groupList[message['opt'][0]]
                    tmp.check_date()
                    _client_socket.send(
                        ('info ' + ' '.join(str(i) for i in tmp.votes.data['last_result'])).encode('utf-8'))
                    continue
            if message['cmd'] == 'game_join':
                now.data['username'] = message['opt'][0]
                now.data['user_type'] = 'player'
                message['opt'][1] = int(message['opt'][1])
                pos = gameList[message['opt'][1]].join(message['opt'][0], now.user_socket)
                if pos == 'refused':
                    _client_socket.send(f'refused 房间已有同名玩家'.encode('utf-8'))
                else:
                    now.in_game = message['opt'][1]
                    _client_socket.send(f'ok {pos}'.encode('utf-8'))
                continue
            if message['cmd'] == 'game_get':
                message['opt'][1] = int(message['opt'][1])
                if gameList[message['opt'][1]].players[now.data['username']][0] != 'gameover':
                    _client_socket.send(str(gameList[message['opt'][1]]).encode('utf-8'))
                else:
                    gameList[message['opt'][1]].remove(now.data['username'])
                    now.in_game = 0
                    _client_socket.send('gameover'.encode('utf-8'))
                continue
            if message['cmd'] == 'game_player':
                gameList[now.in_game].update(now.data['username'], int(message['opt'][0]), int(message['opt'][1]))
                _client_socket.send('ok'.encode('utf-8'))
                continue
        except KeyError:
            break
        except ConnectionResetError:
            break
    print(f"[断开连接] {_addr}")
    now.user_socket = None
    if now.in_game:
        gameList[now.in_game].remove(now.data['username'])
        now.in_game = 0
    client_sockets.remove(_client_socket)
    _client_socket.close()


HOST = '127.0.0.1'
PORT = 2048

server = socket(AF_INET, SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"[服务器启动] 监听 {HOST}:{PORT}")

client_sockets = []

try:
    while True:
        client_socket, addr = server.accept()
        client_sockets.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()
except KeyboardInterrupt:
    print("\n[服务器关闭]")
    server.close()
