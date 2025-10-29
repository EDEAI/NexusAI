/*
 * @LastEditors: biz
 */
import { getSkillInfo } from '@/api/workflow';
import { ProForm, ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useLatest } from 'ahooks';
import { Button, Collapse, Empty, Popover, Space, Typography } from 'antd';
import _ from 'lodash';
import { memo, useEffect, useMemo, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import CodeEditor from '../../components/Editor/CodeEditor';
import {
    SwitchManualConfirmation,
    SwitchWaitForAllPredecessors,
} from '../../components/Form/Switch';
import { SelectVariable } from '../../components/Form/Select';
import useNodeIdUpdate from '../../hooks/useNodeIdUpdate';
import useStore from '../../store';
import { AppNode } from '../../types';
import { resetFormNodes } from '../../utils/resetFormNodes';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { FunctionOutlined, FileOutlined } from '@ant-design/icons';
export default memo(({ node }: { node: AppNode }) => {
    const [nodeInfo, setNodeInfo] = useState(_.cloneDeep(node));
    const intl = useIntl();
    const formRef = useRef(null);
    const updateNode = useStore(state => state.updateNode);
    const updateNodeData = useStore(state => state.updateNodeData);
    const getVariables = useStore(state => state.getOutputVariables);
    const state = useLatest(nodeInfo);
    const [inputList, setInputList] = useState([]);

    // const getVariables = useVariables();
    const [editorOptions, setEditorOptions] = useState([]);
    useEffect(() => {
        skillInfo(node);
    }, []);

    useNodeIdUpdate((nodeId, upNode) => {
        if (!upNode) return;
        setNodeInfo(upNode);
        skillInfo(upNode);
        // const fieldNames = Object.keys(formRef.current.getFieldsValue());
        // fieldNames.forEach((e) => {
        //     formRef.current.setFieldsValue({ [e]: nodeInfo.data[e] });
        // });
        console.log('node', upNode);

        const rest = resetFormNodes(formRef, upNode);
        setTimeout(() => {
            rest();
        }, 100);
        const vars = getVariables(upNode.id).filter(item=>item.createVar.type!= 'file');
        setEditorOptions(vars);
    });

    const skillInfo = async (currentNode?: AppNode) => {
        const targetNode = currentNode || node;
        if (!targetNode.data['baseData']?.app_id) return;
        let res;
        if (targetNode?.data['infoData']) {
            res = {
                code: 0,
                data: targetNode?.data['infoData'],
            };
        } else {
            res = await getSkillInfo(targetNode.data['baseData']?.app_id);
        }

        if (res.code == 0) {
            updateNodeData(targetNode.id, {
                infoData: res.data,
            });
            setNodeInfo(prev => {
                if (!prev || prev.id !== targetNode.id) return prev;
                return {
                    ...prev,
                    data: {
                        ...(prev.data || {}),
                        infoData: res.data,
                    },
                };
            });
            if (res.data?.input_variables?.properties) {
                setInputList(Object.values(res.data?.input_variables?.properties));
            }
        }
    };

    const setNodeChange = (addItem: { [key: string]: any }, allValues) => {
        updateNodeData(node.id, allValues);
    };
    function isValidJson(source) {
        if (!source) return null;
        if (typeof source === 'object') {
            return source;
        }
        if (typeof source === 'string') {
            try {
                return JSON.parse(source);
            } catch (e) {
                console.error(e);
                return null;
            }
        }
        return null;
    }

    const skillInfoData = nodeInfo?.data?.infoData;

    const extractVariables = useMemo(() => {
        const normalize = (variables?: any) => {
            if (!variables) return [];
            if (Array.isArray(variables)) return variables;
            if (typeof variables === 'object' && variables.properties) {
                return Object.values(variables.properties);
            }
            return [];
        };
        const inputVariables = normalize(skillInfoData?.input_variables).sort(
            (a: any, b: any) => (a?.sort_order || 0) - (b?.sort_order || 0),
        );
        const outputVariables = normalize(skillInfoData?.output_variables).sort(
            (a: any, b: any) => (a?.sort_order || 0) - (b?.sort_order || 0),
        );
        return {
            inputVariables,
            outputVariables,
        };
    }, [skillInfoData?.input_variables, skillInfoData?.output_variables]);

    const renderVariableDescription = (description?: string) => (
        <div className="max-h-[480px] max-w-[520px] overflow-auto pr-2">
            {description ? (
                <div className="markdown-body">
                    <ReactMarkdown rehypePlugins={[rehypeHighlight]} remarkPlugins={[remarkGfm]}>
                        {description}
                    </ReactMarkdown>
                </div>
            ) : (
                <div className="text-[#9CA3AF]">
                    {intl.formatMessage({
                        id: 'workflow.skill.noDescription',
                        defaultMessage: 'No description provided',
                    })}
                </div>
            )}
        </div>
    );

    const renderVariableCards = (variables: any[]) => {
        if (!variables.length) {
            return (
                <Empty
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                    description={intl.formatMessage({ id: 'workflow.noData' })}
                />
            );
        }

        const typeIconMap: Record<string, ReactNode> = {
            string: <img src="/icons/text.svg" className="size-4" />,
            long_string: intl.formatMessage({ id: 'workflow.vars.paragraph', defaultMessage: '' }),
            number: <img src="/icons/number.svg" className="size-4" />,
            json: <img src="/icons/json.svg" className="size-4" />,
            file: <FileOutlined />,
        };

        return (
            <Space direction="vertical" className="w-full">
                {variables.map((variable: any) => {
                    const required = variable?.required === true || variable?.required === 1;
        const descriptionContent = renderVariableDescription(variable?.description?.trim() ? variable.description : undefined);

                    return (
                        <div
                            key={variable?.name}
                            className="flex bg-white gap-2 justify-between truncate h-10 items-center p-2 border border-slate-300 rounded-md mt-2"
                        >
                            <div className="flex items-center gap-1 truncate">
                                <div>
                                    <FunctionOutlined />
                                </div>
                                <div className="max-w-28 truncate font-bold">
                                    {variable?.name || '-'}
                                </div>
                                <div className="max-w-20 truncate text-gray-500">
                                    {variable?.display_name || '-'}
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                {required && (
                                    <div className="text-slate-500 text-xs">
                                        {intl.formatMessage({
                                            id: 'workflow.vars.required',
                                            defaultMessage: '',
                                        })}
                                    </div>
                                )}
                                <div>{typeIconMap[variable?.type] || variable?.type}</div>
                                <Popover
                                    overlayStyle={{ maxWidth: 560 }}
                                    content={descriptionContent}
                                    trigger="click"
                                >
                                    <Button type="link" size="small" className="px-0">
                                        {intl.formatMessage({
                                            id: 'workflow.skill.viewDescription',
                                            defaultMessage: 'View Description',
                                        })}
                                    </Button>
                                </Popover>
                            </div>
                        </div>
                    );
                })}
            </Space>
        );
    };
    //
    return (
        <>
            <div>
                <ProForm
                    formRef={formRef}
                    submitter={{
                        render: () => null,
                    }}
                    autoFocusFirstInput={false}
                    omitNil={false}
                    layout="horizontal"
                    className="pt-5"
                    onValuesChange={setNodeChange}
                >
                    {inputList.map((item, index) => {
                        return (
                            <SelectVariable
                                key={index}
                                name={`variable.${item.name}`}
                                label={item.name}
                                showSearch
                                allowClear={false}
                                node={node}
                                filterFn={()=>true}
                                options={editorOptions}
                            ></SelectVariable>
                        );
                    })}
                    <div className="user-form">
                        <SwitchManualConfirmation></SwitchManualConfirmation>
                        <SwitchWaitForAllPredecessors></SwitchWaitForAllPredecessors>
                    </div>
                </ProForm>
                <div className="w-full overflow-x-hidden">
                    <Collapse
                        className="-mx-4"
                        ghost
                        bordered={false}
                        expandIconPosition="end"
                        items={[
                            {
                                key: '0',
                                label: (
                                    <Typography.Title level={5}>
                                        {intl.formatMessage({
                                            id: 'workflow.label.skillConfiguration',
                                            defaultMessage: '',
                                        })}
                                    </Typography.Title>
                                ),
                                children: (
                                    <>
                                        <Space direction="vertical" size={24} className="w-full">
                                            {skillInfoData?.description && (
                                                <div>
                                                    <Typography.Title level={5}>
                                                        {intl.formatMessage({
                                                            id: 'workflow.skill.description',
                                                            defaultMessage: 'Skill Description',
                                                        })}
                                                    </Typography.Title>
                                                    <div className="markdown-body rounded-lg bg-[#F9FAFB] px-4 py-3">
                                                        <ReactMarkdown
                                                            rehypePlugins={[rehypeHighlight]}
                                                            remarkPlugins={[remarkGfm]}
                                                        >
                                                            {skillInfoData.description}
                                                        </ReactMarkdown>
                                                    </div>
                                                </div>
                                            )}
                                            <div>
                                                <Typography.Title level={5}>
                                                    {intl.formatMessage({
                                                        id: 'workflow.skill.inputVariables',
                                                        defaultMessage: 'Input Variables',
                                                    })}
                                                </Typography.Title>
                                                {renderVariableCards(extractVariables.inputVariables)}
                                            </div>
                                            <div>
                                                <Typography.Title level={5}>
                                                    {intl.formatMessage({
                                                        id: 'workflow.skill.outputVariables',
                                                        defaultMessage: 'Output Variables',
                                                    })}
                                                </Typography.Title>
                                                {renderVariableCards(extractVariables.outputVariables)}
                                            </div>
                                            {skillInfoData?.code && isValidJson(skillInfoData.code)?.python3 ? (
                                                <div>
                                                    <Typography.Title level={5}>
                                                        {intl.formatMessage({
                                                            id: 'workflow.label.code',
                                                            defaultMessage: '',
                                                        })}
                                                    </Typography.Title>
                                                    <div className="h-80">
                                                        <CodeEditor
                                                            language="python3"
                                                            value={isValidJson(skillInfoData.code)?.python3}
                                                            readOnly
                                                            onChange={() => {}}
                                                            title={`python3`}
                                                        ></CodeEditor>
                                                    </div>
                                                </div>
                                            ) : null}
                                        </Space>
                                    </>
                                ),
                            },
                        ]}
                    ></Collapse>
                </div>
            </div>
        </>
    );
});
