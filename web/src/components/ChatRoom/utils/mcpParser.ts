/*
 * @LastEditors: biz
 */
import { MCPToolData, ContentBlock, ParsedMCPContent, MCPToolRuntimeData } from '../types/mcp';
import { ContentBlock as StreamingContentBlock } from '../types';

const MCP_START_TAG = '<<<mcp-tool-start>>>';
const MCP_END_TAG = '<<<mcp-tool-end>>>';

export const extractMCPTools = (content: string): { toolData: MCPToolData; startIndex: number; endIndex: number }[] => {
    // Parameter validation
    if (typeof content !== 'string' || content === null || content === undefined) {
        console.warn('extractMCPTools: content is not a valid string:', content);
        return [];
    }

    const tools: { toolData: MCPToolData; startIndex: number; endIndex: number }[] = [];
    let searchStartIndex = 0;

    while (true) {
        const startIndex = content.indexOf(MCP_START_TAG, searchStartIndex);
        if (startIndex === -1) break;

        const endIndex = content.indexOf(MCP_END_TAG, startIndex);
        if (endIndex === -1) break;

        const jsonStart = startIndex + MCP_START_TAG.length;
        const jsonContent = content.substring(jsonStart, endIndex).trim();

        try {
            const rawData = JSON.parse(jsonContent);
            // Adapt the data structure to match MCPToolData interface
            const toolData: MCPToolData = {
                id: rawData.id,
                name: rawData.name || '',
                skill_or_workflow_name: rawData.skill_or_workflow_name || '',
                workflow_run_id: rawData.workflow_run_id || 0,
                workflow_confirmation_status: rawData.workflow_confirmation_status || null,
                args: rawData.args || {},
                result: rawData.result || null
            };
            
            tools.push({
                toolData,
                startIndex,
                endIndex: endIndex + MCP_END_TAG.length
            });
        } catch (error) {
            console.error('Failed to parse MCP tool JSON:', error);
        }

        searchStartIndex = endIndex + MCP_END_TAG.length;
    }

    return tools;
};

export const splitContentBlocks = (content: string): ContentBlock[] => {
    // Parameter validation
    if (typeof content !== 'string' || content === null || content === undefined) {
        console.warn('splitContentBlocks: content is not a valid string:', content);
        return [{
            type: 'text',
            content: ''
        }];
    }

    const tools = extractMCPTools(content);
    
    if (tools.length === 0) {
        return [{
            type: 'text',
            content: content
        }];
    }

    const blocks: ContentBlock[] = [];
    let lastIndex = 0;

    tools.forEach((tool) => {
        // Add text before MCP tool
        if (tool.startIndex > lastIndex) {
            const textContent = content.substring(lastIndex, tool.startIndex).trim();
            if (textContent) {
                blocks.push({
                    type: 'text',
                    content: textContent
                });
            }
        }

        // Add MCP tool block
        blocks.push({
            type: 'mcp-tool',
            content: content.substring(tool.startIndex, tool.endIndex),
            toolData: tool.toolData
        });

        lastIndex = tool.endIndex;
    });

    // Add remaining text after last MCP tool
    if (lastIndex < content.length) {
        const textContent = content.substring(lastIndex).trim();
        if (textContent) {
            blocks.push({
                type: 'text',
                content: textContent
            });
        }
    }

    return blocks;
};

export const parseMCPContent = (content: string): ParsedMCPContent => {
    // Parameter validation
    if (typeof content !== 'string' || content === null || content === undefined) {
        console.warn('parseMCPContent: content is not a valid string:', content);
        return {
            blocks: [{
                type: 'text',
                content: ''
            }],
            hasMCPTools: false
        };
    }

    const blocks = splitContentBlocks(content);
    const hasMCPTools = blocks.some(block => block.type === 'mcp-tool');

    return {
        blocks,
        hasMCPTools
    };
};

// Utility functions for MCP tool state management

/**
 * Update MCP tool state in a message's mcpTools array
 */
