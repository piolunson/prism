import QtQuick
import QtQuick.Window
import "theme"
import "components"

Item {
    id: shell
    objectName: "appShell"

    property var categories: App.categories()
    property var favorites: App.favoriteModules
    property var recents: App.recentModules
    property string view: "home"
    property string categoryId: ""
    property string moduleId: ""
    property int moduleCount: App.moduleCount

    Component.onCompleted: {
        var initial = App.initialView;
        view = (initial.view !== undefined && initial.view !== "") ? initial.view : "home";
        categoryId = initial.categoryId !== undefined ? initial.categoryId : "";
        moduleId = initial.moduleId !== undefined ? initial.moduleId : "";
        if (initial.overlay === "palette")
            palette.show();
        else if (initial.overlay === "settings")
            settingsSheet.show();
    }

    // -- navigation ---------------------------------------------------------- //
    function openHome() {
        view = "home";
    }

    function openCategory(id) {
        categoryId = id;
        view = "category";
    }

    function openModule(id) {
        var loaded = App.moduleSchema(id);
        if (loaded.meta === undefined)
            return;
        categoryId = loaded.meta.category;
        moduleId = id;
        view = "module";
        App.pushRecent(id);
    }

    function toggleTheme() {
        App.setThemeMode(Theme.dark ? "light" : "dark");
    }

    function stepBack() {
        if (view === "module")
            openCategory(categoryId);
        else if (view === "category")
            openHome();
    }

    function categoryName() {
        for (var i = 0; i < categories.length; i++) {
            if (categories[i].id === categoryId)
                return categories[i].title;
        }
        return "";
    }

    function moduleTitle() {
        if (moduleId === "")
            return "";
        var loaded = App.moduleSchema(moduleId);
        return loaded.meta !== undefined ? loaded.meta.title : "";
    }

    function startMove() {
        if (Window.window)
            Window.window.startSystemMove();
    }

    function toggleMaximize() {
        if (!Window.window)
            return;
        if (Window.window.visibility === Window.Maximized)
            Window.window.showNormal();
        else
            Window.window.showMaximized();
    }

    // -- chrome -------------------------------------------------------------- //
    Sidebar {
        id: sidebar
        x: 12
        y: 12
        width: 248
        height: parent.height - 24
        categories: shell.categories
        favorites: shell.favorites
        currentView: shell.view
        currentCategory: shell.categoryId
        currentModule: shell.moduleId
        moduleCount: shell.moduleCount
        onHomeRequested: shell.openHome()
        onCategoryRequested: function (id) { shell.openCategory(id); }
        onModuleRequested: function (id) { shell.openModule(id); }
        onSearchRequested: palette.show()
        onSettingsRequested: settingsSheet.show()
        onThemeToggled: shell.toggleTheme()
        onDragRequested: shell.startMove()
    }

    Item {
        id: topBar
        anchors.left: sidebar.right
        anchors.leftMargin: 20
        anchors.right: parent.right
        anchors.rightMargin: 14
        anchors.top: parent.top
        anchors.topMargin: 12
        height: 44

        MouseArea {
            anchors.fill: parent
            onPressed: shell.startMove()
            onDoubleClicked: shell.toggleMaximize()
        }

        Row {
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            spacing: 6

            IconButton {
                visible: shell.view !== "home"
                icon: "arrow-left"
                iconSize: 15
                size: 28
                label: "Back"
                onClicked: shell.stepBack()
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: "All tools"
                color: shell.view === "home" ? Theme.ink : Theme.inkSecondary
                font.family: Theme.uiFamily
                font.pixelSize: Theme.small
                font.weight: shell.view === "home" ? Font.DemiBold : Font.Normal

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: shell.openHome()
                }
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                visible: shell.view !== "home"
                text: "/"
                color: Theme.inkTertiary
                font.family: Theme.uiFamily
                font.pixelSize: Theme.small
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                visible: shell.view !== "home"
                text: shell.categoryName()
                color: shell.view === "category" ? Theme.ink : Theme.inkSecondary
                font.family: Theme.uiFamily
                font.pixelSize: Theme.small
                font.weight: shell.view === "category" ? Font.DemiBold : Font.Normal

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: shell.openCategory(shell.categoryId)
                }
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                visible: shell.view === "module"
                text: "/"
                color: Theme.inkTertiary
                font.family: Theme.uiFamily
                font.pixelSize: Theme.small
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                visible: shell.view === "module"
                text: shell.moduleTitle()
                color: Theme.ink
                font.family: Theme.uiFamily
                font.pixelSize: Theme.small
                font.weight: Font.DemiBold
            }
        }

        Row {
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            spacing: 12

            WindowButtons {
                anchors.verticalCenter: parent.verticalCenter
                dark: Theme.dark
                onMinimizeRequested: {
                    if (Window.window)
                        Window.window.showMinimized();
                }
                onMaximizeRequested: shell.toggleMaximize()
                onCloseRequested: {
                    if (Window.window)
                        Window.window.close();
                }
            }
        }
    }

    // -- views --------------------------------------------------------------- //
    Item {
        id: viewHost
        anchors.left: sidebar.right
        anchors.leftMargin: 20
        anchors.right: parent.right
        anchors.rightMargin: 14
        anchors.top: topBar.bottom
        anchors.topMargin: 2
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 14

        Home {
            id: homeView
            anchors.fill: parent
            visible: shell.view === "home"
            enabled: visible
            opacity: visible ? 1 : 0
            categories: shell.categories
            recents: shell.recents
            moduleCount: shell.moduleCount
            onCategoryRequested: function (id) { shell.openCategory(id); }
            onModuleRequested: function (id) { shell.openModule(id); }

            Behavior on opacity {
                NumberAnimation {
                    duration: Theme.reducedMotion ? 0 : 200
                    easing.type: Easing.OutCubic
                }
            }
        }

        CategoryView {
            id: categoryView
            anchors.fill: parent
            visible: shell.view === "category"
            enabled: visible
            opacity: visible ? 1 : 0
            categoryId: shell.categoryId
            onHomeRequested: shell.openHome()
            onModuleRequested: function (id) { shell.openModule(id); }

            Behavior on opacity {
                NumberAnimation {
                    duration: Theme.reducedMotion ? 0 : 200
                    easing.type: Easing.OutCubic
                }
            }
        }

        ModuleView {
            id: moduleView
            anchors.fill: parent
            visible: shell.view === "module"
            enabled: visible
            opacity: visible ? 1 : 0
            moduleId: shell.moduleId
            onHomeRequested: shell.openHome()
            onCategoryRequested: function (id) { shell.openCategory(id); }

            Behavior on opacity {
                NumberAnimation {
                    duration: Theme.reducedMotion ? 0 : 200
                    easing.type: Easing.OutCubic
                }
            }
        }
    }

    CommandPalette {
        id: palette
        anchors.fill: parent
        onModuleRequested: function (id) { shell.openModule(id); }
    }

    SettingsSheet {
        id: settingsSheet
        anchors.fill: parent
    }

    // -- keyboard ------------------------------------------------------------ //
    Shortcut {
        sequence: "Ctrl+K"
        onActivated: palette.toggle()
    }

    Shortcut {
        sequence: "Ctrl+F"
        onActivated: palette.show()
    }

    Shortcut {
        sequence: "Escape"
        enabled: !palette.open && !settingsSheet.open && shell.view !== "home"
        onActivated: shell.stepBack()
    }

    Shortcut { sequence: "Ctrl+1"; onActivated: shell.openCategory(shell.categories[0].id) }
    Shortcut { sequence: "Ctrl+2"; onActivated: shell.openCategory(shell.categories[1].id) }
    Shortcut { sequence: "Ctrl+3"; onActivated: shell.openCategory(shell.categories[2].id) }
    Shortcut { sequence: "Ctrl+4"; onActivated: shell.openCategory(shell.categories[3].id) }
    Shortcut { sequence: "Ctrl+5"; onActivated: shell.openCategory(shell.categories[4].id) }
    Shortcut { sequence: "Ctrl+6"; onActivated: shell.openCategory(shell.categories[5].id) }
}
