import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
import QtQuick.Controls.Material 2.0
import QtGraphicalEffects 1.15
import QtQuick.Controls.Styles 1.4
import "SVGs"
import "controls"


Window {
    id: settings
    width: 350
    height: 500
    visible: true
    color: "#f4f4f4"
    title: qsTr("Settings")
    flags: Qt.Window | Qt.FramelessWindowHint

    Rectangle {
        id: background
        x: 0
        y: 0
        z: 1
        width: 350
        height: 500
        gradient: Gradient {
            GradientStop {
                id: gradientStartColor
                position: 1
                color: "#30ffffff"
            }

            GradientStop {
                id: gradientStopColor
                position: 0
                color: "#30ffffff"
            }
        }

    RoundButton {
        id: roundButton
        x: 65
        width: 170
        height: 170
        text: ""
        anchors.top: parent.top
        anchors.horizontalCenterOffset: 3
        anchors.topMargin: 38
        palette.button: backend.get_led_color()
        anchors.horizontalCenter: parent.horizontalCenter
        onClicked: backend.open_color_picker()
    }

    Rectangle {
        id: topbar
        height: 32
        color: "#00000000"
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        transformOrigin: Item.Center
        anchors.rightMargin: 0
        anchors.leftMargin: 0
        anchors.topMargin: 0

        DragHandler {
            onActiveChanged: if(active){
                                 settings.startSystemMove()
                             }
        }

        MenuButton {
            id: close
            iconSource: "SVGs/close_dark.png"
            x: 265
            height: 32
            anchors.right: parent.right
            anchors.top: parent.top
            btnColorMouseOver: "#dd3c3c"
            anchors.topMargin: 0
            anchors.rightMargin: 0
            onClicked: {
                settings.close()
            }
        }
    }
    Rectangle {
        id: tempBg
        y: 271
        height: 200
        color: "#ffffff"
        radius: 12
        z:3
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.leftMargin: 20

        Label {
            id: coffeeTempLabel
            x: 210
            y: 66
            text: Number(coffeeTempSlider.value).toLocaleString(Qt.locale(),'f',2) + "°C"
            anchors.verticalCenter: coffeeTempSlider.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 20
        }

        Label {
            id: teaTempLabel
            x: 210
            y: 126
            text: Number(teaTempSlider.value).toLocaleString(Qt.locale(),'f',2) + "°C"
            anchors.verticalCenter: teaTempSlider.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 20
        }


        Label {
            id: label
            x: 106
            y: 8
            color: "#242424"
            text: qsTr("Temperature")
            styleColor: "#3d4246"
            font.pointSize: 9
            font.bold: true
        }

        Slider {
            id: coffeeTempSlider
            x: 42
            y: 54
            width: 196
            height: 40
            stepSize: 0.5
            to: 62.5
            from: 26
            value: backend.get_coffee_temperature()
            onMoved: backend.set_coffee_temp(coffeeTempSlider.value * 100)
        }

        Image {
            id: image
            x: 0
            y: 60
            width: 18
            height: 25
            anchors.left: parent.left
            source: "SVGs/coffee-outline.svg"
            anchors.leftMargin: 20
            fillMode: Image.PreserveAspectFit
        }

        Slider {
            id: teaTempSlider
            x: 42
            y: 114
            width: 196
            height: 40
            stepSize: 0.5
            value: backend.get_tea_temperature()
            to: 62.5
            from: 26
            onMoved: backend.set_tea_temp(teaTempSlider.value * 100)
        }

        Image {
            id: image1
            x: 9
            y: 122
            width: 18
            height: 25
            anchors.left: parent.left
            source: "SVGs/tea-outline.svg"
            fillMode: Image.PreserveAspectFit
            anchors.leftMargin: 20
        }

    }

    DropShadow{
            anchors.fill: tempBg
            source: tempBg
            verticalOffset: 0
            horizontalOffset: 0
            radius: 0
            color: "#40000000"
            z: 2
        }

    }

    Connections{
        target: backend

        function onSetColor(color) {
            roundButton.palette.button = color
        }

    }


}

/*##^##
Designer {
    D{i:0;formeditorZoom:0.9}
}
##^##*/
