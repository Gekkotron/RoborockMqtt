import miio
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading

################################################################################
UpdateStatusEvery = 600
UpdateConsumableStatusEvery = 24 * 3600
UpdateAliveStatusEvery = 120
VacuumIp = "192.168.1.200"
VacuumToken = "515937654d34554c6e36366f3643614e"
BrokerIp = "localhost"
################################################################################

# https://github.com/rytilahti/python-miio/blob/master/miio/vacuum.py
vac = miio.Vacuum(VacuumIp, VacuumToken)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("roborock/#")
    status()
    consumable_status()
    alive()

def on_message(client, userdata, msg):
    if("roborock/command" in msg.topic):
        function = getattr(vac, msg.payload.decode("utf-8"))
        try:
            result = function()
            print(result)
            publish.single(topic="roborock/result", payload=result)
        except miio.exceptions.DeviceException:
            print("DeviceException: " + msg.payload.decode("utf-8"))

    print(msg.topic + " " + msg.payload.decode("utf-8"))

def status():
    try:
        result = vac.status()
        publish.single(topic="roborock/status", payload=result)
    except miio.exceptions.DeviceException:
        print("DeviceException: status")

    threading.Timer(UpdateStatusEvery, status).start()

def consumable_status():
    try:
        result = vac.consumable_status()
        publish.single(topic="roborock/consumable_status", payload=result)
    except miio.exceptions.DeviceException:
        print("DeviceException: consumable_status")

    threading.Timer(UpdateConsumableStatusEvery, consumable_status).start()

def alive():
    publish.single(topic="roborock/alive", payload="1")

    threading.Timer(UpdateAliveStatusEvery, alive).start()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BrokerIp, 1883, 60)

client.loop_forever()
