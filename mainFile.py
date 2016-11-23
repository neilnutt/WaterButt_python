<<<<<<< HEAD
import json
import requests as r
import pip
try:
	import psycopg2 as ps
except:
	pip.main(['install','psycopg2'])
	import psycopg2
from datetime import datetime
import time
import urllib
try:
	import paho.mqtt.client as mqtt
except:
	pip.main(['install','paho-mqtt'])
	import paho.mqtt.client
import subprocess

def notUsed():
	osgeoPath = r'C:\OSGeo4W\bin'
	pallette = r'C:\temp\pallette.tif'
	shell = subprocess.Popen(r'"C:\Program Files\QGIS 2.16\OSGeo4W.bat"', bufsize=1, stdin=subprocess.PIPE,universal_newlines=True)
	shell.stdin.write('cd c:\\temp \n')
	shell.stdin.write('upload_forecast.bat \n')
	shell.wait()
	shell.stdin.write('upload_radar.bat \n')
	shell.wait()
	#shell.communicate('cd c:\\temp \n')
	#shell.communicate('dir \n')
	#shell.communicate('upload_forecast.bat \n')
	#os.system(r'start "C:\Program Files\QGIS 2.16\OSGeo4W.bat"  cd c:/temp')
	exit()


print(urllib.request.getproxies())

conn = ps.connect("host='localhost' dbname='weather' user='postgres' password='admin'")
print(conn)

def findLocation(postcode):
#http://api.wunderground.com/api/e80a74c68ebbe7be/geolookup/q/France/Paris.json
	jsonStr = r.get("http://api.wunderground.com/api/e80a74c68ebbe7be/geolookup/q/United_Kingdom/BS40_5HB.json")
	print(jsonStr.json())
	exit()

def downloadYesterday(country,locationName):
	# http://api.wunderground.com/api/e80a74c68ebbe7be/yesterday/q/United_Kingdom/City_of_Bristol.json
	jsonStr = r.get("http://api.wunderground.com/api/e80a74c68ebbe7be/yesterday/q/"+country+"/"+locationName+".json")
	t = jsonStr.text.replace("'", '"')
	print (jsonStr.text)
	print (t)
	data = json.loads(t)
	print (data)
	
	forecastTime = str(datetime.now())
	print(forecastTime)	
	forecast = dict()	
	cursor = conn.cursor()
	
	for i in data['response']:
	 print(i,type(i))
	 
	 continue 
	 forecast['snow'] = i['dailysummary']['snow']
	 forecast['wgustm'] = i['wgustm']
	 forecast['wdird'] = i['wdird']
	 forecast['windchillm'] = i['windchillm']
	 forecast['dewptm'] = i['dewptm']
	 forecast['precipm'] = i['precipm']
	 forecast['thunder'] = i['thunder']
	 forecast['utcdate'] = i['utcdate']
	 forecast['pressurem'] = i['pressurem']
	 forecast['conds'] = i['conds']
	 forecast['wspdm'] = i['wspdm']
	 forecast['hum'] = i['hum']
	 forecast['heatindexm'] = i['heatindexm']
	 forecast['tempm'] = i['tempm']
	 forecast['hail'] = i['hail']
	 forecast['rain'] = i['rain']
	exit()

