/*
 * @LastEditors: biz
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
type FlowState = {
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
};
const useUserStore = create(
    devtools<FlowState>((set, get) => ({
        runPanelLogRecord: null,
        appId: null,
        dealtWithData: null,
        submitPromptId: null,
        currentUpdateNodeValue: null,
        currentUpdateNodePanel:null,
        prevConfirmDealtWith: null,
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
    })),
);
export default useUserStore;
