import QtQuick
import "../theme"

GlassPanel {
    id: card

    property var meta: ({})
    property bool favorite: false
    property bool wide: false
    property real cardHeight: wide ? 150 : 132

    signal opened()
    signal favoriteToggled()

    radius: Theme.rLg
    blurAmount: 0.3
    shadowOpacity: hover.hovered ? 0.5 : 0.32
    shadowOffset: hover.hovered ? 18 : 12
    tint: hover.hovered ? Theme.glassTintStrong : Theme.glassTint
    implicitHeight: cardHeight
    activeFocusOnTab: true
    Accessible.role: Accessible.Button
    Accessible.name: (meta.title !== undefined ? meta.title : "") + ". " + (meta.subtitle !== undefined ? meta.subtitle : "")

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

    scale: hover.pressed ? 0.986 : 1
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
        radius: card.radius + 1
        color: "transparent"
        border.width: card.activeFocus ? 2 : 0
        border.color: Theme.ink
        opacity: 0.55
    }

    MouseArea {
        id: hover
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: card.opened()
    }

    Column {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 16
        anchors.verticalCenter: parent.verticalCenter
        spacing: 10

        Item {
            width: parent.width
            height: 36

            Rectangle {
                width: 36
                height: 36
                radius: Theme.rSm
                color: Theme.chip
                border.width: 1
                border.color: Theme.hairline
                Icon {
                    anchors.centerIn: parent
                    name: card.meta.icon !== undefined ? card.meta.icon : "spark"
                    size: 18
                    color: Theme.ink
                }
            }

            IconButton {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                icon: card.favorite ? "star-filled" : "star"
                iconSize: 15
                size: 28
                iconColor: card.favorite ? Theme.ink : Theme.inkSecondary
                opacity: card.favorite || hover.containsMouse ? 1 : 0
                visible: opacity > 0.01
                label: card.favorite ? "Unfavorite" : "Favorite"
                onClicked: card.favoriteToggled()
            }
        }

        Text {
            width: parent.width
            text: card.meta.title !== undefined ? card.meta.title : ""
            color: Theme.ink
            font.family: Theme.uiFamily
            font.pixelSize: Theme.heading
            font.weight: Font.DemiBold
            font.letterSpacing: Theme.headingTracking
            elide: Text.ElideRight
        }

        Text {
            width: parent.width
            text: card.meta.subtitle !== undefined ? card.meta.subtitle : ""
            color: Theme.inkSecondary
            font.family: Theme.uiFamily
            font.pixelSize: Theme.small
            lineHeight: 1.25
            wrapMode: Text.WordWrap
            maximumLineCount: card.wide ? 2 : 1
            elide: Text.ElideRight
        }
    }

    Keys.onReturnPressed: card.opened()
    Keys.onSpacePressed: card.opened()
}
