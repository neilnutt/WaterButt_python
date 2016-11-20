import paho.mqtt.client as mqtt

class MqttClient:

  def on_connect(self,mosq, obj, rc):
    self.mqttc.subscribe("home/garden/sensor/switch", 0)
    print("rc: " + str(rc))

  def on_message(self,mosq, obj, msg):
    #global message
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    self.mqttc.publish("f2",msg.payload);

  def on_publish(self,mosq, obj, mid):
    print("mid: " + str(mid))

  def on_subscribe(self,mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

  def on_log(self,mosq, obj, level, string):
    print(string)

  def __init__(self,host,port):
    mqttc = mqtt.Client()
    # Assign event callbacks
    mqttc.on_message = self.on_message
    mqttc.on_connect = self.on_connect
    mqttc.on_publish = self.on_publish
    mqttc.on_subscribe = self.on_subscribe
    # Connect
    mqttc.connect("iot.eclipse.org",1883,60)

    mqttc.publish("home/garden/sensor/waterlevel",0.55,0,True)
    
    
    # Continue the network loop
    mqttc.loop_forever()

if __name__ == '__main__':
  t=MqttClient("iot.eclipse.org",1883)