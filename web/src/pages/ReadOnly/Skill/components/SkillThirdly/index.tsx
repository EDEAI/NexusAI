import Callword from '@/components/callword';
import { ObjectVariable, Variable as SkillVariable } from '@/py2js/variables.js';
import { useIntl } from '@umijs/max';
import { Form, Input, Radio, Select } from 'antd';
import React, { useEffect, useState } from 'react';

//
const { TextArea, Search } = Input;

interface ChildProps {
    ThirdlyValue: (value: any) => void;
    handleBack: (value: any) => void; //
    Thirdlyref: any;
    Skillinfo: any;
    setSkillInfo: any;
    Operationbentate: any; //-true -false
}
const SkillThirdly: React.FC<ChildProps> = ({
    ThirdlyValue,
    Thirdlyref,
    handleBack,
    Skillinfo,
    setSkillInfo,
    Operationbentate,
}) => {
    const intl = useIntl();
    const [skillRun, setSkillRun] = useState<any>(null);
    const readed = {
        readOnly: true,
    };
    const disabled = {
        disabled: true,
    };
    useEffect(() => {}, []);

    const SkillRadioType = (e: any) => {
        setSkillInfo({ ...Skillinfo, output_type: e.target.value });
    };

    const ThirdlyChange = (value: any) => {
        const input_variables = new ObjectVariable('output', '', '');
        value.users.forEach((item: any) => {
            const variable = new SkillVariable(
                item.name,
                item.type ? item.type : 'string',
                '',
                item.content,
                false,
            );
            input_variables.addProperty(item.name, variable);
        });
        const data = {
            output_type: Skillinfo.output_type,
            output_variables: input_variables,
        };
        ThirdlyValue(data);
    };
    return (
        <div style={{ height: '100%' }}>
            <div className="flex align-center justify-between mt-[30px]">
                <div className="text-base font-medium mb-[30px] text-[#333333]">
                    {intl.formatMessage({ id: 'skill.menu.output' })}
                </div>
            </div>
            <Form
                name="dynamic_form_nest_item"
                onFinish={ThirdlyChange}
                style={{ width: 900 }}
                autoComplete="off"
                form={Thirdlyref}
            >
                <Form.List name="users">
                    {(fields, { add, remove }) => (
                        <>
                            <Form.Item
                                className="mb-[30px]"

                            >
                                <div className="text-[#555555] text-xs mb-[15px] font-medium">
                                    <Callword
                                        name={intl.formatMessage({ id: 'skill.outputvariable' })}
                                        title={intl.formatMessage({
                                            id: 'skill.Callword.outputvariable',
                                        })}
                                    />
                                </div>
                                <Radio.Group
                                    {...disabled}
                                    value={Skillinfo && Skillinfo.output_type}
                                >
                                    <Radio value={1}>
                                        <div className="text-[#555555] text-xs font-normal">
                                            {intl.formatMessage({ id: 'skill.radio.text' })}
                                        </div>
                                    </Radio>
                                    <Radio value={2}>
                                        <div className="text-[#555555] text-xs font-normal">
                                            {intl.formatMessage({ id: 'skill.radio.database' })}
                                        </div>
                                    </Radio>
                                    <Radio value={3}>
                                        <div className="text-[#555555] text-xs font-normal">
                                            {intl.formatMessage({ id: 'skill.radio.code' })}
                                        </div>
                                    </Radio>
                                    <Radio value={4}>
                                        <div className="text-[#555555] text-xs font-normal">
                                            {intl.formatMessage({ id: 'skill.radio.file' })}
                                        </div>
                                    </Radio>
                                </Radio.Group>
                            </Form.Item>
                            <div className="mb-[15px] text-[#555555] text-xs font-medium flex justify-between items-center">
                                <div>
                                    <Callword
                                        name={intl.formatMessage({ id: 'skill.outputv' })}
                                        title={intl.formatMessage({ id: 'skill.Callword.outputv' })}
                                    />
                                </div>
                            </div>
                            <div className="w-full flex justify-start items-center text-xs font-medium px-2.5 text-[#555555] h-12 bg-[#F7F7F7] rounded-t-lg">
                                <div className="w-[300px] mr-[60px] ml-2.5">
                                    {intl.formatMessage({ id: 'skill.variable.name' })}
                                </div>
                                <div className="w-[300px] mr-[50px]">
                                    {intl.formatMessage({ id: 'skill.variable.display' })}
                                </div>
                                <div className="">
                                    {intl.formatMessage({ id: 'skill.variable.type' })}
                                </div>
                            </div>
                            {Thirdlyref &&
                                Thirdlyref.getFieldValue('users') &&
                                Thirdlyref.getFieldValue('users').map(
                                    (item: any, index: number) => {
                                        return (
                                            <div className="w-full h-20 flex justify-start  px-2.5 border-b border-x pt-7 last:rounded-b-lg">
                                                <Form.Item className="m-0">
                                                    <Input
                                                        {...disabled}
                                                        placeholder={intl.formatMessage({
                                                            id: 'skill.variable.name',
                                                        })}
                                                        value={item.name}
                                                        className="w-[280px] mr-[80px]"
                                                    />
                                                </Form.Item>
                                                <Form.Item
                                                    className="m-0"
                                                    rules={[
                                                        {
                                                            required: true,
                                                            message: intl.formatMessage({
                                                                id: 'skill.rules.name',
                                                            }),
                                                        },
                                                    ]}
                                                >
                                                    <Input
                                                        {...disabled}
                                                        placeholder={intl.formatMessage({
                                                            id: 'skill.variable.display',
                                                        })}
                                                        value={item.content}
                                                        className="w-[270px] mr-[80px]"
                                                    />
                                                </Form.Item>
                                                <Form.Item className="w-36 mr-16 m-0">
                                                    <Select
                                                        {...disabled}
                                                        style={{ width: '150px' }}
                                                        value={item.type}
                                                        placeholder="Please select"
                                                        defaultValue={'string'}
                                                        options={[
                                                            { value: 'string', label: 'string' },
                                                            { value: 'number', label: 'number' },
                                                            { value: 'object', label: 'object' },
                                                            {
                                                                value: 'Array[string]',
                                                                label: 'Array[string]',
                                                            },
                                                            {
                                                                value: 'Array[number]',
                                                                label: 'Array[number]',
                                                            },
                                                            {
                                                                value: 'Array[object]',
                                                                label: 'Array[object]',
                                                            },
                                                        ]}
                                                    />
                                                </Form.Item>
                                            </div>
                                        );
                                    },
                                )}
                        </>
                    )}
                </Form.List>
            </Form>
        </div>
    );
};
export default SkillThirdly;
