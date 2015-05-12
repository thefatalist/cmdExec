"""
    Module contains functions which run system commands

    execCMD - simple execution

"""

import pexpect
import FS

from sys      import exit
from time     import time, sleep
from sys import stdout

import logging
logger = logging.getLogger()

timeout_command   = 12*60*60  # Break command if it runs longer than "timeout_command"
timeout_noactions = 2*60*60   # Break command if there is no output longer than "timeout_noactions"
timeout_wait      = 120       # Break command if it is in waiting state longer than "timeout_wait"

printIndent = '--> '



############################################

# Check if data isn't contain any of the elements in "checklist" list
#def checkExpect( checklist=[], data="" ):
#    #if not listoferrors return -1
#    #print "Check %s exists in:\n%s" % (checklist, data)
#    for (i,el) in enumerate(checklist):
#        if el in data:
#            return i
#    return -1

# Check if failif action matched
# Returns the array of checks and matched lines of output
def failifCheck( data, failif ):
    if not failif: return ((),())
    result_patterns = set()
    result_lines    = []
    output = data.split('\n')
    for line in output:
        for (i,el) in enumerate(failif):
            if el in line:
                result_patterns.add( el )
                result_lines.append( line )
    return (result_patterns, result_lines)


# Check if failifNot action matched
# Returns the array of checks that still missing in program output
def failifNotCheck( data, failifnot ):
    if not failifnot: return ()
    #found = 0
    list_to_find = range( len(failifnot) )
    result = []
    for (i,el) in enumerate( failifnot ):
        if el in data:
            #found += 1
            list_to_find.pop( list_to_find.index(i) )
    for el in list_to_find: result.append( failifnot[el] )
    return result


# Execute system command and return status
#def execCMD( cmd, listoferrors=[], silent=False ):
def execCMD( cmd, failif=[], failifnot=[], silent=False ):
    logger.debug( printIndent+"Executing \"%s\" command:" % (cmd))
    logger.debug( printIndent+"  failif   : %s" % (failif)       )
    logger.debug( printIndent+"  failifnot: %s" % (failifnot)    )
    timestart  = time()
    pausesince = time()
    try:
        child = pexpect.spawn( cmd, timeout=0 )
    except Exception as err:
        return( -4, "", err.value )

    output = ""
    while True:
        try:
            line       = child.read_nonblocking(size=100, timeout=timeout_wait)
            line       = line.replace('\r\n','\n')
            pausesince = time()
            output += line
            if not silent: stdout.write( line )

            ## Check if command returned one of the "Error-indicating"
            #if not failif: continue
            #error = checkExpect( failif, output )
            
            #if error >= 0:
            #    return (-1, output, "ERROR template '%s' found in command output." % (failif[error]))

            result_failif    = failifCheck( data=output, failif=failif )
            if result_failif[1]:
                lines = ""
                for line in result_failif[1]:
                    lines += "%s -> %s\n" % (printIndent, line)
                return (-1, output, "Following templates '%s' are found in command output. Lines containing errors:\n%s" % (list(result_failif[0]), lines))

            if timeout_command and time() - timestart > timeout_command:
                return (-2, output, "TIMEOUT (%s)seconds" % timeout_command )

        # Execution has been finished
        except pexpect.EOF:
            child.close()
            status = child.exitstatus

            result_failifnot = failifNotCheck( data=output, failifnot=failifnot )
            if result_failifnot:
                return (-5, output, "Following templates '%s' are NOT found in command output." % (result_failifnot))

            return (status, output, output.replace('\b','\n').replace('\r','\n') )

        # Script didn't return any data for some period of time
        except pexpect.TIMEOUT:
            if timeout_noactions and time() - pausesince > timeout_noactions:
                return (-3, output, "TIMEOUT, no output for (%s)seconds" % timeout_noactions )
            if timeout_command and time() - timestart > timeout_command:
                return (-2, output, "TIMEOUT (%s)seconds" % timeout_command )
            if not silent: print(".")
    return (-1, output, "No errors")


# Exec one action
def execAction( action, failif, failifnot, genCMD, num=0, silent=False ):
    print( "\t%-2d%-40s" % (num, action["cmd"] or '---SKIPPING---') )
    if not action["cmd"]: return None
    action = genCMD( action["cmd"] )
    if not action: return None

    print( printIndent+"Executing: %s" % (action["cmd"]) )
    #result = execCMD( action, listoferrors=listoferrors, failifnot=failifnot, silent=silent )
    result = execCMD( action, failif=failif, silent=silent )
    print( printIndent+"FINISHED with [%s] exit code\n" % (result[0]) )
    return result


