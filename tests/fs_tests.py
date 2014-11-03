#!/usr/bin/python2.7

from time import sleep, gmtime
from mocker import Mocker, ANY, MockerTestCase
from unittest import main, TestCase

import logging

LOGGER_LOGFILE = "./LOGS/test_FS.log"

logger = logging.getLogger()
logger.setLevel( logging.CRITICAL )
#logger.setLevel( logging.DEBUG )

ch = logging.StreamHandler()
ch.setLevel( logging.DEBUG )
formatter = logging.Formatter('%(message)s')
ch.setFormatter( formatter )
logger.addHandler( ch )

fh = logging.FileHandler( LOGGER_LOGFILE )
fh.setLevel( logging.INFO )
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


# Function which replaces output of DLib.echo
def fake_echo( *args, **kwargs ):
	print( "Args: ", args )
	print( "KWArgs: ", kwargs )

def fake_echo_silent( *args, **kwargs ):
	pass



###################################################

# Test config storage
class test_ConfigStorage( MockerTestCase ):
	from modules import FS

	listEmpty = []
	listOne   = ["always_success", ""]

	params   = {
		'DEFAULT_CONFIG'   : "./ExecCMD.yaml",
		'DEFAULT_LOG'      : "./LOGS/ExecCMD_TESTING.log",
		#'DEFAULT_LOGLEVEL' : logging.DEBUG,
		'DEFAULT_LOGLEVEL' : logging.INFO,
		'DONT_EXECUTE'     : False,
		'LIST_ACTIONS'     : False,
		'ACTION'           : None,
				}
	#self.execDetails  = [
	#					{"start":"AAA", "startSec":"BBBB"},
	#					{"start":"AAA", "startSec":"BBBB", "finish":"CCCC", "total":"DDDD"},
	#					]
	execList_empty = []
	execList_one_good = [
		["always_success", "always_fail" ]
	]
	execList_one_bad = [
		["always_fail", "always_fail" ]
	]
	execList_many_bad = [
		["always_success", []            ],
		["always_success", "always_fail" ],
		["always_success", []            ],
		["always_success", []            ],
		["always_fail",    []            ]
	]
	dataNone   = [
							{"confAddr"  : None,
							"actionName" : None},
							{"raise"     : ValueError}
						]
	dataEmpty   = [
							{"confAddr"  : "",
							"actionName" : ""},
							{"raise"     : ValueError}
						]
	dataIncorrect   = [
							{"confAddr"  : 123,
							"actionName" : 456},
							{"raise"     : TypeError}
						]
	dataNoConfig   = [
							{"confAddr"  : "./NOSUCHCONFIG.yaml",
							"actionName" : ""},
							{"raise"     : ValueError}
						]
	dataGoodconfigNoaction   = [
							{"confAddr"  : "./CONFIGS/testconf.yaml",
							"actionName" : ""},
							{"raise"     : ValueError}
						]
	dataGoodconfigBadaction   = [
							{"confAddr"  : "./CONFIGS/testconf.yaml",
							"actionName" : 123},
							{"raise"     : TypeError}
						]
	dataGoodconfigWrongaction   = [
							{"confAddr"  : "./CONFIGS/testconf.yaml",
							"actionName" : "thereisnosuchaction"},
							{"raise"     : ValueError}
						]
	dataGoodconfigCorrectaction   = [
							{"confAddr"  : "./CONFIGS/testconf.yaml",
							"actionName" : "test"},
							{"isinstance" : FS.ConfigStorage }
						]

	def prepare_replaceExecCMD(self, cmd, output):
		self.m_exec = self.mocker.replace('ExecLib.execCMD')
		self.m_exec( cmd=cmd, listoferrors=ANY )
		self.mocker.result( output )

	def prepare_replaceEcho(self, printParams=False):
		self.m_echo = self.mocker.replace('DLib.echo')
		self.m_echo( ANY, level=ANY )
		self.mocker.count( 1, None )
		if printParams:
			self.mocker.call( fake_echo )
		else:
			self.mocker.call( fake_echo_silent )

	#########################
	#### Check procedures
	#########################


	def setUp(self):
		print("replacing CommandExecutor")

		from modules import FS
		self.testObj = FS.ConfigStorage

		FS.logger = logger

		print("Done")
		#from ExecLib import runCommandList
		#self.runCommandList = runCommandList
		#self.m_Details = self.mocker.replace('DLib.getExecDetails')
		##self.m_Details( processPeriod="START", data=ANY )
	
	def checkValues( self, result, compareData ):
		print("\n\nCHECK = %s" % result )
		for key, value in compareData.iteritems():
			if key == "result":
				self.assertEqual( result, value )
				continue
			if key == "isinstance":
				self.assertIsInstance( result, value)
				#self.assertEqual( isinstance(result, value), True )
				continue
			if key == "raise":
				print("SHOULD RAISE ERROR!!!!!!!!!!!!")
			self.fail( "Missing expected data!" )



	def checkProcedure( self, testData ):

		self.mocker.replay()
		print("Test with %s" % testData[0])
		print("Checks %s" % testData[1])

		if testData[1].has_key("raise"):
			print("SHOULD RAISE ERROR!!!!!!!!!!!!")
			with self.assertRaises( testData[1]["raise"] ):
				check = self.testObj( **testData[0] )
			return

		check = self.testObj( **testData[0] )
		print "CHECK = %s" % check
		if check and isinstance( check, dict ):
			for key in check:
				if check[ key ] != testData[1][key]:
					print( " . \"%s\":" % key )
					print( "\t%s" % check[key] )
					print( "\t%s" % testData[1][key] )
				self.assertEqual( check[ key ], testData[1][key] )

		self.checkValues(check, testData[1])


		#self.assertEqual( check, testData[1] )

	#########################
	#### TESTS
	#########################


	#def prepare_replaceExecCMD(self, cmd, output):
	#	self.m_exec = self.mocker.replace('ExecLib.execCMD')
	#	self.m_exec( cmd=cmd, listoferrors=ANY )
	#	self.mocker.result( output )

	def test_init_empty(self):
		self.checkProcedure( self.dataEmpty )
		self.checkProcedure( self.dataNone )

	def test_init_incorrect(self):
		self.checkProcedure( self.dataIncorrect )

	def test_init_noConfig(self):
		self.checkProcedure( self.dataNoConfig )

	def test_init_GoodConfig_BadActions(self):
		self.checkProcedure( self.dataGoodconfigNoaction )
		self.checkProcedure( self.dataGoodconfigBadaction )
		self.checkProcedure( self.dataGoodconfigWrongaction )

	def test_init_GoodConfig_GoodAction(self):
		self.checkProcedure( self.dataGoodconfigCorrectaction )
