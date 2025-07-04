import { useRef, useState } from 'react';
import { useLocation, useParams } from 'umi';

export interface UseChatRoomReturn {
    scrollDomRef: React.RefObject<any>;
    upButtonDom: React.RefObject<any>;
    isStop: boolean;
    setIsStop: (value: boolean) => void;
    instruction: any[];
    setInstruction: (value: any[]) => void;
    id: string | null;
}

export const useChatRoom = (agentChatRoomId?: any): UseChatRoomReturn => {
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

    return {
        scrollDomRef,
        upButtonDom,
        isStop,
        setIsStop,
        instruction,
        setInstruction,
        id,
    };
}; 