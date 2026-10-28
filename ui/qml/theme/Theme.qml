pragma Singleton
import QtQuick

/* Semantic tokens only — components never name a raw colour. */
QtObject {
    id: theme

    property bool dark: false
    property bool reducedMotion: false
    property bool desktopGlass: false
    property string uiFamily: "Segoe UI"
    property string displayFamily: "Segoe UI"
    property string monoFamily: "Consolas"
    property Item wallpaperItem: null
    property int wallpaperRevision: 0
    property real textScale: 1.0

    // -- ink ---------------------------------------------------------------- //
    readonly property color ink: dark ? "#F4F2ED" : "#14161A"
    readonly property color inkSecondary: dark ? "#A9AFB8" : "#5E646D"
    readonly property color inkTertiary: dark ? "#79808A" : "#8A9099"
    readonly property color danger: dark ? "#FF8A7B" : "#B23A2F"

    // -- monochrome interiors ----------------------------------------------- //
    readonly property color paper: dark ? "#121417" : "#FCFBF8"
    readonly property color paperRaised: dark ? "#181B1F" : "#FFFFFF"
    readonly property color paperInk: dark ? "#F1EFE9" : "#101215"
    readonly property color paperInkSecondary: dark ? "#9AA1AA" : "#5C6167"
    readonly property color paperHairline: dark ? Qt.rgba(1, 1, 1, 0.13) : Qt.rgba(0.063, 0.071, 0.082, 0.11)
    readonly property color paperChip: dark ? Qt.rgba(1, 1, 1, 0.07) : Qt.rgba(0.063, 0.071, 0.082, 0.05)

    // -- glass -------------------------------------------------------------- //
    readonly property color glassTint: dark ? Qt.rgba(0.055, 0.063, 0.078, 0.42) : Qt.rgba(1, 1, 1, 0.16)
    readonly property color glassTintStrong: dark ? Qt.rgba(0.035, 0.039, 0.047, 0.5) : Qt.rgba(1, 1, 1, 0.26)
    readonly property color glassEdge: dark ? Qt.rgba(1, 1, 1, 0.16) : Qt.rgba(1, 1, 1, 0.74)
    readonly property color glassEdgeSoft: dark ? Qt.rgba(1, 1, 1, 0.08) : Qt.rgba(0.078, 0.086, 0.102, 0.09)
    readonly property color hairline: dark ? Qt.rgba(1, 1, 1, 0.14) : Qt.rgba(0.063, 0.071, 0.082, 0.1)
    readonly property color hairlineStrong: dark ? Qt.rgba(1, 1, 1, 0.24) : Qt.rgba(0.063, 0.071, 0.082, 0.19)
    readonly property color shadow: dark ? Qt.rgba(0, 0, 0, 0.55) : Qt.rgba(0.09, 0.12, 0.18, 0.16)
    readonly property color scrim: dark ? Qt.rgba(0, 0, 0, 0.6) : Qt.rgba(0.1, 0.11, 0.13, 0.32)

    // -- chrome ------------------------------------------------------------- //
    readonly property color chip: dark ? Qt.rgba(1, 1, 1, 0.07) : Qt.rgba(0.063, 0.071, 0.082, 0.05)
    readonly property color chipHover: dark ? Qt.rgba(1, 1, 1, 0.12) : Qt.rgba(0.063, 0.071, 0.082, 0.09)
    readonly property color chipActive: dark ? Qt.rgba(1, 1, 1, 0.17) : Qt.rgba(0.063, 0.071, 0.082, 0.13)
    readonly property color divider: dark ? Qt.rgba(1, 1, 1, 0.09) : Qt.rgba(0.063, 0.071, 0.082, 0.08)

    // -- geometry ----------------------------------------------------------- //
    readonly property int rXs: 6
    readonly property int rSm: 9
    readonly property int rMd: 13
    readonly property int rLg: 18
    readonly property int rXl: 24
    readonly property int rXxl: 30

    readonly property int sXs: 4
    readonly property int sSm: 8
    readonly property int sMd: 12
    readonly property int sLg: 16
    readonly property int sXl: 24
    readonly property int sXxl: 32
    readonly property int sXxxl: 44

    readonly property int sidebarWidth: 252
    readonly property int titlebarHeight: 52

    // -- type --------------------------------------------------------------- //
    readonly property real display: Math.round(33 * textScale)
    readonly property real title: Math.round(22 * textScale)
    readonly property real heading: Math.round(16 * textScale)
    readonly property real body: Math.round(14 * textScale)
    readonly property real small: Math.round(12.5 * textScale)
    readonly property real caption: Math.round(11 * textScale)

    // Size-specific tracking: tighten as type grows, open it up when tiny.
    readonly property real displayTracking: -0.024
    readonly property real titleTracking: -0.018
    readonly property real headingTracking: -0.011
    readonly property real bodyTracking: 0
    readonly property real smallTracking: 0.004
    readonly property real captionTracking: 0.06

    function alpha(colorValue, value) {
        return Qt.rgba(colorValue.r, colorValue.g, colorValue.b, value)
    }
}
