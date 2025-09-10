/*
 * @LastEditors: biz
 */

/**
 * Agent全屏状态持久化管理工具
 * 根据agentId保存和恢复每个Agent的全屏状态
 */

interface FullscreenStateStorage {
    [agentId: string]: boolean;
}

const FULLSCREEN_STORAGE_KEY = 'agent_fullscreen_states';

/**
 * 获取指定Agent的全屏状态
 * @param agentId - Agent ID
 * @returns boolean - 全屏状态，默认为false
 */
export const getAgentFullscreenState = (agentId: string | number): boolean => {
    try {
        const stored = localStorage.getItem(FULLSCREEN_STORAGE_KEY);
        if (!stored) return false;
        
        const states: FullscreenStateStorage = JSON.parse(stored);
        return states[String(agentId)] || false;
    } catch (error) {
        console.warn('Failed to get agent fullscreen state:', error);
        return false;
    }
};

/**
 * 保存指定Agent的全屏状态
 * @param agentId - Agent ID
 * @param isFullscreen - 全屏状态
 */
export const setAgentFullscreenState = (agentId: string | number, isFullscreen: boolean): void => {
    try {
        const stored = localStorage.getItem(FULLSCREEN_STORAGE_KEY);
        const states: FullscreenStateStorage = stored ? JSON.parse(stored) : {};
        
        states[String(agentId)] = isFullscreen;
        localStorage.setItem(FULLSCREEN_STORAGE_KEY, JSON.stringify(states));
        
        console.log(`Agent ${agentId} fullscreen state saved: ${isFullscreen}`);
    } catch (error) {
        console.warn('Failed to save agent fullscreen state:', error);
    }
};

/**
 * 清除指定Agent的全屏状态记录
 * @param agentId - Agent ID
 */
export const clearAgentFullscreenState = (agentId: string | number): void => {
    try {
        const stored = localStorage.getItem(FULLSCREEN_STORAGE_KEY);
        if (!stored) return;
        
        const states: FullscreenStateStorage = JSON.parse(stored);
        delete states[String(agentId)];
        
        localStorage.setItem(FULLSCREEN_STORAGE_KEY, JSON.stringify(states));
        console.log(`Agent ${agentId} fullscreen state cleared`);
    } catch (error) {
        console.warn('Failed to clear agent fullscreen state:', error);
    }
};

/**
 * 获取所有Agent的全屏状态记录
 * @returns FullscreenStateStorage - 所有Agent的全屏状态映射
 */
export const getAllAgentFullscreenStates = (): FullscreenStateStorage => {
    try {
        const stored = localStorage.getItem(FULLSCREEN_STORAGE_KEY);
        return stored ? JSON.parse(stored) : {};
    } catch (error) {
        console.warn('Failed to get all agent fullscreen states:', error);
        return {};
    }
};

/**
 * 清除所有Agent的全屏状态记录
 */
export const clearAllAgentFullscreenStates = (): void => {
    try {
        localStorage.removeItem(FULLSCREEN_STORAGE_KEY);
        console.log('All agent fullscreen states cleared');
    } catch (error) {
        console.warn('Failed to clear all agent fullscreen states:', error);
    }
}; 



export const checkViewInIframe=()=>{
    return window?.location?.pathname === '/agent_chat_quickly'
}
export const getIframeHostName=()=>{
    return window?.location?.hostname
}

export const getIframeChatWsUrl=()=>{
    return `${getProtocolIsHttps() ? 'wss' : 'ws'}://${getIframeHostName()}/agent_chat_ws`
}

export const getIframeApiUrl=()=>{
    return `${getProtocolIsHttps() ? 'https' : 'http'}://${getIframeHostName()}`
}
export const getProtocolIsHttps=()=>{
    return window?.location?.protocol === 'https:'
}
