import QtQuick
import "../theme"

Item {
    id: row

    property string icon: "spark"
    property string label: ""
    property int count: -1
    property bool selected: false
    property color inkColor: Theme.ink

    signal clicked()

    height: 38
    implicitWidth: 200
    activeFocusOnTab: true
    Accessible.role: Accessible.PageTab
    Accessible.name: label
    Accessible.selected: selected

    Rectangle {
        anchors.fill: parent
        radius: Theme.rSm
        color: row.selected ? Theme.chipActive : (mouse.containsMouse ? Theme.chip : "transparent")
        Behavior on color { ColorAnimation { duration: Theme.reducedMotion ? 0 : 130 } }
    }

    Rectangle {
        visible: row.selected
        x: 2
        anchors.verticalCenter: parent.verticalCenter
        width: 2.5
        height: 15
        radius: 1.5
        color: row.inkColor
    }

    Icon {
        id: glyph
        anchors.left: parent.left
        anchors.leftMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        name: row.icon
        size: 16
        color: row.selected ? row.inkColor : Theme.alpha(row.inkColor, 0.62)
    }

    Text {
        anchors.left: glyph.right
        anchors.leftMargin: 10
        anchors.right: counter.left
        anchors.rightMargin: 8
        anchors.verticalCenter: parent.verticalCenter
        text: row.label
        color: row.selected ? row.inkColor : Theme.alpha(row.inkColor, 0.72)
        font.family: Theme.uiFamily
        font.pixelSize: Theme.body
        font.weight: row.selected ? Font.DemiBold : Font.Medium
        elide: Text.ElideRight
    }

    Text {
        id: counter
        anchors.right: parent.right
        anchors.rightMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        visible: row.count >= 0
        text: row.count
        color: Theme.alpha(row.inkColor, 0.42)
        font.family: Theme.monoFamily
        font.pixelSize: Theme.caption
    }

    Rectangle {
        anchors.fill: parent
        anchors.margins: -1
        radius: Theme.rSm
        color: "transparent"
        border.width: row.activeFocus ? 1.5 : 0
        border.color: Theme.ink
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: row.clicked()
    }

    Keys.onReturnPressed: row.clicked()
    Keys.onSpacePressed: row.clicked()
}
