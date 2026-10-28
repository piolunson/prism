import QtQuick
import "../theme"

Item {
    id: button

    property string icon: "gear"
    property real iconSize: 16
    property color iconColor: Theme.ink
    property color hoverColor: Theme.chipHover
    property color pressColor: Theme.chipActive
    property bool toggled: false
    property string label: ""
    property int size: 30
    property bool circular: false

    signal clicked()

    implicitWidth: size
    implicitHeight: size
    activeFocusOnTab: true
    Accessible.role: Accessible.Button
    Accessible.name: label !== "" ? label : icon

    Rectangle {
        id: backdrop
        anchors.fill: parent
        radius: button.circular ? width / 2 : Theme.rSm
        color: mouse.pressed ? button.pressColor : (mouse.containsMouse || button.activeFocus) ? button.hoverColor : (button.toggled ? button.hoverColor : "transparent")
        border.width: button.activeFocus ? 1 : 0
        border.color: Theme.ink

        Behavior on color { ColorAnimation { duration: Theme.reducedMotion ? 0 : 120 } }
    }

    Icon {
        anchors.centerIn: parent
        name: button.icon
        size: button.iconSize
        color: button.iconColor
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        anchors.margins: -4
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: button.clicked()
    }

    Keys.onReturnPressed: button.clicked()
    Keys.onSpacePressed: button.clicked()
}
