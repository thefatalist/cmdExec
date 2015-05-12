"""
    PLUGIN for grepping

    - action : ACTION_NAME
    - grep   :
        - fail_if_found
        - patterns       :
                         - 'pattern1'
                         - 'pattern2'

    ??? ADD More description here

"""

import logging
logger = logging.getLogger()




############################################

# Check one line if it contains ANY of the provided patterns
def grepLine(line, patterns):
    #print "check '%s'" % line
    for pattern in patterns:
        if pattern in line: return True
    return False


# Grep lines (simulate 'grep' function)
def grep( output, patterns, dont_fail=False ):
    logger.debug("--> Running 'grep' function")
    result_ok   = []
    result_fail = []
    exitcode    = 1
    for line in output.split('\n'):
        if grepLine( line=line, patterns=patterns ):
            exitcode = 0
            result_ok.append(line)
        else:
            result_fail.append(line)
    if dont_fail and exitcode == 1: exitcode = 0
    return (exitcode, result_ok, result_fail)


# Reverse grep lines (simulate 'grep -v' function)
#   returns fail if such pattern is found
def grep_v( output, patterns, dont_fail=True ):
    logger.debug("--> Running 'grep -v' function")
    result_ok   = []
    result_fail = []
    exitcode    = 0
    for line in output.split('\n'):
        if not grepLine( line=line, patterns=patterns ):
            result_ok.append(line)
        else:
            exitcode = 1
            result_fail.append(line)
    if dont_fail and exitcode == 1: exitcode = 0
    return (exitcode, result_ok, result_fail)


# Print out lines that contained templates
def printErrors( output ):
    logger.info(" -> List of lines that caused error:")
    for line in output:
        logger.info( " -> %s" % line )
    logger.info(" ->\n")

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
    print( "\tGrep function support variables substitution (from config)" )
    print( "\tit is possible to set pattern as 'VM ID: %(my_id)s' and it will be replaced with 'VM ID: 12300092'" )
    print( "\t" )
    print( "\t" )
    print( "\t Possible flags:" )
    print( "\t    -v         : reverse grep. Will rise a fail if one of the patterns is matched" )
    print( "\t    dont_fail  : do not return error code in any case. convenient to grep part of the output and then print it out" )
    print( "\t    listerrors : list lines that were found by plugin" )
    print( "\t" )
    print( "\tHow to define:          " )
    print( "\t\t- action : SOME_ACTION" )
    print( "\t\t- grep   :            " )
    print( "\t\t  - -v                " )
    print( "\t\t  - dont_fail         " )
    print( "\t\t  - listerrors        " )
    print( "\t\t  - patterns:         " )
    print( "\t\t         - 'line1'    " )
    print( "\t\t         - 'line2'    " )
    print( "\t\t         - 'line3'    " )
    print( "\t" )
    print( "\tEXAMPLE:" )
    print( "\t\t- action : start_VM " )
    print( "\t\t- grep   :          " )
    print( "\t\t  - -v              " )
    print( "\t\t  - patterns:       " )
    print( "\t\t         - 'ERROR'  " )
    print( "\t\t         - 'Unable' " )
    print( "\t\t         - '%(myline)s' " )
    print( "\t\t                    " )
    print( "\t\t-  print : onfail   " )
    print( "\t" )

#############################################
#  MAIN EXECUTOR FOR PLUGIN
############################################

def getOptions( parameters, config ):
    result = {
      '-v'            : False,   # Inverted search
      'dont_fail'     : False,   # Don't rise the error result in case if function didn't work
      'patterns'      : [],
      'action'        : grep,
      'listerrors'    : False
    }
    for param in parameters:
        if type(param) == dict:
            try:
                result["patterns"] = param["patterns"]
            except:
                logger.debug("Unknown parameter found: %s" % param)
            try:
                # Lets replace patterns with their values in config file
                patterns = []
                for pattern in result["patterns"]:
                    patterns.append( pattern % config )
                result["patterns"] = patterns
            except Exception as err:
                print err
                logger.info("Unable to substitute variable in grep pattersn. ERR:\n\t%s" % err)
        else:
            result[param] = True
    if result["-v"]: result['action'] = grep_v
    return result


# Execute the code of module
def run( action, config, data):
    config = getOptions( parameters=data["param"], config=config )
    exec_parameters = {
                "default" : grep,
                "-v"      : grep_v
            }
    exec_function           = config['action']
    output_old              = data["lastOutput"]
    return_code, output_ok, output_fail = exec_function( output=output_old, patterns=config["patterns"], dont_fail=config["dont_fail"] )
    
    # In case of success, just return what you got
    if return_code == 0:
        data["lastOutput"] = '\n'.join(output_ok)

    else:
        # Else - return previous data, and tell that you failed
        logger.info(" -> Function didn't work for some of the provided patterns:\n -> \t%s\n" % config["patterns"])
        if config["listerrors"]:
            printErrors( output_fail )
        data["lastResult"] = return_code

    return [return_code, "\n".join(output_ok)]

