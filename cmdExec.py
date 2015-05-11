#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Script runs selected actions
#

#from modules  import ExecLib
from modules  import ExecLibrary
from sys      import argv, exit
from modules  import FS
from time     import sleep, gmtime, mktime

import logging

############## DEFAULTS

UTC_TIME         = gmtime()
CURRENT_DATE     = "%s-%s-%s" % (UTC_TIME[0], UTC_TIME[1], UTC_TIME[2])

config = {
    'DEFAULT_CONFIG'   : "./cmdExec.yaml",
    'DEFAULT_LOG'      : "./LOGS/cmdExec" + CURRENT_DATE + ".log",
    #'DEFAULT_LOGLEVEL' : logging.DEBUG,
    'DEFAULT_LOGLEVEL' : logging.INFO,
    'DONT_EXECUTE'     : False,
    'LIST_ACTIONS'     : False,
    'ACTION'           : None,
    'lastOutput'       : '',
    # PARAMETES will be obtained from readline
    'PARAMETERS'       : {}
}

############## PROCEDURES
# Run help from the plugin module
def getPluginHelp( plugin, params ):
    logger.info('Loading "%s" module help' % plugin)
    from sys import path
    path.insert(0, "./modules")
    plugin_name = "plugin_"+plugin
    try:
        plugin = __import__(plugin_name, globals(), locals(), ['object'], -1)
        plugin.help(params)
    except AttributeError as err:
        #logger.error('\nIt is not possible to show help for "%s" module. ERROR:\n\t%s\n' % (plugin_name, err) )
        print('\nIt is not possible to show help for "%s" module. ERROR:\n\t%s\n' % (plugin_name, err) )
    except ImportError as err:
        #logger.error('\nNo module with "%s" is installed. ERROR:\n\t%s\n' % (plugin_name, err))
        print('\nNo module with "%s" name is found. ERROR:\n\t%s\n' % (plugin_name, err))
        print('Consider checking the installed plugins')
        return False
    exit(1)


# Print out plugin help
def displayPluinHelp( data ):
    if not data: return False
    plugin = data[0]
    params = data[1:]
    getPluginHelp( plugin=plugin, params=params )


# Print out list of installed plugins
def listPlugins( data=None ):
    displayPluinHelp( data=data )
    #logger.info("\nList of installed plugins:")
    print("\nList of installed plugins:")
    #config['LIST_ACTIONS'] = True
    from glob import glob
    modules = glob("./modules/plugin_*.py")
    for module in modules:
        print( "\t%s" % module[17:-3])
    logger.info("\nTo read plugin documentation, run `./cmdExec.py (-h|-p) PLUGIN_NAME` command.\n")


# Help message
def displayHelp( data ):
    displayPluinHelp( data = data )

    print "Usage: %s [-h PLUGIN] [-v] [-c CONFIG] -p|-l|ACTION [PARAMETERS...]"
    print "\t-v          : display debug messages"
    print "\t-h [PLUGIN] : display usage help, or display PLUGIN help"
    print "\t-p [PLUGIN] : display list of installed plugin modules, or display PLUGIN help"
    print "\t-c CONFIG   : use specified config file instead of default \"%s\"" % config['DEFAULT_CONFIG']
    #print "\t-p        : don't execute actions, just display them (the same as -l ACTION)"
    print "\t-l          : display list of available commands"
    print "\tACTION      : execute ACTION defined in config file"
    print "\tPARAMETERS  : list of KEY:VAL data that will be used in actions as variables"
    print ""
    exit(1)

# Get parameters from command line
def getParameters( data ):
    """
        All provided data will be split by ":" sign and converted to the dictionary:
        "NAME:VALUE" ->  "NAME" : "VALUE"
        "NAME"       ->  "NAME" : True
    """
    logger.debug("Provided parameters: %s" % data)
    for parameter in data:
        try:
            key, val = parameter.split(':')
        except ValueError:
            key, val = parameter, True
        config['PARAMETERS'][key] = val
    logger.debug("Resulting data: %s" % config['PARAMETERS'])


# Set up logging
def setLogging( args ):
    result = []
    index  = 0
    for arg in args:
        index += 1
        # Enable debug
        if arg == '-v':
            print("Debug is enabled")
            config['DEFAULT_LOGLEVEL'] = logging.DEBUG
        # Change logfile location
        elif arg == '-c':
            config['DEFAULT_CONFIG'] = args[index]
        else:
            result.append( arg )

    # Enable logger
    FS.setLogging( logFileName = config['DEFAULT_LOG'], logLevel=config['DEFAULT_LOGLEVEL'] )
    logger.debug("following list of args will be parsed: %s" % result)
    return result


# Parse command line arguments
def parseArgv( config, logger ):
    args = setLogging( argv[1:] )
    logger.debug("Reading program parameters:")
    if len(args) < 1: args.append('-h')

    prevcmd   = ''
    argindex  = 0
    for arg in args:
        argindex += 1
        if   arg == '-h':     displayHelp(data=args[argindex:])
        elif arg == '-p':
            #config['DONT_EXECUTE'] = True
            #logger.info("\tDont'e execute flag is setup")
            listPlugins(data=args[argindex:])
            exit(1)
        elif arg == '-l':
            config['LIST_ACTIONS'] = True
            logger.info("List actions selected")
        # arg is a COMMAND or FILE Path
        else:
            if not config['ACTION']:
                logger.info( "\tSelected action is \"%s\"" % arg )
                config['ACTION'] = arg
            else:
                getParameters( data = args[argindex-1:] )
                #logger.error("\n\tToo much arguments! Exit.\n")
                #displayHelp()
                #exit(1)
        prevcmd = arg




############################
# Main cycle of the program
if __name__ == "__main__":
    # Get command line parameters
    logger = logging.getLogger()
    parseArgv( config, logger )


    #conf   = FS.ConfigStorage( confAddr=config['DEFAULT_CONFIG'], actionName=config['ACTION'] )
    #executor = CommandExecutor( config=config, execFunc=ExecLib.execAction )
    executor = ExecLibrary.CommandExecutor( config=config )

    logger.debug("\nChecking which action is choosen:")
    #DLib.updateCurrentFile( ovaparams["VMname"], CurrentStatus )
    result = 0

    # Case when we should EXECUTE actions
    if config['ACTION'] and ( not config['LIST_ACTIONS'] and not config['DONT_EXECUTE']):
        logger.debug("\tThe ACTION \"%s\" is set, while LIST_ACTIONS is not set" % config['ACTION'])
        try:
            #executor.runAction( config=conf, action=config['ACTION'] )
            result = executor.runAction( action=config['ACTION'] )
        except KeyboardInterrupt:
            logger.error("\nExit due to Keyboard Interrupt\n")
            exit(1)

    # Case when we should NOT exectue actions
    elif config['LIST_ACTIONS'] or config['DONT_EXECUTE']:
        logger.debug("\tThe LIST_ACTIONS(%s) or DONT_EXECUTE(%s) is set. Running proper procedure" %
                        (config['LIST_ACTIONS'], config['DONT_EXECUTE']))
        executor.listActions( action=config['ACTION'] )
        #listActions( config=conf, action=config['ACTION'] )

    else:
        logger.info("No action specified. Exit\n")
        displayHelp()

    exit(result)
    #DLib.updateCurrentFile( "Not working\n", CurrentStatus )
    #DLib.cleanDescriptors()
