import QtQuick
import "../theme"

/* Monochrome SVG glyph, tinted by the Python icon provider so a single icon
   set works in both themes.  The provider rasterises at 2x for crisp edges. */
Item {
    id: icon

    property string name: "spark"
    property real size: 18
    property color color: Theme.ink
    property real strength: 1

    readonly property int pixels: Math.max(16, Math.min(256, Math.round(icon.size * 2)))

    readonly property string tint: {
        function channel(value) {
            var text = Math.round(Math.max(0, Math.min(1, value)) * 255).toString(16);
            return text.length < 2 ? "0" + text : text;
        }
        return channel(icon.color.r) + channel(icon.color.g) + channel(icon.color.b);
    }

    implicitWidth: size
    implicitHeight: size

    Image {
        anchors.fill: parent
        source: "image://prism-icon/" + icon.name + "/" + icon.tint + "/" + icon.pixels
        sourceSize: Qt.size(icon.pixels, icon.pixels)
        fillMode: Image.PreserveAspectFit
        smooth: true
        opacity: icon.strength
    }
}
