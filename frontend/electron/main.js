import { app, BrowserWindow, shell, ipcMain } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let serverProcess = null;

function getServerPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'PersonalAI', 'PersonalAI');
  }
    return path.join(__dirname, '..', 'resources', 'PersonalAI', 'PersonalAI');
}

function startServer() {
  const serverPath = getServerPath();

  if (!fs.existsSync(serverPath)) {
    console.error('[Server] Binary not found at:', serverPath);
    return;
  }

  serverProcess = spawn(serverPath, [], {
    cwd: path.dirname(serverPath),
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: false,
  });

  serverProcess.stdout.on('data', (data) => {
    console.log('[Server]', data.toString().trim());
  });

  serverProcess.stderr.on('data', (data) => {
    console.error('[Server Error]', data.toString().trim());
  });

  serverProcess.on('exit', (code) => {
    console.log('[Server] exited with code', code);
    serverProcess = null;
  });

  serverProcess.on('error', (err) => {
    console.error('[Server] Failed to start:', err.message);
    serverProcess = null;
  });
}

function stopServer() {
  if (serverProcess) {
    serverProcess.kill();
    serverProcess = null;
  }
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // Check if we're in development mode
  if (process.env.NODE_ENV === 'development' || !app.isPackaged) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

ipcMain.handle('open-external', (_event, url) => {
  // Only allow http(s) URLs - this is invoked from the renderer, so don't
  // let it be used to launch arbitrary local files/protocols.
  if (typeof url === 'string' && /^https?:\/\//i.test(url)) {
    return shell.openExternal(url);
  }
  return Promise.reject(new Error('Refused to open non-http(s) URL'));
});

app.whenReady().then(() => {
  startServer();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    stopServer();
    app.quit();
  }
});

app.on('will-quit', () => {
  stopServer();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