def downloadForecast(country,locationName):
	# jsonStr = r.get("http://api.wunderground.com/api/e80a74c68ebbe7be/hourly/q/United_Kingdom/City_of_Bristol.json") 
	jsonStr = r.get("http://api.wunderground.com/api/e80a74c68ebbe7be/hourly/q/"+country+"/"+locationName+".json") 
	data = jsonStr.json()
	
	#print (data)
	
	forecastTime = str(datetime.now())
	print(forecastTime)	
	forecast = dict()	
	cursor = conn.cursor()
	
	for i in data['hourly_forecast']:
		 forecast['mslp'] = i['mslp']['metric']
		 forecast['dewpoint'] = i['dewpoint']['metric']
		 forecast['temp'] = i['temp']['metric']
		 forecast['windchill'] = i['windchill']['metric']
		 forecast['qpf'] = i['qpf']['metric']
		 forecast['humidity'] = i['humidity']
		 forecast['pop'] = i['pop']
		 forecast['fctcode'] = i['fctcode']
		 forecast['condition'] = i['condition']
		 forecast['snow'] = i['snow']['metric']
		 forecast['heatindex'] = i['heatindex']['metric']
		 forecast['feelslike'] = i['feelslike']['metric']
		 forecast['wspd'] = i['wspd']['metric']
		 
		 timeStr = str(i['FCTTIME'])
		 for t in timeStr.replace('{','').replace("'",'').replace("}",'').split(','):
		 	 a = t.split(':',1)
		 	 if len(a) == 1:
		 	 		continue
		 	 forecast[a[0].replace(' ','')]=a[1]
		 forecast['formatedTime']=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(forecast['epoch'])))
		 #cursor.execute("INSERT INTO wuground.forecast(country,location_name, time_of_forecast, \"time\", temp, mslp) VALUES ('United_Kingdom', 'City_of_Bristol',TIMESTAMP '2016-10-15 18:53:01.662287',  '2016-10-15 18:53:01.662287', 19, 1028);")
		 cursor.execute("INSERT INTO wuground.forecast(country,location_name, time_of_forecast, \"time\", temp, feelslike, windchill, humidity, pop, qpf, mslp) VALUES ('%s', '%s',TIMESTAMP '%s',TIMESTAMP  '%s', %s, %s,'%s', %s, %s,'%s', %s);" 
									% (country,locationName,forecastTime,forecast['formatedTime'],forecast['temp'],forecast['feelslike'],forecast['windchill'],forecast['humidity'],forecast['pop'],forecast['qpf'],forecast['mslp']))
		 conn.commit()

def downloadMetOfficeRadar():
	metApiKey = "50102072-d813-4fd4-89fe-fc41a40687bc"
	for i in range(5):		
		jsonStr = r.get("http://datapoint.metoffice.gov.uk/public/data/layer/wxobs/all/json/capabilities?key="+metApiKey)
		print(jsonStr)
		if str(jsonStr) == "<Response [404]>":
			continue
		else:
			break 
	data = jsonStr.json()
	baseUrl = data['Layers']['BaseUrl']['$']
	#print(baseUrl)

	#for i in data['Layers']['Layer']:
		#print(type(i),i)
	for j in data['Layers']['Layer']:
			#print(type(j),j)
			for observationType in j:
				#print(type(j[observationType]),j[observationType])
				if type(j[observationType]) == type(dict()) and j[observationType]['LayerName'] == 'RADAR_UK_Composite_Highres':
					#print(type(j[observationType]),j[observationType])
					imageFormat = j[observationType]['ImageFormat']
					times = j[observationType]['Times']['Time']
					#print(imageFormat)
					#print(times)
					
					print('Checking for additional radar maps')
					for time in times:
						url = baseUrl.replace('{LayerName}','RADAR_UK_Composite_Highres').replace('{ImageFormat}',imageFormat).replace('{Time}',time).replace('{key}',metApiKey)
						filename = 'RADAR_UK_Composite_Highres'+'_'+time.replace(':','.')
						filepath = 'C:\\temp\\'+filename.replace(':','.')+"."+imageFormat
						
						cursor = conn.cursor()
						cursor.execute("SELECT count(gid) FROM metoffice.radar WHERE filename = '%s'" %(filename) )
						records = cursor.fetchall()
						#print(records[0][0])
						
						
						if records[0][0]== 0:
							try:
								print(urllib.request.urlretrieve(url,filepath))
								createWorldFile(filepath)
							except:
								print("Invalid REST request, file was probably deleted before the script got it...")
								print(url)
						else:
							continue
							#print('Already downloaded: ', filename)


