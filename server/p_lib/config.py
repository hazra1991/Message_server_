import socket
class Config:
    __host = socket.gethostname()
    __port = 1234
    __headersize = 10

    @staticmethod
    def headersize():
        try:
            return int(Config.__headersize)
        except ValueError:
            return None

    @staticmethod
    def gethost():
        return Config.__host

    @staticmethod
    def getport():
        return Config.__port
