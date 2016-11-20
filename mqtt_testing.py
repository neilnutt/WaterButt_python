
import paho.mqtt.client as paho
import time
 
def on_publish(client, userdata, mid):
    print("mid: "+str(mid))
 
client = paho.Client()
client.on_publish = on_publish
client.connect('broker.mqttdashboard.com', 1883)
client.loop_start()
 
while True:
    temperature = 10
    (rc, mid) = client.publish('F0-1F-AF-35-93-57/temperature', str(temperature), qos=1)
    print(rc,mid)
    time.sleep(30)

