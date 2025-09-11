/*
 * @LastEditors: biz
 */
import React, { createContext, useContext, useRef, useState, ReactNode } from 'react';
import { useLocation, useParams } from 'umi';

interface ChatRoomContextType {
    scrollDomRef: React.RefObject<any>;
    upButtonDom: React.RefObject<any>;
    isStop: boolean;
    setIsStop: (value: boolean) => void;
    instruction: any[];
    setInstruction: (value: any[]) => void;
    id: string | null;
    agentList?: any;
}

const ChatRoomContext = createContext<ChatRoomContextType | undefined>(undefined);

interface ChatRoomProviderProps {
    children: ReactNode;
    agentChatRoomId?: any;
    agentList?: any;
}

export const ChatRoomProvider: React.FC<ChatRoomProviderProps> = ({ children, agentChatRoomId, agentList }) => {
    // Refs for DOM elements
    const scrollDomRef = useRef(null);
    const upButtonDom = useRef(null);
    
    // State management
    const [isStop, setIsStop] = useState(false);
    const [instruction, setInstruction] = useState([]);
    
    // URL params handling
    const { id: urlParamId } = useParams<{ id: string }>();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const searchParamId = searchParams.get('id');
    
    // Use URL param id if available, otherwise use search param id
    const id = agentChatRoomId || urlParamId || searchParamId;

    const value: ChatRoomContextType = {
        scrollDomRef,
        upButtonDom,
        isStop,
        setIsStop,
        instruction,
        setInstruction,
        id,
        agentList,
    };

    return (
        <ChatRoomContext.Provider value={value}>
            {children}
        </ChatRoomContext.Provider>
    );
};

export const useChatRoomContext = (): ChatRoomContextType => {
    const context = useContext(ChatRoomContext);
    if (context === undefined) {
        throw new Error('useChatRoomContext must be used within a ChatRoomProvider');
    }
    return context;
}; 