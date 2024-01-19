# CARMA 1tenth Vehicle to Everything

This repo provides code for the CARMA 1tenth (C1T) Vehicle to Everything (V2X) radio emulator (C1T2X) on a Raspberry Pi 4B+.

## Python requirements
This package requires the following three python packages:
- [netifaces](https://pypi.org/project/netifaces/)
- [ruamel.yaml](https://pypi.org/project/ruamel.yaml/)
- [asn1tools](https://pypi.org/project/asn1tools/)

These packages can be installed by navigating to the C1T2X directory, and running:
```
sudo pip install -r ./requirements.txt
```

## Functionality
The C1T2X radios function similar to the DSRC radios used by CARMA Platform equipped vehicles in that they receive UDP packets from a PC and broadcast them "over the air." The radios used by the CARMA Platform are configured to be in Road Side Unit (RSU) mode where messages are forwarded, and C1T2X seeks to emulate this behavior.

The C1T2X radios are intended to use the same driver as the full-scale CARMA vehicle's DSRC radios, specifically the [carma-cohda-dsrc-driver](https://github.com/usdot-fhwa-stol/carma-cohda-dsrc-driver).

The C1T2X solution uses the WiFi band for its Vehicle Area Network (VANET) rather than Dedicated Short Range Communications (DSRC) or Cellular V2X (C-V2X). It is intended to be an educational tool used to facilitate communication and cooperation between scaled-down vehicles and infrastructure - and it not intended as a deployable solution. Public Deployment of a WiFi-based VANET is outside of the scope of the C1T project, and may be susceptible to restrictions/guidelines from the Federal Communications Commission (FCC).

C1T2X radios are capable of running their own applications through threading - provided that message decoding/encoding and parsing is enabled.
At this time, the radios do not decode or encode packets and function only to forward messages - similar to the full scale CARMA Platform vehicles' radios. However, further work can be done to enable this.

At a high level, the C1T2X radios can:
- Receive UDP packets over the LAN from the Jetson Xavier
- Broadcast UDP packets over the VANET to other scaled-down cooperative entities
- Receive UDP packets over the VANET from other scaled-down cooperative entities
- Broadcast UDP packets over the LAN to the Jetson Xavier

Broadcasting over WiFi for the VANET allows for each C1T2X radio to receive its own messages that it broadcasts. The C1T2X radio checks the IP of the device that sends each message, and filters out messages that are sent from its own IP.

## Configuration
The C1T2X radios are connected to both a local area network (the connection between the Pi and a Jetson Xavier NX with a crossover ethernet cable) and a wireless network (the VANET).

The radios should be configured to work on each network by adjusting the parameters in the following two YAML files:
1. `./src/Networking/config/LAN_params.yaml`
2. `./src/Networking/config/VANET_params.yaml`

The IP, Port, and Network interface for each network must be set correctly. The IP and Port that are used for the LAN network should relate to the IP and Port in the ROS2 driver's params.yaml and dsrc.cfg files from the `carma-cohda-dsrc-driver` package.

If the wireless and wired network interfaces are unknown, the following command will identify the available network interfaces:
```
basename -a /sys/class/net/*
```

The VANET IP and Port that are used should be consistent across all radios on the VANET.

## Testing
You can test a full loop of the VANET with the scripts broadcaster.py and returner.py

Configure the parameter YAML files on two machines and:
- on one machine, run:
```
python broadcaster.py vanet
```
- on the other machine, run:
```
python returner.py vanet
```

The broadcaster will create an uper encoded asn.1 message and broadcast it over the vanet.

The returner will receive the message, and send the message back over the vanet.

The broadcaster will receive the message, and it will compare the received copy against the originally broadcasted copy.

## Running
Once all config files are correctly made, run the `C1T2X_OBU.py` script to start the on board unit (OBU) emulator.