import QtQuick
import QtQuick.Effects
import "../theme"

/* A translucent surface that refracts the wallpaper behind it.

   The blur reads the wallpaper layer (never an ancestor), so there is no
   cyclic sampling.  When a real backdrop is unavailable — desktop-glass mode,
   no wallpaper yet, or `frosted: false` — it degrades to a solid-er tint
   instead of stacking two translucent surfaces. */
Item {
    id: panel

    property real radius: Theme.rLg
    property color tint: Theme.glassTint
    property color strongTint: Theme.glassTintStrong
    property color edge: Theme.glassEdge
    property real blurAmount: 0.4
    property int blurMax: 48
    property real saturation: 1.12
    property bool frosted: true
    property bool shadowed: true
    property real shadowBlur: 0.7
    property real shadowOffset: 16
    property real shadowOpacity: 0.5
    property int shadowPad: 48
    property real borderWidth: 1

    default property alias contentData: contentHolder.data

    readonly property bool canFrost: frosted && !Theme.desktopGlass && Theme.wallpaperItem !== null

    // -- soft shadow -------------------------------------------------------- //
    /* A blurred ring hugging the panel edge, so the halo falls outside the
       surface (like a CSS box-shadow) instead of darkening the glass from
       underneath.  Rendered once into a texture: cheap on static content. */
    Item {
        id: shadowWrap
        anchors.fill: parent
        anchors.margins: -panel.shadowPad
        visible: panel.shadowed
        z: -1

        Item {
            id: shadowCaster
            anchors.fill: parent
            anchors.margins: panel.shadowPad
            y: panel.shadowOffset * 0.35

            Rectangle {
                anchors.fill: parent
                radius: panel.radius + 2
                color: "transparent"
                border.width: 12
                border.color: "#000000"
                antialiasing: true
            }
        }

        ShaderEffectSource {
            id: shadowTexture
            anchors.fill: shadowCaster
            sourceItem: shadowCaster
            hideSource: true
            live: false
            smooth: true
            onWidthChanged: scheduleUpdate()
            onHeightChanged: scheduleUpdate()
            Component.onCompleted: scheduleUpdate()
        }

        MultiEffect {
            anchors.fill: shadowCaster
            source: shadowTexture
            blurEnabled: true
            blur: panel.shadowBlur
            blurMax: 44
            opacity: panel.shadowOpacity
        }
    }

    // -- refracted wallpaper ------------------------------------------------ //
    ShaderEffectSource {
        id: backdrop
        anchors.fill: parent
        visible: false
        live: false
        hideSource: false
        recursive: false
        sourceItem: Theme.wallpaperItem
        sourceRect: {
            if (!Theme.wallpaperItem)
                return Qt.rect(0, 0, Math.max(1, panel.width), Math.max(1, panel.height));
            var origin = panel.mapToItem(Theme.wallpaperItem, 0, 0);
            return Qt.rect(origin.x, origin.y, Math.max(1, panel.width), Math.max(1, panel.height));
        }
        onSourceRectChanged: refresh.restart()
        onWidthChanged: refresh.restart()
        onHeightChanged: refresh.restart()
        Component.onCompleted: scheduleUpdate()
        Connections {
            target: Theme
            function onWallpaperRevisionChanged() { refresh.restart(); }
            function onDesktopGlassChanged() { refresh.restart(); }
        }
        Timer {
            id: refresh
            interval: 220
            onTriggered: backdrop.scheduleUpdate()
        }
    }

    Rectangle {
        id: maskShape
        anchors.fill: parent
        radius: panel.radius
        color: "#ffffff"
        visible: false
        layer.enabled: true
    }

    MultiEffect {
        anchors.fill: parent
        visible: panel.canFrost
        source: backdrop
        blurEnabled: true
        blur: panel.blurAmount
        blurMax: panel.blurMax
        saturation: panel.saturation
        maskEnabled: true
        maskSource: maskShape
    }

    // -- tint, edges, content ----------------------------------------------- //
    Rectangle {
        anchors.fill: parent
        radius: panel.radius
        color: panel.canFrost ? panel.tint : panel.strongTint
    }

    Rectangle {
        anchors.fill: parent
        radius: panel.radius
        color: "transparent"
        border.width: panel.borderWidth
        border.color: panel.edge
        opacity: 0.9
    }

    Item {
        id: contentHolder
        anchors.fill: parent
    }
}
