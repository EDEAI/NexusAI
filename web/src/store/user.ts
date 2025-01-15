/*
 * @LastEditors: biz
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export const UPDATE_NOTIFICATIONS = {
    AGENT_LIST: 'agent_list',
    WORKFLOW_LIST: 'workflow_list',
    SKILL_LIST: 'skill_list',
    CHAT_LIST: 'chat_list'
} as const;

interface UpdateNotification {
    id: string;
    timestamp: number;
    payload?: any;
}

interface UserState {
    runPanelLogRecord: any;
    setRunPanelLogRecord: (message: any) => void;
    appId: string;
    setRunId: (id: string) => void;
    dealtWithData: any;
    setDealtWithData: (value: any) => void;
    prevConfirmDealtWith: any;
    setPrevConfirmDealtWith: (value: any) => void;
    submitPromptId: string;
    setSubmitPromptId: (id: string) => void;
    currentUpdateNodeValue: any;
    setCurrentUpdateNodeValue: (value: any) => void;
    currentUpdateNodePanel:any;
    setCurrentUpdateNodePanel: (value: any) => void,
    agentCreateOpen: boolean;
    setAgentCreateOpen: (value: boolean) => void;
    updateNotifications: Map<string, UpdateNotification>;
    setUpdateNotification: (componentId: string, payload?: any) => void;
    clearUpdateNotification: (componentId: string) => void;
    shouldComponentUpdate: (componentId: string, lastCheck?: number) => boolean;
}

const useUserStore = create<UserState>()(
    devtools((set, get) => ({
        runPanelLogRecord: null,
        appId: null,
        dealtWithData: null,
        submitPromptId: null,
        currentUpdateNodeValue: null,
        currentUpdateNodePanel:null,
        prevConfirmDealtWith: null,
        agentCreateOpen: false,
        updateNotifications: new Map(),
        setAgentCreateOpen: (value: boolean) => {
            set({ agentCreateOpen: value });
        },
        setPrevConfirmDealtWith: (value: any) => {
            set({ prevConfirmDealtWith: value });
        },
        setCurrentUpdateNodePanel: (value: any) => {
            set({ currentUpdateNodePanel: value });
        },
        setCurrentUpdateNodeValue: (value: any) => {
            set({ currentUpdateNodeValue: value });
        },
        setSubmitPromptId: (id: string) => {
            set({ submitPromptId: id });
        },
        setDealtWithData: (value: any) => {
            set({ dealtWithData: value });
        },
        setRunPanelLogRecord: message => {
            set({ runPanelLogRecord: message });
        },
        setRunId: id => {
            set({ appId: id });
        },
        setUpdateNotification: (componentId: string, payload?: any) => {
            set(state => {
                const newNotifications = new Map(state.updateNotifications);
                newNotifications.set(componentId, {
                    id: componentId,
                    timestamp: Date.now(),
                    payload
                });
                return { updateNotifications: newNotifications };
            });
        },
        clearUpdateNotification: (componentId: string) => {
            set(state => {
                const newNotifications = new Map(state.updateNotifications);
                newNotifications.delete(componentId);
                return { updateNotifications: newNotifications };
            });
        },
        shouldComponentUpdate: (componentId: string, lastCheck?: number) => {
            const notification = get().updateNotifications.get(componentId);
            if (!notification) return false;
            if (!lastCheck) return true;
            return notification.timestamp > lastCheck;
        },
    }))
);

export default useUserStore;
