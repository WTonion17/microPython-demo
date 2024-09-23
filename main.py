from machine import Pin, ADC, SoftI2C
import sh1106
import network
import time
import math
import onewire
import ds18x20
import blynklib_mp

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c)

ssid = 'Giangvien'
password = 'dhbk@2024'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    print('Connecting to WiFi...')
    time.sleep(1)

print('WiFi connected')
print(station.ifconfig())

BLYNK_TEMPLATE_ID = "TMPL6Z78zEeyN"
BLYNK_TEMPLATE_NAME = "PBL3"
BLYNK_AUTH_TOKEN = "ntlI3mfVTq7OGbENwVtmV6VG89xuipbK"
blynk = blynklib_mp.Blynk("4Sly-C35Dvbbi8FWkc9mmCpMfGfK0NJl")
if blynk is None:
    print('Failed to initialize Blynk')
else:
    print('Blynk initialized successfully')

# Turbidity sensor
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)
def read_turbidity():
    value = adc.read()
    Voltage = value * 3.87 / 1024.0
    NTU =-1120.4 * Voltage*Voltage + 5742.3*Voltage - 4352.9
    print('vol: {:.2f}'.format(Voltage),'Tur: {:.2f}'.format(NTU))
    return NTU
    
# pH sensor
def read_ph():
    adc = ADC(Pin(35))
    buf = [adc.read() for _ in range(10)]
    buf.sort()
    avgValue = sum(buf[2:8]) / 6
    phVol = avgValue * 3.3 / 4095 / 4.3
    phValue = 14.2 - (-5.70 * phVol + 29.5)
    print('PH: {:.2f}'.format(phValue))
    return phValue                                                                                 

# Temperature sensor
# DS18B20 Temperature sensor setup
dat = Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(dat))
roms = ds_sensor.scan()
print('Found DS devices: ', roms)

if not roms:
    print("No DS18B20 devices found!")
def read_temperature():
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        temp = ds_sensor.read_temp(rom)
        print('Temperature: {:.2f} C'.format(temp))
        return temp
    

while True:               
        NTU = read_turbidity()
        phValue = read_ph() 
        temp = read_temperature()
        
        read_temperature()
        display.fill(0)
        display.text("Tur: {:.2f}".format(NTU), 5, 0) 
        display.text("PH: {:.2f}".format(phValue), 5, 45) 
        display.text("Temp: {:.2f} C".format(temp), 5, 30)
        display.show()
        if blynk is not None:
            blynk.virtual_write(1,NTU)
            blynk.virtual_write(2,phValue)
            blynk.virtual_write(0,temp)
        blynk.run()
        time.sleep(2)

