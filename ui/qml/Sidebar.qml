import QtQuick
import QtQuick.Controls
import "theme"
import "components"

GlassPanel {
    id: sidebar

    property var categories: []
    property var favorites: []
    property string currentView: "home"
    property string currentCategory: ""
    property string currentModule: ""
    property int moduleCount: 24
    property bool dark: false

    signal homeRequested()
    signal categoryRequested(string id)
    signal moduleRequested(string id)
    signal searchRequested()
    signal settingsRequested()
    signal themeToggled()
    signal dragRequested()

    radius: Theme.rXl
    tint: Theme.glassTintStrong
    strongTint: Theme.dark ? "#0D0F13F0" : "#FBF9F5F0"
    blurAmount: 0.52
    blurMax: 52
    saturation: 1.18
    shadowOpacity: 0.42
    shadowOffset: 20
    borderWidth: 1

    // Window drag surface behind the header controls.
    MouseArea {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 52
        onPressed: sidebar.dragRequested()
        onDoubleClicked: sidebar.dragRequested()
    }

    Item {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 14
        anchors.bottom: undefined
        height: 40

        Image {
            id: mark
            anchors.verticalCenter: parent.verticalCenter
            x: 0
            width: 26
            height: 26
            source: Theme.dark ? Icons.markDark : Icons.markLight
            sourceSize: Qt.size(52, 52)
            fillMode: Image.PreserveAspectFit
        }

        Text {
            anchors.left: mark.right
            anchors.leftMargin: 10
            anchors.verticalCenter: parent.verticalCenter
            text: "Prism"
            color: Theme.ink
            font.family: Theme.displayFamily
            font.pixelSize: 17
            font.weight: Font.DemiBold
            font.letterSpacing: -0.02
        }

        IconButton {
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            icon: Theme.dark ? "sun" : "moon"
            iconSize: 15
            size: 28
            label: Theme.dark ? "Switch to light" : "Switch to dark"
            onClicked: sidebar.themeToggled()
        }
    }

    SearchPill {
        id: searchPill
        anchors.top: header.bottom
        anchors.topMargin: 12
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: 14
        anchors.rightMargin: 14
        placeholder: "Search " + sidebar.moduleCount + " tools"
        onClicked: sidebar.searchRequested()
    }

    Flickable {
        id: nav
        anchors.top: searchPill.bottom
        anchors.topMargin: 14
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: footer.top
        anchors.bottomMargin: 8
        anchors.leftMargin: 8
        anchors.rightMargin: 8
        contentWidth: width
        contentHeight: navColumn.height + 8
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
            width: 4
            contentItem: Rectangle { radius: 2; color: Theme.inkTertiary; opacity: 0.4 }
        }

        Column {
            id: navColumn
            width: nav.width
            spacing: 2

            SidebarRow {
                width: navColumn.width
                icon: "home"
                label: "All tools"
                count: sidebar.moduleCount
                selected: sidebar.currentView === "home"
                onClicked: sidebar.homeRequested()
            }

            Text {
                x: 10
                width: parent.width - 10
                height: 26
                verticalAlignment: Text.AlignBottom
                bottomPadding: 4
                text: "CATEGORIES"
                color: Theme.inkTertiary
                font.family: Theme.uiFamily
                font.pixelSize: 10
                font.letterSpacing: 0.09
                font.weight: Font.DemiBold
            }

            Repeater {
                model: sidebar.categories

                SidebarRow {
                    required property var modelData
                    width: navColumn.width
                    icon: modelData.icon
                    label: modelData.title
                    count: modelData.count
                    selected: sidebar.currentCategory === modelData.id && sidebar.currentView !== "home"
                    onClicked: sidebar.categoryRequested(modelData.id)
                }
            }

            Rectangle {
                width: navColumn.width - 20
                x: 10
                height: 1
                color: Theme.divider
            }

            Text {
                x: 10
                width: parent.width - 10
                height: 26
                verticalAlignment: Text.AlignBottom
                bottomPadding: 4
                text: "FAVORITES"
                color: Theme.inkTertiary
                font.family: Theme.uiFamily
                font.pixelSize: 10
                font.letterSpacing: 0.09
                font.weight: Font.DemiBold
            }

            Repeater {
                model: sidebar.favorites

                SidebarRow {
                    required property var modelData
                    width: navColumn.width
                    icon: modelData.icon
                    label: modelData.title
                    selected: sidebar.currentView === "module" && sidebar.currentModule === modelData.id
                    onClicked: sidebar.moduleRequested(modelData.id)
                }
            }

            Text {
                width: parent.width - 20
                x: 10
                visible: sidebar.favorites.length === 0
                text: "Star a tool to pin it here."
                color: Theme.inkTertiary
                font.family: Theme.uiFamily
                font.pixelSize: Theme.caption
                wrapMode: Text.WordWrap
                lineHeight: 1.3
            }
        }
    }

    Item {
        id: footer
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 14
        height: 34

        Rectangle {
            anchors.top: parent.top
            width: parent.width
            height: 1
            color: Theme.divider
        }

        Text {
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            text: "v" + App.version + " · local only"
            color: Theme.inkTertiary
            font.family: Theme.monoFamily
            font.pixelSize: 10
        }

        Row {
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            spacing: 2

            IconButton {
                icon: "gear"
                iconSize: 15
                size: 28
                label: "Appearance settings"
                onClicked: sidebar.settingsRequested()
            }
        }
    }
}
