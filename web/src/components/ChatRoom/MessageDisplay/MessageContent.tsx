/*
 * @LastEditors: biz
 */
import React, { FC } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import FileListDisplay from '@/components/FileListDisplay';
import { createRenderers } from '../MarkdownRenderer';
import { downloadFile } from '../utils';
import { parseMCPContent } from '../utils/mcpParser';
import { MCPToolDisplay } from '../MCPToolDisplay';
import { MCPToolRuntimeData, getMCPToolStatus } from '../types/mcp';
import { ContentBlock } from '../types';

interface MessageContentProps {
    content: string;
    fileList?: any[];
    index: number;
    intl: any;
    isAgent: boolean;
    contentId: string;
    mcpTools?: Record<string | number, MCPToolRuntimeData>;
    updateMCPTool?: (id: string | number, updates: Partial<MCPToolRuntimeData>) => void;
    getMCPTool?: (id: string | number) => MCPToolRuntimeData | null;
    item?: any;
    isCurrentMessage?: boolean;
    contentBlocks?: ContentBlock[];  // New: support for streaming content blocks
}

export const MessageContent: FC<MessageContentProps> = props => {
    const { 
        content, 
        fileList, 
        index, 
        intl, 
        isAgent, 
        contentId, 
        mcpTools, 
        updateMCPTool, 
        getMCPTool,
        item,
        contentBlocks
    } = props;
    
    // Use saved parsedContent if available, otherwise parse on-demand
    const parsedContent = item?.parsedContent || parseMCPContent(content);
    
    // Note: MCP tools are now processed when historical messages are loaded,
    // so we don't need to register them here during render
  
    return (
        <div
            className={`text-left inline-block markdown-container text-[14px] font-[400] text-[#213044] bg-[#F7F7F7] p-[15px] pb-[1px] leading-[22px]`}
            style={
                isAgent
                    ? { borderRadius: ' 0px 8px 8px 8px' }
                    : {
                          borderRadius: '8px 0px 8px 8px',
                          background: 'rgba(27,100,243,0.1)',
                          whiteSpace: 'pre-wrap',
                      }
            }
            id={contentId}
        >
            {fileList && fileList.length > 0 && (
                <div className="mb-3">
                    <FileListDisplay
                        fileList={fileList}
                        onDownload={downloadFile}
                    />
                </div>
            )}
            
            {/* 渲染文本内容 - 支持contentBlocks和传统parsedContent双模式 */}
            {contentBlocks && contentBlocks.length > 0 ? (
                // New: contentBlocks rendering mode for streaming messages
                <div>
                    {contentBlocks.map((block, blockIndex) => (
                        <div key={`content-block-${blockIndex}`}>
                            {block.type === 'text' ? (
                                block.content && (
                                    <ReactMarkdown
                                        rehypePlugins={[rehypeHighlight]}
                                        components={createRenderers(index, intl)}
                                    >
                                        {block.content}
                                    </ReactMarkdown>
                                )
                            ) : (
                                // MCP tool block
                                block.toolId && getMCPTool && (
                                    <MCPToolDisplay
                                        toolData={{
                                            id: block.toolId,
                                            name: getMCPTool(block.toolId)?.name || '',
                                            skill_or_workflow_name: getMCPTool(block.toolId)?.skill_or_workflow_name || '',
                                            workflow_run_id: getMCPTool(block.toolId)?.workflow_run_id,
                                            workflow_confirmation_status: getMCPTool(block.toolId)?.workflow_confirmation_status,
                                            args: getMCPTool(block.toolId)?.args || {},
                                            result: getMCPTool(block.toolId)?.result
                                        }}
                                        intl={intl}
                                        runtimeData={getMCPTool(block.toolId)}
                                    />
                                )
                            )}
                        </div>
                    ))}
                </div>
            ) : parsedContent.hasMCPTools ? (
                // Legacy: parsedContent rendering mode for historical messages
                <div>
                    {parsedContent.blocks.map((block, blockIndex) => (
                        <div key={blockIndex}>
                            {block.type === 'text' ? (
                                <ReactMarkdown
                                    rehypePlugins={[rehypeHighlight]}
                                    components={createRenderers(index, intl)}
                                >
                                    {block.content}
                                </ReactMarkdown>
                            ) : (
                                block.toolData && (
                                    <MCPToolDisplay
                                        toolData={block.toolData}
                                        intl={intl}
                                        runtimeData={getMCPTool ? getMCPTool(block.toolData.id) : null}
                                    />
                                )
                            )}
                        </div>
                    ))}
                </div>
            ) : (
                // Default: simple text rendering
                <ReactMarkdown
                    rehypePlugins={[rehypeHighlight]}
                    components={createRenderers(index, intl)}
                >
                    {content}
                </ReactMarkdown>
            )}
            
            {/* 对于当前消息，仅在没有contentBlocks时显示activeMCPTools（向后兼容） */}
            {props.isCurrentMessage && !contentBlocks && item?.activeMCPTools?.length > 0 && (
                <div className="mt-3">
                    {item.activeMCPTools
                        .map((toolId: string | number) => getMCPTool ? getMCPTool(toolId) : null)
                        .filter(Boolean)
                        .map((toolData: MCPToolRuntimeData) => (
                            <MCPToolDisplay
                                key={`current-tool-${toolData.id}`}
                                toolData={{
                                    name: toolData.name,
                                    skill_or_workflow_name: toolData.skill_or_workflow_name,
                                    workflow_run_id: toolData.workflow_run_id,
                                    workflow_confirmation_status: toolData.workflow_confirmation_status,
                                    args: toolData.args,
                                    result: toolData.result,
                                    id: toolData.id
                                }}
                                intl={intl}
                                runtimeData={toolData}
                            />
                        ))}
                </div>
            )}
        </div>
    );
}; 