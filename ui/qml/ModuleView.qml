import QtQuick
import QtQuick.Controls
import "theme"
import "components"

/* The tool itself: a sheet of paper with ink, hairline rules and live results. */
Item {
    id: moduleView
    objectName: "moduleView"

    property string moduleId: ""
    property var schema: ({})
    property var liveFields: ({})
    property var fieldKeys: []
    property var values: ({})
    property var outputs: []
    property string categoryTitle: ""
    property bool favorite: false

    readonly property bool empty: outputs.length === 1 && outputs[0].type === "note"

    signal homeRequested()
    signal categoryRequested(string id)

    onModuleIdChanged: loadModule()

    function loadModule() {
        if (moduleId === "")
            return;
        var loaded = App.moduleSchema(moduleId);
        if (loaded.meta === undefined) {
            // A stale id (renamed or retired tool) must not leave a blank sheet.
            schema = ({ meta: { title: "Tool not found", subtitle: "This tool is no longer available.", icon: "spark" }, fields: [], values: {} });
            liveFields = ({});
            fieldKeys = [];
            values = ({});
            outputs = [{ type: "error", text: "Prism could not find this tool. Pick another one from the sidebar." }];
            categoryTitle = "";
            favorite = false;
            return;
        }
        schema = loaded;
        values = loaded.values;
        fieldKeys = (loaded.fields || []).map(function (field) { return field.key; });
        liveFields = mapFields(loaded.fields);
        categoryTitle = loaded.categoryTitle;
        favorite = App.isFavorite(moduleId);
        outputs = App.runModule(moduleId, JSON.stringify(values)).outputs;
    }

    function mapFields(fields) {
        var map = {};
        for (var i = 0; i < (fields || []).length; i++)
            map[fields[i].key] = fields[i];
        return map;
    }

    function fieldFor(key) {
        return liveFields[key] !== undefined ? liveFields[key] : ({});
    }

    function setValue(key, value) {
        if (values[key] === value)
            return;
        var next = {};
        for (var k in values)
            next[k] = values[k];
        next[key] = value;
        values = next;
        runTimer.restart();
    }

    function runNow() {
        var result = App.runModule(moduleId, JSON.stringify(values));
        values = result.values;
        liveFields = mapFields(result.fields);
        outputs = result.outputs;
    }

    function pressKey(key) {
        var expression = String(values.expr !== undefined ? values.expr : "");
        if (key === "C") {
            setValue("expr", "");
            return;
        }
        if (key === "DEL") {
            setValue("expr", expression.slice(0, Math.max(0, expression.length - 1)));
            return;
        }
        if (key === "=") {
            runNow();
            return;
        }
        var token = key;
        if (key === "÷") token = "/";
        else if (key === "×") token = "*";
        else if (key === "−") token = "-";
        else if (key === "√") token = "sqrt(";
        setValue("expr", expression + token);
    }

    Timer {
        id: runTimer
        interval: 110
        onTriggered: moduleView.runNow()
    }

    Rectangle {
        anchors.fill: parent
        radius: Theme.rLg
        color: Theme.paper
        border.width: 1
        border.color: Theme.paperHairline

        Flickable {
            id: flick
            anchors.fill: parent
            anchors.margins: 1
            contentWidth: width
            contentHeight: sheet.height + 56
            clip: true
            boundsBehavior: Flickable.StopAtBounds

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
                width: 5
                contentItem: Rectangle { radius: 2.5; color: Theme.paperInkSecondary; opacity: 0.4 }
            }

            Column {
                id: sheet
                x: 26
                y: 22
                width: flick.width - 52
                spacing: 20

                // -- header ------------------------------------------------ //
                Item {
                    width: parent.width
                    height: 52

                    Rectangle {
                        width: 44
                        height: 44
                        radius: Theme.rMd
                        color: Theme.paperChip
                        border.width: 1
                        border.color: Theme.paperHairline
                        Icon {
                            anchors.centerIn: parent
                            name: moduleView.schema.meta !== undefined ? moduleView.schema.meta.icon : "spark"
                            size: 21
                            color: Theme.paperInk
                        }
                    }

                    Column {
                        anchors.left: parent.left
                        anchors.leftMargin: 58
                        anchors.right: favoriteButton.left
                        anchors.rightMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 3

                        Text {
                            text: moduleView.categoryTitle.toUpperCase()
                            color: Theme.paperInkSecondary
                            font.family: Theme.uiFamily
                            font.pixelSize: 10
                            font.letterSpacing: 0.11
                            font.weight: Font.DemiBold
                        }

                        Text {
                            width: parent.width
                            text: moduleView.schema.meta !== undefined ? moduleView.schema.meta.title : ""
                            color: Theme.paperInk
                            font.family: Theme.displayFamily
                            font.pixelSize: Math.round(23 * Theme.textScale)
                            font.weight: Font.DemiBold
                            font.letterSpacing: Theme.titleTracking
                            elide: Text.ElideRight
                        }

                        Text {
                            width: parent.width
                            text: moduleView.schema.meta !== undefined ? moduleView.schema.meta.subtitle : ""
                            color: Theme.paperInkSecondary
                            font.family: Theme.uiFamily
                            font.pixelSize: Theme.small
                            elide: Text.ElideRight
                        }
                    }

                    IconButton {
                        id: favoriteButton
                        anchors.right: parent.right
                        anchors.top: parent.top
                        icon: moduleView.favorite ? "star-filled" : "star"
                        iconSize: 19
                        size: 32
                        iconColor: moduleView.favorite ? Theme.paperInk : Theme.alpha(Theme.paperInk, 0.62)
                        label: moduleView.favorite ? "Remove from favorites" : "Add to favorites"
                        onClicked: {
                            App.toggleFavorite(moduleView.moduleId);
                            moduleView.favorite = App.isFavorite(moduleView.moduleId);
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 1
                    color: Theme.paperHairline
                }

                // -- fields + results -------------------------------------- //
                Row {
                    width: parent.width
                    spacing: 30

                    Column {
                        id: fieldsColumn
                        width: Math.min(320, Math.round(sheet.width * 0.42))
                        spacing: 16

                        Repeater {
                            model: moduleView.fieldKeys

                            Field {
                                id: fieldDelegate
                                required property var modelData
                                width: fieldsColumn.width
                                fieldData: moduleView.fieldFor(modelData)
                                value: moduleView.values[modelData]
                                visible: moduleView.fieldFor(modelData).visible !== false
                                onEdited: function (newValue) { moduleView.setValue(fieldDelegate.modelData, newValue); }
                            }
                        }

                        // Calculator keypad, only for the calculator.
                        Grid {
                            width: parent.width
                            columns: 4
                            spacing: 6
                            visible: moduleView.schema.meta !== undefined && moduleView.schema.meta.view === "calculator"

                            Repeater {
                                model: ["7", "8", "9", "÷", "4", "5", "6", "×", "1", "2", "3", "−", "0", ".", "(", ")", "√", "^", "DEL", "C"]

                                Rectangle {
                                    id: keyCap
                                    required property var modelData
                                    width: (fieldsColumn.width - 18) / 4
                                    height: 40
                                    radius: Theme.rXs
                                    color: keyMouse.pressed ? Theme.paperHairline : (keyMouse.containsMouse ? Theme.paperChip : "transparent")
                                    border.width: 1
                                    border.color: Theme.paperHairline
                                    scale: keyMouse.pressed ? 0.96 : 1
                                    Behavior on scale {
                                        SpringAnimation {
                                            spring: Motion.springPress
                                            damping: Motion.dampingPress
                                            epsilon: Theme.reducedMotion ? 100 : 0.4
                                        }
                                    }

                                    Text {
                                        anchors.centerIn: parent
                                        text: keyCap.modelData
                                        color: Theme.paperInk
                                        font.family: Theme.monoFamily
                                        font.pixelSize: Theme.body
                                    }

                                    MouseArea {
                                        id: keyMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: moduleView.pressKey(keyCap.modelData)
                                    }
                                }
                            }
                        }

                        Text {
                            width: parent.width
                            visible: moduleView.schema.meta !== undefined && moduleView.schema.meta.view === "calculator"
                            text: "Results update as you type."
                            color: Theme.paperInkSecondary
                            font.family: Theme.uiFamily
                            font.pixelSize: Theme.caption
                            wrapMode: Text.WordWrap
                        }

                    }

                    Column {
                        width: sheet.width - fieldsColumn.width - 30
                        spacing: 22

                        // Tool with nothing to compute yet: a quiet invitation,
                        // so an untouched tool never reads as a broken one.
                        Item {
                            width: parent.width
                            height: 196
                            visible: moduleView.empty

                            Column {
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.topMargin: 26
                                spacing: 14

                                Rectangle {
                                    width: 42
                                    height: 42
                                    radius: Theme.rMd
                                    color: Theme.paperChip
                                    border.width: 1
                                    border.color: Theme.paperHairline

                                    Icon {
                                        anchors.centerIn: parent
                                        name: moduleView.schema.meta !== undefined ? moduleView.schema.meta.icon : "spark"
                                        size: 19
                                        color: Theme.paperInkSecondary
                                    }
                                }

                                Text {
                                    width: Math.min(parent.width, 280)
                                    text: moduleView.outputs.length > 0 ? String(moduleView.outputs[0].text) : ""
                                    color: Theme.paperInkSecondary
                                    font.family: Theme.uiFamily
                                    font.pixelSize: Theme.small
                                    lineHeight: 1.45
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }

                        Repeater {
                            model: moduleView.empty ? [] : moduleView.outputs

                            ResultBlock {
                                required property var modelData
                                width: parent.width
                                block: modelData
                            }
                        }
                    }
                }

                Item { width: 1; height: 4 }
            }
        }
    }
}
