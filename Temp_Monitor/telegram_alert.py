import requests
import json
import time
import math,statistics

from boltiot import Bolt
import conf

mybolt = Bolt(conf.bolt_api_key, conf.device_id)

def get_sensor_value_from_pin(pin):
	try:
		response = mybolt.analogRead(pin)
		data = json.loads(response)
		if data["success"] != 1:
			print("Request Not Successfull")
			print("This is the Response ->", data)
			return -999
		sensor_value = int(data["value"])
		return sensor_value, data
	except Exception as e:
		print("Error when returning sensor value")
		print(e)
		return -999

def send_telegram_message(message):
	url = "https://api.telegram.org/" + conf.telegram_bot_id + "/sendMessage"
	data = {
		"chat_id": conf.telegram_chat_id,
		"text": message
		}
	try:
		response = requests.request(
			"POST",
			url,
			params = data
			)
		print("This is the Telegram URL")
		print(url)
		print("This is the Telegram Response")
		print(response.text)
		telegram_data = json.loads(response.text)
		return telegram_data["ok"]

	except Exception as e:
		print("An Error occured while sending Alert via Telegram")
		print(e)
		return False

def compute_bounds(history_data,frame_size,factor):
	if len(history_data) < frame_size:
		return None
	
	if len(history_data) > frame_size:
		del history_data[0:len(history_data) - frame_size]
	
	Mn = statistics.mean(history_data)
	variance = 0
	
	for data in history_data:
		variance += math.pow((data-Mn),2)

	Zn = factor * math.sqrt(variance / frame_size)
	High_bound = history_data[frame_size - 1] + Zn
	Low_bound = history_data[frame_size - 1] - Zn
	return [High_bound, Low_bound]

history_data = []	

while True:
	sensor_value, data = get_sensor_value_from_pin("A0")
	print("The Current Temperature is:", sensor_value / 10.24)

	if sensor_value == -999:
		print("Request was unsuccessfull. Skipping.")
		time.sleep(10)
		continue

	if sensor_value >= conf.threshold:
		print("Sensor value has exceeded threshold")
		message = "Alert! Sensor value has exceeded " + str(conf.threshold / 10.24) + ". The current value is " + str(sensor_value / 10.24)
		telegram_status = send_telegram_message(message)
		print("This is the Telegram Status:", telegram_status)
	
	bound = compute_bounds(history_data, conf.FRAME_SIZE, conf.MUL_FACTOR)
	if not bound:
		history_data.append(int(data['value']))
		time.sleep(10)
		continue

	try:
		if sensor_value > bound[0]:
			message = "High Temperature Anomaly detected"
			print(message)
			telegram_status = send_telegram_message(message)
			print("This is the Telegram status:", telegram_status)
		
		elif sensor_value < bound[1]:
			message = "Low Temperature Anomaly detected"
			print(message)
			telegram_status = send_telegram_message(message)
			print("This is the Telegram status:", telegram_status)
		history_data.append(sensor_value)
	
	except Exception as e:
		print("Error in finding Anomaly")
		print(e)
		
	time.sleep(10)
