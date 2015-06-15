#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Script runs selected actions
#

#from modules  import ExecLib
import ExecLib
from sys      import argv, exit
#from modules  import FS
import FS
from time     import sleep, gmtime, mktime

import logging
logger = logging.getLogger()

############## PROCEDURES

# Help message
def displayHelp():
    print "Usage: %s [-h] [-c CONFIG] [-p] -l|ACTION"
    print "\t-h        : display usage help"
    print "\t-c CONFIG : use specified config file instead of default \"%s\"" % config['DEFAULT_CONFIG']
    print "\t-p        : don't execute actions, just display them (the same as -l ACTION)"
    print "\t-l        : display list of available commands"
    print "\tACTION    : execute ACTION defined in config file"
    print ""
    print "CONFIG FORMAT:"
    print "\tITEM_NAME:"
    print "\t  config:           # Script internal variables"
    print "\t    ignoreerrors    : VALUE"
    print "\t    folder          : VALUE"
    print "\t    errorlist       : LIST OF VALUES"
    print "\t        - 1ExecCMD.py"
    print "\t        - drwxrwxrwx"
    print ""
    print "\t  config:           # List of actions to be executed one by one"
    print "\t        - action  :   VALUE"
    print ""
    print "POSSIBLE ACTIONS:"
    print ""
    exit(1)


# Grep procedures
def output_grep( data, pattern ):
    result = [1, '']
    for line in data.split('\n'):
        logger.debug(" -> %s" % (line))
        for pattern in patternlist:
            if pattern in line:
                result = [0, result[1]+line+'\n' ]
    return result

def output_nogrep( data, patternlist ):
    result = [0, '']
    for line in data.split('\n'):
        logger.debug(" x> %s" % (line))
        for pattern in patternlist:
            if pattern in line:
                result = [1, result[1]+line+'\n']
    return result

# Decorator for function execution
# It counts time spent for function execution
def timeExecution( func ):
    def timeFunction( *args, **kwargs ):
        logger.debug("Timing decorator executed for \"%s\" function" % func.func_name )
        time_start =  mktime( gmtime() )

        result = func( *args, **kwargs )

        time_end   =  mktime( gmtime() )
        if result == 0: RESULT     =  "SUCCESS"
        else:           RESULT     =  "FAIL"
        #logger.info( "%s seconds spent to execute \"%s\" Action. [%s]" % (time_end-time_start, config['ACTION'], RESULT) )
        logger.info("\n--------------------------------")
        logger.info( "[%s] | %s seconds spent to execute action." % (RESULT, time_end-time_start) )
        logger.info("--------------------------------\n")

        return result
    return timeFunction


# Check if result containing all of required lines
def resultContainsAllOf( data, checklist ):
    if not checklist: return [0, '']
    if isinstance( checklist, str): checklist = [ checklist ]
    logger.info("[FAILIFNOT] Checking is output contains all of the list %s\n" % checklist )
    for pattern in checklist:
        print " checking for PATTERN [%s]" % pattern
        if not pattern in data:
            print " PATTERN [%s] is NOT FOUND!" % pattern
            return [-5, "The \"%s\" is not found in command output" % pattern ]
    print " ALL PATTERNS ARE PRESENT!\n"
    return [0, data]

########################

class PluginLoader():
    def __init__(self, plugin_template="plugin_"):
        from os import path, listdir
        modules_dir = path.dirname(path.realpath(__file__))

        # Get list of all plugins
        self.files = [file for file in listdir( modules_dir ) if
                                    file.startswith(plugin_template) and
                                    file.endswith('.py') ]
        self.plugins = {}


    def getPlugins(self):
        for file in self.files:
            name = file[:-3]
            logger.debug('Loading "%s" module' % name)
            import plugin_action
            self.plugins[name] = __import__(name, globals(), locals(), ['object'], -1)
        return self.plugins


######################## CLASS

