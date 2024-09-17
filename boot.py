import network
import urequests
import time
import onewire, ds18x20
from machine import Pin

# Kết nối WiFi
ssid = 'NHATRO BM T1'
password = 'nhatro123456t1'
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

while not wifi.isconnected():
    pass

print('Connected to WiFi')

# Khởi tạo cảm biến DS18B20
ds_pin = Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
print('Found DS devices: ', roms)

if not roms:
    print("No DS18B20 devices found!")

# Địa chỉ IP của ESP32-WROOM
esp32_wroom_ip = '192.168.1.100'

while True:
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        temp = ds_sensor.read_temp(rom)
    
    # Gửi dữ liệu đến ESP32-WROOM
    url = f'http://{esp32_wroom_ip}/update?temp={temp}'
    response = urequests.get(url)
    response.close()
    
    time.sleep(10)