export const updateMCPToolInMessage = (
    message: any, 
    id: string | number, 
    updates: Partial<MCPToolRuntimeData>
): any => {
    const newMessage = { ...message };
    
    // Initialize mcpTools array if it doesn't exist
    if (!newMessage.mcpTools) {
        newMessage.mcpTools = [];
    }
    
    // Find existing tool by id or create new one
    const existingToolIndex = newMessage.mcpTools.findIndex((tool: MCPToolRuntimeData) => tool.id === id);
    
    if (existingToolIndex >= 0) {
        // Update existing tool
        newMessage.mcpTools[existingToolIndex] = {
            ...newMessage.mcpTools[existingToolIndex],
            ...updates
        };
    } else {
        // Add new tool with default values
        newMessage.mcpTools.push({
            id,
            status: 'pending' as any,
            name: '',
            skill_or_workflow_name: '',
            workflow_run_id: 0,
            workflow_confirmation_status: null,
            args: {},
            result: null,
            ...updates
        });
    }
    
    return newMessage;
};

/**
 * Get MCP tool by id from message
 */
export const getMCPToolFromMessage = (message: any, id: string | number): MCPToolRuntimeData | null => {
    if (!message.mcpTools || !Array.isArray(message.mcpTools)) {
        return null;
    }
    
    return message.mcpTools.find((tool: MCPToolRuntimeData) => tool.id === id) || null;
};

/**
 * Remove MCP tool by id from message
 */
export const removeMCPToolFromMessage = (message: any, id: string | number): any => {
    const newMessage = { ...message };
    
    if (newMessage.mcpTools && Array.isArray(newMessage.mcpTools)) {
        newMessage.mcpTools = newMessage.mcpTools.filter((tool: MCPToolRuntimeData) => tool.id !== id);
    }
    
    return newMessage;
};

/**
 * Get all MCP tools from message sorted by id
 */
export const getAllMCPToolsFromMessage = (message: any): MCPToolRuntimeData[] => {
    if (!message.mcpTools || !Array.isArray(message.mcpTools)) {
        return [];
    }
    
    // Sort by converting to string for consistent ordering
    return [...message.mcpTools].sort((a, b) => String(a.id).localeCompare(String(b.id)));
};

/**
 * Serialize MCP tool runtime data to content string format
 */
export const serializeMCPToolToContent = (toolData: MCPToolRuntimeData): string => {
    try {
        const mcpToolData: MCPToolData = {
            id: toolData.id,
            name: toolData.name,
            skill_or_workflow_name: toolData.skill_or_workflow_name,
            workflow_run_id: toolData.workflow_run_id,
            workflow_confirmation_status: toolData.workflow_confirmation_status,
            args: toolData.args,
            result: toolData.result
        };
        
        const jsonContent = JSON.stringify(mcpToolData, null, 0);
        return `${MCP_START_TAG}${jsonContent}${MCP_END_TAG}`;
    } catch (error) {
        console.error('Failed to serialize MCP tool:', error);
        return '';
    }
};

/**
 * Reconstruct content string with updated MCP tool states from contentBlocks
 */
export const reconstructContentWithUpdatedMCPTools = (
    contentBlocks: StreamingContentBlock[], 
    getMCPTool: (id: string | number) => MCPToolRuntimeData | null
): string => {
    try {
        if (!contentBlocks || !Array.isArray(contentBlocks)) {
            console.warn('reconstructContentWithUpdatedMCPTools: contentBlocks is not a valid array');
            return '';
        }

        let reconstructedContent = '';

        contentBlocks.forEach(block => {
            if (block.type === 'text') {
                reconstructedContent += block.content || '';
            } else if (block.type === 'mcp' && block.toolId) {
                const runtimeToolData = getMCPTool(block.toolId);
                if (runtimeToolData) {
                    const serializedTool = serializeMCPToolToContent(runtimeToolData);
                    reconstructedContent += serializedTool;
                } else {
                    console.warn(`MCP tool ${block.toolId} not found in runtime data`);
                }
            }
        });

        return reconstructedContent;
    } catch (error) {
        console.error('Failed to reconstruct content with updated MCP tools:', error);
        return '';
    }
}; 