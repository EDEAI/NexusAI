import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
type FlowState = {
    clearMemory: any;
    truncatable:any;
    disableInput:any;
    summaryParams:any;
    runsSummaryShow:any;
    summaryClick:any;
    setClearMemory:(value:any) => void;
    setTruncatable:(value:any) => void;
    setDisableInput:(value:any) => void;
    setSummaryParams:(value:any) => void;
    setRunsSummaryShow:(value:any) => void;
    setSummaryClick:(value:any)=> void;
};
const chatroomStore = create(
    devtools<FlowState>((set, get) => ({
        clearMemory:null,
        truncatable:false,
        disableInput:false,
        summaryParams:null,
        runsSummaryShow:false,
        summaryClick:true,
        setClearMemory:(value:any)=>{
            set({clearMemory:value})
        },
        setTruncatable:(value:any)=>{
            set({truncatable:value})
        },
        setDisableInput:(value:any)=>{
            set({disableInput:value})
        },
        setSummaryParams:(value:any)=>{
            set({summaryParams:value})
        },
        setRunsSummaryShow:(value:any)=>{
            set({runsSummaryShow:value})
        },
        setSummaryClick:(value:any)=>{
            console.log(value);
            
            set({summaryClick:value})
        }
    })),
);
export default chatroomStore;