def downloadMetOfficeRainfallForecast(loadedForecastTime):
	metApiKey = "50102072-d813-4fd4-89fe-fc41a40687bc"
	for i in range(5):		
		jsonStr = r.get("http://datapoint.metoffice.gov.uk/public/data/layer/wxfcs/all/json/capabilities?key="+metApiKey)
		print(jsonStr)
		if str(jsonStr) == "<Response [404]>":
			time.sleep(10.0)
			continue
		else:
			break 
	data = jsonStr.json()
	baseUrl = data['Layers']['BaseUrl']['$']
	#print(baseUrl)


	for j in data['Layers']['Layer']:
			#print('j', type(j),j)
			for observationType in j:
				#print(type(j[observationType]),j[observationType])
				if type(j[observationType]) == type(dict()) and j[observationType]['LayerName'] == 'Precipitation_Rate':
					#print(type(j[observationType]),j[observationType])
					imageFormat = j[observationType]['ImageFormat']
					times = j[observationType]['Timesteps']['Timestep']
					defaultTime = j[observationType]['Timesteps']['@defaultTime']
					#print('image format:', imageFormat)
					#print(type(times),times)
					print ('Checking for new forecast')
					if loadedForecastTime != defaultTime:
						loadedForecastTime = defaultTime
						print ('New forecast found: '+ str(defaultTime))
					
					
						for time in times:
							url = baseUrl.replace('{LayerName}','Precipitation_Rate').replace('{ImageFormat}',imageFormat).replace('{Timestep}',str(time)).replace('{key}',metApiKey).replace('{DefaultTime}',defaultTime)
							#print(url)
							filename = 'Precipitation_Rate_'+str(defaultTime).replace(':','.')+'_'+str(time).replace(':','.')
							filepath = 'C:\\temp\\'+filename.replace(':','.')+"."+imageFormat
							
							
							cursor = conn.cursor()
							cursor.execute("SELECT count(gid) FROM metoffice.rain_forecast WHERE filename = '%s'" %(filename) )
							records = cursor.fetchall()
							#print(records[0][0])
	
	
							print(urllib.request.urlretrieve(url,filepath))
							createWorldFile(filepath)						
							

							

def createWorldFile(file):
	wrldFile = file[:-3]+"wld"
	f = open(wrldFile,'w')
	f.write("0.034\n0\n0\n-0.026\n-12.0\n61.0\n")
	
def on_log(mosq, obj, level, string):
	print(string)

def on_subscribe(mosq, obj, mid, granted_qos):
	print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(mosq, obj, msg):
	#global message
	print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
	mqttc.publish("f2",msg.payload);	

def uploadForecast():
	#radi = ['1km','5km','10km']
	#times = ['0h','3h']
	
	#for time in times:
		#for radius in radi:
			cursor = conn.cursor()
			#cursor.execute("SELECT name, r"+radius+"_rainfall_depth_av, r"+radius+"_depth_stdev FROM metoffice.forecast_rain_stdev_"+time)
			cursor.execute("SELECT name, forecast_hr,av_depth,min_likely_depth, max_likely_rain FROM metoffice.forecast_rain;")
			records = cursor.fetchall()
			
			for record in records:
				command = record[0]+"/f/raindepth/"+str(record[1])+"/max_likely_rain"
				command = command.lower()
				value = str(round(record[4],2))
				print(command,value)
				mqttc.publish(command,value,0,True)
				command = record[0]+"/f/raindepth/"+str(record[1])+"/min_likely_rain"
				command = command.lower()
				value = str(round(record[3],2))
				print (command,value)
				mqttc.publish(command,value,0,True)

if __name__ =='__main__':
	mqttc = mqtt.Client()
	mqttc.connect("iot.eclipse.org",1883,60)	

	mqttc.on_subscribe = on_subscribe
	mqttc.on_message = on_message
	
	
	mqttc.subscribe("uniqueid/wl", 0)
	mqttc.subscribe("uniqueid/maxtargetwl", 0)
	mqttc.loop(timeout=2.0, max_packets=1)
	mqttc.loop_start()
	#mqttc.loop_forever()

	currentForecastTime = None
	shortLoop = 0
	midLoop = 0
	longLoop = 0
	
	while True:
		#  Everything out here is done hourly
		time.sleep(1)
		if time.time() - longLoop > 60*60:
			longLoop = time.time()
			currentForecastTime = downloadMetOfficeRainfallForecast(currentForecastTime)
			print(time.ctime())

		if time.time() - midLoop > 15*60:
			midLoop = time.time()
			# Everything in here is done every 15mins
			uploadForecast()
			downloadMetOfficeRadar()
			print(time.ctime())
		
		if time.time() - shortLoop > 60:
			shortLoop = time.time()
			# Everything in here is done once a minute
			#mqttc.loop_start()
			print('Checking mqtt server',str(time.ctime()))
			mqttc.loop()
		#findLocation('Bristol')
		#downloadForecast("United_Kingdom","City_of_Bristol")
		#downloadYesterday("United_Kingdom","City_of_Bristol")
		#time.sleep(36000)
