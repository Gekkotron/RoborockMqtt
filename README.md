# RoborockMqtt
Bridge between python-miio to mqtt (https://github.com/rytilahti/python-miio/blob/master/miio/vacuum.py)

You can send a simple command with :
mosquitto_pub -t roborock/command -m "stop"
mosquitto_pub -t roborock/command -m "start"
mosquitto_pub -t roborock/command -m "home"

The status is send to your broker every 10 minutes to roborock/status
The consumable status is send to your broker every 24 hours to roborock/consumable_status

The soft send roborock/alive with payload 1 every 120 seconds
