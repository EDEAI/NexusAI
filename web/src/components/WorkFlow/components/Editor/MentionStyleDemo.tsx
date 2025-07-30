import React from 'react';
import { Card, Typography, Space, Divider } from 'antd';
import { useIntl } from '@umijs/max';
import './SlateEditorV3.css';

const { Title, Text } = Typography;

const MentionStyleDemo: React.FC = () => {
    const intl = useIntl();
    // 模拟不同类型的变量数据 (包含更多项目来测试滚动)
    const mockVariables = [
        { type: 'input', name: '用户输入', meta: 'user_input', title: '用户输入变量' },
        { type: 'output', name: '模型输出', meta: null, title: '模型输出变量' },
        { type: 'input', name: '系统提示', meta: 'system_prompt', title: '系统提示变量' },
        { type: 'output', name: '长变量名称示例测试', meta: null, title: '这是一个很长的变量名称用于测试省略效果' },
        { type: 'input', name: '数据源', meta: 'data_source', title: '数据源变量' },
        { type: 'output', name: '处理结果', meta: null, title: '处理结果变量' },
        { type: 'input', name: '配置参数', meta: 'config_params', title: '配置参数变量' },
        { type: 'output', name: '分析报告', meta: null, title: '分析报告变量' },
        { type: 'input', name: '用户偏好', meta: 'user_preferences', title: '用户偏好设置' },
        { type: 'output', name: '推荐列表', meta: null, title: '推荐内容列表' },
        { type: 'input', name: '查询条件', meta: 'search_criteria', title: '搜索查询条件' },
        { type: 'output', name: '搜索结果', meta: null, title: '搜索返回结果' },
        { type: 'input', name: '文件路径', meta: 'file_path', title: '文件路径变量' },
        { type: 'output', name: '文件内容', meta: null, title: '读取的文件内容' },
        { type: 'input', name: '时间范围', meta: 'time_range', title: '时间范围选择' },
    ];

    const renderMockMention = (variable: any, index: number) => {
        const baseClasses = `
            mention-tag inline-flex items-center gap-1 px-2 py-1 rounded-md text-sm font-medium
            transition-all duration-200 ease-in-out cursor-default select-none border
            ${variable.type === 'input' 
                ? 'bg-gradient-to-r from-green-50 to-emerald-50 text-green-700 border-green-200 hover:from-green-100 hover:to-emerald-100' 
                : 'bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 border-blue-200 hover:from-blue-100 hover:to-indigo-100'
            }
        `;

        return (
            <span key={index} className={baseClasses}>
                {/* 变量类型图标 */}
                <span className={`
                    mention-icon w-3 h-3 rounded-full flex items-center justify-center text-xs font-bold
                    ${variable.type === 'input' 
                        ? 'bg-green-500 text-white' 
                        : 'bg-blue-500 text-white'
                    }
                `}>
                    {variable.type === 'input' ? 'I' : 'V'}
                </span>
                
                {/* 变量名称 */}
                <span className="mention-name font-medium">
                    {variable.title}
                </span>
                
                {/* 输入变量的额外信息 */}
                {variable.meta && (
                    <span className="mention-meta text-xs opacity-75">
                        ({variable.meta})
                    </span>
                )}
            </span>
        );
    };

    return (
        <div className="p-4 space-y-4">
            <Card>
                <Title level={4}>
                    {intl.formatMessage({
                        id: 'workflow.editor.demo.title',
                        defaultMessage: 'Variable Tag Style Preview',
                    })}
                </Title>
                <Text type="secondary">
                    {intl.formatMessage({
                        id: 'workflow.editor.demo.description',
                        defaultMessage: 'Showcase the new styling effects for variable tags in the editor',
                    })}
                </Text>
                
                <Divider />
                
                <div className="space-y-4">
                    <div>
                        <Text strong>
                            {intl.formatMessage({
                                id: 'workflow.editor.demo.basicStyle',
                                defaultMessage: 'Basic Style Effects:',
                            })}
                        </Text>
                        <div className="mt-2 p-4 bg-gray-50 rounded-md">
                            <Space wrap>
                                {mockVariables.map((variable, index) => 
                                    renderMockMention(variable, index)
                                )}
                            </Space>
                        </div>
                    </div>
                    
                    <div>
                        <Text strong>
                            {intl.formatMessage({
                                id: 'workflow.editor.demo.inTextStyle',
                                defaultMessage: 'Effects in Text:',
                            })}
                        </Text>
                        <div className="mt-2 p-4 bg-gray-50 rounded-md leading-relaxed">
                            <span>{intl.formatMessage({
                                id: 'workflow.editor.demo.exampleText',
                                defaultMessage: 'Please generate a reply based on {input} and refer to the format of {output}. The system will use {system} to guide the generation process.',
                            }, {
                                input: renderMockMention(mockVariables[0], 100),
                                output: renderMockMention(mockVariables[1], 101),
                                system: renderMockMention(mockVariables[2], 102),
                            })}</span>
                        </div>
                    </div>
                    
                    <div>
                        <Text strong>
                            {intl.formatMessage({
                                id: 'workflow.editor.demo.colorExplanation',
                                defaultMessage: 'Color Legend:',
                            })}
                        </Text>
                        <ul className="mt-2 space-y-1 text-sm">
                            <li>• <span className="text-green-600 font-medium">
                                {intl.formatMessage({
                                    id: 'workflow.editor.demo.greenLabel',
                                    defaultMessage: 'Green Tags',
                                })}
                            </span>：{intl.formatMessage({
                                id: 'workflow.editor.demo.inputVariables',
                                defaultMessage: 'Input Variables',
                            })}</li>
                            <li>• <span className="text-blue-600 font-medium">
                                {intl.formatMessage({
                                    id: 'workflow.editor.demo.blueLabel',
                                    defaultMessage: 'Blue Tags',
                                })}
                            </span>：{intl.formatMessage({
                                id: 'workflow.editor.demo.outputVariables',
                                defaultMessage: 'Output Variables',
                            })}</li>
                            <li>• <strong>I</strong> {intl.formatMessage({
                                id: 'workflow.editor.demo.inputIcon',
                                defaultMessage: 'Input Variable Identifier',
                            })}</li>
                            <li>• <strong>V</strong> {intl.formatMessage({
                                id: 'workflow.editor.demo.variableIcon',
                                defaultMessage: 'Variable Identifier',
                            })}</li>
                        </ul>
                    </div>
                </div>
            </Card>
        </div>
    );
};

export default MentionStyleDemo; 