# MainScreen Component

## Overview
`MainScreen` is the primary container component that serves as the root layout when the app launches. It provides a consistent background color and contains all application routes.

## Features
- Full viewport height and width coverage
- Uses `primary_bg_color` from the design system
- Flexbox layout for easy child component arrangement
- Integrates with React Router's `<Outlet />` for nested routing

## Usage

### Basic Usage with Router

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainScreen } from '../shared/components';

const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainScreen />}>
          <Route index element={<HomePage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
```

### Integration in App.tsx

```tsx
import AppRouter from './AppRouter';

function App() {
  return <AppRouter />;
}
```

## File Location
- Component: `/src/shared/components/MainScreen.tsx`
- Export: `/src/shared/components/index.ts`

## Properties
Currently, MainScreen doesn't accept any props. It serves as a simple container with consistent styling.

## Styling
- **Background Color**: Uses `primary_bg_color` from design system (currently `#ffffff`)
- **Layout**: Flexbox with column direction
- **Size**: 100% width, 100vh minimum height

## Next Steps
You can extend MainScreen to include:
- Navigation header
- Sidebar
- Footer
- Loading states
- Error boundaries