=======
import json
import requests as r
import pip
try:
	import psycopg2 as ps
except:
	pip.main(['install','psycopg2'])
	import psycopg2
from datetime import datetime
import time
import urllib
try:
	import paho.mqtt.client as mqtt
except:
	pip.main(['install','paho-mqtt'])
	import paho.mqtt.client
import subprocess

def notUsed():
	osgeoPath = r'C:\OSGeo4W\bin'
	pallette = r'C:\temp\pallette.tif'
	shell = subprocess.Popen(r'"C:\Program Files\QGIS 2.16\OSGeo4W.bat"', bufsize=1, stdin=subprocess.PIPE,universal_newlines=True)
	shell.stdin.write('cd c:\\temp \n')
	shell.stdin.write('upload_forecast.bat \n')
	shell.wait()
	shell.stdin.write('upload_radar.bat \n')
	shell.wait()
	#shell.communicate('cd c:\\temp \n')
	#shell.communicate('dir \n')
	#shell.communicate('upload_forecast.bat \n')
	#os.system(r'start "C:\Program Files\QGIS 2.16\OSGeo4W.bat"  cd c:/temp')
	exit()


print(urllib.request.getproxies())

conn = ps.connect("host='localhost' dbname='weather' user='postgres' password='admin'")
print(conn)

def findLocation(postcode):
#http://api.wunderground.com/api/e80a74c68ebbe7be/geolookup/q/France/Paris.json
	jsonStr = r.get("http://api.wunderground.com/api/e80a74c68ebbe7be/geolookup/q/United_Kingdom/BS40_5HB.json")
	print(jsonStr.json())
	exit()

def downloadYesterday(country,locationName):
	# http://api.wunderground.com/api/e80a74c68ebbe7be/yesterday/q/United_Kingdom/City_of_Bristol.json
	jsonStr = r.get("http://api.wunderground.com/api/e80a74c68ebbe7be/yesterday/q/"+country+"/"+locationName+".json")
	t = jsonStr.text.replace("'", '"')
	print (jsonStr.text)
	print (t)
	data = json.loads(t)
	print (data)
	
	forecastTime = str(datetime.now())
	print(forecastTime)	
	forecast = dict()	
	cursor = conn.cursor()
	
	for i in data['response']:
	 print(i,type(i))
	 
	 continue 
	 forecast['snow'] = i['dailysummary']['snow']
	 forecast['wgustm'] = i['wgustm']
	 forecast['wdird'] = i['wdird']
	 forecast['windchillm'] = i['windchillm']
	 forecast['dewptm'] = i['dewptm']
	 forecast['precipm'] = i['precipm']
	 forecast['thunder'] = i['thunder']
	 forecast['utcdate'] = i['utcdate']
	 forecast['pressurem'] = i['pressurem']
	 forecast['conds'] = i['conds']
	 forecast['wspdm'] = i['wspdm']
	 forecast['hum'] = i['hum']
	 forecast['heatindexm'] = i['heatindexm']
	 forecast['tempm'] = i['tempm']
	 forecast['hail'] = i['hail']
	 forecast['rain'] = i['rain']
	exit()

