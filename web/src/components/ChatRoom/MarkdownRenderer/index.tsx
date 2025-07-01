/*
 * @LastEditors: biz
 */
import React from 'react';
import { Button, Image } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { copyToClipboard } from '../utils/clipboard';
import { extractTextFromArray } from '../utils';

// Markdown renderers for code blocks and images
export const createRenderers = (index: any, intl: any) => {
    return {
        code: ({ node, className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '');
            if (match?.length) {
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

            return (
                <div className="relative group">
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
    };
}; 