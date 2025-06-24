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
        item
    } = props;
    
    // Use saved parsedContent if available, otherwise parse on-demand
    const parsedContent = item?.parsedContent || parseMCPContent(content);
    
    // Note: MCP tools are now processed when historical messages are loaded,
    // so we don't need to register them here during render
    
    console.log(parsedContent);
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
            
            {parsedContent.hasMCPTools ? (
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
                <ReactMarkdown
                    rehypePlugins={[rehypeHighlight]}
                    components={createRenderers(index, intl)}
                >
                    {content}
                </ReactMarkdown>
            )}
        </div>
    );
}; 