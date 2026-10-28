import QtQuick
import "../theme"

Item {
    id: row

    property string label: ""
    property string description: ""
    default property alias controlData: slot.data

    width: parent ? parent.width : 200
    height: Math.max(46, textColumn.implicitHeight + 8)

    Column {
        id: textColumn
        anchors.left: parent.left
        anchors.right: slot.left
        anchors.rightMargin: 20
        anchors.verticalCenter: parent.verticalCenter
        spacing: 2

        Text {
            text: row.label
            color: Theme.ink
            font.family: Theme.uiFamily
            font.pixelSize: Theme.body
            font.weight: Font.Medium
        }

        Text {
            width: parent.width
            visible: row.description !== ""
            text: row.description
            color: Theme.inkSecondary
            font.family: Theme.uiFamily
            font.pixelSize: Theme.caption
            wrapMode: Text.WordWrap
            lineHeight: 1.3
        }
    }

    Row {
        id: slot
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        spacing: 8
    }
}
