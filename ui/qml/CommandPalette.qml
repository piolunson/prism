import QtQuick
import QtQuick.Controls
import "theme"
import "components"

Item {
    id: palette
    objectName: "palette"

    property bool open: false
    property var results: []
    property int index: 0

    signal moduleRequested(string id)

    z: 900
    visible: scrim.opacity > 0.001 || panel.opacity > 0.001

    function refresh() {
        var query = searchField.text.trim();
        results = query === "" ? App.allModules() : App.search(query, 14);
        index = 0;
        list.currentIndex = 0;
        list.positionViewAtBeginning();
    }

    function toggle() {
        if (open)
            close();
        else
            show();
    }

    function show() {
        open = true;
        searchField.text = "";
        refresh();
        searchField.forceActiveFocus();
    }

    function close() {
        open = false;
    }

    function move(delta) {
        if (results.length === 0)
            return;
        index = Motion.clamp(index + delta, 0, results.length - 1);
        list.currentIndex = index;
        list.positionViewAtIndex(index, ListView.Contain);
    }

    function activate() {
        if (index < 0 || index >= results.length)
            return;
        var chosen = results[index];
        close();
        moduleRequested(chosen.id);
    }

    onOpenChanged: {
        if (open)
            refresh();
    }

    Rectangle {
        id: scrim
        anchors.fill: parent
        color: Theme.scrim
        opacity: palette.open ? 1 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: Theme.reducedMotion ? 0 : 200
                easing.type: Easing.OutCubic
            }
        }
        MouseArea {
            anchors.fill: parent
            onClicked: palette.close()
        }
    }

    GlassPanel {
        id: panel
        x: Math.round((parent.width - width) / 2)
        y: palette.open ? 86 : 70
        width: Math.min(640, parent.width - 130)
        height: Math.min(468, parent.height - 180)
        radius: Theme.rXl
        tint: Theme.dark ? Qt.rgba(0.048, 0.052, 0.06, 0.975) : Qt.rgba(0.992, 0.988, 0.976, 0.965)
        strongTint: Theme.dark ? Qt.rgba(0.048, 0.052, 0.06, 0.975) : Qt.rgba(0.992, 0.988, 0.976, 0.965)
        blurAmount: 0.5
        shadowOpacity: 0.72
        shadowOffset: 26
        opacity: palette.open ? 1 : 0
        scale: palette.open ? 1 : 0.972

        Behavior on opacity {
            NumberAnimation {
                duration: Theme.reducedMotion ? 0 : 170
                easing.type: Easing.OutCubic
            }
        }
        Behavior on scale {
            SpringAnimation {
                spring: Motion.springSettle
                damping: Motion.dampingSettle
                epsilon: Theme.reducedMotion ? 200 : 0.4
            }
        }
        Behavior on y {
            SpringAnimation {
                spring: Motion.springSettle
                damping: Motion.dampingSettle
                epsilon: 0.5
            }
        }

        Column {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            Item {
                width: parent.width
                height: 34

                Icon {
                    id: searchIcon
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    name: "search"
                    size: 17
                    color: Theme.inkSecondary
                }

                TextField {
                    id: searchField
                    objectName: "paletteSearch"
                    anchors.left: searchIcon.right
                    anchors.leftMargin: 10
                    anchors.right: escBadge.left
                    anchors.rightMargin: 10
                    anchors.verticalCenter: parent.verticalCenter
                    placeholderText: "Search tools…"
                    placeholderTextColor: Theme.inkSecondary
                    color: Theme.ink
                    font.family: Theme.uiFamily
                    font.pixelSize: 17
                    leftPadding: 0
                    rightPadding: 0
                    background: Item {}
                    selectByMouse: true
                    selectionColor: Theme.ink
                    selectedTextColor: Theme.paper
                    onTextChanged: palette.refresh()
                    Keys.onDownPressed: palette.move(1)
                    Keys.onUpPressed: palette.move(-1)
                    Keys.onReturnPressed: palette.activate()
                    Keys.onEnterPressed: palette.activate()
                    Keys.onEscapePressed: palette.close()
                }

                Rectangle {
                    id: escBadge
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    width: escText.width + 12
                    height: 18
                    radius: Theme.rXs
                    color: Theme.chip
                    border.width: 1
                    border.color: Theme.glassEdgeSoft
                    Text {
                        id: escText
                        anchors.centerIn: parent
                        text: "esc"
                        color: Theme.inkTertiary
                        font.family: Theme.monoFamily
                        font.pixelSize: 10
                    }
                }
            }

            Rectangle {
                width: parent.width
                height: 1
                color: Theme.divider
            }

            ListView {
                id: list
                width: parent.width
                height: parent.height - 96
                clip: true
                model: palette.results
                currentIndex: palette.index
                boundsBehavior: Flickable.StopAtBounds
                spacing: 1

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                    width: 4
                    contentItem: Rectangle { radius: 2; color: Theme.inkTertiary; opacity: 0.35 }
                }

                delegate: Item {
                    id: row
                    required property var modelData
                    required property int index
                    width: list.width
                    height: 46

                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: 1
                        radius: Theme.rSm
                        color: palette.index === row.index ? Theme.chipActive : (rowMouse.containsMouse ? Theme.chip : "transparent")
                    }

                    Icon {
                        id: rowIcon
                        anchors.left: parent.left
                        anchors.leftMargin: 10
                        anchors.verticalCenter: parent.verticalCenter
                        name: row.modelData.icon
                        size: 16
                        color: Theme.ink
                    }

                    Column {
                        anchors.left: rowIcon.right
                        anchors.leftMargin: 12
                        anchors.right: categoryLabel.left
                        anchors.rightMargin: 10
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 1

                        Text {
                            width: parent.width
                            text: row.modelData.title
                            color: Theme.ink
                            font.family: Theme.uiFamily
                            font.pixelSize: Theme.body
                            font.weight: Font.Medium
                            elide: Text.ElideRight
                        }

                        Text {
                            width: parent.width
                            text: row.modelData.subtitle
                            color: Theme.inkSecondary
                            font.family: Theme.uiFamily
                            font.pixelSize: Theme.caption
                            elide: Text.ElideRight
                        }
                    }

                    Text {
                        id: categoryLabel
                        anchors.right: parent.right
                        anchors.rightMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        text: row.modelData.categoryTitle !== undefined ? row.modelData.categoryTitle : ""
                        color: Theme.inkTertiary
                        font.family: Theme.uiFamily
                        font.pixelSize: Theme.caption
                    }

                    MouseArea {
                        id: rowMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onPositionChanged: palette.index = row.index
                        onClicked: {
                            palette.index = row.index;
                            palette.activate();
                        }
                    }
                }
            }

            Item {
                width: parent.width
                height: 20

                Text {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    text: palette.results.length + " result" + (palette.results.length === 1 ? "" : "s")
                    color: Theme.inkTertiary
                    font.family: Theme.monoFamily
                    font.pixelSize: 10
                }

                Text {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    text: "↑ ↓ move   ·   ↵ open"
                    color: Theme.inkTertiary
                    font.family: Theme.uiFamily
                    font.pixelSize: Theme.caption
                }
            }
        }
    }

    Shortcut {
        sequence: "Escape"
        enabled: palette.open
        onActivated: palette.close()
    }

}
