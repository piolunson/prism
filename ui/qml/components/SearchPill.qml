import QtQuick
import "../theme"

Item {
    id: pill

    property string placeholder: "Search tools"
    property string shortcut: "Ctrl K"
    property bool compact: false

    signal clicked()

    height: 32
    implicitWidth: compact ? 190 : 260
    activeFocusOnTab: true
    Accessible.role: Accessible.Button
    Accessible.name: "Search"

    Rectangle {
        anchors.fill: parent
        radius: Theme.rSm
        color: mouse.containsMouse ? Theme.chipHover : Theme.chip
        border.width: pill.activeFocus ? 1.5 : 1
        border.color: pill.activeFocus ? Theme.ink : Theme.glassEdgeSoft
    }

    Icon {
        anchors.left: parent.left
        anchors.leftMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        name: "search"
        size: 13
        color: Theme.inkSecondary
    }

    Text {
        anchors.left: parent.left
        anchors.leftMargin: 30
        anchors.right: badge.left
        anchors.rightMargin: 8
        anchors.verticalCenter: parent.verticalCenter
        text: pill.placeholder
        color: Theme.inkSecondary
        font.family: Theme.uiFamily
        font.pixelSize: Theme.small
        elide: Text.ElideRight
    }

    Rectangle {
        id: badge
        anchors.right: parent.right
        anchors.rightMargin: 7
        anchors.verticalCenter: parent.verticalCenter
        visible: !pill.compact
        width: shortcutText.width + 12
        height: 18
        radius: Theme.rXs
        color: Theme.chip
        border.width: 1
        border.color: Theme.glassEdgeSoft

        Text {
            id: shortcutText
            anchors.centerIn: parent
            text: pill.shortcut
            color: Theme.inkTertiary
            font.family: Theme.monoFamily
            font.pixelSize: 10
        }
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: pill.clicked()
    }

    Keys.onReturnPressed: pill.clicked()
    Keys.onSpacePressed: pill.clicked()
}
