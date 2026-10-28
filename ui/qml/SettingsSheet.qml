import QtQuick
import "theme"
import "components"

Sheet {
    id: settings
    objectName: "settingsSheet"
    title: "Appearance & motion"
    panelHeight: 520

    SettingRow {
        label: "Theme"
        description: "Follow Windows, or pin a side."

        Segmented {
            options: [
                { value: "system", label: "System" },
                { value: "light", label: "Light" },
                { value: "dark", label: "Dark" }
            ]
            value: App.themeMode
            width: 210
            onSelected: function (chosen) { App.setThemeMode(chosen); }
        }
    }

    SettingRow {
        label: "Motion"
        description: "Full uses springs. Reduced cross-fades instead."

        Segmented {
            options: [
                { value: "system", label: "System" },
                { value: "full", label: "Full" },
                { value: "reduced", label: "Reduced" }
            ]
            value: App.motionMode
            width: 210
            onSelected: function (chosen) { App.setMotionMode(chosen); }
        }
    }

    SettingRow {
        label: "Desktop glass"
        description: App.glassSupported ? "Let Windows blur the real desktop behind Prism." : "Needs Windows 11."

        Switch {
            checked: App.desktopGlass
            enabledControl: App.glassSupported
            onToggled: function (value) { App.setDesktopGlass(value); }
        }
    }

    Rectangle {
        width: parent.width
        height: 1
        color: Theme.divider
    }

    Text {
        text: "SHORTCUTS"
        color: Theme.inkTertiary
        font.family: Theme.uiFamily
        font.pixelSize: 10
        font.letterSpacing: 0.1
        font.weight: Font.DemiBold
    }

    Column {
        width: parent.width
        spacing: 7

        Repeater {
            model: [
                { keys: "Ctrl K", action: "Search every tool" },
                { keys: "Ctrl 1 – 6", action: "Jump to a category" },
                { keys: "Esc", action: "Close, or step back" },
                { keys: "Tab", action: "Move between controls" }
            ]

            Item {
                required property var modelData
                width: parent.width
                height: 18

                Text {
                    anchors.left: parent.left
                    width: 110
                    text: modelData.keys
                    color: Theme.inkSecondary
                    font.family: Theme.monoFamily
                    font.pixelSize: Theme.caption
                }

                Text {
                    anchors.left: parent.left
                    anchors.leftMargin: 110
                    text: modelData.action
                    color: Theme.ink
                    font.family: Theme.uiFamily
                    font.pixelSize: Theme.caption
                }
            }
        }
    }

    Rectangle {
        width: parent.width
        height: 1
        color: Theme.divider
    }

    Text {
        width: parent.width
        text: "Prism " + App.version + " · " + App.moduleCount + " tools · everything runs on this machine. Nothing is uploaded, and nothing needs an account."
        color: Theme.inkSecondary
        font.family: Theme.uiFamily
        font.pixelSize: Theme.caption
        wrapMode: Text.WordWrap
        lineHeight: 1.35
    }
}
