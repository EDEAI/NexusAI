import { PutagentOutputset } from '@/api/agents';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { Button, Form, Input, Radio, Select, Space, message } from 'antd';
import React, { useEffect, useState } from 'react';
const { TextArea } = Input;

interface ChildProps {
    handleBack: (value: any) => void;
    Detaillist: any;
    setDetaillist: any;
    agent_select_list: any;
    setAgent_select_list: any;
    agent_select_list_old: any;
    Tformref: any;
    Operationbentate: any;
}
const AgentsThirdly: React.FC<ChildProps> = ({
    handleBack,
    Detaillist,
    setDetaillist,
    agent_select_list,
    setAgent_select_list,
    agent_select_list_old,
    Tformref,
    Operationbentate,
}) => {
    const [default_output_format, setDefault_output_format] = useState(null);
    const [agnet_select_show, setAgent_select_show] = useState<any>();
    useEffect(() => {}, []);

    const nextStep = (values: any) => {
        const params = {
            default_output_format: Detaillist && Detaillist.agent.default_output_format,
            abilities_output_format_data: values.users,
            agent_id: Detaillist.agent.agent_id,
        };

        if (Operationbentate == 'false') {
            agentOutputSet(params);
        }
        handleBack(3);
    };

    const agentOutputSet = async (values: any) => {
        const res = await PutagentOutputset(values);
        if (res.code == 0) {
            message.success('');
        } else {
            message.warning('');
        }
    };

    const overallRadiochange = (e: any) => {
        setDefault_output_format(e.target.value);
        setDetaillist({
            ...Detaillist,
            agent: { ...Detaillist.agent, default_output_format: e.target.value },
        });
    };

    const newdata = () => {
        const abilityIds = new Set(
            Tformref.getFieldsValue().users.map(ability => ability && ability.agent_ability_id),
        );
        const differentValues = agent_select_list_old.filter(value => !abilityIds.has(value.value));
        setTimeout(() => {
            setAgent_select_list(differentValues);
        }, 100);
    };

    return (
        <div className="m-4" style={{ height: '100%', width: '800px', marginLeft: '30px' }}>
            <div className="text-3xl mb-8"></div>
            <div className="flex justify-end items-center mb-8">
                <span className="text-base mr-6"></span>
                <Radio.Group
                    value={Detaillist && Detaillist.agent.default_output_format}
                    onChange={e => {
                        overallRadiochange(e);
                    }}
                >
                    <Radio value={1}>text</Radio>
                    <Radio value={2}>json</Radio>
                    <Radio value={3}>code</Radio>
                </Radio.Group>
            </div>
            <div className="w-full my-2">
                <Form
                    name="dynamic_form_nest_item"
                    onFinish={nextStep}
                    style={{ maxWidth: 600 }}
                    autoComplete="off"
                    form={Tformref}
                    onFieldsChange={newdata}
                >
                    <Form.List name="users">
                        {(fields, { add, remove }) => (
                            <>
                                {fields.map(({ key, name, ...restField }) => (
                                    <Space
                                        key={key}
                                        style={{
                                            display: 'flex',
                                            marginBottom: 8,
                                            flexWrap: 'wrap',
                                        }}
                                        align="baseline"
                                    >
                                        <Form.Item
                                            {...restField}
                                            name={[name, 'agent_ability_id']}
                                            rules={[{ required: true, message: '' }]}
                                        >
                                            <Select
                                                placeholder=""
                                                // defaultValue="jack"
                                                style={{ width: 280 }}
                                                options={agent_select_list}
                                            />
                                        </Form.Item>
                                        <Form.Item
                                            className="w-full my-2"
                                            {...restField}
                                            name={[name, 'output_format']}
                                            rules={[
                                                { required: true, message: 'Missing first name' },
                                            ]}
                                        >
                                            <Radio.Group defaultValue={1}>
                                                <Radio value={1}>text string</Radio>
                                                <Radio value={2}>format json</Radio>
                                                <Radio value={3}>code</Radio>
                                            </Radio.Group>
                                        </Form.Item>
                                        <MinusCircleOutlined
                                            onClick={() => {
                                                remove(name);
                                            }}
                                        />
                                    </Space>
                                ))}
                                {Tformref.getFieldsValue().users &&
                                agent_select_list_old &&
                                Tformref.getFieldsValue().users.length <
                                    agent_select_list_old.length ? (
                                    <Form.Item>
                                        <Button
                                            type="dashed"
                                            onClick={() => {
                                                add();
                                            }}
                                            block
                                            icon={<PlusOutlined />}
                                        >

                                        </Button>
                                    </Form.Item>
                                ) : null}
                            </>
                        )}
                    </Form.List>
                    <div className="h-10 w-1"></div>
                </Form>
            </div>
        </div>
    );
};
export default AgentsThirdly;
