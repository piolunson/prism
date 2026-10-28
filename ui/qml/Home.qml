import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "theme"
import "components"

Item {
    id: home
    objectName: "homeView"

    property var categories: []
    property var recents: []
    property int moduleCount: 24

    signal categoryRequested(string id)
    signal moduleRequested(string id)

    Flickable {
        id: flick
        anchors.fill: parent
        contentWidth: width
        contentHeight: content.height + 48
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
            width: 5
            contentItem: Rectangle { radius: 2.5; color: Theme.inkTertiary; opacity: 0.35 }
        }

        Column {
            id: content
            x: 28
            y: 18
            width: flick.width - 56
            spacing: 22

            // -- hero ----------------------------------------------------- //
            Item {
                width: parent.width
                height: heroColumn.height + 10

                Column {
                    id: heroColumn
                    width: Math.max(280, parent.width - 130)
                    spacing: 10

                    Text {
                        text: home.moduleCount + " TOOLS  ·  6 CATEGORIES  ·  100% LOCAL"
                        color: Theme.alpha(Theme.ink, 0.52)
                        font.family: Theme.uiFamily
                        font.pixelSize: 11
                        font.letterSpacing: 0.12
                        font.weight: Font.DemiBold
                    }

                    Text {
                        width: parent.width
                        text: "Everything,\nin one place."
                        color: Theme.ink
                        font.family: Theme.displayFamily
                        font.pixelSize: Math.round(38 * Theme.textScale)
                        font.weight: Font.DemiBold
                        font.letterSpacing: Theme.displayTracking
                        lineHeight: 0.98
                    }

                    Text {
                        width: Math.min(430, parent.width)
                        text: "Small, fast, private tools for the work between the work. Pick a category, or press Ctrl K."
                        color: Theme.alpha(Theme.ink, 0.62)
                        font.family: Theme.uiFamily
                        font.pixelSize: Theme.body
                        lineHeight: 1.4
                        wrapMode: Text.WordWrap
                    }
                }

                Image {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.topMargin: 8
                    width: 84
                    height: 84
                    source: Theme.dark ? Icons.markDark : Icons.markLight
                    sourceSize: Qt.size(168, 168)
                    fillMode: Image.PreserveAspectFit
                    opacity: 0.92
                }
            }

            // -- recents -------------------------------------------------- //
            Column {
                width: parent.width
                spacing: 8
                visible: home.recents.length > 0

                Text {
                    text: "RECENT"
                    color: Theme.inkTertiary
                    font.family: Theme.uiFamily
                    font.pixelSize: 10
                    font.letterSpacing: 0.12
                    font.weight: Font.DemiBold
                }

                Flow {
                    width: parent.width
                    spacing: 8

                    Repeater {
                        model: home.recents

                        Rectangle {
                            required property var modelData
                            width: chipRow.implicitWidth + 22
                            height: 30
                            radius: height / 2
                            color: chipMouse.containsMouse ? Theme.chipHover : Theme.chip
                            border.width: 1
                            border.color: Theme.glassEdgeSoft

                            Row {
                                id: chipRow
                                anchors.centerIn: parent
                                spacing: 6
                                Icon { name: modelData.icon; size: 12; color: Theme.ink; anchors.verticalCenter: parent.verticalCenter }
                                Text {
                                    text: modelData.title
                                    color: Theme.ink
                                    font.family: Theme.uiFamily
                                    font.pixelSize: Theme.small
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }

                            MouseArea {
                                id: chipMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: home.moduleRequested(modelData.id)
                            }
                        }
                    }
                }
            }

            // -- categories ------------------------------------------------ //
            GridLayout {
                id: grid
                width: parent.width
                columns: Math.max(2, Math.floor(width / 254))
                columnSpacing: 14
                rowSpacing: 14

                Repeater {
                    model: home.categories

                    CategoryTile {
                        required property var modelData
                        Layout.fillWidth: true
                        Layout.minimumWidth: 200
                        Layout.preferredHeight: 184
                        category: modelData
                        tools: App.modulesIn(modelData.id)
                        onOpened: home.categoryRequested(modelData.id)
                    }
                }
            }

            Item { width: 1; height: 4 }
        }
    }
}
