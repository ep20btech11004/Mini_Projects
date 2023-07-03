from boltiot import Bolt
api_key = "a69086ed-5158-4f2c-9a05-56950aa5b1af"
device_id = "BOLT13166896"
mybolt = Bolt(api_key, device_id)
response = mybolt.restart()
print(response)
