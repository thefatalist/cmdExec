"""
	PLUGIN for print function

	- action : ACTION_NAME
	  print

	  will print the result of action execution to STDOUT

"""

#import logging
#logger = logging.getLogger()




############################################

# Exec if comman execution was NOT successful
def grep( output, lines ):
	result = []
	for line in output:
		if line in lines:
			result.append(line)
	return result

#############################################
#  HELP FUNCTION
############################################
def help( params ):
	print( "" )
	print( " FUNCTION grep:" )
	print( "\t" )
	print( "\tIt works with last command output." )
	print( "\tFunction keeps all lines contained in the list of grep command")
	print( "\tand drops all lines that doesn't")
	print( "\t" )
	print( "\tHow to define:          " )
	print( "\t\t- action : SOME_ACTION" )
	print( "\t\t  grep   :            " )
	print( "\t\t    - 'line1'         " )
	print( "\t\t    - 'line2'         " )
	print( "\t\t    - 'line3'         " )
	print( "\t" )
	print( "\tEXAMPLE:" )
	print( "\t\t- action : start_VM" )
	print( "\t\t  grep   :         " )
	print( "\t\t    - 'ERROR'      " )
	print( "\t\t    - 'Started'    " )
	print( "\t\t-                  " )
	print( "\t\t  print            " )
	print( "\t" )

#############################################
#  MAIN EXECUTOR FOR PLUGIN
############################################

def run( action, config, data):
	exec_function = exec_parameters.get( data["param"], "default" )
	output_old = data["lastOutput"]
	output_new = grep( output=output_old, lines=data["param"] )
	data["lastOutput"] = output_new
