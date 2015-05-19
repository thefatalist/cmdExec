"""
    PLUGIN to get data from console output

    - get_variable : 
        - line       : 1
        - delimeters : '| '
        - index      : '1:2'
        - pattern    : '....-....-....-....'
        - saveas     : 'VM_id'
        - dontfail   : True
 
      will print the result of action execution to STDOUT

"""

import logging
logger = logging.getLogger()




############################################

# Configure exec parameters
def setParameters( params ):
    # List of default parameters
    config = {
          "line"       : 0
         ,"delimeter"  : '|'            # Delimeter symbol
         ,"joiner"     : '-'            # How to join strings if we look for a range
         ,"index"      : '0:1'          # Range of strings to find
         ,"strip"      : True           # Strip spaces after line split (for each element)
         ,"pattern"    : ''             # Check that resulting line corresponds to the pattarn
         ,"saveas"     : 'VM_id'        # Save result in config under this name
         ,"dontfail"   : True           # Do not rise error in case if result isn't match the pattern
    }
    for el in params:
        for key, val in el.iteritems():
            config[key] = val
    return config


# Split line into chunks
def splitLine( line, params ):
    result = line.split( params["delimeter"] )
    if params["strip"]:
        strip_result = []
        for el in result:
            newdata = el.strip()
            if newdata:
                strip_result.append( newdata )
        result = strip_result
    return result


# Get list slice according to string index
def sliceList( data_list, slice_index ):
    slice_from, slice_to = slice_index.split(':')
    if not slice_from: slice_from = 0
    else:              slice_from = int(slice_from)
    if not slice_to:   slice_to   = len(data_list)
    else:              slice_to   = int(slice_to)
    return data_list[slice_from:slice_to]


# Check if line corresponds to the pattern
def checkLine( line, pattern ):
    if not pattern:
        logger.debug("No pattern is provided. Skipping regex check")
        return (0, line)
    import re
    checker = re.compile(pattern)
    match   = checker.match(line)
    if match:
        logger.debug("String is matched the pattern")
        return (0, line)
    logger.debug("String is not matched the pattern")
    return (2, "")

# Get the requested data from last ouput
def getVariable( lines, params ):
    lines = lines.split("\n")
    try:
        line = lines[params["line"]]
    except IndexError:
        logger.info("Unable to get requested line (%s) from last output for parsing" % params["line"])
        return (1, "")
    data   = splitLine( line=line, params=params )
    result = sliceList( data_list=data, slice_index=params["index"] )
    result_line = params["joiner"].join(result)
    result_code, result_line = checkLine( line=result_line, pattern=params["pattern"] )

    return (result_code, result_line)


#############################################
#  HELP FUNCTION
############################################
def help( params ):
    print( "" )
    print( " FUNCTION get_variable:" )
    print( "\t" )
    print( "\tIt catches the data from previous command output" )
    print( "\tResult will be saved in config variable" )
    print( "\t" )
    print( "\tHow to define:" )
    print( "\t\t- get_variable     :" )
    print( "\t\t    - line       : 0" )
    print( "\t\t    - delimeters : '|'" )
    print( "\t\t    - index      : '1:2'" )
    print( "\t\t    - pattern    : '^....-....-....-....$'" )
    print( "\t\t    - saveas     : 'VM_id'" )
    print( "\t\t    - dontfail   : False" )
    print( "\t" )
    print( "\t\tOPTIONS:" )
    print( "\t\t   line" )
    print( "\t\t      id of the line where to get the variable data" )
    print( "\t\t   " )
    print( "\t\t   delimeter" )
    print( "\t\t      symbol which will be used to split line" )
    print( "\t\t   " )
    print( "\t\t   index" )
    print( "\t\t      list slice in python notation ('X:Y', ':Y', 'X:', ':') " )
    print( "\t\t      will construct variable by joining list elements from this slice" )
    print( "\t\t   " )
    print( "\t\t   pattern" )
    print( "\t\t      regexp to check resulting variable" )
    print( "\t\t      will be not checked if omited or empty" )
    print( "\t\t   " )
    print( "\t\t   saveas" )
    print( "\t\t      name of the variable in config to save result" )
    print( "\t\t   " )
    print( "\t\t   dontfail" )
    print( "\t\t      if 'True', script will always return 0 exit code (OK)" )
    print( "\t\t   " )
    print( "\t" )
    print( "\tEXAMPLE:" )
    print( "\t\t- action        : start_VM" )
    print( "\t\t- grep          :" )
    print( "\t\t  - patterns :" )
    print( "\t\t     - '%(VM_NAME)s'" )
    print( "\t\t- get_variable  :" )
    print( "\t\t  - index      : '0:1'" )
    print( "\t\t  - pattern    : ^........-....-....-....-............$" )
    print( "\t\t  - saveas     : 'VM_id'" )
    print( "\t" )

#############################################
#  MAIN EXECUTOR FOR PLUGIN
############################################

def run( action, config, data):
    return_code, return_line = 0, "All OK"

    #print "--------get var----------- %s" % data["param"]
    #print "--------get var----------- %s" % config["lastOutput"]

    run_parameters           = setParameters( params=data["param"] )
    return_code, return_line = getVariable( lines=config["lastOutput"], params=run_parameters )

    if return_code == 0:
        logger.debug("Saving '%s' into config['%s']" % (return_line, run_parameters["saveas"]))
        config[run_parameters["saveas"]] = return_line

    if run_parameters["dontfail"]: return_code = 0
    return (return_code, return_line)
