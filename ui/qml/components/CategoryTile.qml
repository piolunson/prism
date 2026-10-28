import QtQuick
import "../theme"

GlassPanel {
    id: tile

    property var category: ({})
    property var tools: []

    signal opened()

    radius: Theme.rLg
    blurAmount: 0.3
    shadowOpacity: hover.hovered ? 0.5 : 0.34
    shadowOffset: hover.hovered ? 18 : 12
    tint: hover.hovered ? Theme.glassTintStrong : Theme.glassTint
    implicitHeight: 184
    activeFocusOnTab: true
    Accessible.role: Accessible.Button
    Accessible.name: category.title !== undefined ? category.title : ""

    transform: Translate {
        y: hover.hovered ? -3 : 0
        Behavior on y {
            SpringAnimation {
                spring: Motion.springSettle
                damping: Motion.dampingSettle
                epsilon: Theme.reducedMotion ? 100 : 0.4
            }
        }
    }

    scale: hover.pressed ? 0.988 : 1
    Behavior on scale {
        SpringAnimation {
            spring: Motion.springPress
            damping: Motion.dampingPress
            epsilon: Theme.reducedMotion ? 100 : 0.4
        }
    }

    Rectangle {
        anchors.fill: parent
        anchors.margins: -1
        radius: tile.radius + 1
        color: "transparent"
        border.width: tile.activeFocus ? 2 : 0
        border.color: Theme.ink
        opacity: 0.55
    }

    MouseArea {
        id: hover
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: tile.opened()
    }

    Column {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 8

        Item {
            width: parent.width
            height: 34

            Rectangle {
                width: 34
                height: 34
                radius: Theme.rSm
                color: Theme.chip
                border.width: 1
                border.color: Theme.hairline
                Icon {
                    anchors.centerIn: parent
                    name: tile.category.icon !== undefined ? tile.category.icon : "spark"
                    size: 17
                    color: Theme.ink
                }
            }

            Row {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                spacing: 6

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: (tile.tools.length) + " tools"
                    color: Theme.inkTertiary
                    font.family: Theme.monoFamily
                    font.pixelSize: 10
                }

                Icon {
                    anchors.verticalCenter: parent.verticalCenter
                    name: "chevron-right"
                    size: 12
                    color: Theme.inkTertiary
                    opacity: hover.containsMouse ? 1 : 0.45
                }
            }
        }

        Item { width: 1; height: 2 }

        Text {
            width: parent.width
            text: tile.category.title !== undefined ? tile.category.title : ""
            color: Theme.ink
            font.family: Theme.uiFamily
            font.pixelSize: Theme.heading + 1
            font.weight: Font.DemiBold
            font.letterSpacing: Theme.headingTracking
        }

        Text {
            width: parent.width
            text: tile.category.subtitle !== undefined ? tile.category.subtitle : ""
            color: Theme.inkSecondary
            font.family: Theme.uiFamily
            font.pixelSize: Theme.small
            elide: Text.ElideRight
        }

        Item { width: 1; height: 2 }

        Text {
            width: parent.width
            text: tile.names()
            color: Theme.alpha(Theme.ink, 0.62)
            font.family: Theme.uiFamily
            font.pixelSize: Theme.caption
            lineHeight: 1.4
            wrapMode: Text.WordWrap
            maximumLineCount: 2
            elide: Text.ElideRight
        }
    }

    Keys.onReturnPressed: tile.opened()
    Keys.onSpacePressed: tile.opened()

    function names() {
        var out = [];
        for (var i = 0; i < tools.length; i++)
            out.push(tools[i].title);
        return out.join("  ·  ");
    }
}
