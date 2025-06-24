import { MessageInstance } from 'antd/es/message/interface';

// Base types
export interface Agent {
    id: string;
    name: string;
    avatar?: string;
    model?: string;
    [key: string]: any;
}

export interface Ability {
    id: string;
    name: string;
    description?: string;
    [key: string]: any;
}

export interface FileItem {
    id: string;
    name: string;
    url: string;
    type: string;
    size: number;
    [key: string]: any;
}

export interface ChatMessage {
    id: string;
    content: string;
    role: 'user' | 'assistant' | 'system';
    timestamp: number;
    agentId?: string;
    files?: FileItem[];
    [key: string]: any;
}

// Component Props Interfaces
export interface BaseChatProps {
    messageApi?: MessageInstance;
    agentList?: Agent[];
    agentChatRoomId?: string;
    abilitiesList?: Ability[];
    id?: string | null;
}

export interface ScrollProps {
    scrollDomRef?: React.RefObject<HTMLDivElement>;
    upButtonDom?: React.RefObject<HTMLDivElement>;
}

export interface ChatControlProps {
    isStop?: boolean;
    setIsStop?: (value: boolean) => void;
    instruction?: any[];
    setInstruction?: (value: any[]) => void;
}

export interface MessageProps extends BaseChatProps {
    item: ChatMessage;
    index: number;
    idName?: string;
    cidName?: string;
}

export interface ActionButtonProps {
    messageApi?: MessageInstance;
    content?: string;
    roomid?: string;
}

export interface InputFieldProps extends BaseChatProps, ScrollProps, ChatControlProps {
    // Additional input-specific props can be added here
}

export interface ChatContentProps extends BaseChatProps, ScrollProps, ChatControlProps {
    // Additional content-specific props can be added here
}

export interface ChatWindowProps extends BaseChatProps, ScrollProps {
    sendValue?: string;
    setCurrentMessageContent?: (content: any) => void;
    setisEnd?: (value: boolean) => void;
    setSendValue?: (value: string) => void;
    setIsStop?: (value: boolean) => void;
}

// WebSocket message types
export interface WebSocketMessage {
    type: string;
    data: any;
    timestamp?: number;
}

// File upload types
export interface UploadFile {
    uid: string;
    name: string;
    status: 'uploading' | 'done' | 'error' | 'removed';
    url?: string;
    response?: any;
    [key: string]: any;
} 