from machine import Pin, ADC, SoftI2C
import sh1106
import network
import time
import math
import onewire
import ds18x20

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c)

ssid = 'NHATRO BM T1'
password = 'nhatro123456t1'
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while not wlan.isconnected():
        print('Connecting to network...')
        time.sleep(1)

    print('connected wifi: ', ssid)
    print('Network config:', wlan.ifconfig())

connect_wifi(ssid, password)

# Turbidity sensor
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)
def read_turbidity():
    volt = 0
    for _ in range(800):
        volt += adc.read() / 4095 * 3.3 * 2.41
    volt /= 800
    volt = round(volt, 1)
    if volt < 2.5:
        NTU = 3000
    else:
        NTU = -1120.4 * math.sqrt(volt) + 5742.3 * volt - 4352.9
    print('vol: {:.2f}'.format(volt),'Tur: {:.2f}'.format(NTU))
    display.text("Tur: {:.2f}".format(NTU), 5, 0) 
    

# pH sensor
def read_ph():
    adc = ADC(Pin(35))
    buf = [adc.read() for _ in range(10)]
    buf.sort()
    avgValue = sum(buf[2:8]) / 6
    phVol = avgValue * 3.3 / 4095 / 4.3
    phValue = 14.2 - (-5.70 * phVol + 29.5)
    print('PH: {:.2f}'.format(phValue))
    display.text("PH: {:.2f}".format(phValue), 5, 45)   
                                                                                         

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
            
            # Hiển thị nhiệt độ lên OLED
        # display.fill(0)
        display.text("Temp: {:.2f} C".format(temp), 5, 30)
        # display.show()
    

# # Main loop
#     connect_wifi()
while True:
        # read_turbidity()
        # read_ph()
        # read_temperature()
        
        # Update OLED display 
        # display.sleep(False)
        display.fill(0)
        read_turbidity()
        read_ph() 
        # read_temperature()
        display.show()
        
        time.sleep(2)

# from machine import Pin, ADC, I2C
# import network
# import time
# import math
# from ssd1306 import SSD1306_I2C
# import blynklib
# import onewire, ds18x20

# # Blynk credentials
# BLYNK_AUTH_TOKEN = "4Sly-C35Dvbbi8FWkc9mmCpMfGfK0NJl"
# ssid = "NHATRO BM T1"
# password = "nhatro123456t1"

# # Initialize Blynk
# blynk = blynklib.Blynk(BLYNK_AUTH_TOKEN)

# # WiFi connection
# def connect_wifi():
#     wlan = network.WLAN(network.STA_IF)
#     wlan.active(True)
#     wlan.connect(ssid, password)
#     while not wlan.isconnected():
#         pass
#     print('WiFi connected')
#     print('IP:', wlan.ifconfig()[0])

# # OLED Display setup
# i2c = I2C(0, scl=Pin(22), sda=Pin(21))
# display = SSD1306_I2C(128, 64, i2c)

# # DS18B20 Temperature sensor setup
# dat = Pin(4)
# ds_sensor = ds18x20.DS18X20(onewire.OneWire(dat))

# # Turbidity sensor
# def read_turbidity():
#     adc = ADC(Pin(34))
#     volt = 0
#     for _ in range(800):
#         volt += adc.read() / 4095 * 3.3 * 2.41
#     volt /= 800
#     volt = round(volt, 1)
#     if volt < 2.5:
#         NTU = 3000
#     else:
#         NTU = -1120.4 * math.sqrt(volt) + 5742.3 * volt - 4352.9
#     print(f"{volt} V\t{NTU} NTU")
#     blynk.virtual_write(1, NTU)

# # pH sensor
# def read_ph():
#     adc = ADC(Pin(35))
#     buf = [adc.read() for _ in range(10)]
#     buf.sort()
#     avgValue = sum(buf[2:8]) / 6
#     phVol = avgValue * 3.3 / 4095 / 4.3
#     phValue = 14.2 - (-5.70 * phVol + 29.5)
#     print(f"pH: {phValue}")
#     blynk.virtual_write(2, phValue)

# # Temperature sensor
# def read_temperature():
#     roms = ds_sensor.scan()
#     ds_sensor.convert_temp()
#     time.sleep_ms(750)
#     for rom in roms:
#         temp = ds_sensor.read_temp(rom)
#         print(f"{temp} C")
#         blynk.virtual_write(0, temp)

# # Main loop
# def main():
#     connect_wifi()
#     while True:
#         blynk.run()
#         read_turbidity()
#         read_ph()
#         read_temperature()
        
#         # Update OLED display
#         display.clear()
#         display.text(f"Temp: {temp} C", 0, 0)
#         display.text(f"pH: {phValue}", 0, 10)
#         display.text(f"Turbidity: {NTU}", 0, 20)
#         display.show()
        
#         time.sleep(2)

# if _name_ == "_main_":
#     main()