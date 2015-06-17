import SocketServer
import subprocess
import string
import time
import struct
import threading
import socket
import sys
import os


lock = threading.RLock()


class download(threading.Thread):
    def __init__(self,fobj,start_size,end_size,oldfile,ip):
        self.start_size = start_size
        self.end_size = end_size
        self.oldfile = oldfile
        self.fobj = fobj
        self.buffer = buffer
	self.ip = ip
        threading.Thread.__init__(self)
    def run(self):
        self.down()
    def down(self):
	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sock.connect(self.ip)
	namesize = len(self.oldfile)
	print namesize
	sendfile = struct.pack('3i'+str(namesize)+'s',namesize,self.start_size,self.end_size,self.oldfile)
	sock.send(sendfile)
	block = ''
	rest =  self.end_size-self.start_size+1
	while True:
		if rest == 0:
			break
		if rest < 4096:
			data = sock.recv(rest)
			block = block + data
			break
		data = sock.recv(4096)
		block = block + data
		rest = rest -4096
        with lock:
            self.fobj.seek(self.start_size,0)
            self.fobj.write(block)
	sock.close()

def maindownload(new,thread,oldfile,ip,size):
    fobj = open(new,'wb')
    avg_size,pad_size = divmod(size,thread)
    plist = []
    for i in xrange(thread):
        start_size = i*avg_size
        end_size = start_size +avg_size-1
        if i==thread -1: 
            end_size = end_size + pad_size + 1
        t = download(fobj,start_size,end_size,oldfile,ip[i])
        plist.append(t)
    for t in plist:
        t.start()
    for t in plist:
        t.join()

    fobj.close()


class MyTcpServer(SocketServer.BaseRequestHandler):

    def sendfile(self,filename,start_size,end_size):
        print "starting send file"
        
        f = open(filename,'rb')
	f.seek(start_size,0)
        rest = end_size-start_size+1
	while True:
		if rest==0:
			break
		if rest < 4096:
			data = f.read(rest)
			self.request.send(data)
			break	
		data = f.read(4096)
        	self.request.send(data)
		rest = rest -4096
        f.close()

    def handle(self):
	print 'connect from ',self.client_address
        while True:
            try:
                recvfile = self.request.recv(12)
                if not recvfile:
                    break
                else:
                    namesize,start_size,end_size = struct.unpack('3i',recvfile)
		    filename = self.request.recv(namesize)
	            self.sendfile(filename,start_size,end_size)

            except Exception,e:
                print "Error at:",e
class myserver(threading.Thread):
	def __init__(self):
		self.host = '127.0.0.1'
        	self.port = 8002
		threading.Thread.__init__(self)
	def run(self):
		s = SocketServer.ThreadingTCPServer((self.host,self.port),MyTcpServer)
		s.serve_forever()
if __name__ == '__main__':
    	t = myserver()
	t.start()
	print 'now server is starting'
	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	while True:
		name = raw_input('input name\n')
		pwd = raw_input('input passwd\n')
		if not name:
			continue
		if not pwd:
			continue
		namesize = len(name)
		pwdsize = len(pwd)		
		sendfile = struct.pack('3i'+str(namesize)+'s'+str(pwdsize)+'s',8002,namesize,pwdsize,name,pwd)					
		
		sock.connect(('127.0.0.1',8000))
		sock.send(sendfile)
		s = sock.recv(2)		
		
		if s=='OK':
			print 'welcome'
			break
		elif s=='NO':
			sock.close()
			print 'wrong pwd or wrong name'
		
		else :
			sock.close()
			print 'please check your net state'
	sendfile = ''
	s = os.listdir('.')
	for e in s:
		sendfile = sendfile + ' ' + e + '&' +str(os.stat(e).st_size)
	size = len(sendfile)
	sock.send(struct.pack('i',size))
	sock.send(sendfile) 
	
	listsize = sock.recv(4)
	listsize = struct.unpack('i',listsize)[0]
	mlist = sock.recv(listsize)
	
	f=open('list','wb')
	f.write(mlist)

	mlist = {}
	
	f = open('list','rb')
	s = f.read()
	
	for l in s.split('$'):
		if l:
			h,m = l.split('@')
			a = []
			for n in m.split('#'):
				if n:
					a.append(n)		
			mlist[h]=a
	f.close()
	
	print mlist
	while True:	
		cmd = raw_input('input command')
		cmd,old,size,new = cmd.split()
		size = int(size)
		ip = []
		for l in mlist[old+'&'+str(size)]:
			address , port = l.split(':')
			port = int(port)
			ip.append((address,port))
		thread = len(ip)
		maindownload(new,thread,old,ip,size)
			
	t.join()
	
