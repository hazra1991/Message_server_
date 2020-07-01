import sqlite3

class NoUserFound(Exception):
    pass

class PasswordMissMatch(Exception):
    pass

class Database:
    def __init__(self):
        self.connection =  sqlite3.connect('userdb.db')
        self.cur = self.connection.cursor()

        self.cur.execute("CREATE TABLE IF NOT EXISTS userinfo (username PRIMARY KEY,password)")    #db queries are not case sensitive,capitalized just to distinguise
        self.cur.execute("CREATE TABLE IF NOT EXISTS user_record (username PRIMARY KEY,object)")
        self.connection.commit()

    def login(self,username,password):
        self.cur.execute("select password from userinfo where username=(?)",(username,))
        passwd= self.cur.fetchone()
        print(passwd)
        if passwd is None:
            raise NoUserFound
        if passwd[0] ==  password:
            return True
        else:
            return False
        
    def create_user(self,username,password,user_object):
        try:
            self.cur.execute('INSERT INTO userinfo values(?,?)',(username,password))
            self.cur.execute("INSERT INTO user_record values(?,?)",(username,user_object))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        

    def update_user(self,username,user_object):
        self.cur.execute("UPDATE user_record SET object=(?) WHERE username=(?)",(user_object,username))
        self.connection.commit() 
    # Todo need to checck the password mechanism
    def change_password(self,username,old_pass,new_pass):

        self.cur.execute("select password from userinfo where username=(?)",(username,))
        password = self.cur.fetchone()[0]
        print(password)
        if password == old_pass:
            self.cur.execute("UPDATE userinfo SET password=(?) WHERE username=(?)",(new_pass,username))
        else:
            raise PasswordMissMatch


    def retrive_userobj(self,username):
        self.cur.execute("SELECT object from user_record where username=(?)",(username,))
        return self.cur.fetchone()[0] 

    
