import SocketServer
import subprocess
import string
import time
import struct
import threading
import socket
import sys
import os

def savelist(lists):
	f = open('list','wb')
	for l in lists:
		f.write(l+'@')
		for e in lists[l]:
			f.write(e+'#')
		f.write('$')
	f.close()


class MyTcpServer(SocketServer.BaseRequestHandler):

    def sendfile(self,filename,start_size,end_size):
        print "starting send file"
        
        f = open('list','rb')
	f.seek(start_size,0)
        data = f.read(end_size-start_size+1)
        self.request.send(data)
        f.close()

    def handle(self):
        while True:
            try:
		while True:
                	recvfile = self.request.recv(12)
                	if not recvfile:
                    		pass
                	else:
                    		port,namesize,pwdsize = struct.unpack('3i',recvfile)
		    		name = self.request.recv(namesize)
		    		pwd = self.request.recv(pwdsize)
	            		
				f = open('member','rb')
				key = f.read().split()
				members = {}
				l = len(key)/2
				for i in range(l):
					members[key[2*i]]=key[2*i+1]

				if members[name]==pwd:
					self.request.send('OK')
					listsize = self.request.recv(4)
					listsize = struct.unpack('i',listsize)[0]
					print listsize
					alist = self.request.recv(listsize)
					
					alist = alist.split()
					print alist
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

					address ,rest = self.client_address
					address = address + ':' + str(port) 
					for a in alist:
						print a
						if a in mlist:
							if address not in mlist[a]: 
								mlist[a].append(address)	
						else:
							mlist[a]=[address]
					print mlist
					savelist(mlist)
					listsize = os.stat('list').st_size
					self.request.send(struct.pack('i',listsize))
					self.sendfile('list',0,listsize)
				else:
					self.request.send('NO')					
            except Exception,e:
               	print "Error at:",e
class myserver(threading.Thread):
	def __init__(self):
		self.host = '127.0.0.1'
        	self.port = 8000
		threading.Thread.__init__(self)
	def run(self):
		s = SocketServer.ThreadingTCPServer((self.host,self.port),MyTcpServer)
		s.serve_forever()
if __name__ == '__main__':
    	t = myserver()
	t.start()
	print 'now server is starting'
	t.join()
	
