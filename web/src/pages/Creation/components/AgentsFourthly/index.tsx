import { PutagentPublish, PutagentRun } from '@/api/agents';
import CodeEditor from '@/components/WorkFlow/components/Editor/CodeEditor';
import SlateEditor from '@/components/WorkFlow/components/Editor/SlateEditor';
import { createPromptFromObject } from '@/py2js/prompt.js';
import { Variable as AgentsVariable, ObjectVariable } from '@/py2js/variables.js';
import { useIntl } from '@umijs/max';
import { Button, Form, Input, message, Select, Spin, Typography } from 'antd';
import React, { useEffect, useState } from 'react';
import { history } from 'umi';
const { Title } = Typography;

const { TextArea, Search } = Input;

interface ChildProps {
    handleBack: (value: any) => void;
    Detaillist: any;
    Fourthly_select_list: any;
    setFourthly_config_id: any;
    Fourthly_config_id: any;
    setDetaillist: any;
    Fourthlyref: any;
    Fourthly_abilities_list: any;
    Operationbentate: any;
    callwordlist: any;
    newagentid: any;
}
const AgentsFourthly: React.FC<ChildProps> = ({
    handleBack,
    Detaillist,
    setDetaillist,
    Fourthly_select_list,
    setFourthly_config_id,
    Fourthly_config_id,
    Fourthlyref,
    Fourthly_abilities_list,
    Operationbentate,
    callwordlist,
    newagentid,
}) => {
    const intl = useIntl();
    const [abilities_id, setabilities_id] = useState(0);
    const [Fourthly_prompt, setFourthly_prompt] = useState('');
    const [Fourthly_operation_data, setFourthly_operation_data] = useState('');
    const [loading, setLoading] = useState(false);

    const Editorrunchange = (value: any) => {
        const promptObj = {
            user: {
                value: serialize(value),
            },
        };
        setFourthly_prompt(new createPromptFromObject(promptObj));
    };

    const FourthlyChange = (e: any) => {
        const promptObj = {
            user: {
                value: e.target.value,
            },
        };
        setFourthly_prompt(new createPromptFromObject(promptObj));
    };

    const Fourthlyabilities = (value: any) => {
        setabilities_id(value);
    };

    const nextStep = (value: any) => {
        const typelist = value.users.filter((item: any, i: any) => {
            return item.type == 'number' && !Number(item.value) && !!item.value;
        });
        if (!Fourthly_prompt.user) {
            message.warning(intl.formatMessage({ id: 'agent.message.warning.callword' }));
        } else if (typelist.length > 0) {
            message.warning(intl.formatMessage({ id: 'agent.message.warning.datatype' }));
        } else {
            setLoading(true);
            const input_variables = new ObjectVariable('input', '', '');
            value.users.forEach((item: any) => {
                const variable = new AgentsVariable(
                    item.name,
                    item.type ? item.type : 'string',
                    item.type == 'string' ? item.value : Number(item.value),
                    item.content,
                    item.status,
                );
                input_variables.addProperty(item.name, variable);
            });
            const AgentRunData = {
                agent_id: newagentid ? newagentid : Detaillist.agent.agent_id,
                ability_id: abilities_id,
                input_dict: input_variables,
                prompt: Fourthly_prompt,
            };
            AgentRun(AgentRunData);
        }
    };

    const serialize = (nodes: any) => {
        return nodes
            .map((node: any) => {
                if (node.type === 'mention') {
                    return node.id;
                } else if (node.children) {
                    return serialize(node.children);
                } else {
                    return node.text;
                }
            })
            .join('');
    };

    const AgentRun = (data: any) => {
        PutagentRun(data)
            .then(res => {
                message.success(intl.formatMessage({ id: 'agent.message.success.runpublish' }));
                setFourthly_operation_data(res.data.outputs.text);
                setLoading(false);
            })
            .catch(err => {
                setLoading(false);
            });
    };

    const AgentPublish = async () => {
        const res = await PutagentPublish(newagentid ? newagentid : Detaillist.agent.agent_id);

        if (res.code == 0) {
            message.success('');
        } else {
            message.error('');
        }
    };

    const Goamend = async () => {
        history.push(`/Agents?app_id=${Detaillist.app.app_id}&type=false`);
        location.reload();
    };

    useEffect(() => {}, []);
    return (
        <div style={{ height: '100%' }}>
            <div className="text-base font-medium text-[#333333] my-[30px]">
                {intl.formatMessage({ id: 'agent.operationrun' })}
            </div>

            <div className="mb-[30px]">
                <div className="mb-[15px] text-[#555555] text-xs font-medium">
                    {intl.formatMessage({ id: 'agent.selectivepower' })}
                </div>
                <Select
                    placeholder={intl.formatMessage({ id: 'agent.pleaseselect' })}
                    defaultValue={intl.formatMessage({ id: 'agent.allability' })}
                    style={{ width: 390, fontSize: '12px', color: '#BBBBBB', fontWeight: '400' }}
                    onChange={Fourthlyabilities}
                    options={Fourthly_abilities_list}
                />
            </div>
            {/* <Input readOnly={true} /> */}
            <div>
                <Form
                    name="dynamic_form_nest_item"
                    onFinish={nextStep}
                    style={{ width: 900 }}
                    autoComplete="off"
                    form={Fourthlyref}
                >
                    <div className="mb-[15px] text-[#555555] text-xs font-medium">
                        {intl.formatMessage({ id: 'agent.inputvariable' })}
                    </div>
                    <Form.List name="users">
                        {(fields, {}) => (
                            <>
                                <div className="w-full flex justify-start items-center text-xs font-medium px-[10px] text-[#213044] h-12 bg-[#F7F7F7]  rounded-t-lg">
                                    <div className="w-48 mr-5 ml-2.5">
                                        {intl.formatMessage({ id: 'agent.variable.name' })}
                                    </div>
                                    <div className="w-52">
                                        {intl.formatMessage({ id: 'agent.variable.value' })}
                                    </div>
                                </div>
                                {/* last:rounded-b-lg */}
                                <div className="mb-[30px]">
                                    {fields.map(({ key, name, ...restField }) => (
                                        <div className="w-full h-20 flex justify-start  px-2.5 border-b border-x pt-7 last:rounded-b-lg">
                                            <Form.Item
                                                {...restField}
                                                name={[name, 'content']}
                                            >
                                                <Input
                                                    className="w-48 mr-5"
                                                    style={{
                                                        color: '#213044',
                                                        fontWeight: '400',
                                                        fontSize: '12px',
                                                    }}
                                                    variant="borderless"
                                                    disabled
                                                />
                                            </Form.Item>
                                            <Form.Item
                                                {...restField}
                                                name={[name, 'value']}
                                                rules={[
                                                    {
                                                        required:
                                                            Fourthlyref.getFieldsValue() &&
                                                            Fourthlyref.getFieldsValue().users[key]
                                                                .status == true
                                                                ? true
                                                                : false,
                                                        message: intl.formatMessage({
                                                            id: 'agent.rules.veriablevalue',
                                                        }),
                                                    },
                                                ]}
                                            >
                                                <Input
                                                    style={{ width: '660px' }}
                                                    placeholder={
                                                        Fourthlyref.getFieldsValue() &&
                                                        Fourthlyref.getFieldsValue().users[key]
                                                            .status == true
                                                            ? intl.formatMessage({
                                                                  id: 'agent.variable.required.value',
                                                              })
                                                            : intl.formatMessage({
                                                                  id: 'agent.variable.value',
                                                              })
                                                    }
                                                />
                                            </Form.Item>
                                        </div>
                                    ))}
                                </div>
                            </>
                        )}
                    </Form.List>
                    <Form.Item
                        rules={[
                            {
                                required: true,
                                message: intl.formatMessage({ id: 'agent.rules.callwordvalue' }),
                            },
                        ]}
                    >
                        <div className="mb-[15px] text-[#555555] text-xs font-medium">
                            {intl.formatMessage({ id: 'agent.runpreview' })}
                        </div>
                        <Spin spinning={loading}>
                            <div className="bg-[#F7F7F7] p-3.5 rounded-lg">
                                <div
                                    className="h-[345px] mb-[30px]" /*  style={{ minHeight: '402px' }} */
                                >
                                    {/* {Fourthly_operation_data} */}
                                    {Fourthly_operation_data ? (
                                        <CodeEditor
                                            language="python3"
                                            value={
                                                Fourthly_operation_data &&
                                                JSON.stringify(Fourthly_operation_data)
                                            }
                                        />
                                    ) : null}
                                </div>

                                <div
                                    className="agents-input p-2 bg-white border rounded-md my-2 flex items-center justify-between"
                                    style={{ border: '1px solid #EEE' }}
                                >
                                    <div className="w-full">
                                        <SlateEditor
                                            onChange={value => {
                                                Editorrunchange(value);
                                            }}
                                            options={callwordlist}
                                        ></SlateEditor>
                                    </div>
                                    <div className="w-8 h-8 bg-[#e8effc] rounded-md">
                                        <Button
                                            className="bg-[#e8effc]"
                                            icon={<img src="/icons/fs.svg" />}
                                            type="link"
                                            htmlType="submit"
                                            block
                                        ></Button>
                                    </div>
                                </div>
                            </div>
                        </Spin>
                    </Form.Item>
                </Form>
            </div>
            {/* </Spin> */}
            <div className="w-28">
                {Detaillist?.agent.publish_status === 1 && Detaillist?.is_creator === 1 ? (
                    <div>
                        <Button
                            type="primary"
                            htmlType="submit"
                            className="w-full"
                            onClick={Goamend}
                        >
                            {intl.formatMessage({ id: 'agent.amend' })}
                        </Button>
                    </div>
                ) : (
                    <div>
                        <Button
                            type="primary"
                            htmlType="submit"
                            className="w-full"
                            disabled={Operationbentate == 'false' ? false : true}
                            onClick={AgentPublish}
                        >
                            {intl.formatMessage({ id: 'agent.publish' })}
                        </Button>
                    </div>
                )}
            </div>
            <div className="h-[30px] w-1"></div>
        </div>
    );
};
export default AgentsFourthly;
