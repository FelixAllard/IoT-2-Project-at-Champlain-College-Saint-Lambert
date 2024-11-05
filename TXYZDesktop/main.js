const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        frame: false, // Removes the default frame for a custom top bar
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: true,  // Allows the use of require in renderer process
            contextIsolation: false // Allows ipcRenderer to work without restrictions
        }
    });

    win.loadFile('./Template/NavBar/NavBar.html');
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
