import QtQuick
import QtQuick.Window
import "theme"

Window {
    id: app

    width: 1280
    height: 830
    minimumWidth: 1000
    minimumHeight: 660
    visible: true
    title: "Prism"
    color: Theme.desktopGlass ? "transparent" : (Theme.dark ? "#0A0B0E" : "#EDE9E2")
    flags: Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint

    Binding { target: Theme; property: "dark"; value: App.dark }
    Binding { target: Theme; property: "reducedMotion"; value: App.reducedMotion }
    Binding { target: Theme; property: "desktopGlass"; value: App.desktopGlass }
    Binding { target: Theme; property: "uiFamily"; value: App.uiFont }
    Binding { target: Theme; property: "displayFamily"; value: App.displayFont }
    Binding { target: Theme; property: "monoFamily"; value: App.monoFont }
    Binding { target: Theme; property: "wallpaperItem"; value: wallpaperLayer }

    // -- wallpaper ----------------------------------------------------------- //
    Item {
        id: wallpaperLayer
        anchors.fill: parent
        opacity: Theme.desktopGlass ? 0.62 : 1

        Behavior on opacity { NumberAnimation { duration: Theme.reducedMotion ? 0 : 220 } }

        Image {
            anchors.fill: parent
            source: Icons.wallpaperLight
            fillMode: Image.PreserveAspectCrop
            opacity: Theme.dark ? 0 : 1
            Behavior on opacity {
                NumberAnimation {
                    duration: Theme.reducedMotion ? 0 : 380
                    easing.type: Easing.InOutCubic
                }
            }
            onStatusChanged: {
                if (status === Image.Ready)
                    Theme.wallpaperRevision++;
            }
        }

        Image {
            anchors.fill: parent
            source: Icons.wallpaperDark
            fillMode: Image.PreserveAspectCrop
            opacity: Theme.dark ? 1 : 0
            Behavior on opacity {
                NumberAnimation {
                    duration: Theme.reducedMotion ? 0 : 380
                    easing.type: Easing.InOutCubic
                }
            }
            onStatusChanged: {
                if (status === Image.Ready)
                    Theme.wallpaperRevision++;
            }
        }

        Image {
            anchors.fill: parent
            source: Icons.noise
            fillMode: Image.Tile
            opacity: 0.5
        }
    }

    // -- shell --------------------------------------------------------------- //
    AppShell {
        id: shell
        anchors.fill: parent
    }

    // -- theme transition veil ----------------------------------------------- //
    Rectangle {
        id: veil
        anchors.fill: parent
        color: Theme.dark ? "#0B0C0F" : "#F3EFE8"
        opacity: 0
        visible: opacity > 0.01
        z: 1000

        Behavior on opacity {
            NumberAnimation {
                duration: 320
                easing.type: Easing.OutCubic
            }
        }

        Timer {
            id: veilTimer
            interval: 30
            onTriggered: veil.opacity = 0
        }

        Connections {
            target: Theme
            function onDarkChanged() {
                veil.opacity = 0.55;
                veilTimer.restart();
            }
        }
    }

    // -- frameless resize edges ---------------------------------------------- //
    MouseArea {
        width: 6
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        cursorShape: Qt.SizeHorCursor
        onPressed: app.startSystemResize(Qt.LeftEdge)
    }

    MouseArea {
        width: 6
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        cursorShape: Qt.SizeHorCursor
        onPressed: app.startSystemResize(Qt.RightEdge)
    }

    MouseArea {
        height: 6
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        cursorShape: Qt.SizeVerCursor
        onPressed: app.startSystemResize(Qt.TopEdge)
    }

    MouseArea {
        height: 6
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        cursorShape: Qt.SizeVerCursor
        onPressed: app.startSystemResize(Qt.BottomEdge)
    }

    MouseArea {
        width: 10
        height: 10
        anchors.left: parent.left
        anchors.top: parent.top
        cursorShape: Qt.SizeFDiagCursor
        onPressed: app.startSystemResize(Qt.LeftEdge | Qt.TopEdge)
    }

    MouseArea {
        width: 10
        height: 10
        anchors.right: parent.right
        anchors.top: parent.top
        cursorShape: Qt.SizeBDiagCursor
        onPressed: app.startSystemResize(Qt.RightEdge | Qt.TopEdge)
    }

    MouseArea {
        width: 10
        height: 10
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        cursorShape: Qt.SizeBDiagCursor
        onPressed: app.startSystemResize(Qt.LeftEdge | Qt.BottomEdge)
    }

    MouseArea {
        width: 10
        height: 10
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        cursorShape: Qt.SizeFDiagCursor
        onPressed: app.startSystemResize(Qt.RightEdge | Qt.BottomEdge)
    }
}
