import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "theme"
import "components"

Item {
    id: categoryView
    objectName: "categoryView"

    property string categoryId: ""
    property var category: ({})
    property var tools: []

    signal homeRequested()
    signal moduleRequested(string id)

    onCategoryIdChanged: refresh()

    Component.onCompleted: refresh()

    function refresh() {
        var all = App.categories();
        for (var i = 0; i < all.length; i++) {
            if (all[i].id === categoryId) {
                category = all[i];
                break;
            }
        }
        tools = App.modulesIn(categoryId);
    }

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
            y: 16
            width: flick.width - 56
            spacing: 18

            Row {
                width: parent.width
                spacing: 14

                Rectangle {
                    width: 48
                    height: 48
                    radius: Theme.rMd
                    color: Theme.chip
                    border.width: 1
                    border.color: Theme.hairline
                    Icon {
                        anchors.centerIn: parent
                        name: categoryView.category.icon !== undefined ? categoryView.category.icon : "spark"
                        size: 23
                        color: Theme.ink
                    }
                }

                Column {
                    width: parent.width - 62
                    spacing: 4
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        text: categoryView.category.title !== undefined ? categoryView.category.title : ""
                        color: Theme.ink
                        font.family: Theme.displayFamily
                        font.pixelSize: Math.round(28 * Theme.textScale)
                        font.weight: Font.DemiBold
                        font.letterSpacing: Theme.displayTracking
                    }

                    Text {
                        width: parent.width
                        text: categoryView.category.subtitle !== undefined ? categoryView.category.subtitle : ""
                        color: Theme.inkSecondary
                        font.family: Theme.uiFamily
                        font.pixelSize: Theme.body
                        elide: Text.ElideRight
                    }
                }
            }

            Rectangle {
                width: parent.width
                height: 1
                color: Theme.divider
            }

            GridLayout {
                width: parent.width
                columns: Math.max(1, Math.floor(width / 380))
                columnSpacing: 14
                rowSpacing: 14

                Repeater {
                    model: categoryView.tools

                    ModuleCard {
                        required property var modelData
                        Layout.fillWidth: true
                        Layout.minimumWidth: 240
                        Layout.preferredHeight: 128
                        wide: false
                        meta: modelData
                        favorite: App.isFavorite(modelData.id)
                        onOpened: categoryView.moduleRequested(modelData.id)
                        onFavoriteToggled: {
                            App.toggleFavorite(modelData.id);
                            favorite = App.isFavorite(modelData.id);
                        }
                    }
                }
            }

            Text {
                visible: categoryView.tools.length === 0
                text: "Nothing here yet."
                color: Theme.inkSecondary
                font.pixelSize: Theme.body
            }

            Item { width: 1; height: 8 }
        }
    }
}
