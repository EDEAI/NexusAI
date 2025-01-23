import Callword from '@/components/callword';
import { ObjectVariable, Variable as SkillVariable } from '@/py2js/variables.js';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Button, Form, Input, Radio, Select } from 'antd';
import React, { useEffect, useState } from 'react';

const { TextArea, Search } = Input;

interface ChildProps {
    ThirdlyValue: (value: any) => void;
    handleBack: (value: any) => void;
    Thirdlyref: any;
    Skillinfo: any;
    setSkillInfo: any;
    Operationbentate: any;
    firstjudgingcondition: any;
    pageKeyfun: any;
    skillmenudisabled: any;
    setskillmenudisabled: any;
    skillupdata: any;
}
const SkillThirdly: React.FC<ChildProps> = ({
    ThirdlyValue,
    Thirdlyref,
    handleBack,
    Skillinfo,
    setSkillInfo,
    Operationbentate,
    firstjudgingcondition,
    pageKeyfun,
    skillmenudisabled,
    setskillmenudisabled,
    skillupdata,
}) => {
    const intl = useIntl();
    const [skillRun, setSkillRun] = useState<any>(null);

    useEffect(() => {}, []);
    const SkillRadioType = (e: any) => {
        // setSkill_Radio_Type(e.target.value);
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
    //
    const updata = () => {
        if (firstjudgingcondition(Thirdlyref.getFieldsValue().users, 2)) {
        } else {
            Thirdlyref.validateFields()
                .then(value => {
                    skillupdata();
                })
                .catch(err => {
                });
            // pageKeyfun('4')
            // setskillmenudisabled({ ...skillmenudisabled, second: false, })
        }
    };

    return (
        <div style={{ height: '100%' }}>
            <div className="flex align-center justify-between mt-[30px]">
                <div className="text-base font-medium mb-[30px] text-[#333333]">
                    {' '}
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
                            <Form.Item className="mb-[30px]">
                                <div className="text-[#555555] text-xs mb-[15px] font-medium">
                                    <Callword
                                        name={intl.formatMessage({ id: 'skill.outputvariable' })}
                                        title={intl.formatMessage({
                                            id: 'skill.Callword.outputvariable',
                                        })}
                                    />
                                </div>
                                <Radio.Group
                                    onChange={SkillRadioType}
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
                            <div className="mb-[11px] text-[#555555] text-xs font-medium flex justify-between items-center">
                                <div>
                                    <Callword
                                        required={true}
                                        name={intl.formatMessage({ id: 'skill.outputv' })}
                                        title={intl.formatMessage({ id: 'skill.Callword.outputv' })}
                                    />
                                </div>
                                <div>
                                    <Button
                                        type="link"
                                        onClick={() => add()}
                                        block
                                        icon={<PlusOutlined />}
                                    >
                                        {intl.formatMessage({ id: 'skill.add' })}
                                    </Button>
                                </div>
                            </div>
                            <div className="w-full flex justify-start items-center text-xs font-medium px-2.5 text-[#555555] h-12 bg-[#F7F7F7] rounded-t-lg">
                                <div className="w-[290px] ml-2.5">
                                    {intl.formatMessage({ id: 'skill.variable.name' })}
                                </div>
                                <div className="w-[290px]">
                                    {intl.formatMessage({ id: 'skill.variable.display' })}
                                </div>
                                <div className="w-[240px]">
                                    {intl.formatMessage({ id: 'skill.variable.type' })}
                                </div>
                                <div className="">
                                    {intl.formatMessage({ id: 'skill.variable.operation' })}
                                </div>
                            </div>
                            {fields.map(({ key, name, ...restField }) => (
                                <div className="w-full h-20 flex justify-start  px-2.5 border-b border-x pt-7 last:rounded-b-lg">
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'name']}
                                        rules={[
                                            {
                                                required: true,
                                                message: intl.formatMessage({
                                                    id: 'skill.rules.name',
                                                }),
                                            },
                                            {
                                                pattern: /^[a-zA-Z0-9_]+$/,
                                                message: intl.formatMessage({
                                                    id: 'skill.rules.verifydescription',
                                                }),
                                            },
                                        ]}
                                        className="m-0"
                                    >
                                        <Input
                                            placeholder={intl.formatMessage({
                                                id: 'skill.variable.name',
                                            })}
                                            className="w-[270px] mr-[20px]"
                                        />
                                    </Form.Item>
                                    <Form.Item
                                        className="m-0"
                                        {...restField}
                                        name={[name, 'content']}
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
                                            placeholder={intl.formatMessage({
                                                id: 'skill.variable.display',
                                            })}
                                            className="w-[260px] mr-[20px]"
                                        />
                                    </Form.Item>
                                    <Form.Item
                                        // className='w-[290] m-0'
                                        {...restField}
                                        name={[name, 'type']}
                                    >
                                        <Select
                                            style={{ width: '150px', marginRight: '115px' }}
                                            placeholder="Please select"
                                            defaultValue={'string'}
                                            options={[
                                                { value: 'string', label: 'String' },
                                                { value: 'number', label: 'Number' },
                                                { value: 'json', label: 'Object' },
                                             
                                            ]}
                                        />
                                    </Form.Item>
                                    <Form.Item>
                                        {Thirdlyref &&
                                        Thirdlyref.getFieldsValue().users.length > 1 ? (
                                            <DeleteOutlined onClick={() => remove(name)} />
                                        ) : null}
                                    </Form.Item>
                                </div>
                            ))}
                        </>
                    )}
                </Form.List>
                <div>
                    <Button
                        type="primary"
                        className="mr-[20px] mt-[30px]"
                        onClick={() => {
                            updata();
                        }}
                    >
                        {' '}
                        {intl.formatMessage({ id: 'skill.btn.savedebug' })}
                    </Button>
                    <Button
                        onClick={() => {
                            history.back();
                        }}
                    >
                        {intl.formatMessage({ id: 'skill.btn.back' })}
                    </Button>
                </div>
                <div className="h-[30px] w-1"></div>
            </Form>
        </div>
    );
};
export default SkillThirdly;