class CommandExecutor():
    #def __init__(self, config, execFunc ):
    def __init__(self, config ):
        #self.config   = PluginLoader("config_")
        self.actions  = PluginLoader("plugin_").getPlugins()

        self.yaml     = FS.ConfigStorage( confAddr=config['DEFAULT_CONFIG'], actionName=config['ACTION'], cmdParameters=config['PARAMETERS'] )
        self.genCMD   = self.yaml.genCMD
        self.execFunc = ExecLib.execAction
        #self.execFunc = execFunc

    # Function which will list all available actions in config file
    def listActions( self, action=None ):
        yaml = self.yaml
        if not action:
            print("Listing available actions:")
            dataDict = yaml.dataDict
            for key in sorted( dataDict.keys() ):
                if key in ["config","commands"]: continue
                print "\t%s" % key
        else:
            print("List of commands to be executed for the \"%s\" action:" % action)
            print("\t%42s |   | %s" % ("== Action ==", "== Fallback action ==" ))
            fallback = ''
            for num, step in enumerate( yaml.actions ):
                status = ''
                if step.has_key('action') or step.has_key('fallback'):
                    step_action   = step.get('action',  {}).get('cmd','')
                    step_fallback = step.get('fallback',{}).get('cmd','')
                    print ("\t%42s |   | %s" % (step_action, step_fallback) )


    # Function which will execute selected action
    @timeExecution
    def runAction( self, action ):
        yaml = self.yaml
        cancelonerror = yaml.config.get('ignoreerrors', False)
        errorlist = []
        print("Runing commands for the \"%s\" action (Ignore errors %s ):" % (action, cancelonerror))

        lastresult = self.execActionList( actionlist=self.yaml.actions, cancelonerror=cancelonerror )

        if lastresult[0] != 0:
            logger.info("The \"%s\" command returned (%s) errorcode.\n" % (action, lastresult[0]) )

            # Prepare list of fallback actions to execute
            fallback_actions = []
            for num, action in enumerate( lastresult[2][::-1] ):
                if not action: continue
                fallback_actions.append( {'action' : action} )

            # Run the prepared list of actions
            result = self.execActionList( actionlist=fallback_actions, cancelonerror=False )

        return lastresult[0]

    # Execute one action step
    def execStep(self, step, action, config, data):
        retry_count  = int(   step.pop("retry_count", 1  ) )
        retry_sleep  = float( step.pop("retry_sleep", 0.0) )

        print config
        for i in xrange( retry_count ):
            result = self.actions["plugin_action"].run(
                         action = action
                        ,config = config
                        ,data   = data
                     )
    #        result = self.execFunc( action=action, listoferrors=failif, genCMD=self.genCMD, num=num+1, silent=True )
            if not result: break

    #        if (lastresult[0] == 0) or (retry_count == i+1) :
            if (result[0] == 0) or (retry_count == i+1) :
                break

            print("\nExecution failed [%s/%s], retry in %s seconds.\n" % (i+1, retry_count, retry_sleep) )
            sleep( retry_sleep )
        return result




    #############################
    # Executes list of actions
    #
    # For each step it should get "ACTION" (execute) and "FALLBACK" (put in a queue) commands
    # Then it executes other commands
    #
    #############################
    def execActionList( self, actionlist, cancelonerror=False ):
        totalresults         = []
        lastresult           = [0, '']
        fallbacklist         = []
        config               = self.yaml.config
        config["lastOutput"] = ""
        config["lastResult"] = 0
        config["exitStatus"] = 0
        data = {
             "genCMD"     : self.genCMD
            ,"num"        : 0
            ,"lastOutput" : ""
            ,"lastResult" : None
            ,"failif"     : ""
            ,"failifnot"  : ""
        }
        #print "------------->"
        #print config
        #print "------------->"
        for num, step in enumerate( actionlist ):
            #logger.debug( step )

            action = step.pop("action", "")
            fallbacklist.append( step.pop("fallback", "") )

            data["num"]  = num
            data["step"] = step

            result = ""

            # Check if previous run of action command were failed
            #if config["exitStatus"] != 0 and not cancelonerror: return (lastresult[0], lastresult[1], fallbacklist )
            #if config["exitStatus"] != 0 and not cancelonerror: return (config["exitStatus"], lastresult[1], fallbacklist )

            # RUN Action
            if action:
                if config["exitStatus"] != 0 and not cancelonerror: return (config["exitStatus"], lastresult[1], fallbacklist )
                logger.debug( "\n## RUNNING ACTION" )
                logger.info("")
                #result = self.execStep( step=step, action=action, config=config, data=data )
                data[ "plugin" ] = "action"
                data[ "param"  ] = action
                result = self.actions["plugin_action2"].run(
                                     action  = action
                                    ,config  = config
                                    ,data    = data
                )
                totalresults.append( result[0] )

            else:
                # Now we can run other action plugins
                for plugin, param in step.iteritems():
                    logger.debug( "\n## RUNNING Other commands" )
                    data[ "plugin" ] = plugin
                    data[ "param"  ] = param
                    result = self.actions["plugin_"+plugin].run(
                                         action  = action
                                        ,config  = config
                                        ,data    = data
                    )

            if not result: continue

            if lastresult[0] == 0: lastresult = result

            if result[0] != 0:
                if config["exitStatus"] == 0:
                    #print( "Changing exit status to '%s'" % result[0] )
                    config["exitStatus"] = result[0]
                logger.error("--> ERROR: %s\n" % result[1] )

            #if lastresult[0] != 0 and not cancelonerror: return (lastresult[0], lastresult[1], fallbacklist )
            
            config["lastOutput"] = lastresult[1]

    
        #return [lastresult[0], lastresult[1], fallbacklist]
        return [config["exitStatus"], lastresult[1], fallbacklist]



############################
# Main cycle of the program
if __name__ == "__main__":
    FS.setLogging( logFileName = config['DEFAULT_LOG'], logLevel=config['DEFAULT_LOGLEVEL'] )
    logger = logging.getLogger()

    parseArgv( config, logger )

    #conf   = FS.ConfigStorage( confAddr=config['DEFAULT_CONFIG'], actionName=config['ACTION'] )
    #conf   = FS.ConfigStorage( confAddr=config['DEFAULT_CONFIG'], actionName=config['ACTION'] )
    executor = CommandExecutor( config=config, execFunc=ExecLib.execAction )

    logger.debug("\nChecking which action is choosen:")
    #DLib.updateCurrentFile( ovaparams["VMname"], CurrentStatus )
    result = 0
    if config['ACTION'] and ( not config['LIST_ACTIONS'] and not config['DONT_EXECUTE']):
        logger.debug("\tThe ACTION \"%s\" is set, while LIST_ACTIONS is not set" % config['ACTION'])
        try:
            #executor.runAction( config=conf, action=config['ACTION'] )
            result = executor.runAction( action=config['ACTION'] )
        except KeyboardInterrupt:
            logger.error("\nExit due to Keyboard Interrupt\n")
            exit(1)

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