def downloadForecast(country,locationName):
	# jsonStr = r.get("http://api.wunderground.com/api/e80a74c68ebbe7be/hourly/q/United_Kingdom/City_of_Bristol.json") 
	jsonStr = r.get("http://api.wunderground.com/api/e80a74c68ebbe7be/hourly/q/"+country+"/"+locationName+".json") 
	data = jsonStr.json()
	
	#print (data)
	
	forecastTime = str(datetime.now())
	print(forecastTime)	
	forecast = dict()	
	cursor = conn.cursor()
	
	for i in data['hourly_forecast']:
		 forecast['mslp'] = i['mslp']['metric']
		 forecast['dewpoint'] = i['dewpoint']['metric']
		 forecast['temp'] = i['temp']['metric']
		 forecast['windchill'] = i['windchill']['metric']
		 forecast['qpf'] = i['qpf']['metric']
		 forecast['humidity'] = i['humidity']
		 forecast['pop'] = i['pop']
		 forecast['fctcode'] = i['fctcode']
		 forecast['condition'] = i['condition']
		 forecast['snow'] = i['snow']['metric']
		 forecast['heatindex'] = i['heatindex']['metric']
		 forecast['feelslike'] = i['feelslike']['metric']
		 forecast['wspd'] = i['wspd']['metric']
		 
		 timeStr = str(i['FCTTIME'])
		 for t in timeStr.replace('{','').replace("'",'').replace("}",'').split(','):
		 	 a = t.split(':',1)
		 	 if len(a) == 1:
		 	 		continue
		 	 forecast[a[0].replace(' ','')]=a[1]
		 forecast['formatedTime']=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(forecast['epoch'])))
		 #cursor.execute("INSERT INTO wuground.forecast(country,location_name, time_of_forecast, \"time\", temp, mslp) VALUES ('United_Kingdom', 'City_of_Bristol',TIMESTAMP '2016-10-15 18:53:01.662287',  '2016-10-15 18:53:01.662287', 19, 1028);")
		 cursor.execute("INSERT INTO wuground.forecast(country,location_name, time_of_forecast, \"time\", temp, feelslike, windchill, humidity, pop, qpf, mslp) VALUES ('%s', '%s',TIMESTAMP '%s',TIMESTAMP  '%s', %s, %s,'%s', %s, %s,'%s', %s);" 
									% (country,locationName,forecastTime,forecast['formatedTime'],forecast['temp'],forecast['feelslike'],forecast['windchill'],forecast['humidity'],forecast['pop'],forecast['qpf'],forecast['mslp']))
		 conn.commit()

def downloadMetOfficeRadar():
	metApiKey = "50102072-d813-4fd4-89fe-fc41a40687bc"
	for i in range(5):		
		jsonStr = r.get("http://datapoint.metoffice.gov.uk/public/data/layer/wxobs/all/json/capabilities?key="+metApiKey)
		print(jsonStr)
		if str(jsonStr) == "<Response [404]>":
			continue
		else:
			break 
	data = jsonStr.json()
	baseUrl = data['Layers']['BaseUrl']['$']
	#print(baseUrl)

	#for i in data['Layers']['Layer']:
		#print(type(i),i)
	for j in data['Layers']['Layer']:
			#print(type(j),j)
			for observationType in j:
				#print(type(j[observationType]),j[observationType])
				if type(j[observationType]) == type(dict()) and j[observationType]['LayerName'] == 'RADAR_UK_Composite_Highres':
					#print(type(j[observationType]),j[observationType])
					imageFormat = j[observationType]['ImageFormat']
					times = j[observationType]['Times']['Time']
					#print(imageFormat)
					#print(times)
					
					print('Checking for additional radar maps')
					for time in times:
						url = baseUrl.replace('{LayerName}','RADAR_UK_Composite_Highres').replace('{ImageFormat}',imageFormat).replace('{Time}',time).replace('{key}',metApiKey)
						filename = 'RADAR_UK_Composite_Highres'+'_'+time.replace(':','.')
						filepath = 'C:\\temp\\'+filename.replace(':','.')+"."+imageFormat
						
						cursor = conn.cursor()
						cursor.execute("SELECT count(gid) FROM metoffice.radar WHERE filename = '%s'" %(filename) )
						records = cursor.fetchall()
						#print(records[0][0])
						
						
						if records[0][0]== 0:
							try:
								print(urllib.request.urlretrieve(url,filepath))
								createWorldFile(filepath)
							except:
								print("Invalid REST request, file was probably deleted before the script got it...")
								print(url)
						else:
							continue
							#print('Already downloaded: ', filename)


