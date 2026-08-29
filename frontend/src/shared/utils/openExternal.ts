/**
 * Opens a URL in the OS default browser.
 *
 * Google's OAuth consent screen actively blocks embedded/WebView browsers
 * (disallowed_useragent), so this must NOT open inside the Electron
 * BrowserWindow - it needs the real system browser. Uses the
 * `window.electronAPI.openExternal` bridge when running inside Electron,
 * falling back to a plain `window.open` when running as a browser tab
 * (e.g. `npm run dev`).
 */
export function openExternal(url: string): void {
  const electronApi = (window as unknown as { electronAPI?: { openExternal?: (url: string) => void } }).electronAPI;
  if (electronApi?.openExternal) {
    electronApi.openExternal(url);
    return;
  }
  window.open(url, '_blank', 'noopener');
}
