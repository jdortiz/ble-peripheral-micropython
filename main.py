# import sys
import aioble
import bluetooth
import machine
import uasyncio as asyncio
from micropython import const

import struct
import random

# Constants
MANUFACTURER_ID = const(0x02A29)
MODEL_NUMBER_ID = const(0x2A24)
SERIAL_NUMBER_ID = const(0x2A25)

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

# Frequency for advertising beacons
_ADV_INTERVAL_MS = const(250000)

# Register BLE service with one characteristic
temp_service = aioble.Service(_ENV_SENSE_UUID)
temp_char = aioble.Characteristic(
    temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True
)
aioble.register_services(temp_service)


# def uid():
#     """ Return the unique id of the device as a string """
#     return "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(*machine.unique_id())

led = machine.Pin('LED', machine.Pin.OUT)

# _GENERIC = bluetooth.UUID()
# device_info = aioble.Service()


def _encode_temperature(temp_celsius):
    return struct.pack("<h", int(temp_celsius * 100))


async def sensor_task():
    t = 24.5
    while True:
        temp_char.write(_encode_temperature(t))
        t += random.uniform(-0.5, 0.5)
        await asyncio.sleep_ms(1000)


async def flash_led():
    for t in range(0, 3):
        led.on()
        await asyncio.sleep(1)
        led.off()
        await asyncio.sleep(1)


async def peripheral_task():
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            # Required for the official Generic Access service
            name="pico-temp",
            # Required for the official Generic Access service
            appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
            services=[_ENV_SENSE_UUID],
        ) as connection:
            task = asyncio.create_task(flash_led())
            print("Connection from", connection.device)
            await connection.disconnected()
            await task
            print("Disconnected")


# while True:
#     connection = await aioble.advertise(
#         _ADV_INTERVAL_MS,
#         name="temp-sense",
#         services=[_ENV_SENSE_UUID],
#         appearance=_GENERIC_THERMOMETER,
#         manufacturer=(0xabcd, b"1234"),
#     )
#     print("Connection from", device)


async def main():
    print("Temperature sensor started")
    task_1 = asyncio.create_task(sensor_task())
    task_2 = asyncio.create_task(peripheral_task())
    await asyncio.gather(task_1, task_2)


asyncio.run(main())
