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
        print('\nNo module with "%s" is installed. ERROR:\n\t%s\n' % (plugin_name, err))

    exit(1)


# Print out list of installed plugins
def listPlugins( ):
    logger.info("\nList of installed plugins:")
    #config['LIST_ACTIONS'] = True
    from glob import glob
    modules = glob("./modules/plugin_*.py")
    for module in modules:
        print( "\t%s" % module[17:-3])
    logger.info("\nTo read plugin documentation, run `./cmdExec.py -h PLUGIN_NAME` command.\n")


# Help message
def displayHelp( data ):
    data.pop( data.index('-h') )
    if data:
        plugin = data[0]
        params = data[1:]
        getPluginHelp( plugin=plugin, params=params )

    print "Usage: %s [-h PLUGIN] [-v] [-c CONFIG] -p|-l|ACTION"
    print "\t-v          : display debug messages"
    print "\t-h [PLUGIN] : display usage help, or display PLUGIN help"
    print "\t-p          : display list of installed plugin modules"
    print "\t-c CONFIG   : use specified config file instead of default \"%s\"" % config['DEFAULT_CONFIG']
    #print "\t-p        : don't execute actions, just display them (the same as -l ACTION)"
    print "\t-l          : display list of available commands"
    print "\tACTION      : execute ACTION defined in config file"
    print ""
    exit(1)


# Parse command line arguments
def parseArgv( config, logger ):
    logger.debug("Reading program parameters:")
    if len(argv) < 2: argv.append('-h')

    prevcmd   = ''
    for arg in argv[1:]:
        if   arg == '-h':     displayHelp(data=argv[1:])
        elif arg == '-c':     logger.info("\tCustom config file is used")
        elif arg == '-v':
            print("Debug is enabled")
            config['DEFAULT_LOGLEVEL'] = logging.DEBUG
        elif arg == '-p':
            #config['DONT_EXECUTE'] = True
            #logger.info("\tDont'e execute flag is setup")
            listPlugins()
            exit(1)
        elif arg == '-l':
            config['LIST_ACTIONS'] = True
            logger.info("List actions selected")
        # arg is a COMMAND or FILE Path
        else:
            if prevcmd == '-c':  config['DEFAULT_CONFIG'] = arg
            elif not config['ACTION']:
                logger.info( "\tSelected action is \"%s\"" % arg )
                config['ACTION'] = arg
            else:
                logger.error("\n\tToo much arguments! Exit.\n")
                displayHelp()
        prevcmd = arg




############################
# Main cycle of the program
if __name__ == "__main__":
    # Get command line parameters
    logger = logging.getLogger()
    parseArgv( config, logger )

    # Open the log files according to run parameters
    FS.setLogging( logFileName = config['DEFAULT_LOG'], logLevel=config['DEFAULT_LOGLEVEL'] )

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
