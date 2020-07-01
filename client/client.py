import select,sys,socket,subprocess,os
from p_lib.communication import Client , ConnectionErr
from p_lib.user import Message
import pickle

HOST = socket.gethostname()
PORT = 1234
HEADERSIZE = None

auth_info = {
                'username':'',
                'password':'',
                'new_pass':None,
                'request_type':'',
                'response_code':None

            }

# class Message:
#     def __init__(self,uname,msg_type,message,send_to):
#         self.username=uname
#         self.msg_type = msg_type
#         self.message =  message
#         self.send_to = send_to


class SetupClient(Client):
    # TODO implementation pending 
    # def authenticate_user(self):
    #     print('enter the proper selection (Usage type "1" or "2"): -\n 1:- register\n 2:- login')
    #     data = input('>').strip()
    #     if data == '1':
    #         # register()
    #         pass
    #     elif data == '2':
    #         # login()
    #         pass
    #     else:
    #         print('Enter a valid selection')
    #         exit(0)

    # TODO construction needed 
    def auth_or_register(self,sock_to_monitor):
        global auth_info
        print('Please select an option or ctrl^c to quit::(usage type 1 or 2 or 3 and press enter)********** \n1) Register \n2) Login \n3) Change Pass' )
        while True:
            # import time
            # time.sleep(2)
            r ,w, er = select.select(sock_to_monitor,[],[])
            print('Processing please wait............')
            for i in r:
                if i == sys.stdin:
                    cmd = sys.stdin.readline()
                    if cmd.strip() == '1':
                        auth_info['username'] = input('username> ').strip()
                        auth_info['password'] = input('password> ')
                        auth_info['request_type'] = 'create_user'
                        self.send(pickle.dumps(auth_info))

                    elif cmd.strip() == '2':
                        auth_info['username'] = input('username> ').strip()
                        auth_info['password'] = input('password> ')
                        auth_info['request_type'] = 'login'
                        self.send(pickle.dumps(auth_info))
                    elif cmd.strip() == '3':
                        auth_info['username'] = input('username> ').strip()
                        auth_info['password'] = input('old password> ')
                        auth_info['new_pass'] = input('new password> ')
                        auth_info['request_type'] = 'change_pass'
                        self.send(pickle.dumps(auth_info))
                    else:
                        print('please provide a proper input')
                else:
                    resp = pickle.loads(self.recv())
                    if resp['response_code'] == 200:
                        print('User accepted !! start communicating ')
                        return
                    if resp['response_code'] == 203:
                        print("Password has bee successfully updated !! please login")
                    elif resp['response_code'] == 404:
                        print('Username not registered\nPlease try again or ctr^c to quit')
                    elif resp['response_code'] == 401:
                        print("login failed !!. Enter a proper password")
                    elif resp['response_code'] == 403:
                        print("user doesnot exists !! Please create the same and try again")
                    elif resp['response_code'] == 501:
                        print("User already exist !!! .Please login or create a new acc")
                    elif resp['response_code'] == 1:
                        print('The entered old password is invalid .Try again')

    def getheader(self):
        try:
            he = self.recv()
            if he != None:
                return int(he)
            else:
                return None
        except ConnectionErr:
            self.close()
            exit(0)
        except ValueError:
            print("wrong header at server end,continueing with none")
            self.close()
    
    # def start(self,so_to_moniter):
    #     global HEADERSIZE
    #     print('**welcome to the broadcast group**\n\nplease enter connect <username> to enter a private chat ')
    #     while True:
    #         cmd =  input('> ')
    #         if len(cmd) > 0 and cmd == ''
            


    
    def start_texting(self,so_to_moniter):
        global auth_info
        global username
        global HEADERSIZE
        username = auth_info['username']
        print('Start messaging to broadcast or type @connect <username> to ping a specifig user')
        while True:
            read ,wrt ,err = select.select(so_to_moniter,[],so_to_moniter)
            for r in read:
                if r == sys.stdin:
                    msg = sys.stdin.readline().strip()
                    if len(msg.split()) == 2 and '@connect' in msg.split():
                        self.start_p2p(username,so_to_moniter,msg.split()[1])   

                    elif len(msg) > 0:
                        packet = Message(username,'broadcast',msg,'ALL')
                        # print(packet)
                        packet =  pickle.dumps(packet)
                        self.send(packet,header=HEADERSIZE)
                    
                else:
                    msg = self.recv(header=HEADERSIZE)
                    packet = pickle.loads(msg)
                    # print(packet)
                    if packet.msg_type == 'p2p':
                        print('p2p:- ',packet.username,':- ',packet.message)
                    elif packet.msg_type == 'broadcast':
                        print('@broadcast-msg:> {} :- {}'.format(packet.username,packet.message))
                    # print(msg.decode('utf-8'))

    def start_p2p(self,username,so_to_moniter,send_to):
        print('type exit(1) to exit')
        while True:
            r ,w, e = select.select(so_to_moniter,[],so_to_moniter)
            for i in r:
                if i == sys.stdin:
                    msg=sys.stdin.readline().strip()
                    if msg == 'exit(1)':
                        return
                    if len(msg) > 0:
                        packet =  Message(username,'p2p',msg,send_to)
                        packet = pickle.dumps(packet)
                        self.send(packet,header=HEADERSIZE)
                else:
                    msg = self.recv(header=HEADERSIZE)
                    packet = pickle.loads(msg)
                    if packet.msg_type == 'p2p':
                        print(packet.username,':- ',packet.message)
                    elif packet.msg_type == 'broadcast':
                        print('@broadcast-message saved')
                    elif packet.msg_type == 404:
                        print('\tThe user is unregisted !!!!!!\n\tExiting p2p chat !!!!!!')
                        return
                    # print(msg.decode('utf-8'))

    
def run_client():
    global HEADERSIZE
    client = SetupClient(HOST,PORT)
    client.connect_sock()
    HEADERSIZE = client.getheader()
    print(HEADERSIZE)
    sock_to_moniter = [client.get_fd(),sys.stdin]
    client.auth_or_register(sock_to_moniter)
    client.start_texting(sock_to_moniter)
    
if __name__== '__main__':
    run_client()
