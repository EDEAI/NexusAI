import { useChatRoomContext } from '../context/ChatRoomContext';

export interface UseChatRoomReturn {
    scrollDomRef: React.RefObject<any>;
    upButtonDom: React.RefObject<any>;
    isStop: boolean;
    setIsStop: (value: boolean) => void;
    instruction: any[];
    setInstruction: (value: any[]) => void;
    id: string | null;
}

// Backward compatibility hook that uses context
export const useChatRoom = (agentChatRoomId?: any): UseChatRoomReturn => {
    return useChatRoomContext();
}; 