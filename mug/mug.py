import asyncio
from bleak import BleakScanner, BleakClient
from sys import platform

DEVICE_NAME = "Ember Ceramic Mug"

UUIDS = {
    "target_temp": "fc540003-236c-4c94-8fa9-944a3e5353fa", 
    "led_color": "fc540014-236c-4c94-8fa9-944a3e5353fa", 
    "current_temp": "fc540002-236c-4c94-8fa9-944a3e5353fa", 
    "current_bat": "fc540007-236c-4c94-8fa9-944a3e5353fa", 
}

class Mug: 
    def __init__(self, useCelcius: bool = True, coffeeTemp = 5500, teaTemp = 5900):
        self.useCelcius = useCelcius
        self.coffeeTemp = coffeeTemp
        self.teaTemp = teaTemp
        self.keepConnectionAlive = True
        self.searchForDevice = True
        self.connectedClient = BleakClient(None)
            
    async def getCurrentLEDColor(self): 
        """Get the current LED color.

        The value of the current color is stored as in UUIDS["led_color"] as array.

        Returns:
            The current color as bytearray.
        """
        if  self.connectedClient is not None:
            c = await self.connectedClient.read_gatt_char(UUIDS["led_color"]) 
            return c        
        else:
            print("not connected")
            
    async def getTargetTemp(self):
        """Get the current target temperature value.

        The value of the target temperature is given as bytes and needs to be converted 
        to a unsigned integer in little endian form. Afterwards it will be converted 
        to a float value with two decimal places.

        Returns:
            the target temperature as float.
        """
        if await self.connectedClient.is_connected():
            currentTargetTemp = await self.connectedClient.read_gatt_char(UUIDS["target_temp"])
            targetDegree = float(int.from_bytes(currentTargetTemp, byteorder = 'little', signed = False)) * 0.01
            print("Target temp set to {0}".format(targetDegree))
            return targetDegree
        else:
            print("not connected")
            
    async def getCurrentBattery(self): 
        """Get the current battery level.

        The value of the current battery level is given after requesting UUIDS["current_bat"]. 
        It will be converted to a float before returning. 

        Returns:
            the current battery level as float.
        """
        if await self.connectedClient.is_connected():
            curBat = await self.connectedClient.read_gatt_char(UUIDS["current_bat"])
            currentBattery = float(curBat[0])
            print("Current Bat: {0}".format(currentBattery))
            return currentBattery
        else:
            print("not connected")

    async def getCurrentTemp(self):
        """Get the current temperature value.

        The value of the current temperature is given as bytes and needs to be converted 
        to a unsigned integer in little endian form. Afterwards it will be converted 
        to a float value with two decimal places.

        Returns:
            the current temperature as float.
        """
        try:
            if await self.connectedClient.is_connected():
                currentTemp = await self.connectedClient.read_gatt_char(
                    UUIDS["current_temp"]
                )
                currentDegree = (
                    float(int.from_bytes(currentTemp, byteorder = "little", signed = False))
                    * 0.01
                )
                # Unit conversion
                if not self.useCelcius:
                    currentTemperature = (currentDegree * 1.8) + 32
                else: 
                    currentTemperature = round(currentDegree, 1)
                print("Current Temp: {0}".format(currentTemperature))
                return currentTemperature
            else:
                print("not connected")
        except Exception as exc:
            print("Error: {}".format(exc))

    async def setLEDColor(self, color):
        """Sets the LED Color.

        Args:
        color (bytearray): the LED color as bytearray

        Returns:
            no value
        """
        if await self.connectedClient.is_connected():
            await self.connectedClient.write_gatt_char(UUIDS["led_color"], color, False)
            print("Changed Color to {0}".format(color))
        else:
            print("not connected")
            
    async def setTargetTemp(self, temp): 
        """Sets the target temperature.

        Args:
        temp (float): the target temperature.

        Returns:
            no value
        """
        if await self.connectedClient.is_connected():
            newtarget = temp.to_bytes(2, 'little')
            await self.connectedClient.write_gatt_char(UUIDS["target_temp"], newtarget, False)
        else:
            print("not connected")
                        
    async def connect(self):
        """Tries to connect to the first Ember Mug it finds.

        Returns:
            no value
        """
        try:
            print("Searching..", end = '')
            # Search for the mug
            while self.searchForDevice:
                print('.', end = '')
                scanner = BleakScanner()
                await scanner.start()
                await asyncio.sleep(5.0)
                await scanner.stop()
                devices = await scanner.get_discovered_devices()

                for device in devices:
                    if device.name == DEVICE_NAME:
                        # We found the ember mug!
                        print(device.address)
                        print(device.name)
                        # try to connect to the mug
                        async with BleakClient(device) as client:
                            self.connectedClient = client
                            
                            x = await client.is_connected()
                            print("Connected")
                            if platform != "darwin":
                                # Avoid this on mac, since CoreBluetooth doesnt support pairing.
                                y = await client.pair()
                                print("Paired: {0}".format(y))
                            # Set connection parameters and use signal to send it to the UI.
                            self.keepConnectionAlive = True

                            # connected, now keeping the connecting alive.
                            while self.keepConnectionAlive:
                                # We stay in here to keep the client alive
                                # once keepConnectionAlive is set to false
                                # the client will also disconnect automatically
                                print(".")
                                await asyncio.sleep(2)
                                self.keepConnectionAlive = await self.connectedClient.is_connected()

        except Exception as exc:
            # self.connectionChanged.emit(False)
            print('Error: {}'.format(exc))