#############################################
#  HELP FUNCTION!
############################################
def help( *params ):
    print( "" )
    print( " FUNCTION action:" )
    print( "\t" )
    print( "\tIt executes the selected action using EXPECT library," )
    print( "\tusing expect allows to drop command execution in case of specific output." )
    print( "\tAction parameters are defined in included sublist" )
    print( "\t" )
    print( "\tHow to define:" )
    print( "\t\t- action :" )
    print( "\t\t     cmd           : ACTION" )
    print( "\t\t    [retry_count   : NUMBER]" )
    print( "\t\t    [retry_sleep   : NUMBER]" )
    print( "\t\t    [ignore_errors : True|False]" )
    print( "\t\t    [print         : True|False]" )
    print( "\t\t    [failif        :            " )
    print( "\t\t        - 'ERROR'               " )
    print( "\t\t        - 'ALERT'               " )
    print( "\t\t    ]" )
    print( "\t\t    [failifnot     :            " )
    print( "\t\t        - 'ALLGOOD'" )
    print( "\t\t    ]" )
    print( "\t" )
    print( "\t\tcmd:" )
    print( "\t\t   could be any action specified in \"commands:\" secion in yaml config file" )
    print( "\t" )
    print( "\t\tretry_count:" )
    print( "\t\t   could be any positive integer" )
    print( "\t\t   in case if command execution fails, it will restart indicated number of times" )
    print( "\t" )
    print( "\t\tretry_sleep:" )
    print( "\t\t   could be any positive float" )
    print( "\t\t   in case if command execution fails, it will wait selected amount of seconds before retry" )
    print( "\t" )
    print( "\t\tignore_errors:" )
    print( "\t\t   ." )
    print( "\t\t   ." )
    print( "\t" )
    print( "\t\tprint:" )
    print( "\t\t   Could be either True or False (False is a default value)" )
    print( "\t\t   Forces the script to print out the information received durin execution" )
    print( "\t" )
    print( "\t\tfailif:" )
    print( "\t\t   List of strings, which appearance in program execution output will cause error" )
    print( "\t\t   (NOTE!) In case if any of strings are matched. No retry cycle will be performed" )
    print( "\t" )
    print( "\t\tfailifnot" )
    print( "\t\t   Script will return error code in case if output doesn't contain this set of strings" )
    print( "\t" )
    print( "\tEXAMPLE:" )
    print( "\t\t- action :" )
    print( "\t\t    cmd          : create_vm" )
    print( "\t\t- action :" )
    print( "\t\t    cmd          : check_vm_ok" )
    print( "\t\t    retry_count  : 10" )
    print( "\t\t    retry_sleep  : 30" )
    print( "\t\t    print        : False" )
    print( "\t\t-" )
    print( "\t\t  print  : onfail" )
    print( "\t" )



#############################################
#  MAIN EXECUTOR FOR PLUGIN
############################################
#
#  Used parameters:
#        cmd           : action_name
#        retry_count   : amount of retry attempts
#        retry_sleep   : how long to wait till retry
#        ignore_errors : ignore error returned by action [return 0]


def run( action, config, data):
    if type(action) is not dict or not action.has_key("cmd"):
        logger.error("cmd parameter is not setup!")
        exit(1)

    # Display current step number
    print( printIndent+"%-2d%-40s" % ( data["num"]+1, action["cmd"] or '---SKIPPING---') )

    genCMD    = data["genCMD"]
    param     = data["param"]
    actionCMD = genCMD( action["cmd"] )
    failif    = param.get("failif", [])
    failifnot = param.get("failifnot", [])

    if not action: return [0,None]

    retry_count  = int(   action.get("retry_count", 1  ) )
    retry_sleep  = float( action.get("retry_sleep", 0.0) )
    silent       = float( action.get("silent", True) )

    print( printIndent+"Executing: %s" % (action["cmd"]) )
    for i in xrange( retry_count ):
        #result = execCMD( actionCMD, listoferrors=data["failif"], silent=(not action.get("print", False)) )
        result = execCMD( actionCMD, failif=failif, failifnot=failifnot, silent=(not action.get("print", False)) )
        print( printIndent+"FINISHED with [%s] exit code" % (result[0]) )
        if result[0] in (-1,): break
        #result = execAction(
        #                     action       = action
        #                    ,listoferrors = config.get("errorlist", [])
        #                    ,genCMD       = data["genCMD"]
        #                    ,num          = data["num"]+1
        #                    ,silent       = True
        #                    )
        if not result: break

        if (result[0] == 0) or (retry_count == i+1) :
            break

        print(printIndent+"Execution failed [%s/%s], retry in %s seconds.\n" % (i+1, retry_count, retry_sleep) )
        sleep( retry_sleep )

    data["lastResult"] = result[0]
    data["lastOutput"] = result[1]
    return [result[0], result[2]]

