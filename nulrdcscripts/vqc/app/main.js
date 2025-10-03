const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let flaskProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 900,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
        },
        icon: path.join(__dirname, 'build', 'icon.png'),
        title: 'MeduSight - Video Quality Control',
    });

    // Start Flask server
    startFlaskServer();

    // Wait a bit for Flask to start, then load
    setTimeout(() => {
        mainWindow.loadURL('http://127.0.0.1:5000');
    }, 2000);

    // Handle window close
    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

function startFlaskServer() {
    const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';

    flaskProcess = spawn(pythonExecutable, [
        path.join(__dirname, 'app.py')
    ]);

    flaskProcess.stdout.on('data', (data) => {
        console.log(`Flask: ${data}`);
    });

    flaskProcess.stderr.on('data', (data) => {
        console.error(`Flask Error: ${data}`);
    });

    flaskProcess.on('close', (code) => {
        console.log(`Flask process exited with code ${code}`);
    });
}

function stopFlaskServer() {
    if (flaskProcess) {
        flaskProcess.kill();
        flaskProcess = null;
    }
}

// App lifecycle
app.whenReady().then(() => {
    createWindow();

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', function () {
    stopFlaskServer();
    if (process.platform !== 'darwin') app.quit();
});

app.on('quit', function () {
    stopFlaskServer();
});