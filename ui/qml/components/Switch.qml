import QtQuick
import "../theme"

Item {
    id: control

    property bool checked: false
    property bool enabledControl: true

    signal toggled(bool value)

    implicitWidth: 44
    implicitHeight: 26
    opacity: enabledControl ? 1 : 0.4

    Rectangle {
        anchors.fill: parent
        radius: height / 2
        color: control.checked ? Theme.paperInk : Theme.paperChip
        border.width: control.checked ? 0 : 1
        border.color: Theme.paperHairline

        Rectangle {
            width: 20
            height: 20
            radius: 10
            y: 3
            x: control.checked ? parent.width - width - 3 : 3
            color: control.checked ? Theme.paper : Theme.paperRaised
            border.width: control.checked ? 0 : 1
            border.color: Theme.paperHairline
            Behavior on x {
                SpringAnimation {
                    spring: Motion.springPress
                    damping: Motion.dampingPress
                    epsilon: Theme.reducedMotion ? 100 : 0.5
                }
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        anchors.margins: -6
        enabled: control.enabledControl
        cursorShape: Qt.PointingHandCursor
        onClicked: control.toggled(!control.checked)
    }
}
