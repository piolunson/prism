pragma Singleton
import QtQuick

/* Asset lookup.  Everything is resolved relative to this file so the same
   paths work from source and from inside a PyInstaller bundle. */
QtObject {
    readonly property url iconDir: Qt.resolvedUrl("../../../assets/icons/")
    readonly property url logoLight: Qt.resolvedUrl("../../../assets/logo.svg")
    readonly property url logoDark: Qt.resolvedUrl("../../../assets/logo-dark.svg")
    readonly property url markLight: Qt.resolvedUrl("../../../assets/mark.svg")
    readonly property url markDark: Qt.resolvedUrl("../../../assets/mark-dark.svg")
    readonly property url wallpaperLight: Qt.resolvedUrl("../../../assets/graphics/wallpaper-light.svg")
    readonly property url wallpaperDark: Qt.resolvedUrl("../../../assets/graphics/wallpaper-dark.svg")
    readonly property url noise: Qt.resolvedUrl("../../../assets/graphics/noise.png")

    function path(name) {
        return iconDir + (name || "spark") + ".svg";
    }

    function logo(isDark) {
        return isDark ? markDark : markLight;
    }

    function wallpaper(isDark) {
        return isDark ? wallpaperDark : wallpaperLight;
    }
}
