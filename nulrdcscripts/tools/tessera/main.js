const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false
        },
        icon: path.join(__dirname, 'icon.png') // Fixed: removed 'assets/' path
    });

    mainWindow.loadFile('index.html');

    // Optional: Open DevTools in development
    // mainWindow.webContents.openDevTools();

    // Create application menu
    const template = [
        {
            label: 'File',
            submenu: [
                {
                    label: 'Save Session',
                    accelerator: 'CmdOrCtrl+S',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('document.getElementById("saveBtn").click()');
                    }
                },
                {
                    label: 'Load Session',
                    accelerator: 'CmdOrCtrl+O',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('document.getElementById("loadBtn").click()');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Export VTT',
                    accelerator: 'CmdOrCtrl+E',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('document.getElementById("exportBtn").click()');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Quit',
                    accelerator: 'CmdOrCtrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: 'Edit',
            submenu: [
                { role: 'undo' },
                { role: 'redo' },
                { type: 'separator' },
                { role: 'cut' },
                { role: 'copy' },
                { role: 'paste' },
                { role: 'selectAll' }
            ]
        },
        {
            label: 'View',
            submenu: [
                { role: 'reload' },
                { role: 'forceReload' },
                { role: 'toggleDevTools' },
                { type: 'separator' },
                { role: 'resetZoom' },
                { role: 'zoomIn' },
                { role: 'zoomOut' },
                { type: 'separator' },
                { role: 'togglefullscreen' }
            ]
        },
        {
            label: 'Help',
            submenu: [
                {
                    label: 'README',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('document.getElementById("readmeModal").classList.add("show")');
                    }
                },
                {
                    label: 'License',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('document.getElementById("licenseModal").classList.add("show")');
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Handle any uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
});