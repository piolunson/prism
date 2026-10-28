import QtQuick
import "../theme"

/* A sheet that tracks the finger 1:1, rubber-bands past its resting point,
   projects the release velocity and can be grabbed again mid-flight. */
Item {
    id: overlay

    property bool open: false
    property int panelHeight: 470
    property string title: ""

    default property alias contentData: inner.data

    z: 800
    visible: open || panel.y < height - 2

    readonly property real restY: Math.max(12, height - Math.min(panelHeight, height - 80) - 18)

    function show() {
        open = true;
        panel.y = restY;
    }

    function hide() {
        open = false;
        panel.y = overlay.height + 30;
    }

    onRestYChanged: if (open && !grab.pressed)
        panel.y = restY

    Rectangle {
        anchors.fill: parent
        color: Theme.scrim
        opacity: overlay.open ? 1 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: Theme.reducedMotion ? 0 : 220
                easing.type: Easing.OutCubic
            }
        }
        MouseArea {
            anchors.fill: parent
            onClicked: overlay.hide()
        }
    }

    GlassPanel {
        id: panel
        y: overlay.height + 30
        width: Math.min(620, parent.width - 80)
        x: Math.round((parent.width - width) / 2)
        height: Math.min(overlay.panelHeight, overlay.height - 80)
        radius: Theme.rXl
        tint: Theme.dark ? Qt.rgba(0.048, 0.052, 0.06, 0.975) : Qt.rgba(0.992, 0.988, 0.976, 0.965)
        strongTint: Theme.dark ? Qt.rgba(0.048, 0.052, 0.06, 0.975) : Qt.rgba(0.992, 0.988, 0.976, 0.965)
        shadowOpacity: 0.7
        shadowOffset: 24
        borderWidth: 1

        Behavior on y {
            enabled: !grab.pressed
            SpringAnimation {
                spring: Motion.springSheet
                damping: Motion.dampingSheet
                epsilon: Theme.reducedMotion ? 200 : 0.6
            }
        }

        MouseArea {
            id: grab
            width: parent.width
            height: 48
            y: 0
            cursorShape: Qt.SizeVerCursor

            property real pressY: 0
            property real startY: 0
            property real lastY: 0
            property real lastTime: 0
            property real velocity: 0

            onPressed: function (mouse) {
                pressY = mouse.y;
                startY = panel.y;
                lastY = mouse.y;
                lastTime = Date.now();
                velocity = 0;
            }

            onPositionChanged: function (mouse) {
                if (!pressed)
                    return;
                var target = startY + (mouse.y - pressY);
                if (target < overlay.restY)
                    target = overlay.restY - Motion.rubberband(overlay.restY - target, overlay.height);
                panel.y = target;
                var now = Date.now();
                if (now > lastTime)
                    velocity = ((mouse.y - lastY) / (now - lastTime)) * 1000;
                lastY = mouse.y;
                lastTime = now;
            }

            onReleased: {
                var projected = panel.y + Motion.project(velocity);
                if (velocity > 650 || projected > overlay.height - overlay.panelHeight * 0.55)
                    overlay.hide();
                else
                    panel.y = overlay.restY;
            }
        }

        Column {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 14

            Item {
                width: parent.width
                height: 26

                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: -10
                    width: 34
                    height: 4
                    radius: 2
                    color: Theme.inkTertiary
                    opacity: 0.45
                }

                Text {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    text: overlay.title
                    color: Theme.ink
                    font.family: Theme.uiFamily
                    font.pixelSize: Theme.heading
                    font.weight: Font.DemiBold
                    font.letterSpacing: Theme.headingTracking
                }

                IconButton {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    icon: "close"
                    size: 28
                    iconSize: 15
                    label: "Close"
                    onClicked: overlay.hide()
                }
            }

            Rectangle {
                width: parent.width
                height: 1
                color: Theme.divider
            }

            Column {
                id: inner
                width: parent.width
                spacing: 16
            }
        }
    }

    Shortcut {
        sequence: "Escape"
        enabled: overlay.open
        onActivated: overlay.hide()
    }
}
