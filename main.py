import subprocess
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

def miiocli(command):
    command_line = f"miiocli -o json_pretty vacuum"
    command_line += f" --ip {VacuumIp}"
    command_line += f" --token {VacuumToken}"
    command_line += f" {command}"

    process = subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE)
    process.wait()

    return process.stdout.read().rstrip().decode("utf-8")

def sendResultTomqtt(topic, message):
    if("Error" in message):
        publish.single(topic="roborock/error", payload=message.replace("Error:", topic + " --> "))
    else:
        publish.single(topic=topic, payload=message)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("roborock/#")
    status()
    consumable_status()
    alive()

def on_message(client, userdata, msg):
    if("roborock/command" in msg.topic):
        result = miiocli(msg.payload.decode("utf-8"))
        sendResultTomqtt("roborock/result", result)

    print(msg.topic + " " + msg.payload.decode("utf-8"))

def status():
    result = miiocli("status")
    sendResultTomqtt("roborock/status", result)

    threading.Timer(UpdateStatusEvery, status).start()

def consumable_status():
    result = miiocli("consumable_status")
    sendResultTomqtt("roborock/consumable_status", result)

    threading.Timer(UpdateConsumableStatusEvery, consumable_status).start()

def alive():
    publish.single(topic="roborock/alive", payload="1")

    threading.Timer(UpdateAliveStatusEvery, alive).start()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BrokerIp, 1883, 60)

client.loop_forever()
