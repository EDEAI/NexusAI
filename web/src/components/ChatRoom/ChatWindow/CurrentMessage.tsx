/*
 * @LastEditors: biz
 */
import React, { FC } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import Avatar from '@/components/ChatAvatar';
import FileListDisplay from '@/components/FileListDisplay';
import { userinfodata } from '@/utils/useUser';
import { createRenderers } from '../MarkdownRenderer';
import { downloadFile } from '../utils';
import { MCPToolDisplay } from '../MCPToolDisplay';
import { MCPToolRuntimeData } from '../types/mcp';

interface CurrentMessageProps {
    currentMessage: any;
    agentChatRoomId?: any;
    intl: any;
}

export const CurrentMessage: FC<CurrentMessageProps> = props => {
    const { currentMessage, agentChatRoomId, intl } = props;

    if (!currentMessage.name) {
        return null;
    }

    return (
        <div
            className={`w-full flex gap-[15px] pt-[15px] pb-[15px] ${
                currentMessage.is_agent != 1 ? 'flex-row-reverse' : ''
            }`}
        >
            {currentMessage.is_agent == 1 ? (
                <Avatar data={currentMessage} />
            ) : (
                <Avatar data={{ avatar: '/icons/user_header.svg' }} />
            )}
            <div
                className={`flex1 ${agentChatRoomId ? '' : 'max-w-[560px]'} text-right`}
                id={`addcontent`}
            >
                <div
                    className={`${
                        currentMessage.is_agent == 1 ? 'text-left' : 'text-right'
                    } font-[500] text-[14px] text-[#213044] pb-[8px]`}
                >
                    {currentMessage.name
                        ? currentMessage.name
                        : userinfodata('GET').nickname}
                </div>
                <div
                    className={`flex ${
                        currentMessage.is_agent == 1 ? 'flex-row' : 'flex-row-reverse'
                    }`}
                >
                    <div
                        className={`text-left inline-block markdown-container text-[14px] font-[400] text-[#213044] bg-[#F7F7F7] p-[15px] pb-[1px] leading-[22px]`}
                        style={
                            currentMessage.is_agent == 1
                                ? { borderRadius: ' 0px 8px 8px 8px' }
                                : {
                                      borderRadius: '8px 0px 8px 8px',
                                      background: 'rgba(27,100,243,0.1)',
                                      whiteSpace: 'pre-wrap',
                                  }
                        }
                        id={`addchilContent`}
                    >
                        {currentMessage.file_list &&
                            currentMessage.file_list.length > 0 && (
                                <div className="mb-3">
                                    <FileListDisplay
                                        fileList={currentMessage.file_list}
                                        onDownload={downloadFile}
                                    />
                                </div>
                            )}
                            
                        <ReactMarkdown
                            rehypePlugins={[rehypeHighlight]}
                            components={createRenderers('add', intl)}
                        >
                            {currentMessage.content}
                        </ReactMarkdown>
                        
                        {/* Display MCP tools if they exist - after text content */}
                        {currentMessage.mcpTools && currentMessage.mcpTools.length > 0 && (
                            <div className="mt-3">
                                {currentMessage.mcpTools.map((toolData: MCPToolRuntimeData, index: number) => (
                                    <MCPToolDisplay
                                        key={`mcp-tool-${toolData.id}`}
                                        toolData={{
                                            name: toolData.name,
                                            skill_or_workflow_name: toolData.skill_or_workflow_name,
                                            workflow_run_id: toolData.workflow_run_id,
                                            workflow_confirmation_status: toolData.workflow_confirmation || toolData.workflow_confirmation_status,
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
                </div>
            </div>
        </div>
    );
}; 