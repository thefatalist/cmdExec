"""
	Module contains functions which run system commands

	execCMD - simple execution

"""

import pexpect
import FS

from sys      import exit
from time     import time
from sys import stdout

import logging
logger = logging.getLogger()

timeout_command   = 12*60*60  # Break command if it runs longer than "timeout_command"
timeout_noactions = 2*60*60   # Break command if there is no output longer than "timeout_noactions"
timeout_wait      = 120       # Break command if it is in waiting state longer than "timeout_wait"



# Check if data isn't contain any of the elements in "listoferrors" list
def checkExpect( listoferrors=[], data="" ):
	#if not listoferrors return -1
	for (i,el) in enumerate(listoferrors):
		if el in data:
			return i
	return -1

# Execute system command and return status
def execCMD( cmd, listoferrors=[], silent=False ):
	logger.debug( "Executing \"%s\" command %s:" % (cmd, listoferrors)  )
	timestart  = time()
	pausesince = time()
	try:
		child = pexpect.spawn( cmd, timeout=0 )
	except Exception as err:
		return( -4, err.value )

	output = ""
	while True:
		try:
			line       = child.read_nonblocking(size=100, timeout=timeout_wait)
			line       = line.replace('\r\n','\n')
			pausesince = time()
			output += line
			#print line.replace('\e','\n').replace('\r','\n'),
			#print line.replace('\e','\n'),
			if not silent: stdout.write( line )

			# Check if command returned one of the "Error-indicating"
			if not listoferrors: continue
			error = checkExpect( listoferrors, output )
			if error >= 0:
				return (-1, error)
			if timeout_command and time() - timestart > timeout_command:
				return (-2, "TIMEOUT (%s)seconds" % timeout_command )

		# Execution has been finished
		except pexpect.EOF:
			child.close()
			status = child.exitstatus
			return (status, output.replace('\b','\n').replace('\r','\n') )

		# Script didn't return any data for some period of time
		except pexpect.TIMEOUT:
			if timeout_noactions and time() - pausesince > timeout_noactions:
				return (-3, "TIMEOUT, no output for (%s)seconds" % timeout_noactions )
			if timeout_command and time() - timestart > timeout_command:
				return (-2, "TIMEOUT (%s)seconds" % timeout_command )
			if not silent: print(".")
	return (-1, output)


# Exec one action
def execAction( action, listoferrors, genCMD, num=0, silent=False ):
	print( "\t%-2d%-40s" % (num, action or '---SKIPPING---') )
	if not action: return None
	action = genCMD( action )
	if not action: return None

	print( "\tExecuting: %s" % (action) )
	result = execCMD( action, listoferrors=listoferrors, silent=silent )
	print( "\tFINISHED with [%s] exit code\n" % (result[0]) )
	return result

