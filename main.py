# This Python file uses the following encoding: utf-8
import sys
import os
import asyncio
from struct import *
from sys import platform
from bleak import BleakScanner
from bleak import BleakClient
from qasync import QEventLoop, asyncClose
from PySide2.QtWidgets import QApplication, QColorDialog
from PySide2.QtGui import QColor
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import QObject, Slot, Signal, QTimer, QSettings

TARGET_TEMP = "fc540003-236c-4c94-8fa9-944a3e5353fa"
LED_COLOR_UUID = "fc540014-236c-4c94-8fa9-944a3e5353fa"
CURRENT_TEMP = "fc540002-236c-4c94-8fa9-944a3e5353fa"
CURRENT_BAT = "fc540007-236c-4c94-8fa9-944a3e5353fa"

class MainWindow(QObject):
    def __init__(self):
        QObject.__init__(self)
        # Settings
        self.globalSettings = QSettings("Pledi", "EmberControl")
        # Check for settings
        if self.globalSettings.value("coffeeTemp") is None:
            self.globalSettings.setValue("coffeeTemp", 5500)
        if self.globalSettings.value("teaTemp") is None:
            self.globalSettings.setValue("teaTemp", 5900)
        # Init
        self.coffeeTemp = int(self.globalSettings.value("coffeeTemp"))
        self.teaTemp = int(self.globalSettings.value("teaTemp"))
        self.keepConnectionAlive = True
        self.searchForDevice = True
        self.connectedClient = None
        # try to connect
        asyncio.ensure_future(self.connectToMug(self))


    # function to get the current temp from the async loop.
    def fetchCurrentTemperature(self):
        if self.connectedClient is not None:
            asyncio.ensure_future(self.getCurrentTemp(self))

    # function to get the current temp from the async loop.
    def fetchCurrentBattery(self):
        if self.connectedClient is not None:
            asyncio.ensure_future(self.getCurrentBattery(self))

    @staticmethod
    async def getCurrentTemp(self):
        try:
            if await self.connectedClient.is_connected():
                currentTemp = await self.connectedClient.read_gatt_char(CURRENT_TEMP)
                CurrentDegree = float(int.from_bytes(currentTemp, byteorder='little', signed=False)) * 0.01
                print(CurrentDegree)
                # Send UI Signal
                self.getDegree.emit(float(CurrentDegree))
            else:
                self.connectionChanged.emit(False)
                print("not connected")
        except Exception as exc:
            print('Error: {}'.format(exc))

    @staticmethod
    async def setLEDColor(self, color):
        if await self.connectedClient.is_connected():
            await self.connectedClient.write_gatt_char(LED_COLOR_UUID, color, False)
            print("Changed Color to {0}".format(color))
        else:
            self.connectionChanged.emit(False)
            print("not connected")

    @staticmethod
    async def fetchLEDColor(self):
        if await self.connectedClient.is_connected():
            c = await self.connectedClient.read_gatt_char(LED_COLOR_UUID)
            self.ledColor = QColor(c[0],c[1],c[2],c[3])
            # Send UI Signal
            self.getColor.emit(self.ledColor)
            print("Changed Color to {0}".format(self.ledColor))
        else:
            self.connectionChanged.emit(False)
            print("not connected")

    @staticmethod
    async def getTargetTemp(self):
        if await self.connectedClient.is_connected():
            currentTemp = await self.connectedClient.read_gatt_char(TARGET_TEMP)
            TargetDegree = float(int.from_bytes(currentTemp, byteorder='little', signed=False)) * 0.01
            print(TargetDegree)
        else:
            self.connectionChanged.emit(False)
            print("not connected")

    @staticmethod
    async def getCurrentBattery(self):

        if await self.connectedClient.is_connected():
            currentBat = await self.connectedClient.read_gatt_char(CURRENT_BAT)
            print(float(currentBat[0]))
            # Send UI Signal
            self.getBattery.emit(float(currentBat[0]))
        else:
            self.connectionChanged.emit(False)
            print("not connected")

    @staticmethod
    async def setToTemp(self, temp):
        if await self.connectedClient.is_connected():
            print("try setting the target temperature")
            newtarget = temp.to_bytes(2, 'little')
            await self.connectedClient.write_gatt_char(TARGET_TEMP, newtarget,False)
            currentTarget = await self.connectedClient.read_gatt_char(TARGET_TEMP)
            print("new target temp: {0}".format(currentTarget))
            # Send UI Signal
            self.getDegree.emit(float(temp * 0.01))

        else:
            self.connectionChanged.emit(False)
            print("not connected")

    @staticmethod
    async def cleanup(self):
        tasks = [t for t in asyncio.all_tasks() if t is not
                 asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()
        print("stopped")

    @staticmethod
    async def connectToMug(self):
        try:
            print("Searching..", end='')
            self.connectionChanged.emit(False)
            # Search for the mug as long til we find it.
            while self.searchForDevice:
                print('.', end='')
                scanner = BleakScanner()
                # scanner.register_detection_callback(detection_callback)
                await scanner.start()
                await asyncio.sleep(5.0)
                await scanner.stop()
                devices = await scanner.get_discovered_devices()

                for device in devices:
                    if device.name == "Ember Ceramic Mug":
                        # We found the ember mug!
                        print(device.address)
                        print(device.name)
                        print(device.details)
                        # try to connect to the mug
                        async with BleakClient(device) as client:
                            self.connectedClient = client
                            x = await client.is_connected()
                            print("Connected: {0}".format(x))
                            if platform != "darwin":
                                # Avoid this on mac, since CoreBluetooth doesnt support pairing.
                                y = await client.pair()
                                print("Paired: {0}".format(y))
                            # Set connection parameters and use signal to send it to the UI.
                            self.keepConnectionAlive = True
                            self.connectionChanged.emit(True)
                            await self.fetchLEDColor(self)
                            # Auto update Temp and Battery
                            self.timer = QTimer()
                            self.timer.timeout.connect(lambda: self.fetchCurrentTemperature())
                            self.timer.timeout.connect(lambda: self.fetchCurrentBattery())
                            self.timer.start(3000)

                            # we are connected, get the settings we need.
                            while self.keepConnectionAlive:
                                # We stay in here to keep the client alive
                                # once keepConnectionAlive is set to false
                                # the client will also disconnect automatically
                                print(".")
                                await asyncio.sleep(2)
                                self.keepConnectionAlive = await self.connectedClient.is_connected()

        except Exception as exc:
            self.connectionChanged.emit(False)
            print('Error: {}'.format(exc))

    @Slot()
    def closeEvent(self):
        print("close")
        self.searchForDevice = False
        self.keepConnectionAlive = False
        if hasattr(self, 'timer'):
            self.timer.stop()
        asyncio.ensure_future(self.cleanup(self))

    # UI Signal getDegree
    getDegree = Signal(float)

    # UI Signal getBattery
    getBattery = Signal(float)

    # UI Signal getColor
    getColor = Signal(QColor)

    # UI Signal wroteColor
    wroteColor = Signal(QColor)

    # UI Signal connectionChanged
    connectionChanged = Signal(bool)

    # UI SLOTS
    @Slot(int)
    def setCoffeeTemp(self, temp):
        print((temp))
        self.globalSettings.setValue("coffeeTemp", int(temp))

    @Slot(int)
    def setTeaTemp(self, temp):
        print((temp))
        self.globalSettings.setValue("coffeeTemp", int(temp))

    @Slot(result=float)
    def getTeaTemperature(self):
        return self.teaTemp * 0.01

    @Slot(result=float)
    def getCoffeeTemperature(self):
        return self.coffeeTemp * 0.01

    @Slot(result=QColor)
    def getLEDColor(self):
        asyncio.ensure_future(self.fetchLEDColor(self))
        print("color atm: {0}".format(self.ledColor))
        return self.ledColor

    @Slot()
    def setCoffee(self):
        asyncio.ensure_future(self.setToTemp(self, self.coffeeTemp))
        asyncio.ensure_future(self.getTargetTemp(self))

    @Slot()
    def setTea(self):
        asyncio.ensure_future(self.setToTemp(self, self.teaTemp))

    @Slot()
    def openColorPicker(self):
        col = QColorDialog.getColor(options=QColorDialog.ShowAlphaChannel)
        if col.isValid():
            color = bytearray([col.red(), col.green(), col.blue(), col.alpha()])
            asyncio.ensure_future(self.setLEDColor(self, color))
            self.wroteColor.emit(col)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    # Event Loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Get Context
    main = MainWindow()
    engine.rootContext().setContextProperty("backend", main)

    # Load QML File
    engine.load(os.path.join(os.path.dirname(__file__), "main.qml"))

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit) as e:
        logging.info(f"{e.__class__.__name__} received")
    except Exception as e:
        exception_manager.handle_exception(e)
    finally:
        sys.exit(0)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
