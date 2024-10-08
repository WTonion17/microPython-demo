from machine import Pin, ADC, SoftI2C
import sh1106
import network
import time
import math
import onewire
import ds18x20
import blynklib_mp
import urequests
import ntptime

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c)

def connect_WIFI():
    ssid = 'NHATRO BM T1'
    password = 'nhatro123456t1'

    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)
    while not station.isconnected():
        print('Connecting to WiFi...')
        time.sleep(1)

    print('WiFi connected to:', ssid)
    print(station.ifconfig())

ntptime.host = 'pool.ntp.org'  # Use this or another known NTP server

server_url = 'https://script.google.com/macros/s/AKfycbwEBDMV7npCrkxAaN1BUHYQaHLqwUZRsOI8U5uhgOT5i89fABizurx9U6Zq6vz7RizY/exec'

BLYNK_TEMPLATE_ID = "TMPL6Z78zEeyN"
BLYNK_TEMPLATE_NAME = "PBL3"
BLYNK_AUTH_TOKEN = "ntlI3mfVTq7OGbENwVtmV6VG89xuipbK"
blynk = blynklib_mp.Blynk("4Sly-C35Dvbbi8FWkc9mmCpMfGfK0NJl")
if blynk is None:
    print('Failed to initialize Blynk')
else:
    print('Blynk initialized successfully')

def get_ntp_time():
    try:
        ntptime.settime()  # Synchronize the system time with NTP
        tm = time.localtime(time.time())  # Get local time
        formatted_time = "{:02d}:{:02d}:{:02d}".format(tm[3], tm[4], tm[5])
        return formatted_time
    except Exception as e:
        print("Error getting NTP time:", e)
        return None

# Turbidity sensor
def read_turbidity():
    adc = ADC(Pin(35))
    adc.atten(ADC.ATTN_11DB)
    Volt = 0
    Volt = adc.read() / 4095 * 5  # Chuyển đổi giá trị đọc từ ADC thành điện áp (5V tham chiếu)
    
    # Lấy trung bình 800 lần đọc để giảm nhiễu
    for _ in range(800):
        Volt += (adc.read() / 4095) * 5
    Volt /= 800

    if Volt < 2.5:
        NTU = 3000
    elif Volt > 4.2:
        NTU = 0
    else:
        NTU = -1120.4 * Volt * Volt + 5742.3 * Volt - 4352.9
    print('VOLTAGE: {:.2f} V'.format(Volt) , 'TURBIDITY: {:.2f} NTU'.format(NTU))
    return NTU
    
# pH sensor
def read_ph():
    adc = ADC(Pin(34))
    buf = [adc.read() for _ in range(10)]
    buf.sort()
    avgValue = sum(buf[2:8]) / 6
    phVol = avgValue * 3.3 / 4095 / 4.3
    phValue = 14.2 - (-5.70 * phVol + 29.5)
    print('PH: {:.2f}'.format(phValue))
    return phValue                                                                                 

# Temperature sensor
# DS18B20 Temperature sensor setup

def read_temperature():
    dat = Pin(4)
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(dat))
    roms = ds_sensor.scan()
    print('Found DS18B20 devices: ', roms)
    if not roms:
        print("No DS18B20 devices found!")
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        temp = ds_sensor.read_temp(rom)
        print('Temperature: {:.2f} C'.format(temp))
        return temp
    
def main_loop():
    while True:               
        NTU = read_turbidity()
        phValue = read_ph() 
        temp = read_temperature()
        
        display.fill(0)
        display.text("Tur: {:.2f} NTU".format(NTU), 5, 0) 
        display.text("PH: {:.2f}".format(phValue), 5, 45) 
        display.text("Temp: {:.2f} C".format(temp), 5, 30)
        display.show()
        
        if blynk is not None:
            blynk.virtual_write(1,NTU)
            blynk.virtual_write(2,phValue)
            blynk.virtual_write(0,temp)
            blynk.run()
        
        # Get current time
        timestamp = get_ntp_time()

    # Prepare JSON payload
        json_data = {
            "method": "append",
            "temp": temp,
            "NTU": NTU,
            "phValue": phValue,
            "timestamp": timestamp,
        }

    # Send HTTP POST request
        try:
            response = urequests.post(server_url, json=json_data)
            print("Response:", response.status_code, response.text)
            response.close()
        except Exception as e:
            print("Error sending data:", e)
            
        time.sleep(5)

if __name__ == "__main__":
    connect_WIFI()
    main_loop()


