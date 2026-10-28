import QtQuick
import QtQuick.Controls
import "../theme"

/* One control that knows every field type the engine can declare. */
Item {
    id: root

    property var fieldData: ({})
    property var value: ""
    property bool showLabel: true

    signal edited(var newValue)

    readonly property string kind: fieldData.type !== undefined ? fieldData.type : "text"
    readonly property bool mono: fieldData.mono === true || kind === "number"
    implicitHeight: column.implicitHeight
    implicitWidth: 200

    Column {
        id: column
        width: root.width
        spacing: 6

        Row {
            width: parent.width
            spacing: 8
            visible: root.showLabel

            Text {
                id: labelText
                text: root.fieldData.label !== undefined ? root.fieldData.label : ""
                color: Theme.paperInkSecondary
                font.family: Theme.uiFamily
                font.pixelSize: Theme.caption
                font.weight: Font.DemiBold
                font.letterSpacing: 0.02
            }

            Item {
                height: 1
                width: Math.max(0, parent.width - labelText.width - (readout.visible ? readout.width : 0) - 16)
            }

            Text {
                id: readout
                visible: root.kind === "slider"
                text: String(root.value)
                color: Theme.paperInk
                font.family: Theme.monoFamily
                font.pixelSize: Theme.caption
            }
        }

        // -- text --------------------------------------------------------- //
        TextField {
            id: textInput
            width: parent.width
            height: 36
            visible: root.kind === "text" || root.kind === "number"
            placeholderText: root.fieldData.placeholder !== undefined ? root.fieldData.placeholder : ""
            placeholderTextColor: Theme.paperInkSecondary
            color: Theme.paperInk
            font.family: root.mono ? Theme.monoFamily : Theme.uiFamily
            font.pixelSize: Theme.body
            selectByMouse: true
            selectionColor: Theme.paperInk
            selectedTextColor: Theme.paper
            leftPadding: 10
            rightPadding: 10
            text: {
                if (root.kind === "number")
                    return String(root.value);
                return root.value === undefined || root.value === null ? "" : String(root.value);
            }
            onTextEdited: {
                if (root.kind === "number") {
                    var parsed = parseFloat(text.replace(",", "."));
                    if (!isNaN(parsed))
                        root.edited(parsed);
                } else {
                    root.edited(text);
                }
            }
            background: Rectangle {
                radius: Theme.rSm
                color: Theme.paperChip
                border.width: textInput.activeFocus ? 1.5 : 1
                border.color: textInput.activeFocus ? Theme.paperInk : Theme.paperHairline
            }
        }

        // -- textarea ----------------------------------------------------- //
        ScrollView {
            width: parent.width
            height: Math.max(76, 22 * (root.fieldData.rows !== undefined ? root.fieldData.rows : 3))
            visible: root.kind === "textarea"
            clip: true

            TextArea {
                id: textArea
                placeholderText: root.fieldData.placeholder !== undefined ? root.fieldData.placeholder : ""
                placeholderTextColor: Theme.paperInkSecondary
                color: Theme.paperInk
                font.family: root.mono ? Theme.monoFamily : Theme.uiFamily
                font.pixelSize: Theme.body
                wrapMode: TextArea.Wrap
                selectByMouse: true
                selectionColor: Theme.paperInk
                selectedTextColor: Theme.paper
                leftPadding: 10
                rightPadding: 10
                topPadding: 8
                bottomPadding: 8
                text: root.value === undefined || root.value === null ? "" : String(root.value)
                onTextChanged: {
                    // Only user edits are forwarded: writing back during a
                    // binding update would be a loop.
                    if (activeFocus && text !== String(root.value))
                        root.edited(text);
                }
                background: Rectangle {
                    radius: Theme.rSm
                    color: Theme.paperChip
                    border.width: textArea.activeFocus ? 1.5 : 1
                    border.color: textArea.activeFocus ? Theme.paperInk : Theme.paperHairline
                }
            }
        }

        // -- select ------------------------------------------------------- //
        Item {
            id: selectBox
            width: parent.width
            height: 36
            visible: root.kind === "select"

            readonly property var items: root.fieldData.options !== undefined ? root.fieldData.options : []
            readonly property var currentOption: {
                for (var i = 0; i < items.length; i++) {
                    if (items[i].value === root.value)
                        return items[i];
                }
                return items.length > 0 ? items[0] : ({ label: "—", value: "" });
            }

            Rectangle {
                anchors.fill: parent
                radius: Theme.rSm
                color: selectMouse.containsMouse || selectMenu.visible ? Theme.paperChip : Theme.paperChip
                border.width: selectMenu.visible ? 1.5 : 1
                border.color: selectMenu.visible ? Theme.paperInk : Theme.paperHairline
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 10
                anchors.right: chevron.left
                anchors.rightMargin: 6
                text: selectBox.currentOption.label
                color: Theme.paperInk
                font.family: Theme.uiFamily
                font.pixelSize: Theme.body
                elide: Text.ElideRight
            }

            Icon {
                id: chevron
                anchors.right: parent.right
                anchors.rightMargin: 9
                anchors.verticalCenter: parent.verticalCenter
                name: "chevron-down"
                size: 13
                color: Theme.paperInkSecondary
            }

            MouseArea {
                id: selectMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: selectMenu.visible ? selectMenu.close() : selectMenu.open()
            }

            Popup {
                id: selectMenu
                x: 0
                y: selectBox.height + 4
                width: selectBox.width
                padding: 4
                closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
                background: Rectangle {
                    color: Theme.paperRaised
                    radius: Theme.rSm
                    border.width: 1
                    border.color: Theme.paperHairline
                }
                contentItem: ListView {
                    implicitHeight: Math.min(contentHeight, 236)
                    model: selectBox.items
                    clip: true
                    boundsBehavior: Flickable.StopAtBounds
                    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded; width: 6 }
                    delegate: Item {
                        id: optionRow
                        required property var modelData
                        width: ListView.view.width
                        height: 32
                        Rectangle {
                            anchors.fill: parent
                            anchors.margins: 1
                            radius: Theme.rXs
                            color: optionMouse.containsMouse ? Theme.paperChip : "transparent"
                        }
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left
                            anchors.leftMargin: 10
                            anchors.right: parent.right
                            anchors.rightMargin: 10
                            text: optionRow.modelData.label
                            color: Theme.paperInk
                            font.family: Theme.uiFamily
                            font.pixelSize: Theme.small
                            elide: Text.ElideRight
                        }
                        MouseArea {
                            id: optionMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                root.edited(optionRow.modelData.value);
                                selectMenu.close();
                            }
                        }
                    }
                }
            }
        }

        // -- toggle ------------------------------------------------------- //
        Item {
            width: parent.width
            height: 26
            visible: root.kind === "toggle"

            Rectangle {
                id: track
                width: 40
                height: 24
                radius: 12
                color: root.value ? Theme.paperInk : Theme.paperChip
                border.width: root.value ? 0 : 1
                border.color: Theme.paperHairline

                Rectangle {
                    id: knob
                    width: 18
                    height: 18
                    radius: 9
                    y: 3
                    x: root.value ? track.width - width - 3 : 3
                    color: root.value ? Theme.paper : Theme.paperRaised
                    border.width: root.value ? 0 : 1
                    border.color: Theme.paperHairline
                    Behavior on x {
                        SpringAnimation {
                            spring: Motion.springPress
                            damping: Motion.dampingPress
                            epsilon: Theme.reducedMotion ? 100 : 0.5
                        }
                    }
                }
            }

            MouseArea {
                anchors.fill: parent
                anchors.margins: -6
                cursorShape: Qt.PointingHandCursor
                onClicked: root.edited(!root.value)
            }
        }

        // -- slider ------------------------------------------------------- //
        Slider {
            id: slider
            width: parent.width
            height: 28
            visible: root.kind === "slider"
            from: root.fieldData.min !== undefined ? root.fieldData.min : 0
            to: root.fieldData.max !== undefined ? root.fieldData.max : 100
            stepSize: root.fieldData.step !== undefined ? root.fieldData.step : 1
            value: Number(root.value) || 0
            onMoved: root.edited(value)
            leftPadding: 0
            rightPadding: 0

            background: Rectangle {
                x: slider.leftPadding
                y: slider.topPadding + slider.availableHeight / 2 - height / 2
                width: slider.availableWidth
                height: 4
                radius: 2
                color: Theme.paperHairline

                Rectangle {
                    width: slider.visualPosition * parent.width
                    height: parent.height
                    radius: 2
                    color: Theme.paperInk
                }
            }

            handle: Rectangle {
                x: slider.leftPadding + slider.visualPosition * (slider.availableWidth - width)
                y: slider.topPadding + slider.availableHeight / 2 - height / 2
                width: 17
                height: 17
                radius: 9
                color: Theme.paperRaised
                border.width: 2
                border.color: Theme.paperInk
                scale: slider.pressed ? 1.12 : 1
                Behavior on scale {
                    SpringAnimation {
                        spring: Motion.springPress
                        damping: Motion.dampingPress
                        epsilon: Theme.reducedMotion ? 100 : 0.5
                    }
                }
            }
        }

        // -- color -------------------------------------------------------- //
        Row {
            width: parent.width
            spacing: 8
            visible: root.kind === "color"

            Rectangle {
                width: 36
                height: 36
                radius: Theme.rSm
                color: root.value && String(root.value).length > 0 ? root.value : "transparent"
                border.width: 1
                border.color: Theme.paperHairline
            }

            TextField {
                id: colorInput
                width: parent.width - 44
                height: 36
                text: root.value === undefined ? "" : String(root.value)
                color: Theme.paperInk
                font.family: Theme.monoFamily
                font.pixelSize: Theme.body
                leftPadding: 10
                selectByMouse: true
                onTextEdited: root.edited(text)
                background: Rectangle {
                    radius: Theme.rSm
                    color: Theme.paperChip
                    border.width: colorInput.activeFocus ? 1.5 : 1
                    border.color: colorInput.activeFocus ? Theme.paperInk : Theme.paperHairline
                }
            }
        }

        Text {
            width: parent.width
            visible: root.fieldData.hint !== undefined && root.fieldData.hint !== ""
            text: root.fieldData.hint !== undefined ? root.fieldData.hint : ""
            color: Theme.paperInkSecondary
            font.family: Theme.uiFamily
            font.pixelSize: Theme.caption
            wrapMode: Text.WordWrap
            opacity: 0.85
        }
    }
}
