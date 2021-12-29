# This Python file uses the following encoding: utf-8
import sys
import os
import asyncio
from struct import *
from qasync import QEventLoop
from PySide2.QtWidgets import QApplication, QColorDialog
from PySide2.QtGui import QColor
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import QObject, Slot, Signal, QSettings
from mug.mug import Mug

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
        self.keepConnectionAlive = True
        self.searchForDevice = True
        self.connectedClient = None
        self.mug = Mug(True, self.globalSettings.value("coffeeTemp"),self.globalSettings.value("teaTemp"))

    # UI Signals
    getDegree = Signal(float)
    getBattery = Signal(float)
    getColor = Signal(QColor)
    setColor = Signal(QColor)
    connectionChanged = Signal(bool)

    # UI SLOTS
    @Slot()
    def close_event(self):
        print("close")
        self.searchForDevice = False
        self.keepConnectionAlive = False
        if hasattr(self, 'timer'):
            self.timer.stop()
        asyncio.ensure_future(self.cleanup())
    @Slot(int)
    def set_coffee_temp(self, temp):
        print("Set Coffee Temperature to {}".format(temp))
        self.globalSettings.setValue("coffeeTemp", int(temp))

    @Slot(int)
    def set_tea_temp(self, temp):
        print("Set Tea Temperature to {}".format(temp))
        self.globalSettings.setValue("teaTemp", int(temp))

    @Slot(result = float)
    def get_tea_temperature(self):
        return self.globalSettings.value("teaTemp") * 0.01

    @Slot(result = float)
    def get_coffee_temperature(self):
        return self.globalSettings.value("coffeeTemp") * 0.01
        
    @Slot(result = QColor)
    def get_led_color(self):
        return self.currentColor

    @Slot()
    def set_coffee(self):
        asyncio.ensure_future(self.mug.setTargetTemp(self.globalSettings.value("coffeeTemp")))
        asyncio.ensure_future(self.mug.getTargetTemp())

    @Slot()
    def set_tea(self):
        asyncio.ensure_future(self.mug.setTargetTemp(self.globalSettings.value("teaTemp")))
        asyncio.ensure_future(self.mug.getTargetTemp())

    @Slot()
    def open_color_picker(self):
        col = QColorDialog.getColor(options = QColorDialog.ShowAlphaChannel)
        if col.isValid():
            color = bytearray([col.red(), col.green(), col.blue(), col.alpha()])
            asyncio.ensure_future(self.mug.setLEDColor(color))
            self.setColor.emit(col)
    
    # Threads 
    @asyncio.coroutine
    async def ConnectToMug(self):
        await self.mug.connect()
    
    @asyncio.coroutine
    async def UpdateUI(self):
        """Coroutine to update the UI

        Every 5 seconds we will update the UI elements
        with the current values.

        Returns:
            nothing, it will run unless the routine is killed.
        """
        while True:        
            if await self.mug.connectedClient.is_connected():
                currentTemp = await self.mug.getCurrentTemp()
                currentBat = await self.mug.getCurrentBattery()
                ledColor = await self.mug.getCurrentLEDColor()
                self.currentColor = QColor(ledColor[0], ledColor[1], ledColor[2], ledColor[3])  
                # UI Signal Calls
                self.connectionChanged.emit(True)
                self.getDegree.emit(currentTemp)
                self.getBattery.emit(currentBat)
                self.setColor.emit(self.currentColor)
                await asyncio.sleep(5)
            else:
                await asyncio.sleep(5) 
                print("Mug disconnected")
                self.connectionChanged.emit(False)    
                  
    async def cleanup(self):
        tasks = [t for t in asyncio.all_tasks() if t is not
                 asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions = True)
        loop.stop()
        print("stopped all tasks")

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
        asyncio.ensure_future(main.ConnectToMug())
        asyncio.ensure_future(main.UpdateUI())
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit) as e:
        print(f"{e.__class__.__name__} received")
    except Exception as e:
        print(e)
    finally:
        sys.exit(0)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
