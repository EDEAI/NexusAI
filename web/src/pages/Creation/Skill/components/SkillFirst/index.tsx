import Callword from '@/components/callword';
import Variable from '@/components/WorkFlow/components/Variable';
import { ObjectVariable, Variable as SkillVariable } from '@/py2js/variables.js';
import { useIntl } from '@umijs/max';
import { Button, Form, Input, Switch } from 'antd';
import React, { useEffect } from 'react';

const { TextArea } = Input;
interface ChildProps {
    loading: boolean;
    FirstValue: (value: any) => void;
    FirstSkillref: any;
    Skillinfo: any;
    setSkillInfo: any;
    Operationbentate: any;
    pageKeyfun: any;
    skillmenudisabled: any;
    setskillmenudisabled: any;
    isCreate: boolean;
}
const SkillFirst: React.FC<ChildProps> = ({
    loading,
    FirstValue,
    FirstSkillref,
    Skillinfo,
    setSkillInfo,
    Operationbentate,
    pageKeyfun,
    skillmenudisabled,
    setskillmenudisabled,
    isCreate,
}) => {
    const intl = useIntl();

    const SkillFSwitch = (checked: any) => {
        setSkillInfo({ ...Skillinfo, is_public: checked ? 1 : 0 });
    };
    const attrFirstAPI = (checked: any) => {
        setSkillInfo({ ...Skillinfo, attrs_are_visible: checked ? 1 : 0 });
    };
    const handleVariableChange = (value: any) => {
        setSkillInfo({ ...Skillinfo, input_variables: value.free });
    };
    //
    const nextStep = (value: any, type: any) => {
        const input_variables = new ObjectVariable('output', '', '');
        value.users.forEach((item: any) => {
            const variable = new SkillVariable(
                item.name,
                item.type ? item.type : 'string',
                '',
                item.content,
                item.status,
            );
            input_variables.addProperty(item.name, variable);
        });
        const data = {
            input_variables: input_variables,
            is_public: Skillinfo.is_public,
            attrs_are_visible: Skillinfo.attrs_are_visible,
        };
        FirstValue(data);
    };

    // Save data and proceed to next step
    const updata = () => {
        FirstSkillref.validateFields()
            .then(value => {
                pageKeyfun('2');
                setskillmenudisabled({ ...skillmenudisabled, second: false });
            })
            .catch(err => {
                console.error('Form validation failed:', err);
            });
    };
    return (
        <div style={{ height: '100%', width: '100%' }}>
            <div className="flex align-center justify-between mt-[30px]">
                <div className="text-base font-medium mb-[30px] text-[#333333]">
                    {intl.formatMessage({ id: 'skill.inputsetting' })}
                </div>
            </div>

            <Form
                name="dynamic_form_nest_item"
                onFinish={value => {
                    FirstValue(value);
                }}
                style={{ width: '100%' }}
                autoComplete="off"
                form={FirstSkillref}
            >
                <Form.List name="users">
                    {(fields, { add, remove }) => (
                        <>
                            <Form.Item className="mb-[30px]">
                                <div className="text-[#555555] text-xs font-medium  mb-[15px]">
                                    {intl.formatMessage({ id: 'skill.appname' })}
                                </div>
                                <div className="text-[#555555] w-full my-2 p-[15px] flex text-xs  items-center bg-[#F7F7F7] rounded-lg">
                                    {Skillinfo && Skillinfo.name}&nbsp;
                                </div>
                            </Form.Item>
                            <Form.Item className="mb-[30px]">
                                <div className="text-[#555555] text-xs font-medium mb-[15px]">
                                    {intl.formatMessage({ id: 'skill.appdescription' })}
                                </div>
                                <div className="text-[#555555] w-full my-2 p-[15px] flex text-xs  items-center bg-[#F7F7F7] rounded-lg">
                                    {Skillinfo && Skillinfo.description}
                                </div>
                            </Form.Item>
                            <Form.Item className="mb-[30px]">
                                <div className="mb-[15px]">
                                    <Callword
                                        className="font-medium text-xs text-[#555555]"
                                        name={intl.formatMessage({ id: 'skill.teamvisibility' })}
                                        title={intl.formatMessage({ id: 'skill.Callword.title' })}
                                    />
                                </div>
                                <Switch
                                    size="small"
                                    onChange={SkillFSwitch}
                                    checked={Skillinfo && Skillinfo.is_public == 1 ? true : false}
                                />
                            </Form.Item>
                            <Form.Item className="mb-[30px]">
                                <div className="mb-[15px] text-[#555555] text-xs">
                                    <Callword
                                        className="font-medium"
                                        name={intl.formatMessage({
                                            id: 'agent.attrVisible',
                                        })}
                                        title={intl.formatMessage({
                                            id: 'skill.explain.attrVisible',
                                        })}
                                    />
                                </div>
                                <Switch
                                    size="small"
                                    onChange={attrFirstAPI}
                                    checked={
                                        Skillinfo && Skillinfo.attrs_are_visible == 1 ? true : false
                                    }
                                />
                            </Form.Item>

                            {!loading && (
                                <div className="mb-[30px]">
                                    <Variable
                                        title={
                                            <div className="text-[#555555] text-xs">
                                                <Callword
                                                    className="font-medium"
                                                    required={true}
                                                    name={intl.formatMessage({
                                                        id: 'skill.inputvariable',
                                                    })}
                                                    title={intl.formatMessage({
                                                        id: 'skill.Callword.inputvariable',
                                                    })}
                                                />
                                            </div>
                                        }
                                        variableTypes={['string', 'number', 'json', 'file']}
                                        variables={Object.values(
                                            Skillinfo?.input_variables?.properties || {},
                                        )}
                                        onChange={handleVariableChange}
                                    />
                                </div>
                            )}

                            {/* <div className="w-full flex justify-start items-center text-xs font-medium px-2.5 text-[#555555] h-12 bg-[#F7F7F7] rounded-t-lg">
                                <div className="w-48 mr-5 ml-[10px]">
                                    {intl.formatMessage({ id: 'skill.variable.name' })}
                                </div>
                                <div className="w-52 mr-5">
                                    {intl.formatMessage({ id: 'skill.variable.display' })}
                                </div>
                                <div className="w-36 mr-[100px]">
                                    {intl.formatMessage({ id: 'skill.variable.type' })}
                                </div>
                                <div className="w-14 mr-[90px]">
                                    {intl.formatMessage({ id: 'skill.variable.required' })}
                                </div>
                                <div>{intl.formatMessage({ id: 'skill.variable.operation' })}</div>
                            </div>
                            <div>
                                {fields.map(({ key, name, ...restField }) => (
                                
                                    <div
                                        className="w-full h-20 flex justify-start  px-2.5 border-b border-x pt-7 last:rounded-b-lg"
                                        key={key}
                                    >
                                        <Form.Item
                                            className="m-0"
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
                                        >
                                            <Input
                                                placeholder={intl.formatMessage({
                                                    id: 'skill.variable.name',
                                                })}
                                                className="w-48 mr-5"
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
                                                        id: 'skill.rules.displayname',
                                                    }),
                                                },
                                            ]}
                                        >
                                            <Input
                                                placeholder={intl.formatMessage({
                                                    id: 'skill.variable.display',
                                                })}
                                                className="w-52 mr-5"
                                            />
                                        </Form.Item>
                                        <Form.Item
                                            className="w-36 mr-[110px] m-0"
                                            {...restField}
                                            name={[name, 'type']}
                                        >
                                            <Select
                                              
                                                defaultValue={'string'}
                                                options={[
                                                    { value: 'string', label: 'String' },
                                                    { value: 'number', label: 'Number' },
                                                    { value: 'json', label: 'Object' },
                                                ]}
                                            />
                                        </Form.Item>
                                        <Form.Item
                                            className="w-12 mr-[100px] m-0"
                                            {...restField}
                                            name={[name, 'status']}
                                          
                                        >
                                            <Switch size="small" />
                                        </Form.Item>
                                        <Form.Item>
                                            {FirstSkillref &&
                                            FirstSkillref.getFieldsValue().users.length > 1 ? (
                                                <DeleteOutlined onClick={() => remove(name)} />
                                            ) : null}
                                        </Form.Item>
                                    </div>
                              
                                ))}
                            </div> */}
                        </>
                    )}
                </Form.List>
                <div className="mt-[20px]">
                    <Button
                        type="primary"
                        className="mr-[20px]"
                        onClick={() => {
                            updata();
                        }}
                    >
                        {intl.formatMessage({ id: 'skill.btn.nextstep' })}
                    </Button>
                    {/* <Button
                        onClick={() => {
                            history.back();
                        }}
                    >
                        {intl.formatMessage({ id: 'skill.btn.back' })}
                    </Button> */}
                </div>
                <div className="h-[30px] w-1"></div>
            </Form>
        </div>
    );
};
export default SkillFirst;
