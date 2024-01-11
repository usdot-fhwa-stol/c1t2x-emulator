#!/usr/bin/env python3

# Written by the USDOT Volpe National Transportation Systems Center
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.


import os, logging, time
from ruamel.yaml import YAML
from threading import Thread

from Networking.networking import UDP_NET

### Logging
c1t2x_logger = None
LOGGING_LEVEL = logging.INFO
logs_directory = os.path.join(os.getcwd(), "Logs")

# IF: Check if the Logs directory does not exist
if not os.path.exists(logs_directory):
	# Create Logs directory
	os.mkdir(logs_directory, 0o777)

# Setup logger with formatting
log_filename = "c1t2x_OBU.log"
c1t2x_logger = logging.getLogger(__name__)
c1t2x_logger.setLevel(LOGGING_LEVEL)
c1t2x_logger_handler = logging.FileHandler(os.path.join(logs_directory, log_filename), "w")
c1t2x_logger_handler.setLevel(LOGGING_LEVEL)
c1t2x_logger_formatter = logging.Formatter("[%(asctime)s.%(msecs)03d] %(levelname)s - %(message)s", datefmt= "%d-%b-%y %H:%M:%S")
c1t2x_logger_handler.setFormatter(c1t2x_logger_formatter)
c1t2x_logger.addHandler(c1t2x_logger_handler)
# Start logging
c1t2x_logger.info("\n---------------------------\nStarting C1T2X OBU Logger\n---------------------------")

# Initialize error
error = False

# Default to printing output
printData = True

### Import Configs
script_dir = os.path.dirname(__file__)
fpath = 'config/params.yaml'
file_path = os.path.join(script_dir, fpath)
try:
	y = YAML(typ='safe')
	with open(file_path,'r') as f:
		params = y.load(f)
	parseLANPacket = params['LAN_DECODE']
	parseVANETPacket = params['VANET_DECODE']
	radioApps = params['RADIO_APPS']
	printData = params['print_data']
	loopTime = params['loop_time']
	logLevel = params['logging_level']
except:
	c1t2x_logger.error("Unable to import master yaml configs")
	error = True
	print("Unable to import yaml configs")
	raise ImportError

if logLevel == 'DEBUG': c1t2x_logger.setLevel(logging.DEBUG)
elif logLevel == 'INFO': c1t2x_logger.setLevel(logging.INFO)
elif logLevel == 'ERROR': c1t2x_logger.setLevel(logging.ERROR)
elif logLevel == 'WARNING': c1t2x_logger.setLevel(logging.WARNING)
else: 
	c1t2x_logger.setLevel(logging.WARNING)
	print("Configured LOGGING LEVEL is invalid. Level is set to WARNING.")
	c1t2x_logger.warning("Configured LOGGING LEVEL is invalid. Level is set to WARNING.")


### Instantiate networks
# LAN
try:
	lan = UDP_NET(CONFIG_FILE='LAN_params.yaml',logger=c1t2x_logger)
except:
	error = True
try:
	lan.start_connection()
except:
	c1t2x_logger.warning("Not connected to a LAN interface")
	if printData:
		print("Not connected to a LAN interface")

# VANET
try:
	vanet = UDP_NET(CONFIG_FILE='VANET_params.yaml',logger=c1t2x_logger)
except:
	error = True
try:
	vanet.start_connection()
except:
	c1t2x_logger.warning("Not connected to a VANET interface")
	if printData:
		print("Not connected to a VANET interface")

def sendVANET(vPacket):
	global vanet
	vanet.send_data(vPacket)

def sendLAN(lPacket):
	global lan
	lan.send_data(lPacket)

def VANET_listening_thread():
	global error

	while not error and not vanet.error:
		try:
			pkt = vanet.recv_packets()
			c1t2x_logger.debug("Received %s from VANET" %pkt)
			if pkt:
				if not parseVANETPacket:
					sendLAN(pkt[0])
				else:
					# feature to parse incoming VANET message is not yet enabled
					c1t2x_logger.error("Feature to parse incoming VANET message is not yet enabled")
					raise NotImplementedError
				if printData:
					print(pkt)
		except:
			if printData:
				print("Waiting to configure LAN")
			c1t2x_logger.info("Waiting to configure LAN")
			time.sleep(0.25)
		time.sleep(loopTime)

	error = True
	c1t2x_logger.info("Terminating VANET Thread")

def LAN_listening_thread():
	global error

	while not error and not lan.error:
		try:
			pkt = lan.recv_packets()
			if pkt:
				if not parseLANPacket:
					sendVANET(pkt[0])
				else:
					# feature to parse incoming LAN packet is not enabled
					# this feature may be used for things like responding to requests from the LAN connection, etc.
					# there is no intent for this feature to be enabled but it is being allocated space in the code
					c1t2x_logger.error("Feature to parse incoming LAN is not enabled")
					raise NotImplementedError
		except:
			if printData:
				print("Waiting to configure VANET")
			c1t2x_logger.debug("Waiting to configure VANET")
			time.sleep(0.25)
		time.sleep(loopTime)

	error = True

	c1t2x_logger.info("Terminating LAN Thread")

def main():

	global error

	# set up threads
	threads = []

	LAN_mt = Thread(target= LAN_listening_thread)
	VANET_mt = Thread(target= VANET_listening_thread)

	threads.append(LAN_mt)
	threads.append(VANET_mt)

	for thread in threads:
		c1t2x_logger.debug("Starting %s" %thread.name)
		thread.daemon=True
		thread.start()
		time.sleep(0.2)
	c1t2x_logger.debug("All Threads Started")

	try:
		while not error:
			time.sleep(1)
	except KeyboardInterrupt:
		c1t2x_logger.critical("Keyboard Interrupt Occurred")
	finally:
		error = True
		c1t2x_logger.critical("\n---------------------------\nTerminating C1T2X OBU Logger\n---------------------------")

# code starts here
if __name__ == '__main__':

	# print to terminal that C1T2X radio is starting up
	print("----------------------------------------------------\nSTARTING C1T2X RADIO\n----------------------------------------------------")
	
	main()
