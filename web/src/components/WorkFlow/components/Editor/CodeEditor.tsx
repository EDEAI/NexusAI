/*
 * @LastEditors: biz
 */
import { ArrowsAltOutlined, FullscreenExitOutlined } from '@ant-design/icons';
import Editor, { loader } from '@monaco-editor/react';
import { useLocalStorageState } from 'ahooks';
import { Button } from 'antd';
import type { FC } from 'react';
import React, { memo, useCallback, useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import remarkGfm from 'remark-gfm';
import { useResizePanel } from '../../hooks/use-resize-panel';
// load file from local instead of cdn https://github.com/suren-atoyan/monaco-react/issues/482
loader.config({ paths: { vs: '/vs' } });

const CODE_EDITOR_LINE_HEIGHT = 18;

export type Props = {
    value?: string | object;
    placeholder?: string;
    onChange?: (value: string) => void;
    title?: string | JSX.Element;
    language: string;
    headerRight?: JSX.Element;
    readOnly?: boolean;
    isJSONStringifyBeauty?: boolean;
    height?: number;
    isInNode?: boolean;
    onMount?: (editor: any, monaco: any) => void;
    noWrapper?: boolean;
    isExpand?: boolean;
    mdValue?: string;
    onFullscreenChange?: (isFullscreen: boolean) => void;
    showMaximize?: boolean;
};

const languageMap = {
    javascript: 'javascript',
    python3: 'python',
    json: 'json',
};

const DEFAULT_THEME = {
    base: 'vs',
    inherit: true,
    rules: [],
    colors: {
        'editor.background': '#F2F4F7', // #00000000 transparent. But it will has a blue border
    },
};

const CodeEditor: FC<Props> = memo(
    ({
        value = '',
        placeholder = '',
        onChange = () => {},
        title = '',
        language,
        readOnly,
        isJSONStringifyBeauty,
        height,
        mdValue,
        onMount,
        noWrapper,
        onFullscreenChange,
        showMaximize = true,
    }) => {
        const [isFocus, setIsFocus] = React.useState(false);

        const [showBig, setShowBig] = useState(false);
        const [isMounted, setIsMounted] = React.useState(false);
        const minHeight = height || 200;
        const [editorContentHeight, setEditorContentHeight] = useState(56);

        const valueRef = useRef(value);
        useEffect(() => {
            valueRef.current = value;
        }, [value]);

        const editorRef = useRef<any>(null);
        const resizeEditorToContent = () => {
            if (editorRef.current) {
                const contentHeight = editorRef.current.getContentHeight(); // Math.max(, minHeight)
                setEditorContentHeight(contentHeight);
            }
        };

        const handleEditorChange = (value: string | undefined) => {
            valueRef.current = value;
            onChange(value || '');
            setTimeout(() => {
                resizeEditorToContent();
            }, 10);
        };

        const handleEditorDidMount = (editor: any, monaco: any) => {
            editorRef.current = editor;
            resizeEditorToContent();

            editor.onDidFocusEditorText(() => {
                setIsFocus(true);
            });
            editor.onDidBlurEditorText(() => {
                setIsFocus(false);
            });

            monaco.editor.defineTheme('default-theme', DEFAULT_THEME);

            monaco.editor.defineTheme('blur-theme', {
                base: 'vs',
                inherit: true,
                rules: [],
                colors: {
                    'editor.background': '#F2F4F7',
                },
            });

            monaco.editor.defineTheme('focus-theme', {
                base: 'vs',
                inherit: true,
                rules: [],
                colors: {
                    'editor.background': '#ffffff',
                },
            });

            monaco.editor.setTheme('default-theme');

            onMount?.(editor, monaco);
            setIsMounted(true);
        };

        const outPutValue = (() => {
            if (!isJSONStringifyBeauty) return value as string;
            try {
                return JSON.stringify(value as object, null, 2);
            } catch (e) {
                return value as string;
            }
        })();

        const theme = (() => {
            if (noWrapper) return 'default-theme';

            return isFocus ? 'focus-theme' : 'blur-theme';
        })();

        const Main = ({ key }) => (
            <>
                <Editor
                    key={key}
                    // className='min-h-[100%]' // h-full
                    // language={language === CodeLanguage.javascript ? 'javascript' : 'python'}
                    language={languageMap[language] || 'python'}
                    theme={isMounted ? theme : 'default-theme'}
                    value={
                        (!readOnly && typeof valueRef?.current == 'string' && valueRef?.current) ||
                        outPutValue
                    }
                    onChange={handleEditorChange}
                    options={{
                        readOnly,
                        domReadOnly: true,
                        quickSuggestions: false,
                        minimap: { enabled: false },
                        lineNumbersMinChars: 1,
                        wordWrap: 'on',

                        unicodeHighlight: {
                            ambiguousCharacters: false,
                        },
                    }}
                    onMount={handleEditorDidMount}
                />
                {!outPutValue && (
                    <div className="pointer-events-none absolute left-[36px] top-0 leading-[18px] text-[13px] font-normal text-gray-300">
                        {placeholder}
                    </div>
                )}
            </>
        );

        const [editorTypeJson, setEditorJson] = useState(true);
        const ToggleMd = () => {
            return (
                <Button
                    type="link"
                    className="absolute top-1 right-10"
                    onClick={() => {
                        console.log(editorTypeJson);

                        setEditorJson(prev => {
                            return !prev;
                        });
                    }}
                >
                    {editorTypeJson ? 'MD' : 'JSON'}
                </Button>
            );
        };

        const renderMaximizeButton = () => {
            if (!showMaximize) return null;

            return (
                <Button
                    className="absolute top-1 right-1"
                    onClick={() => setShowBig(!showBig)}
                    type="text"
                    icon={
                        !showBig ? (
                            <ArrowsAltOutlined className="size-5 cursor-pointer text-lg" />
                        ) : (
                            <FullscreenExitOutlined className="size-5 cursor-pointer text-lg" />
                        )
                    }
                />
            );
        };

        const RenderFix = ({ key }) => {
            return (
                <div
                    style={{ background: isFocus || !editorTypeJson ? '#ffffff' : '#f2f4f7' }}
                    className={`relative h-full w-full top-0 flex flex-col p-2 border rounded-md  box-border border-slate-200`}
                >
                    <div className="h-8">
                        {title && <div className="font-bold pb-2">{title}</div>}
                    </div>
                    {renderMaximizeButton()}
                    {mdValue && <ToggleMd></ToggleMd>}
                    {editorTypeJson ? (
                        <div className="flex-1">
                            <Main key={key}></Main>
                        </div>
                    ) : (
                        <div className="w-full h-full flex-1 overflow-auto p-4">
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                rehypePlugins={[rehypeHighlight]}
                            >
                                {mdValue}
                            </ReactMarkdown>
                        </div>
                    )}
                </div>
            );
        };
        const [panelWidth, setPanelWidth] = useLocalStorageState('ani-workflow-code-width', {
            defaultValue: 415,
        });
        const handleResize = useCallback(
            (width: number) => {
                setPanelWidth(width);
            },
            [setPanelWidth],
        );

        const RenderWrap = useCallback(() => {
            if (showBig) {
                const { triggerRef, containerRef } = useResizePanel({
                    direction: 'horizontal',
                    triggerDirection: 'left',
                    minWidth: 415,
                    maxWidth: window.innerWidth - 20,
                    onResize: handleResize,
                });
                return (
                    <div
                        style={{
                            height: 'calc(100vh - 84px)',
                            position: 'fixed',
                            zIndex: '9999',
                            top: '65px',
                            right: '8px',
                            width: `${panelWidth}px`,
                        }}
                        ref={containerRef}
                    >
                        <div
                            ref={triggerRef}
                            className="absolute top-1/2 -translate-y-1/2 -left-2 w-3 h-6 cursor-col-resize resize-x"
                        >
                            <div className="w-1 h-6 bg-gray-300 rounded-sm"></div>
                        </div>
                        <RenderFix key={`editor-instance-${showBig}`}></RenderFix>
                    </div>
                );
            }
            return <RenderFix key={`editor-instance-${showBig}`}></RenderFix>;
        }, [showBig, value, editorTypeJson]);

        const handleFullscreenChange = useCallback(() => {
            const newShowBig = !showBig;
            setShowBig(newShowBig);
            onFullscreenChange?.(newShowBig);
        }, [showBig, onFullscreenChange]);

        return <RenderWrap></RenderWrap>;
    },
);

export default CodeEditor;
