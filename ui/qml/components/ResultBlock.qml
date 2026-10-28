import QtQuick
import QtQuick.Controls
import "../theme"

/* Every engine output block, rendered monochromatically. */
Item {
    id: root

    property var block: ({})
    property int index: 0

    readonly property string kind: block.type !== undefined ? block.type : "note"
    implicitHeight: layout.implicitHeight
    implicitWidth: 200
    opacity: 0

    Component.onCompleted: fade.restart()

    NumberAnimation {
        id: fade
        target: root
        property: "opacity"
        to: 1
        duration: Theme.reducedMotion ? 0 : 220
        easing.type: Easing.OutCubic
    }

    Column {
        id: layout
        width: root.width
        spacing: 8

        // -- label row with copy ----------------------------------------- //
        Item {
            width: parent.width
            height: 18
            visible: root.block.label !== undefined && root.block.label !== ""

            Text {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                text: root.block.label !== undefined ? String(root.block.label).toUpperCase() : ""
                color: Theme.paperInkSecondary
                font.family: Theme.uiFamily
                font.pixelSize: Theme.caption
                font.letterSpacing: Theme.captionTracking
                font.weight: Font.DemiBold
            }

            Item {
                id: copyHint
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                width: 62
                height: 18
                visible: layout.copyable && (copyMouse.containsMouse || layout.copied)

                Row {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 4
                    Icon {
                        name: layout.copied ? "check" : "copy"
                        size: 11
                        color: Theme.paperInkSecondary
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    Text {
                        text: layout.copied ? "Copied" : "Copy"
                        color: Theme.paperInkSecondary
                        font.pixelSize: Theme.caption
                        font.family: Theme.uiFamily
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }

            MouseArea {
                id: copyMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    App.copy(root.copyText());
                    layout.copied = true;
                    copyTimer.restart();
                }
            }
        }

        property bool copied: false
        readonly property bool copyable: root.copyText().length > 0

        Timer {
            id: copyTimer
            interval: 1400
            onTriggered: layout.copied = false
        }

        // -- value -------------------------------------------------------- //
        Text {
            width: parent.width
            visible: root.kind === "value"
            text: root.block.text !== undefined ? String(root.block.text) : ""
            color: Theme.paperInk
            font.family: Theme.monoFamily
            font.pixelSize: Math.round(24 * Theme.textScale)
            font.weight: Font.Medium
            font.letterSpacing: -0.01
            wrapMode: Text.WrapAnywhere
            textFormat: Text.PlainText
        }

        // -- key / value -------------------------------------------------- //
        Column {
            width: parent.width
            spacing: 0
            visible: root.kind === "kv"

            Repeater {
                model: root.block.pairs !== undefined ? root.block.pairs : []

                Item {
                    required property var modelData
                    width: layout.width
                    height: 30

                    Text {
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width * 0.4
                        text: modelData.k
                        color: Theme.paperInkSecondary
                        font.family: Theme.uiFamily
                        font.pixelSize: Theme.small
                        elide: Text.ElideRight
                    }

                    Text {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width * 0.58
                        horizontalAlignment: Text.AlignRight
                        text: modelData.v
                        color: Theme.paperInk
                        font.family: root.block.mono === false ? Theme.uiFamily : Theme.monoFamily
                        font.pixelSize: Theme.small
                        elide: Text.ElideRight
                    }

                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width
                        height: 1
                        color: Theme.paperHairline
                        opacity: 0.6
                    }
                }
            }
        }

        // -- list --------------------------------------------------------- //
        Column {
            width: parent.width
            spacing: 4
            visible: root.kind === "list"

            Repeater {
                model: root.block.items !== undefined ? root.block.items : []

                Text {
                    required property var modelData
                    width: layout.width
                    text: modelData
                    color: Theme.paperInk
                    font.family: root.block.mono === false ? Theme.uiFamily : Theme.monoFamily
                    font.pixelSize: Theme.small
                    wrapMode: Text.WrapAnywhere
                }
            }
        }

        // -- multi-line text ---------------------------------------------- //
        Rectangle {
            width: parent.width
            visible: root.kind === "text"
            height: textBody.implicitHeight + 20
            radius: Theme.rSm
            color: Theme.paperChip
            border.width: 1
            border.color: Theme.paperHairline

            Text {
                id: textBody
                x: 10
                y: 10
                width: parent.width - 20
                text: root.block.text !== undefined ? String(root.block.text) : ""
                color: Theme.paperInk
                font.family: root.block.mono === false ? Theme.uiFamily : Theme.monoFamily
                font.pixelSize: Theme.small
                wrapMode: Text.WrapAnywhere
                textFormat: Text.PlainText
                lineHeight: 1.35
            }
        }

        // -- swatches ----------------------------------------------------- //
        Column {
            width: parent.width
            spacing: 8
            visible: root.kind === "swatches"

            Row {
                spacing: 6
                Repeater {
                    model: root.block.colors !== undefined ? root.block.colors : []
                    Column {
                        required property var modelData
                        spacing: 5
                        Rectangle {
                            readonly property int count: Math.max(1, (root.block.colors || []).length)
                            width: Math.max(42, Math.min(76, (layout.width - 6 * count) / count))
                            height: 52
                            radius: Theme.rSm
                            color: modelData
                            border.width: 1
                            border.color: Theme.paperHairline
                        }
                        Text {
                            text: modelData
                            color: Theme.paperInkSecondary
                            font.family: Theme.monoFamily
                            font.pixelSize: 10
                        }
                    }
                }
            }

            Text {
                visible: root.block.caption !== undefined && root.block.caption !== ""
                text: root.block.caption !== undefined ? String(root.block.caption) : ""
                color: Theme.paperInkSecondary
                font.family: Theme.uiFamily
                font.pixelSize: Theme.caption
                wrapMode: Text.WrapAnywhere
            }
        }

        // -- meter -------------------------------------------------------- //
        Column {
            width: parent.width
            spacing: 6
            visible: root.kind === "meter"

            Rectangle {
                width: parent.width
                height: 6
                radius: 3
                color: Theme.paperHairline
                Rectangle {
                    width: Math.max(4, parent.width * (root.block.ratio !== undefined ? root.block.ratio : 0))
                    height: parent.height
                    radius: 3
                    color: Theme.paperInk
                }
            }

            Text {
                text: root.block.caption !== undefined ? String(root.block.caption) : ""
                color: Theme.paperInkSecondary
                font.family: Theme.monoFamily
                font.pixelSize: Theme.caption
            }
        }

        // -- note --------------------------------------------------------- //
        Item {
            width: parent.width
            height: root.kind === "note" ? noteText.implicitHeight : 0
            visible: root.kind === "note"

            Rectangle {
                width: 2
                height: parent.height
                radius: 1
                color: Theme.paperHairline
            }

            Text {
                id: noteText
                x: 12
                width: parent.width - 12
                text: root.block.text !== undefined ? String(root.block.text) : ""
                color: Theme.paperInkSecondary
                font.family: Theme.uiFamily
                font.pixelSize: Theme.small
                wrapMode: Text.WordWrap
                lineHeight: 1.4
            }
        }

        // -- error -------------------------------------------------------- //
        Item {
            width: parent.width
            height: root.kind === "error" ? errorText.implicitHeight : 0
            visible: root.kind === "error"

            Rectangle {
                width: 2
                height: parent.height
                radius: 1
                color: Theme.danger
            }

            Text {
                id: errorText
                x: 12
                width: parent.width - 12
                text: root.block.text !== undefined ? String(root.block.text) : ""
                color: Theme.danger
                font.family: Theme.uiFamily
                font.pixelSize: Theme.small
                wrapMode: Text.WordWrap
                lineHeight: 1.4
            }
        }
    }

    function copyText() {
        if (root.kind === "value" || root.kind === "text")
            return root.block.text !== undefined ? String(root.block.text) : "";
        if (root.kind === "kv") {
            var pairs = root.block.pairs || [];
            var lines = [];
            for (var i = 0; i < pairs.length; i++)
                lines.push(pairs[i].k + ": " + pairs[i].v);
            return lines.join("\n");
        }
        if (root.kind === "list")
            return (root.block.items || []).join("\n");
        if (root.kind === "swatches")
            return (root.block.colors || []).join(", ");
        return "";
    }
}
