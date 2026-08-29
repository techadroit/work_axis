const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Add any APIs you want to expose to the renderer process
  platform: process.platform,
  // Opens a URL in the OS default browser (not the Electron window) - needed
  // for Google OAuth, which blocks embedded/WebView browsers outright.
  openExternal: (url) => ipcRenderer.invoke('open-external', url)
});

