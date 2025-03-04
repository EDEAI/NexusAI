import Callword from '@/components/callword';
import { useIntl } from '@umijs/max';
import { Form, Input, Radio, Switch } from 'antd';
import React, { useEffect } from 'react';
const { TextArea } = Input;

interface ChildProps {
    Detaillist: any;
    Sformref: any;
}

const readed = {
    readOnly: true,
};
const disabled = {
    disabled: true,
};
const AgentsSecond: React.FC<ChildProps> = ({ Detaillist, Sformref }) => {
    const intl = useIntl();
 
    useEffect(() => {});
    return (
        <div style={{ height: '100%' ,width:'100%'}}>
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
                    {...disabled}
                    size="small"
                    checked={Detaillist && Detaillist.agent.auto_match_ability == 1 ? true : false}
                />
            </div>
            <div className="w-full">
                <Form
                    name="dynamic_form_nest_item"
                    style={{ width: '100%' }}
                    autoComplete="off"
                    form={Sformref}
                >
                    <div className="w-full flex items-center justify-between mb-[11px]">
                        <div className="text-[#555555] text-xs font-medium">
                            {intl.formatMessage({ id: 'agent.capability' })}
                        </div>
                    </div>
                    {Sformref &&
                        Sformref.getFieldValue('users') &&
                        Sformref.getFieldValue('users').map((item: any, index: number) => {
                            return (
                                <div className="bg-[#F7F7F7] p-[15px] rounded-lg mb-[20px]">
                                    <Form.Item className="mb-0">
                                        <div className="w-full flex justify-between items-center mb-[15px]">
                                            <div className="text-[#555555] text-xs font-medium">
                                                {intl.formatMessage({ id: 'agent.capabilityname' })}
                                            </div>
                                        </div>
                                    </Form.Item>
                                    <Form.Item className="mb-[20px]">
                                        <Input
                                            {...disabled}
                                            placeholder={intl.formatMessage({
                                                id: 'agent.capabilityname',
                                            })}
                                            value={item.name}
                                            className="w-full"
                                        />
                                    </Form.Item>
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
                                    <Form.Item className="w-full mb-[20px]">
                                        <TextArea
                                            value={item.content}
                                            {...disabled}
                                            placeholder={intl.formatMessage({
                                                id: 'agent.capabilitydescription',
                                            })}
                                            autoSize={{ minRows: 3, maxRows: 10 }}
                                            style={{ width: '100%' }}
                                        />
                                    </Form.Item>
                                    <div className="text-[#555555] text-xs font-medium mb-[15px]">
                                        {intl.formatMessage({ id: 'agent.capabilitystatus' })}
                                    </div>
                                    <Form.Item className="mb-[20px]">
                                        <Radio.Group
                                            value={item.status}
                                            optionType="button"
                                            buttonStyle="solid"
                                            {...disabled}
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
                                    <Form.Item className="mb-0">
                                        <Radio.Group
                                            defaultValue={0}
                                            value={item.output_format}
                                            {...disabled}
                                        >
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
                            );
                        })}

                    <div className="h-[30px] w-1"></div>
                </Form>
            </div>
        </div>
    );
};
export default AgentsSecond;
