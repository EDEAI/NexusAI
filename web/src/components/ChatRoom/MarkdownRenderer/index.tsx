/*
 * @LastEditors: biz
 */
import React, { useState, useEffect, memo } from 'react';
import { Button, Image } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { copyToClipboard } from '../utils/clipboard';
import { extractTextFromArray } from '../utils';
import MermaidChart from './MermaidChart';

// Debounced wrapper to delay Mermaid rendering until code is stable for 1s
type DebouncedMermaidProps = { code: string; index: number; isCurrentMessage: boolean };

const DebouncedMermaidBase: React.FC<DebouncedMermaidProps> = ({ code, index, isCurrentMessage }) => {
    if(!isCurrentMessage) return <MermaidChart code={code} index={index} />
    const [ready, setReady] = useState(false);

    useEffect(() => {
        setReady(false);
        const timer = setTimeout(() => setReady(true), 1000);
        return () => clearTimeout(timer);
    }, [code]);

    if (!ready) {
        return (
            <div className="my-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                <div className="flex justify-center items-center min-h-[200px] text-gray-500">
                    <div className="text-sm">Loading Mermaid chart...</div>
                </div>
            </div>
        );
    }

    return <MermaidChart code={code} index={index} />;
};

// Memoize DebouncedMermaid to avoid unnecessary re-renders
const areDebouncedPropsEqual = (prev: DebouncedMermaidProps, next: DebouncedMermaidProps) => {
    return prev.code === next.code && prev.index === next.index;
};

const DebouncedMermaid = memo(DebouncedMermaidBase, areDebouncedPropsEqual);

// Markdown renderers for code blocks and images
export const createRenderers = (index: any, intl: any,isCurrentMessage:boolean=false) => {
    const downloadFile = (url: string, filename: string) => {
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
    return {
        code: ({ node, className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '');
            if (match?.length) {
                // Handle Mermaid charts with debounce via DebouncedMermaid
                if (match[1] === 'mermaid') {
                    const mermaidCode = extractTextFromArray(children);
                    return <DebouncedMermaid code={mermaidCode} index={index} isCurrentMessage={isCurrentMessage} />;
                }
                
                // Handle regular code blocks
                const id = Math.random().toString(36).substr(2, 9);
                return (
                    <div className=" rounded-md border overflow-hidden">
                        <div className="flex h-12 items-center justify-between bg-zinc-100 px-4 bg-zinc-900">
                            <div className="flex items-center gap-2">
                                <p className="text-sm  text-[#fff] mb-[0]">{match[1]}</p>
                            </div>
                            <div
                                className="text-[12px] text-[#fff] mb-[0] cursor-pointer flex gap-x-[5px]"
                                onClick={async (e: any) => {
                                    try {
                                        let ct = e.currentTarget;
                                        const success = await copyToClipboard(extractTextFromArray(children));
                                        if (success && ct) {
                                            ct.children[1].innerText = intl.formatMessage({
                                                id: 'app.chatroom.content.copySucceed',
                                            });
                                            setTimeout(() => {
                                                if (ct)
                                                    ct.children[1].innerText = intl.formatMessage({
                                                        id: 'app.chatroom.content.copycode',
                                                    });
                                            }, 200);
                                        } else if (ct) {
                                            ct.children[1].innerText = intl.formatMessage({
                                                id: 'app.chatroom.content.copyFailed',
                                            }) || 'Copy failed';
                                            setTimeout(() => {
                                                if (ct)
                                                    ct.children[1].innerText = intl.formatMessage({
                                                        id: 'app.chatroom.content.copycode',
                                                    });
                                            }, 1000);
                                        }
                                    } catch (err) {
                                        console.error('Failed to copy text: ', err);
                                    }
                                }}
                            >
                                <img src="/icons/chat_copy_w.svg"></img>
                                <span>
                                    {intl.formatMessage({ id: 'app.chatroom.content.copycode' })}
                                </span>
                            </div>
                        </div>
                        <div className="overflow-x-auto bg-[#282c34] text-[#abb2bf]">
                            <div id={`${id}${index}`} className="p-4">
                                {children}
                            </div>
                        </div>
                    </div>
                );
            } else {
                return <code {...props}>{children}</code>;
            }
        },
        img: ({ node, ...props }) => {
            return (
                <div className="relative group" key={props.src}>
                    <Image
                        src={props.src}
                        alt={props.alt}
                        className="max-w-full max-h-40 h-auto rounded-md"
                    />
                    <div className="absolute top-0 right-0 p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                            type="primary"
                            size="small"
                            icon={<DownloadOutlined />}
                            onClick={e => {
                                e.stopPropagation();
                                downloadFile(props.src || '', props.alt || 'image.png');
                            }}
                        />
                    </div>
                </div>
            );
        },
        table: ({ node, children, ...props }) => {
            return (
                <div className="overflow-x-auto my-4 border border-gray-300 rounded-lg">
                    <table className="min-w-full" {...props}>
                        {children}
                    </table>
                </div>
            );
        },
        thead: ({ node, children, ...props }) => {
            return <thead className="bg-gray-50" {...props}>{children}</thead>;
        },
        tbody: ({ node, children, ...props }) => {
            return <tbody className="bg-white" {...props}>{children}</tbody>;
        },
        tr: ({ node, children, ...props }) => {
            return <tr className="border-b border-gray-200 hover:bg-gray-50" {...props}>{children}</tr>;
        },
        th: ({ node, children, ...props }) => {
            return (
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700 border-r border-gray-200 last:border-r-0" {...props}>
                    {children}
                </th>
            );
        },
        td: ({ node, children, ...props }) => {
            return (
                <td className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200 last:border-r-0" {...props}>
                    {children}
                </td>
            );
        },
    };
}; 