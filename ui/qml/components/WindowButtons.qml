import QtQuick
import "../theme"

Row {
    id: controls

    property bool dark: false
    signal minimizeRequested()
    signal maximizeRequested()
    signal closeRequested()

    spacing: 2

    IconButton {
        icon: "minimize"
        iconSize: 14
        size: 30
        label: "Minimize"
        onClicked: controls.minimizeRequested()
    }

    IconButton {
        icon: (Window.window && Window.window.visibility === Window.Maximized) ? "restore" : "maximize"
        iconSize: 13
        size: 30
        label: "Maximize"
        onClicked: controls.maximizeRequested()
    }

    IconButton {
        icon: "close"
        iconSize: 14
        size: 30
        label: "Close"
        iconColor: closeMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.96) : Theme.ink
        hoverColor: Theme.danger
        pressColor: Theme.danger

        MouseArea {
            id: closeMouse
            anchors.fill: parent
            anchors.margins: -4
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: controls.closeRequested()
        }
    }
}
