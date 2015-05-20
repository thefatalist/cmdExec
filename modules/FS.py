#!/usr/bin/python

#
#   Base library to Downloader and Uploader scripts
#

#from time import sleep, gmtime, mktime
from time import gmtime

#import lockfile
from sys import exit
from os import makedirs
from os.path import isfile, exists, dirname
import smtplib

import yaml
import logging

logger = None

################## USEFUL FUNCTIONS
# Substitute variable data if it is necessary
def getSubstitutedVariable( key, config ):
    #if '%(' not in data[key]: return data[key]
    try:
        value = config[key] % config
    except TypeError:
        value = config[key]
        return True
    if '%(' not in value:
        config[key] = str(value)
        return True
    logger.debug('\t\tNested substitution for key "%s" is needed. Current value is "%s"' % (key, config[key]))
    return False


# Substitute all strings
def getSubstitutedDict( config ):
    repeat = False
    for key in config.iterkeys():
        if not getSubstitutedVariable( key=key, config=config ): repeat = True
    if repeat: getSubstitutedDict( config=config )


################## CLASSES
class ConfigStorage():
    def __init__( self, confAddr, actionName, cmdParameters ):
        if not confAddr:
            logger.error("confAddr(%s) is missing" % (confAddr))
            raise ValueError
        if not isinstance(confAddr, str) or (actionName and not isinstance(actionName, str)):
            logger.error("confAddr(%s) or actionName(%s) aren't strings" % (type(confAddr), type(actionName)))
            raise TypeError
        self.cmdParameters            = cmdParameters
        self.dataDict                 = self.readConfigFile( confAddr=confAddr     )
        self.config, self.actionDict  = self.getConfig(      actionName=actionName )
        self.actions                  = self.getExecList(    actionName=actionName )
        #if not self.actions:
        #    raise ValueError("Selected action is invalid, no data returned")


    # Reads script configuration file
    def readConfigFile( self, confAddr="" ):
        if not isfile( confAddr ):
            logging.error( "No configuration file with name \"%s\" found.\n" % confAddr )
            return None
        with open( confAddr, "r" ) as stream:
            try:
                cfg = yaml.load( stream )
            except Exception as err:
                logging.error(
                                       "\nERROR:\nCould not Parse configuration file \"%s\":\n%s\n" %
                                (confAddr, err) )
                #logging.exception( "Could not Parse configuration file \"%s\"\n" % (confAddr) )
                cfg = None
        return cfg
    
    
    # Reads only configuration data + configs of selected action
    def getConfig( self, actionName="test" ):
        if not self.dataDict: return None
        baseConfig    = self.dataDict.get( "config",   {} )
        actionDict    = self.dataDict.get( "commands", {} )
        actionData    = self.dataDict.get( actionName, {} )
        cmdParameters = self.dataDict.get( "cmdParameters", {} )
        actionConfig  = actionData.get(    "config",   {} )
        cmdParameters = self.cmdParameters

        config = {}
        logger.debug("\nGetting base config")
        for el in baseConfig:
            logger.debug("\tadding %20s [ %-45s ]" % (el, baseConfig[el]) )
            config[ el ] = baseConfig[ el ]

        logger.debug("\nGetting \"%s\" action config" % actionName)
        for el in actionConfig:
            logger.debug("\tadding %20s [ %-45s ]" % (el, actionConfig[el]) )
            config[ el ] = actionConfig[ el ]

        logger.debug("\nGetting command line config options")
        for el in cmdParameters:
            logger.debug("\tadding %20s [ %-45s ]" % (el, cmdParameters[el]) )
            config[ el ] = cmdParameters[ el ]

        logger.debug("==============================")
        logger.debug("\nResulting set of config options:")
        getSubstitutedDict( config=config )
        for key,val in config.iteritems():
            #try:
            #    val = val % config
            #except TypeError:
            #    val = val
            #config[key] = val
            logger.debug("\t       %20s [ %-45s ]" % (key, val) )


        return (config, actionDict)
    
    # Reads exec list for selected action
    def getExecList( self, actionName="test" ):
        logger.debug("Reading action list for \"%s\" action" % actionName )
        actionData   = self.dataDict.get( actionName, {} )
        actions      = actionData.get( "execlist", {} )
        return actions


    # Generates list of commands from action and fallback items
    def genCMDs(self, cmdList):
        result = []
        for cmd in cmdList:
            if not cmd:
                result.append("")
                continue
            logger.debug("\tProcessing: %20s ( %s ):" % (cmd, self.actionDict[cmd]) )
            try:
                line = self.actionDict[cmd] % self.config
            except KeyError:
                logger.exception("\n! Unknown key in the following command:\n%s\nAborting." % self.actionDict[cmd])
                exit(1)
            logger.debug("\tGenerated line: %s" % line)
            result.append( line )
        return result

    # Generates list of commands from action and fallback items
    def genCMD(self, cmd):
        if not cmd: return None
        try:
            line = self.actionDict[cmd] % self.config
        except KeyError:
            #print cmd
            logger.exception("\n! Unknown key in the following command:\n%s\nAborting." % self.actionDict[cmd])
            return None
        return line


################## DEFINED FUNCTIONS
# Setup Logging
def setLogging( logFileName="temp.log", logLevel=logging.DEBUG ):
    global logger
    if not exists( dirname( logFileName) ):
        makedirs( dirname( logFileName) )

    logger = logging.getLogger()
    logger.setLevel( logging.DEBUG )

    ch = logging.StreamHandler()
    ch.setLevel( logLevel )
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter( formatter )
    logger.addHandler( ch )

    fh = logging.FileHandler( logFileName )
    fh.setLevel( logging.INFO )
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)



# Sends email
def emailSend( message, recipient, subject="Uploader or Downloader script notification", FROM="Uploader_noreply@wolterskluwer.com"):
    BODY = "\r\n".join((
                "From: %s"    % FROM,
                "To: %s"      % recipient,
                "Subject: %s" % subject,
                "",
message
            ))
    print( BODY )

    server = smtplib.SMTP( ProgramConf.get("mailhost","10.60.40.16") )
    server.sendmail( FROM, recipient.split("; "), BODY)
    server.quit()


if __name__ == "__main__":
    print( "You should not run this file alone." )
    print( "Use it as imported module" )
