import socket       

class ConnectionErr(Exception):
    pass

class Client(object):
    def __init__(self,host,port,address_f = socket.AF_INET,proto=socket.SOCK_STREAM,blocking=True):
        self.host = host
        self.port = port
        self.proto = proto
        self.blocking = blocking
        self.so =  socket.socket(address_f,proto)
        
        
    def get_fd(self):
        return self.so

    def connect_sock(self):
        self.so.connect((self.host,self.port))
        self.so.setblocking(self.blocking)

    def send(self,msg,header=None):
        _send_msg(self.so,msg,header)

    def recv(self,header=None,buffer=1024):
        return _recv_msg(self.so,header,buffer)
    
    def close(self):
        self.so.close()

    def shutdown(self):
        self.so.shutdown(socket.SHUT_RDWR)
        
    
class Server(object):
    def __init__(self,host,port,address_f = socket.AF_INET,proto=socket.SOCK_STREAM,listen_buf = 5,blocking=True):
        self.host = host
        self.port = port
        self.proto = proto
        self.blocking = blocking
        self.server =  socket.socket(address_f,proto)
        self.listen_buf =listen_buf
    
    def get_fd(self):
        return self.server
    
    def bind(self):
        self.server.bind((self.host,self.port))
        self.server.listen(self.listen_buf)
        self.server.setblocking(self.blocking)

    def accept_conn(self):
        conn , addr = self.server.accept()
        return conn,addr

    @staticmethod
    def send(conn,msg,header=None):
        _send_msg(conn,msg,header)
    
    @staticmethod
    def recv(conn,header=None,buffer=1024):
        return _recv_msg(conn,header,buffer)
    
    def close(self):
        self.server.close()
    
    def shutdown(self):
        self.so.shutdown(socket.SHUT_RDWR)


        

def _recv_msg(conn,header,buffer,force_decoding=True):
    msg = b''
    if header !=  None:
        msglength = 0
        new_msg = True
        while True:
            data = conn.recv(buffer)
            print(data)
            if not data:
                raise ConnectionErr('remote end disconnected')
            if new_msg:
                msglength = int(data[:header].strip()) 
                print(msglength)
                new_msg = False 
            msg = msg + data
            if (len(msg) - header) == msglength:
                break
        return msg[header:]
    else:
        msg = conn.recv(buffer)
        if not msg:
            raise ConnectionErr('remote end disconnected')
        
    return msg

def _send_msg(conn,msg,header,force_encoding=True):

    if header != None:
        padding = '{:<{header}}'.format(len(msg),header=header)
        output =  padding.encode('utf-8') + msg
        conn.send(output)

    else:
        conn.send(msg)
        