def downloadMetOfficeRainfallForecast(loadedForecastTime):
	metApiKey = "50102072-d813-4fd4-89fe-fc41a40687bc"
	for i in range(5):		
		jsonStr = r.get("http://datapoint.metoffice.gov.uk/public/data/layer/wxfcs/all/json/capabilities?key="+metApiKey)
		print(jsonStr)
		if str(jsonStr) == "<Response [404]>":
			time.sleep(10.0)
			continue
		else:
			break 
	data = jsonStr.json()
	baseUrl = data['Layers']['BaseUrl']['$']
	#print(baseUrl)


	for j in data['Layers']['Layer']:
			#print('j', type(j),j)
			for observationType in j:
				#print(type(j[observationType]),j[observationType])
				if type(j[observationType]) == type(dict()) and j[observationType]['LayerName'] == 'Precipitation_Rate':
					#print(type(j[observationType]),j[observationType])
					imageFormat = j[observationType]['ImageFormat']
					times = j[observationType]['Timesteps']['Timestep']
					defaultTime = j[observationType]['Timesteps']['@defaultTime']
					#print('image format:', imageFormat)
					#print(type(times),times)
					print ('Checking for new forecast')
					if loadedForecastTime != defaultTime:
						loadedForecastTime = defaultTime
						print ('New forecast found: '+ str(defaultTime))
					
					
						for time in times:
							url = baseUrl.replace('{LayerName}','Precipitation_Rate').replace('{ImageFormat}',imageFormat).replace('{Timestep}',str(time)).replace('{key}',metApiKey).replace('{DefaultTime}',defaultTime)
							#print(url)
							filename = 'Precipitation_Rate_'+str(defaultTime).replace(':','.')+'_'+str(time).replace(':','.')
							filepath = 'C:\\temp\\'+filename.replace(':','.')+"."+imageFormat
							
							
							cursor = conn.cursor()
							cursor.execute("SELECT count(gid) FROM metoffice.rain_forecast WHERE filename = '%s'" %(filename) )
							records = cursor.fetchall()
							#print(records[0][0])
	
	
							print(urllib.request.urlretrieve(url,filepath))
							createWorldFile(filepath)						
							

							

def createWorldFile(file):
	wrldFile = file[:-3]+"wld"
	f = open(wrldFile,'w')
	f.write("0.034\n0\n0\n-0.026\n-12.0\n61.0\n")
	
def on_log(mosq, obj, level, string):
	print(string)

def on_subscribe(mosq, obj, mid, granted_qos):
	print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(mosq, obj, msg):
	#global message
	print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
	mqttc.publish("f2",msg.payload);	

def uploadForecast():
	#radi = ['1km','5km','10km']
	#times = ['0h','3h']
	
	#for time in times:
		#for radius in radi:
			cursor = conn.cursor()
			#cursor.execute("SELECT name, r"+radius+"_rainfall_depth_av, r"+radius+"_depth_stdev FROM metoffice.forecast_rain_stdev_"+time)
			cursor.execute("SELECT name, forecast_hr,av_depth,min_likely_depth, max_likely_rain FROM metoffice.forecast_rain;")
			records = cursor.fetchall()
			
			for record in records:
				command = record[0]+"/f/raindepth/"+str(record[1])+"/max_likely_rain"
				command = command.lower()
				value = str(round(record[4],2))
				print(command,value)
				mqttc.publish(command,value,0,True)
				command = record[0]+"/f/raindepth/"+str(record[1])+"/min_likely_rain"
				command = command.lower()
				value = str(round(record[3],2))
				print (command,value)
				mqttc.publish(command,value,0,True)

if __name__ =='__main__':
	mqttc = mqtt.Client()
	mqttc.connect("iot.eclipse.org",1883,60)	

	mqttc.on_subscribe = on_subscribe
	mqttc.on_message = on_message
	
	
	mqttc.subscribe("uniqueid/wl", 0)
	mqttc.subscribe("uniqueid/maxtargetwl", 0)
	mqttc.loop(timeout=2.0, max_packets=1)
	mqttc.loop_start()
	#mqttc.loop_forever()

	currentForecastTime = None
	shortLoop = 0
	midLoop = 0
	longLoop = 0
	
	while True:
		#  Everything out here is done hourly
		time.sleep(1)
		if time.time() - longLoop > 60*60:
			longLoop = time.time()
			currentForecastTime = downloadMetOfficeRainfallForecast(currentForecastTime)
			print(time.ctime())

		if time.time() - midLoop > 15*60:
			midLoop = time.time()
			# Everything in here is done every 15mins
			uploadForecast()
			downloadMetOfficeRadar()
			print(time.ctime())
		
		if time.time() - shortLoop > 60:
			shortLoop = time.time()
			# Everything in here is done once a minute
			#mqttc.loop_start()
			print('Checking mqtt server',str(time.ctime()))
			mqttc.loop()
		#findLocation('Bristol')
		#downloadForecast("United_Kingdom","City_of_Bristol")
		#downloadYesterday("United_Kingdom","City_of_Bristol")
		#time.sleep(36000)
>>>>>>> origin/master
		