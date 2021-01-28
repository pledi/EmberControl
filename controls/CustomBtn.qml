import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15

Button {
    id: customBtn
    // Custom Property
    property url iconSource: "../SVGs/chevron-up.svg"

    QtObject {

    }

    background: buttonBackground
    Rectangle {
        id: buttonBackground
        implicitWidth: 40
        implicitHeight: 40
        opacity: enabled ? 1 : 0.3
        color: "#00000000"
        radius: 2

        Image {
            id: iconBtn
            source: iconSource
            sourceSize.height: 48
            sourceSize.width: 48
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            height: 25
            width: 25
            antialiasing: true
            fillMode: Image.PreserveAspectFit
        }

    }
}

/*##^##
Designer {
    D{i:0;height:40;width:40}
}
##^##*/
