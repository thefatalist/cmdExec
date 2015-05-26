"""
    PLUGIN that print out message

    - action : ACTION_NAME
    - echo   :
      - message : "Something went wrong! Go to http://myhome.com for details"
      - when    : onfail

"""

import logging
logger = logging.getLogger()




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

# Get program parameters:
def getConfig( data, config ):
    conf = {
         'onfail'     : True
        ,'when'       : data.get('when', 'UNKNOWN')
        ,'message'    : data.get('message', 'No defined message')
        ,'lastResult' : config['lastResult']
        ,'exitStatus' : config['exitStatus']
    }
    if conf['when'] == 'always':
        conf['onfail'] = False
    else:
        conf['onfail'] = True
    return conf


# Print out the message according to parameters
def runPrint( conf ):
    if conf['onfail'] and conf["exitStatus"] == 0: return
    printWithIndent( data=conf['message'] )


#############################################
#  HELP FUNCTION
############################################
def help( params ):
    print( "" )
    print( " FUNCTION echo:" )
    print( "\t" )
    print( "\tIt prints out contecnt of the 'message' parameter to stdout" )
    print( "\tthe 'when' parameter controls when to print out message" )
    print( "\t" )
    print( "\tHow to define:" )
    print( "\t\t- action : SOME_ACTION" )
    print( "\t\t- echo   : [OPTION]" )
    print( "\t\t    - message : 'Something went wrong! Go to http://myhome.com for details'" )
    print( "\t\t    - when    : onfail" )
    print( "\t" )
    print( "\t\tOPTIONS:" )
    print( "\t\t   message                - string with message to print out" )
    print( "\t\t   when : [onfail|always] - when to print out:" )
    print( "\t\t       always - always print message" )
    print( "\t\t       onfail - print message ONLY if error occured during last command execution" )
    print( "\t" )
    print( "\tEXAMPLE:" )
    print( "\t\t- action : start_VM" )
    print( "\t\t   - failif : " )
    print( "\t\t      - 'ERROR. Network is unreachable'" )
    print( "\t\t- echo   :" )
    print( "\t\t   - message  : 'Network is unreachable. Please check the 'http://confluence/doc/network_hotfix.html' document for instructions" )
    print( "\t\t   - when     : onfail" )
    print( "\t" )

#############################################
#  MAIN EXECUTOR FOR PLUGIN
############################################

def run( action, config, data):
    #logger.debug( "--> Running echo command with '%s' parameter" % data["param"] )
    #logger.debug( "--------echo-CONFIG----------\n %s" % config)
    conf = getConfig( data=data['param'], config=config )
    runPrint( conf=conf )
