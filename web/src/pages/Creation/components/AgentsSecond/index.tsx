import Callword from '@/components/callword';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Button, Form, Input, message, Radio, Switch } from 'antd';
import React, { useEffect, useState } from 'react';
const { TextArea } = Input;

interface ChildProps {
    SecondValue: (value: any) => void;
    handleBack: (value: any) => void;
    Detaillist: any;
    setDetaillist: any;
    Sformref: any;
    Operationbentate: any; 
    pageKeyfun: any;
    secondjudgingcondition: any;
    SkillMenuClick: any;
    agentupdata: any;
}

const AgentsSecond: React.FC<ChildProps> = ({
    SecondValue,
    handleBack,
    Detaillist,
    setDetaillist,
    Sformref,
    Operationbentate,
    pageKeyfun,
    secondjudgingcondition,
    SkillMenuClick,
    agentupdata,
}) => {
   
    const intl = useIntl();
    const [messageApi, contextHolder] = message.useMessage();
    const [agentAbilities, setAgentAbilities] = useState({
        auto_match_ability: 0,
        agent_abilities: [
            {
                agent_ability_id: 0,
                name: 'string',
                content: 'string',
                status: 0,
            },
        ],
    });

    useEffect(() => {});
  

  
    const nextStep = (values: any) => {
        // const messagetype = values.users.filter((item: any) => item.status)
        if (
            values.users.length == 1 &&
            ((!values.users[0].content && values.users[0].name) ||
                (values.users[0].content && !values.users[0].name))
        ) {
            return message.warning(
                intl.formatMessage({ id: 'agent.message.warning.selectknowledgebase' }),
            );
        } else {
            const agent_abilities = values.users.map((item: any) => {
                return {
                    ...item,
                    status: item.status ? 1 : 2,
                    agent_ability_id: item.agent_ability_id ? item.agent_ability_id : 0,
                };
            });
            const params = {
                agent_id: Detaillist.agent.agent_id,
                // values.users.length == 1 && !values.users[0].content && !values.users[0].name
                data: {
                    auto_match_ability: Detaillist.agent.auto_match_ability,
                    agent_abilities:
                        values.users.length == 1 &&
                        !values.users[0].content &&
                        !values.users[0].name
                            ? []
                            : agent_abilities,
                },
            };
            if (Operationbentate == 'false') {
                AgentAbilitiesSet();
            }
            SecondValue({ ...agentAbilities });
        }
    };
  
    const AgentAbilitiesSet = async () => {
        if (secondjudgingcondition()) {
        } else {
            agentupdata();
        }
    };

   
    const AutoSwitch = (checked: boolean) => {
        setDetaillist({
            ...Detaillist,
            agent: { ...Detaillist.agent, auto_match_ability: checked ? 1 : 0 },
        });
    };
    return (
        <div style={{ height: '100%' }}>
            <div className="text-base font-medium text-[#333333] my-[30px]">
                {intl.formatMessage({ id: 'agent.Applicationcapabilitysetting' })}
            </div>
            <div className="mb-[30px]">
                <div className="mb-[15px] text-[#555555] text-xs font-medium">
                    <Callword
                        name={intl.formatMessage({ id: 'agent.automatch' })}
                        title={intl.formatMessage({ id: 'agent.explain.automatch' })}
                    />
                </div>
                <Switch
                    size="small"
                    checked={Detaillist && Detaillist.agent.auto_match_ability == 1 ? true : false}
                    onChange={AutoSwitch}
                />
            </div>
            <div className="w-full">
                <Form
                    name="dynamic_form_nest_item"
                    onFinish={nextStep}
                    style={{ width: 900 }}
                    // labelCol={{ span: 24 }}
                    // wrapperCol={{ span: 24 }}
                    autoComplete="off"
                    form={Sformref}
                >
                    <Form.List name="users">
                        {(fields, { add, remove }) => (
                            <>
                                <div className="w-full flex items-center justify-between mb-[11px]">
                                    <div className=" text-[#555555] text-xs font-medium">
                                        {intl.formatMessage({ id: 'agent.capability' })}
                                    </div>
                                    <div>
                                        <Button
                                            type="link"
                                            onClick={() => add()}
                                            block
                                            icon={<PlusOutlined />}
                                        >
                                            {intl.formatMessage({ id: 'agent.add' })}
                                        </Button>
                                    </div>
                                </div>
                                {fields.map(({ key, name, ...restField }) => (
                                    <div className="bg-[#F7F7F7] p-[15px] rounded-lg mb-[20px]">
                                        <Form.Item className="mb-0">
                                            <div className="w-full flex justify-between items-center mb-[15px]">
                                                <div className="text-[#555555] text-xs font-medium">
                                                    {intl.formatMessage({
                                                        id: 'agent.capabilityname',
                                                    })}
                                                </div>
                                                <div>
                                                    {' '}
                                                    <DeleteOutlined onClick={() => remove(name)} />
                                                </div>
                                            </div>
                                        </Form.Item>
                                        <Form.Item
                                            className="mb-[20px]"
                                            {...restField}
                                            name={[name, 'name']}
                                            rules={[
                                                {
                                                    required: fields.length !== 1,
                                                    message: intl.formatMessage({
                                                        id: 'agent.capabilityname',
                                                    }),
                                                },
                                            ]}
                                        >
                                            <Input
                                                placeholder={intl.formatMessage({
                                                    id: 'agent.capabilityname',
                                                })}
                                                className="w-full"
                                            />
                                        </Form.Item>
                                        {/* </Space> */}
                                        <div className="mb-[15px]">
                                            <Callword
                                                className="text-[#555555] text-xs font-medium"
                                                name={intl.formatMessage({
                                                    id: 'agent.capabilitydescription',
                                                })}
                                                title={intl.formatMessage({
                                                    id: 'agent.explain.capabilitydescription',
                                                })}
                                            />
                                        </div>
                                        <Form.Item
                                            className="w-full mb-[20px]"
                                            {...restField}
                                            name={[name, 'content']}
                                            rules={[
                                                {
                                                    required: fields.length !== 1,
                                                    message: intl.formatMessage({
                                                        id: 'agent.capabilitydescription',
                                                    }),
                                                },
                                            ]}
                                        >
                                            <TextArea
                                                placeholder={intl.formatMessage({
                                                    id: 'agent.capabilitydescription',
                                                })}
                                                autoSize={{ minRows: 3, maxRows: 10 }}
                                                className="w-full"
                                            />
                                        </Form.Item>
                                        <div className="text-[#555555] text-xs font-medium mb-[15px]">
                                            {intl.formatMessage({ id: 'agent.capabilitystatus' })}
                                        </div>
                                        <Form.Item
                                            className="mb-[20px]"
                                            {...restField}
                                            name={[name, 'status']}
                                            // label={''}
                                        >
                                            <Radio.Group
                                                optionType="button"
                                                buttonStyle="solid"
                                                defaultValue={true}
                                            >
                                                <Radio value={true}>
                                                    {intl.formatMessage({
                                                        id: 'agent.capabilitystatus.enable',
                                                    })}
                                                </Radio>
                                                <Radio value={false}>
                                                    {intl.formatMessage({
                                                        id: 'agent.capabilitystatus.disable',
                                                    })}
                                                </Radio>
                                            </Radio.Group>
                                        </Form.Item>
                                        <div className="text-[#555555] text-xs font-medium mb-[11px]">
                                            {intl.formatMessage({ id: 'agent.enableall' })}
                                        </div>
                                        <Form.Item className="mb-0" name={[name, 'output_format']}>
                                            <Radio.Group defaultValue={0}>
                                                <Radio value={0}>
                                                    <div className="text-[#555555] text-xs font-normal">
                                                        {intl.formatMessage({ id: 'agent.menu' })}
                                                    </div>
                                                </Radio>
                                                <Radio value={1}>
                                                    <div className="text-[#555555] text-xs font-normal">
                                                        text string
                                                    </div>
                                                </Radio>
                                                <Radio value={2}>
                                                    <div className="text-[#555555] text-xs font-normal">
                                                        format json
                                                    </div>
                                                </Radio>
                                                <Radio value={3}>
                                                    <div className="text-[#555555] text-xs font-normal">
                                                        code
                                                    </div>
                                                </Radio>
                                            </Radio.Group>
                                        </Form.Item>
                                    </div>
                                ))}
                            </>
                        )}
                    </Form.List>
                    <div>
                        <Button
                            type="primary"
                            className="mr-[20px]"
                            onClick={() => {
                                AgentAbilitiesSet();
                            }}
                        >
                            {intl.formatMessage({ id: 'agent.btn.savedebug' })}
                        </Button>
                        <Button
                            onClick={() => {
                                history.back();
                            }}
                        >
                            {intl.formatMessage({ id: 'agent.btn.back' })}
                        </Button>
                    </div>
                    <div className="h-[30px] w-1"></div>
                </Form>
            </div>
        </div>
    );
};
export default AgentsSecond;
