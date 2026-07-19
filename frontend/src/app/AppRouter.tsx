import {HashRouter, Route, Routes} from 'react-router-dom';
import MainScreen from "../shared/components/MainScreen.tsx";
import {Provider} from "react-redux";
import {userStore, UserStoreContext} from "../shared/stores/userStore.ts";
import {chatSessionStore, ChatSessionStoreContext} from "../shared/stores/chatSessionStore.ts";
import {chatStore, ChatStoreContext} from "../features/chat/stores/chatStore.ts";
import {ChatInterface} from "../features/chat/components/ChatInterface.tsx";
import {SettingsPage} from "../features/settings/components/SettingsPage.tsx";
import { ROUTES } from "../shared/utils";
import {ModelProviderPage, EmailIntegrationPage} from "../features/settings";
import { HomeLanding } from '../features/home/components/HomeLanding.tsx';
import { settingsStore, SettingsStoreContext } from '../features/settings/stores/settingsStore.ts';

/**
 * AppRouter - Main routing configuration
 * MainScreen serves as the root layout with nested routes
 * Uses custom contexts to avoid nested Provider conflicts
 */
const AppRouter = () => {
    return (
        <HashRouter>
            <Routes>
                <Route path={ROUTES.HOME} element={
                    <Provider store={userStore} context={UserStoreContext as any}>
                        <Provider store={chatSessionStore} context={ChatSessionStoreContext as any}>
                            <Provider store={chatStore} context={ChatStoreContext as any}>
                                <Provider store={settingsStore} context={SettingsStoreContext as any}>
                                    <MainScreen/>
                                </Provider>
                            </Provider>
                        </Provider>
                    </Provider>
                }>
                    {/* Child routes will be rendered inside MainScreen's Outlet */}
                    <Route index element={<HomeLanding/>}/>
                    <Route path={ROUTES.HOME} element={<ChatInterface/>}/>
                    <Route path={ROUTES.CHAT_SESSION}  element={<ChatInterface/>}/>
                    <Route path={ROUTES.CHAT}  element={<ChatInterface/>}/>
                    <Route path={ROUTES.SETTINGS} element={<SettingsPage/>}/>
                    <Route path={ROUTES.SETTINGS_GENERAL} element={<SettingsPage/>}/>
                    <Route path={ROUTES.SETTINGS_MODELS} element={<ModelProviderPage/>}/>
                    <Route path={ROUTES.SETTINGS_EMAIL_INTEGRATIONS} element={<EmailIntegrationPage/>}/>
                </Route>
            </Routes>
        </HashRouter>
    );
};

export default AppRouter;
