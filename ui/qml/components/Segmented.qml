import QtQuick
import "../theme"

Item {
    id: segmented

    property var options: []
    property string value: ""
    property color inkColor: Theme.paperInk
    property color trackColor: Theme.paperChip
    property color thumbColor: Theme.paperRaised
    property real fontSize: Theme.small

    signal selected(string value)

    implicitHeight: 32
    implicitWidth: row.implicitWidth + 8

    Rectangle {
        anchors.fill: parent
        radius: Theme.rSm
        color: segmented.trackColor
        border.width: 1
        border.color: Theme.paperHairline
    }

    Row {
        id: row
        anchors.fill: parent
        anchors.margins: 3
        spacing: 2

        Repeater {
            model: segmented.options

            Item {
                id: segment
                required property var modelData
                width: Math.max(46, label.implicitWidth + 20)
                height: row.height
                readonly property bool current: segmented.value === modelData.value

                Rectangle {
                    anchors.fill: parent
                    radius: Theme.rXs
                    color: segment.current ? segmented.thumbColor : "transparent"
                    border.width: segment.current ? 1 : 0
                    border.color: Theme.paperHairline
                }

                Text {
                    id: label
                    anchors.centerIn: parent
                    text: segment.modelData.label
                    color: segment.current ? segmented.inkColor : Theme.paperInkSecondary
                    font.pixelSize: segmented.fontSize
                    font.family: Theme.uiFamily
                    font.weight: segment.current ? Font.DemiBold : Font.Normal
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: segmented.selected(segment.modelData.value)
                }
            }
        }
    }
}
