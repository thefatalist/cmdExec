# -*- coding: utf-8 -*-
# v.1.0
import json
import socket
from struct import pack,unpack
import sys

_DEBUG_ = 0

class ZSender:
	def __init__(self, host, zhostname,port=10051,_DEBUG_=0):
		self.zHost=host
		self.zPort=port
		self.zHostName=zhostname
		self._DEBUG_=_DEBUG_
		return

	def __prepare(self,payload):
		prep_payload=self.__data_transform(payload)           
		json_payload=json.dumps(prep_payload)
		data_header = 'ZBXD\1'+pack('I', len(json_payload)) + '\0\0\0\0'
		return data_header+json_payload    
    
	def send(self,payload):
		prepared_payload = self.__prepare(payload)
		send_result = self.__zbx_net_send(prepared_payload)
		
		return send_result
    
	def __data_transform(self,unpep_payload): #transfom from plain dict (key:value) to json-ready list with proper format
		dta=[]
		for delmt in unpep_payload:
			dta.append({"host":self.zHostName,"key":delmt,"value":str(unpep_payload[delmt]) })
	
		prep_payload={"request":"sender data","data":dta}
		if self._DEBUG_ == 1: print json.dumps(prep_payload,indent=4) #DEBUG
		if self._DEBUG_ == 2:
			fdH = open('/tmp/pyjo_dbg.txt', 'w')
			for line in unpep_payload:
				fdH.write("%s --> %s\n" % (line,unpep_payload[line]))
			abcd=json.dumps(prep_payload,indent=4)
			fdH.write(abcd)
			fdH.close()
		return prep_payload 



	def __zbx_net_send(self,payload):
		#create client socket client_s
		try:
			client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client_s.connect((self.zHost, self.zPort))
		except socket.error, (value,message):
			if client_s:
				client_s.close()
			print "Could not open socket: " + message
			sys.exit(1) 
		#send payload
		client_s.send(payload)
		#read response from server
		srv_resp_head = client_s.recv(5)
		if not srv_resp_head == 'ZBXD\1':
			return 'Got invalid response from server'
		# read length of response from header and we need only 4 bytes 
		srv_resp_data_len = client_s.recv(8)[:4]
		resp_len = unpack('I', srv_resp_data_len)[0]
		resp_body_raw = client_s.recv(resp_len)
		#closing connection
		client_s.close()
		response = json.loads(resp_body_raw)
		
		return response

    
    


