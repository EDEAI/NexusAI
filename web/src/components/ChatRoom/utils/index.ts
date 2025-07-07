/*
 * @LastEditors: biz
 */
import React, { ReactNode } from 'react';
import { ContentDetectionConfig, MessageWithContent, MessageContentAnalysis } from '../types';

// Download file utility function
export const downloadFile = (url: string, filename: string) => {
    try {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (e) {}
};

// Extract text from React element
export const extractTextFromElement = (element: ReactNode): string => {
    if (typeof element === 'string') {
        return element;
    }
    if (Array.isArray(element)) {
        return element.map(extractTextFromElement).join('');
    }
    if (React.isValidElement(element)) {
        return extractTextFromElement(element.props.children);
    }
    return '';
};

// Extract text from array
export const extractTextFromArray = (arr: any) => {
    return extractTextFromElement(arr);
};

/**
 * Smart content detector for chat messages (Enhanced with configuration)
 * Checks if a message contains any meaningful content across multiple dimensions
 * @param message - The message object to check
 * @param config - Configuration options for content detection
 * @returns boolean - true if message has content, false if empty
 */
export const hasMessageContent = (
    message: MessageWithContent | any, 
    config: ContentDetectionConfig = {}
): boolean => {
    try {
        // Safety check: ensure message is an object
        if (!message || typeof message !== 'object') {
            console.warn('hasMessageContent: Invalid message object provided');
            return false;
        }

        // Default configuration
        const {
            checkText = true,
            checkFiles = true,
            checkMCPTools = true,
            checkStreaming = true,
            minTextLength = 1
        } = config;

        // 1. Text content detection
        const hasTextContent = () => {
            if (!checkText) return false;
            try {
                const content = message.content;
                return content && 
                       typeof content === 'string' && 
                       content.trim().length >= minTextLength;
            } catch (error) {
                console.warn('Error checking text content:', error);
                return false;
            }
        };

        // 2. File attachment detection
        const hasFileContent = () => {
            if (!checkFiles) return false;
            try {
                const fileList = message.fileList || message.file_list;
                return fileList && 
                       Array.isArray(fileList) && 
                       fileList.length > 0;
            } catch (error) {
                console.warn('Error checking file content:', error);
                return false;
            }
        };

        // 3. MCP tools detection (multiple formats)
        const hasMCPContent = () => {
            if (!checkMCPTools) return false;
            try {
                // Check parsedContent format
                if (message.parsedContent?.hasMCPTools) {
                    return true;
                }

                // Check contentBlocks format
                if (message.contentBlocks && Array.isArray(message.contentBlocks)) {
                    const hasMCPBlocks = message.contentBlocks.some(
                        (block: any) => block && block.type === 'mcp' && block.toolId
                    );
                    if (hasMCPBlocks) {
                        return true;
                    }
                }

                // Check activeMCPTools format
                if (message.activeMCPTools && Array.isArray(message.activeMCPTools)) {
                    return message.activeMCPTools.length > 0;
                }

                return false;
            } catch (error) {
                console.warn('Error checking MCP content:', error);
                return false;
            }
        };

        // 4. Streaming content detection (for current messages)
        const hasStreamingContent = () => {
            if (!checkStreaming) return false;
            try {
                // If message is in streaming state and has accumulated some content
                if (message.contentBlocks && Array.isArray(message.contentBlocks)) {
                    return message.contentBlocks.some(
                        (block: any) => block && 
                                       block.type === 'text' && 
                                       block.content && 
                                       block.content.trim().length >= minTextLength
                    );
                }
                return false;
            } catch (error) {
                console.warn('Error checking streaming content:', error);
                return false;
            }
        };

        // Comprehensive content check: any dimension with content = true
        return hasTextContent() || 
               hasFileContent() || 
               hasMCPContent() || 
               hasStreamingContent();

    } catch (error) {
        // Error safety: default to showing message to avoid hiding content accidentally
        console.error('hasMessageContent unexpected error:', error);
        return true; // Fail-safe: show message when in doubt
    }
};

/**
 * Detailed content analysis for debugging and advanced use cases
 * @param message - The message object to analyze
 * @returns object with detailed content breakdown
 */
export const analyzeMessageContent = (message: MessageWithContent | any): MessageContentAnalysis => {
    try {
        const content = message?.content || '';
        const fileList = message?.fileList || message?.file_list || [];
        const parsedContent = message?.parsedContent || {};
        const contentBlocks = message?.contentBlocks || [];
        const activeMCPTools = message?.activeMCPTools || [];

        return {
            hasText: content && typeof content === 'string' && content.trim().length > 0,
            hasFiles: Array.isArray(fileList) && fileList.length > 0,
            hasParsedMCP: Boolean(parsedContent.hasMCPTools),
            hasContentBlocksMCP: contentBlocks.some((block: any) => block?.type === 'mcp'),
            hasActiveMCP: Array.isArray(activeMCPTools) && activeMCPTools.length > 0,
            hasStreamingText: contentBlocks.some((block: any) => 
                block?.type === 'text' && block?.content?.trim()
            ),
            textLength: content ? content.trim().length : 0,
            fileCount: Array.isArray(fileList) ? fileList.length : 0,
            mcpToolCount: Array.isArray(activeMCPTools) ? activeMCPTools.length : 0,
            blockCount: Array.isArray(contentBlocks) ? contentBlocks.length : 0
        };
    } catch (error) {
        console.error('analyzeMessageContent error:', error);
        // Return safe defaults
        return {
            hasText: false,
            hasFiles: false,
            hasParsedMCP: false,
            hasContentBlocksMCP: false,
            hasActiveMCP: false,
            hasStreamingText: false,
            textLength: 0,
            fileCount: 0,
            mcpToolCount: 0,
            blockCount: 0
        };
    }
};

/**
 * Check for the last Agent message in message history
 * @param messages - Array of messages (should be in reverse chronological order)
 * @param config - Content detection configuration
 * @returns Last valid agent message or null
 */
export const checkLastAgentMessage = (
    messages: any[], 
    config: ContentDetectionConfig = {}
): any | null => {
    try {
        // Parameter validation
        if (!messages || !Array.isArray(messages) || messages.length === 0) {
            return null;
        }
        
        // Find the last Agent message (messages already in reverse chronological order)
        for (const message of messages) {
            if (message && 
                message.is_agent === 1 && 
                hasMessageContent(message, {
                    checkText: false,
                    checkFiles: true,
                    checkMCPTools: true,
                    minTextLength: 1,
                    ...config
                })) {
                return message;
            }
        }
        
        return null;
    } catch (error) {
        console.error('checkLastAgentMessage error:', error);
        return null;
    }
};

/**
 * Convert parsedContent.blocks to contentBlocks format
 * @param parsedContent - Parsed content object
 * @returns Array of ContentBlock objects
 */
export const convertParsedContentToContentBlocks = (parsedContent: any): any[] => {
    if (!parsedContent?.blocks || !Array.isArray(parsedContent.blocks)) {
        return [];
    }
    
    return parsedContent.blocks.map((block: any) => {
        if (block.type === 'text') {
            return {
                type: 'text',
                content: block.content || '',
                timestamp: Date.now()
            };
        } else if (block.type === 'mcp-tool' && block.toolData?.id) {
            return {
                type: 'mcp',
                toolId: block.toolData.id,
                timestamp: Date.now()
            };
        }
        // Skip invalid blocks
        return null;
    }).filter(Boolean);
};

/**
 * Extract MCP tool IDs from contentBlocks
 * @param contentBlocks - Array of content blocks
 * @returns Array of MCP tool IDs
 */
export const extractMCPToolIds = (contentBlocks: any[]): (string | number)[] => {
    return contentBlocks
        .filter(block => block.type === 'mcp' && block.toolId)
        .map(block => block.toolId);
};

/**
 * Prepare history message for CurrentMessage format
 * @param message - History message object
 * @param getMCPTool - Function to get MCP tool data
 * @returns Prepared message object for CurrentMessage
 */
export const prepareHistoryMessageForCurrent = (
    message: any,
    getMCPTool?: (id: string | number) => any | null
): any => {
    try {
        // Base message structure conversion
        const preparedMessage = {
            ...message,
            content: message.content || '',
            activeMCPTools: message.activeMCTools || []
        };
        
        // Handle contentBlocks conversion
        let contentBlocks = message.contentBlocks;
        if (!contentBlocks && message.parsedContent) {
            contentBlocks = convertParsedContentToContentBlocks(message.parsedContent);
        } else if (!contentBlocks && message.content) {
            contentBlocks = [{
                type: 'text',
                content: message.content,
                timestamp: Date.now()
            }];
        }
        
        // Sync MCP tool state
        if (getMCPTool && contentBlocks) {
            const mcpToolIds = extractMCPToolIds(contentBlocks);
            preparedMessage.activeMCPTools = mcpToolIds;
        }
        
        preparedMessage.contentBlocks = contentBlocks || [];
        
        return preparedMessage;
    } catch (error) {
        console.error('prepareHistoryMessageForCurrent error:', error);
        return message; // Return original message as fallback
    }
}; 