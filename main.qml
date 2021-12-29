import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls.Material 2.0
import QtQuick.Controls 2.15
import "controls"
import QtGraphicalEffects 1.15

Window {
    id: window
    width: 300
    height: 400
    visible: true
    color: "#00000000"
    title: qsTr("Ember Control")

    flags: Qt.Window | Qt.FramelessWindowHint

    QtObject{
        id: internal
        function showSettings(){
            var component = Qt.createComponent("Settings.qml")
            var win = component.createObject()
            win.show()
        }
    }

    Rectangle {
        id: background
        x: 0
        y: 0
        width: 300
        height: 400
        color: "#ff5858"
        layer.enabled: true
        rotation: -360
        z: 1
        gradient: Gradient {
            GradientStop {
                id: gradientStartColor
                position: 1
                color: "#ff5858"
            }

            GradientStop {
                id: gradientStopColor
                position: 0
                color: "#f09819"
            }
        }

        PropertyAnimation {
            id: animationCold2
            target: gradientStartColor
            property: "color"
            to: "#0E1533"
            duration: 10000
        }

        PropertyAnimation {
            id: animationCold1
            target: gradientStopColor
            property: "color"
            to: "#294663"
            duration: 10000
        }

        PropertyAnimation {
            id: animationwarm2
            target: gradientStartColor
            property: "color"
            to: "#873746"
            duration: 10000
        }

        PropertyAnimation {
            id: animationwarm1
            target: gradientStopColor
            property: "color"
            to: "#8D6F3E"
            duration: 10000
        }

        PropertyAnimation {
            id: animationHot2
            target: gradientStartColor
            property: "color"
            to: "#ff5858"
            duration: 10000
        }

        PropertyAnimation {
            id: animationHot1
            target: gradientStopColor
            property: "color"
            to: "#f09819"
            duration: 10000
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
                                     window.startSystemMove()
                                 }
            }

            Image {
                id: image
                x: 3
                y: 3
                width: 15
                height: 15
                horizontalAlignment: Image.AlignRight
                visible: text2.text !== ""
                source: "SVGs/battery-80.png"
                cache: true
                autoTransform: false
                sourceSize.height: 40
                sourceSize.width: 40
                fillMode: Image.PreserveAspectFit

            }

            Text {
                id: text2
                x: 20
                y: 3
                color: "#ffffff"
                text: qsTr("")
                font.pixelSize: 12
                horizontalAlignment: Text.AlignHCenter
                styleColor: "#00000000"
            }

            MenuButton {
                id: close
                iconSource: "SVGs/close.png"
                x: 265
                height: 32
                anchors.right: parent.right
                anchors.top: parent.top
                btnColorMouseOver: "#dd3c3c"
                anchors.topMargin: 0
                anchors.rightMargin: 0
                onClicked: {
                    backend.close_event()
                    window.close()
                }
            }

            MenuButton {
                id: minimize
                x: 224
                width: 35
                height: 32
                anchors.right: close.left
                anchors.top: parent.top
                anchors.topMargin: 0
                iconSource: "SVGs/minus.png"
                anchors.rightMargin: 0
                btnColorMouseOver: "#5cffffff"
                onClicked: window.showMinimized()
            }
        }

        Rectangle {
            id: content
            color: "#00000000"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: topbar.bottom
            anchors.bottom: parent.bottom
            anchors.rightMargin: 0
            anchors.bottomMargin: 55
            anchors.leftMargin: 0
            anchors.topMargin: 0

            Text {
                id: text1
                x: 89
                y: 138
                color: "#ffffff"
                text: qsTr("")
                anchors.verticalCenter: parent.verticalCenter
                font.pixelSize: 50
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignTop
                renderType: Text.QtRendering
                anchors.horizontalCenter: parent.horizontalCenter
                style: Text.Normal
                font.styleName: "Regular"
                font.bold: true
            }

            BusyIndicator {
                id: busyIndicator
                anchors.verticalCenter: parent.verticalCenter
                visible: text1.text == ""
                Component.onCompleted: {
                    contentItem.pen = "white"
                    contentItem.fill = "white"
                }
                anchors.verticalCenterOffset: 0
                anchors.horizontalCenterOffset: 2
                anchors.horizontalCenter: parent.horizontalCenter
            }

        }

        Rectangle {
            id: bottombar
            height: 40
            color: "#00000000"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.leftMargin: 0
            anchors.rightMargin: 0

            PropertyAnimation {
                id: animationMenu
                target: bottombar
                property: "anchors.bottomMargin"
                to: if(bottombar.anchors.bottomMargin == 40) return 0; else return 40;
                duration: 200
                easing.type: Easing.InOutQuint
            }

            CustomBtn {
                id: expand
                anchors.fill: parent
                enabled: false
                anchors.rightMargin: 0
                anchors.bottomMargin: 0
                anchors.leftMargin: 0
                anchors.topMargin: 0
                autoRepeat: false
                iconSource: if(bottombar.anchors.bottomMargin == 40) return "SVGs/chevron-down.png"; else return "SVGs/chevron-up.png";
                flat: false
                onClicked: animationMenu.running = true

                Row {
                    id: presets
                    x: -8
                    y: 40
                    height: 41
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    rightPadding: 20
                    leftPadding: 20
                    spacing: 70
                    anchors.rightMargin: 0
                    anchors.leftMargin: 0
                    anchors.bottomMargin: -41

                    CustomBtn {
                        id: coffeeBtn
                        iconSource: "SVGs/coffee-outline.png"
                        display: AbstractButton.IconOnly
                        onClicked: backend.set_coffee()
                    }

                    CustomBtn {
                        id: button1
                        text: qsTr("Button")
                        iconSource: "SVGs/tea-outline.png"
                        display: AbstractButton.IconOnly
                        onClicked: backend.set_tea()
                    }

                    CustomBtn {
                        id: button2
                        width: 40
                        height: 40
                        text: qsTr("Button")
                        iconSource: "SVGs/thermometer-plus.png"
                        display: AbstractButton.IconOnly
                        onClicked: internal.showSettings()


                    }
                }
            }
        }
    }

    DropShadow {
        visible: false
        anchors.fill: background
        horizontalOffset: 0
        verticalOffset: 0
        radius: 10
        samples: 16
        color: "#80000000"
        source: background
        z: 0
    }

    Connections{
        target: backend

        //function to disable buttons when no mug is connected
        //Still needs to automatically hide or kill the settings window.
        function onConnectionChanged(connected){
            if(connected){
                busyIndicator.visible = false
                expand.enabled = true
                coffeeBtn.enabled = true
                button1.enabled = true
                button2.enabled = true
            }else{
                expand.enabled = false
                coffeeBtn.enabled = false
                button1.enabled = false
                button2.enabled = false
            }
        }

        function onGetDegree(degree) {
            text1.text = String(degree) + "°C"
            if(degree > 53.0){
                animationHot1.running = true
                animationHot2.running = true
            }else if(degree > 40.0){
                animationwarm1.running = true
                animationwarm2.running = true
            }else{
                animationCold1.running = true
                animationCold2.running = true
            }
        }

        function onGetBattery(battery) {
            text2.text = String(battery) + "%"
            if(battery > 90.0){
                image.source = "SVGs/battery.png"
            }else if(battery > 75.0){
                image.source = "SVGs/battery-80.png"
            }else if(battery > 30.0){
                image.source = "SVGs/battery-50.png"
            }else{
                image.source = "SVGs/battery-20.png"
            }
        }
    }

}

/*##^##
Designer {
    D{i:0;formeditorZoom:1.66}
}
##^##*/
