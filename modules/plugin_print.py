"""
    PLUGIN for print function

    - action : ACTION_NAME
      print

      will print the result of action execution to STDOUT

"""

#import logging
#logger = logging.getLogger()




############################################

# Print data in frame
def frameIt( printFunc ):
    def printWithFrame( *arg, **kwarg ):
        print "..............................."
        printFunc( *arg, **kwarg )
        print "...............................\n"
    return printWithFrame

# Print each line with tabs in front
@frameIt
def printWithIndent( data, indentCount=1 ):
    for line in data.split('\n'):
        #if not line: continue
        print ("..."+"\t"*indentCount)+line

# Exec one action
def printOutput( data ):
    #print data["lastOutput"]
    printWithIndent( data["lastOutput"], 1 )


# Exec if comman execution was successful
def printIfSuccess( data ):
    if data["lastResult"] == 0:
        #print data["lastOutput"]
        printWithIndent( data["lastOutput"], 2 )

# Exec if comman execution was NOT successful
def printIfNOTSuccess( data ):
    if data["lastResult"] != 0:
        #print data["lastOutput"]
        printWithIndent( data["lastOutput"], 2 )

#############################################
#  HELP FUNCTION
############################################
def help( params ):
    print( "" )
    print( " FUNCTION print:" )
    print( "\t" )
    print( "\tIt prints out content of the last command output" )
    print( "\tCould be defined together with action, or alone (without any actions)" )
    print( "\t" )
    print( "\tHow to define:" )
    print( "\t\t- action : SOME_ACTION" )
    print( "\t\t  print  : [OPTION]" )
    print( "\t" )
    print( "\t\tOPTIONS:" )
    print( "\t\t   always  - [DEFAULT] Always print output" )
    print( "\t\t   success - Print ONLY if last command exit code is 0" )
    print( "\t\t   onfail  - Print ONLY if last command exit code is NOT 0" )
    print( "\t" )
    print( "\tEXAMPLE:" )
    print( "\t\t- action : start_VM" )
    print( "\t\t  ungrep : '^#'" )
    print( "\t\t-  " )
    print( "\t\t  print  : onfail" )
    print( "\t" )

#############################################
#  MAIN EXECUTOR FOR PLUGIN
############################################

def run( action, config, data):
    #print "--------print-----------"
    #print data
    exec_parameters = {
         "default" : printOutput
        ,"always"  : printOutput
        ,"success" : printIfSuccess
        ,"onfail"  : printIfNOTSuccess
    }
    #print " => %s" % data["plugin"]
    exec_function = exec_parameters.get( data["param"], "default" )
    run_result = exec_function(
                            data = data
                            )
