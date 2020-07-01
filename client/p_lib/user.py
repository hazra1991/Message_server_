try:
    from queue import Queue
except:
    from Queue import Queue
import pickle,random

class User:
    def __init__(self,username,conn):
        self.username = username
        self.pending_message = Queue()
        self.group_id = username + '@' + str(random.getrandbits(32)) 
        self.conn_obj = conn

    def add_message(self):
        pass

    def add_groupe(self):
        pass
    
    def del_group(self):
        pass
    

def get_obj(obj):
    print('entered object',obj)
    return pickle.loads(obj)

def create_userobj(username,conn):
    obj = User(username,conn)
    return obj

def save_obj(obj):
    return pickle.dumps(obj)

class Message:
    def __init__(self,uname,msg_type,message,send_to):
        self.username=uname
        self.msg_type = msg_type
        self.message =  message
        self.send_to = send_to
