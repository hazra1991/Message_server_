import select,sys,socket
import threading
from p_lib.communication import Server,ConnectionErr
from p_lib.config import Config
from p_lib.user import get_obj , create_userobj ,Message,save_obj,User
# from p_lib import database
from p_lib.database import NoUserFound , PasswordMissMatch, Database



userlist = {}
HOST = Config.gethost()
PORT = Config.getport()
HEADERSIZE = Config.headersize()
t_pool = ['activator','message']
conn_pool = []                          # raw connection pool
address_pool= []                        # raw address pool
live_users = {}                         # live user objects with the username as unique key

class MessageModule(threading.Thread):

    def p2p_message(self,message,co):
        print('entered p2p')
        packet = save_obj(message)
        send_to = message.send_to
        if send_to in live_users:
            user_obj =  live_users[send_to]
            print(packet)
            try:
                Server.send(user_obj.conn_obj,packet,header=HEADERSIZE)
                return
            except:
                del live_users[send_to]

        if send_to in userlist:
            saved_userobject = get_obj(userlist[send_to])
            saved_userobject.pending_message.append(packet)
            userlist[send_to] = save_obj(saved_userobject)
        else:
            print('404')
            message.msg_type = 404
            packet = save_obj(message)
            Server.send(co,packet,header=HEADERSIZE)
            
    
    def run(self):
        while True:
            re , wrt, err = select.select(conn_pool,[],conn_pool,0.5)
            for r in re:
                try:
                    print('inmessageloop')
                    msg = Server.recv(r,header=HEADERSIZE)
                    message =  get_obj(msg)
                    print(type(message))
                    print(message)
                    print(live_users)
                    if message.msg_type == 'p2p':
                        threading.Thread(target=self.p2p_message,args=(message,r)).start()
                        # Server.send(r,'under cunstruciton'.encode('utf-8'),header=HEADERSIZE)
                        
                    elif message.msg_type == 'broadcast':
                                                
                        temp = []
                        message = save_obj(message)
                        for x in live_users.keys():
                            # final_message= message.username +':- '+ message.message
                            print(message,live_users[x].conn_obj)
                            try:
                                Server.send(live_users[x].conn_obj,message,header=HEADERSIZE)
                            except:
                                temp.append(x)
                      
                        for e in temp:
                            del live_users[e]    
                                
                except ConnectionErr:

                    r.close()
                    conn_pool.remove(r)


            

# @authenticate\
class connectionActivator(threading.Thread):

    def activate(self,conn):
        global live_users
        global userlist
        while True:
            re ,_,_ = select.select([conn],[],[])
            for i in re:
                request = get_obj(Server.recv(i))
                db = Database()
                uname =request['username']
                passwd = request['password']
                req_type = request['request_type']
                if req_type == 'create_user':
                    user_obj = create_userobj(uname,'dummy_conn')
                    if db.create_user(uname,passwd,save_obj(user_obj)):
                        request['response_code'] = 200
                        Server.send(conn,save_obj(request))
                        conn_pool.append(conn)
                        user_obj.conn_obj = conn
                        live_users[uname] = user_obj
                        return
                    else:
                        request['response_code'] = 501
                        Server.send(conn,save_obj(request))
                        del user_obj
                elif req_type == 'login':
                    try:
                        if db.login(uname,passwd):
                            user_obj = get_obj(db.retrive_userobj(uname))
                            print(user_obj)
                            request['response_code'] = 200 
                            user_obj.conn_obj = conn
                            live_users[uname] = user_obj
                            Server.send(conn,save_obj(request))
                            conn_pool.append(conn)
                            return
                        else:
                            request['response_code'] = 401
                            Server.send(conn,save_obj(request))
                    except NoUserFound:
                        print('no user')
                        request['response_code'] = 403
                        Server.send(conn,save_obj(request))

                elif req_type == 'change_pass':
                    try:
                        db.change_password(uname,passwd,new_pass)
                        request['response_code'] = 203
                        Server.send(conn,save_obj(request))
                    except:
                        request['response_code'] = 1
                        Server.send(conn,save_obj(request))


        # try:
        #     username = Server.recv(conn).decode('utf-8')
        #     print(username)

        #     conn_pool.append(conn)
        #     if username in userlist:
        #         live_users[username]= get_obj(userlist[username])
        #     else:
        #         live_users[username]=create_userobj(username,conn)

        # except ConnectionErr:
        #     print('activator error ')
        #     conn.close()   

    def run(self):
        global HOST
        global PORT
        global HEADERSIZE
        server = Server(HOST,PORT)
        server.bind()

        while True:
            conn , add = server.accept_conn()
            # conn_pool.append(conn)
            # address_pool.append(add)
            try:
                Server.send(conn,str(HEADERSIZE).encode('utf-8'))
                print(f'Connected to {add} and header size sent {HEADERSIZE}')
                threading.Thread(target=self.activate,args=(conn,)).start()
            except:
                pass





if __name__ == "__main__":
    t_pool[0]= connectionActivator()
    t_pool[0].start()
    t_pool[1] =  MessageModule()
    t_pool[1].start()

