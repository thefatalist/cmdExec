"""
	PLUGIN for sleep function ONLY if previous command succeeded

	- sleep  : N

	  will sleep N seconds

"""

from time import sleep

#############################################
#  HELP FUNCTION
############################################
def help( params ):
	print( "" )
	print( " FUNCTION sleep:" )
	print( "\t" )
	print( "\tJust sleeps selected amount of time in seconds")
	print( "\tRuns ONLY if previous command is SUCCESSFULLY finished")
#	print( "\tCould be defined together with action, or alone (without any actions)" )
	print( "\tCould be used ONLY separately. Not with action" )
	print( "\t" )
	print( "\tHow to define:" )
	print( "\t\t- action : SOME_ACTION" )
	print( "\t\t  print  : [FLOAT]" )
	print( "\t" )
	print( "\t\tFLOAT:" )
	print( "\t\t   any float number")
	print( "\t\t   1.0 second is a default value")
	print( "\t" )
	print( "\tEXAMPLE:" )
#	print( "\t\t- action : start_VM" )
#	print( "\t\t  ungrep : '^#'" )
	print( "\t\t-  " )
	print( "\t\t  sleep  : 3.5" )
	print( "\t" )

#############################################
#  MAIN EXECUTOR FOR PLUGIN
############################################

def run( action, config, data):
	#print action
	#print config
	if data["lastResult"] not in [0,"","0"]: return
	sleep_time = data["param"]
	sleep(sleep_time)
