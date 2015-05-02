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

import argparse
import logging
logger = logging.getLogger()

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
#def getPluginHelp( plugin, params ):
#    logger.info('Loading "%s" module help' % plugin)
#    from sys import path
#    path.insert(0, "./modules")
#    plugin_name = "plugin_"+plugin
#    plugin = __import__(plugin_name, globals(), locals(), ['object'], -1)
#    try:
#        plugin.help(params)
#    except AttributeError as err:
#        logger.error('\nIt is not possible to show help for "%s" module. ERROR:\n\t%s\n' % (plugin_name, err) )
#    exit(1)

def getPluginHelp( data ):
    plugin, params = data.module[0], data.module[1:]
    logger.info('Loading "%s" module help' % plugin)
    from sys import path
    path.insert(0, "./modules")
    plugin_name = "plugin_"+plugin
    plugin = __import__(plugin_name, globals(), locals(), ['object'], -1)
    try:
        plugin.help(params)
    except AttributeError as err:
        logger.error('\nIt is not possible to show help for "%s" module. ERROR:\n\t%s\n' % (plugin_name, err) )


# Help message
#def displayHelp( data ):
#    print data
#    data.pop( data.index('-h') )
#    if data:
#        plugin = data[0]
#        params = data[1:]
#        getPluginHelp( plugin=plugin, params=params )
#
#    print "Usage: %s [-h] [-c CONFIG] [-p] -l|ACTION"
#    print "\t-h        : display usage help"
#    print "\t-c CONFIG : use specified config file instead of default \"%s\"" % config['DEFAULT_CONFIG']
#    print "\t-p        : don't execute actions, just display them (the same as -l ACTION)"
#    print "\t-l        : display list of available commands"
#    print "\tACTION    : execute ACTION defined in config file"
#    print ""
#    exit(1)


# Print out list of installed plugins
def listPlugins( data ):
    logger.info("List of installed plugins:")
    config['LIST_ACTIONS'] = True
    from glob import glob
    modules = glob("./modules/plugin_*.py")
    for module in modules:
        print( "\t%s" % module[17:-3])


# Check that config file exists
def configFile(filename):
    from os.path import isfile
    if not isfile(filename):
        raise argparse.ArgumentTypeError("File '%s' could not be found" % filename)
    return filename


# List action
def listActions( data ):
    executor = ExecLibrary.CommandExecutor( config=config )
    logger.debug("\tThe LIST_ACTIONS(%s) or DONT_EXECUTE(%s) is set. Running proper procedure" %
                (config['LIST_ACTIONS'], config['DONT_EXECUTE']))
    #executor.listActions( action=config['ACTION'] )
    #executor.listActions( action=data.action )
    executor.listActions( action=None )



# Run actions
def runActions( data ):
    config['ACTION'] = data.action
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
        #displayHelp()

    exit(result)



# Parse args using argparser module
def parse_args():
    parser = argparse.ArgumentParser(description="This tool is designed to run short command scripts with possible fallback actions")
    parser.add_argument("-v", "--debug",   action="store_const", help="Enable debugging", const=logging.DEBUG)
    parser.add_argument("-c", "--config",
            type    = configFile,
            #type    = argparse.FileType('r'),
            action  = "store", help="use specified config file instead of default \"%s\"" % config['DEFAULT_CONFIG'],
            default = config['DEFAULT_CONFIG'])
    parser.add_argument("-p", "--prevent", action="store_true", help="don't execute actions, just display them (the same as -l ACTION)")
    #parser.add_argument("-l", "--list", action="store_true", help="display list of available commands")
    #parser.add_argument("doc", nargs="+", help="Get documentation for one of the modules. To list modules, use -l key")
    #parser.add_argument("action", help="execute ACTION defined in config file")
    subparser  = parser.add_subparsers(help="Sub commands help")

    # Prints out modules internal documentation
    doc_parser = subparser.add_parser("doc", help="Get documentation for one of the plugin modules. To list modules, use 'list' key")
    doc_parser.add_argument("module", nargs="+", help="Name of the module to see it's documentation")
    doc_parser.set_defaults(func=getPluginHelp)

    # List all installed modules
    doc_parser = subparser.add_parser("plugins", help="List all installed plugin modules. To read module documentation, use 'doc' key")
    doc_parser.set_defaults(func=listPlugins)

    # List all actions in config file
    doc_parser = subparser.add_parser("actions", help="List all actions in the config file")
    doc_parser.set_defaults(func=listActions)

    # Run action list from config file
    doc_parser = subparser.add_parser("run", help="Execute list of actions from config file")
    doc_parser.add_argument("action", nargs="?", help="Name of the action")
    doc_parser.set_defaults(func=runActions)

    # Put obtained parameters into config
    parser = parser.parse_args()
    FS.setLogging( logFileName = config['DEFAULT_LOG'], logLevel=parser.debug or config["DEFAULT_LOGLEVEL"] )
    config['DONT_EXECUTE']   = parser.prevent
    config['DEFAULT_CONFIG'] = parser.config
    return parser

# Parse command line arguments
#def parseArgv( config, logger ):
#    logger.debug("Reading program parameters:")
#    if len(argv) < 2: argv.append('-h')
#
#    prevcmd   = ''
#    for arg in argv[1:]:
#        if   arg == '-h':     displayHelp(data=argv[1:])
#        elif arg == '-c':     logger.info("\tCustom config file is used")
#        elif arg == '-d':
#            logger.setLevel( logging.DEBUG )
#            logger.debug("\tDebug enabled")
#        elif arg == '-p':
#            config['DONT_EXECUTE'] = True
#            logger.info("\tDont'e execute flag is setup")
#        elif arg == '-l':
#            config['LIST_ACTIONS'] = True
#            logger.info("List actions selected")
#        # arg is a COMMAND or FILE Path
#        else:
#            if prevcmd == '-c':  config['DEFAULT_CONFIG'] = arg
#            elif not config['ACTION']:
#                logger.info( "\tSelected action is \"%s\"" % arg )
#                config['ACTION'] = arg
#            else:
#                logger.error("\n\tToo much arguments! Exit.\n")
#                displayHelp()
#        prevcmd = arg




############################
# Main cycle of the program
if __name__ == "__main__":

    args = parse_args()
    args.func(args)
    exit(1)

    # Open the log files
    #FS.setLogging( logFileName = config['DEFAULT_LOG'], logLevel=args.debug or config["DEFAULT_LOGLEVEL"] )
    #FS.setLogging( logFileName = config['DEFAULT_LOG'], logLevel=config['DEFAULT_LOGLEVEL'] )
    #logger = logging.getLogger()

    # Get command line parameters
    #parseArgv( config, logger )

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
