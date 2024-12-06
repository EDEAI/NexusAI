import { PostskillRun, PutskillPublish } from '@/api/skill';
import CodeEditor from '@/components/WorkFlow/components/Editor/CodeEditor';
import { ObjectVariable, Variable as SkillVariable } from '@/py2js/variables.js';
import { useIntl } from '@umijs/max';
import { Button, Form, Input, message, Spin } from 'antd';
import React, { useEffect, useState } from 'react';
import { history } from 'umi';

const { TextArea, Search } = Input;

interface ChildProps {
    FourthlyValue: (value: any) => void;
    handleBack: (value: any) => void;
    Fourthlyref: any;
    Skillinfo: any;
    Operationbentate: any;
}
const skillFourthly: React.FC<ChildProps> = ({
    FourthlyValue,
    Fourthlyref,
    handleBack,
    Skillinfo,
    Operationbentate,
}) => {
    const intl = useIntl();
    const [skillRun, setSkillRun] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    useEffect(() => {}, []);

    const AgentPublish = async () => {
        const res = await PutskillPublish(Skillinfo.app_id);
        if (res.code == 0) {
            message.success(intl.formatMessage({ id: 'skill.publishsuccess' }));
        } else {
            message.error(intl.formatMessage({ id: 'skill.select.value' }));
        }
    };
    //
    const FourthlyChange = (value: any) => {
        const typelist = value.users.filter((item: any, i: any) => {
            return item.type == 'number' && !Number(item.value) && !!item.value;
        });
        if (typelist.length > 0) {
            message.warning(intl.formatMessage({ id: 'skill.message.warning.vlaue' }));
        } else {
            setLoading(true);
            const input_variables = new ObjectVariable('output', '', '');
            value.users.forEach((item: any) => {
                const variable = new SkillVariable(
                    item.name,
                    item.type,
                    item.type == 'string' ? item.value : Number(item.value),
                    item.content,
                    item.status,
                );
                input_variables.addProperty(item.name, variable);
            });
            const param = {
                skill_id: Skillinfo.id,
                input_dict: input_variables,
            };
            SkillRun(param);
        }
    };

    const SkillRun = async (param: any) => {
        PostskillRun(param)
            .then(res => {
                message.success(intl.formatMessage({ id: 'skill.run.success' }));
                setSkillRun(res.data.outputs);
                setLoading(false);
            })
            .catch(err => {
                setLoading(false);
            });
    };

    const Goamend = async () => {
        history.push(`/Skill?app_id=${Skillinfo?.app_id}&type=false`);
        location.reload();
    };

    return (
        <div style={{ height: '100%' }}>
            <div className="flex align-center justify-between mt-[30px]">
                <div className="text-base font-medium mb-[30px] text-[#333333]">
                    {intl.formatMessage({ id: 'skill.operationrun' })}
                </div>
            </div>
            <Form
                name="dynamic_form_nest_item"
                onFinish={FourthlyChange}
                style={{ width: 900 }}
                autoComplete="off"
                form={Fourthlyref}
            >
                <div className="text-[#555555] text-xs font-medium  mb-[15px]">
                    <div>{intl.formatMessage({ id: 'skill.inputvariable' })}</div>
                </div>
                <div className="w-full flex justify-start items-center text-xs font-medium px-[10px] text-[#213044] h-12 bg-[#F7F7F7]  rounded-t-lg">
                    <div className="w-48 mr-5 ml-2.5">
                        {intl.formatMessage({ id: 'skill.variable.name' })}
                    </div>
                    <div className="w-52 mr-5">
                        {intl.formatMessage({ id: 'skill.variable.display' })}
                    </div>
                </div>
                <Form.List name="users">
                    {(fields, {}) => (
                        <>
                            <div className="mb-[30px]">
                                {fields.map(({ key, name, ...restField }) => (
                                    <div className="w-full h-20 flex justify-start  px-2.5 border-b border-x pt-7 last:rounded-b-lg">
                                        <Form.Item {...restField} name={[name, 'content']}>
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
                                                        id: 'skill.message.variantcontent',
                                                    }),
                                                },
                                            ]}
                                        >
                                            <Input
                                                placeholder={
                                                    Fourthlyref.getFieldsValue() &&
                                                    Fourthlyref.getFieldsValue().users[key]
                                                        .status == true
                                                        ? intl.formatMessage({
                                                              id: 'skill.variantcontent.required',
                                                          })
                                                        : intl.formatMessage({
                                                              id: 'skill.variantcontent',
                                                          })
                                                }
                                                style={{ width: '660px' }}
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
                            message: intl.formatMessage({ id: 'skill.rules.callword' }),
                        },
                    ]}
                >
                    <div className="mb-[15px] text-[#555555] text-xs font-medium">
                        {intl.formatMessage({ id: 'skill.runpreview' })}
                    </div>
                    <Spin spinning={loading}>
                        <div className="bg-[#F7F7F7] p-3.5 rounded-lg">
                            <div
                                className="h-[345px] mb-[30px]" /* style={{ minHeight: '402px' }} */
                            >
                                {' '}
                                {/*  className='h-[345px]' */}
                                {/* {skillRun && JSON.stringify(skillRun)} */}
                                {/* <ReactMarkdown rehypePlugins={[rehypeHighlight]} >
                                    {skillRun && JSON.stringify(skillRun.result)}
                                </ReactMarkdown> */}
                                {skillRun ? (
                                    <CodeEditor
                                        language="python3"
                                        value={skillRun && JSON.stringify(skillRun)}
                                    />
                                ) : null}
                            </div>
                            <div className="w-full flex justify-end items-center">
                                <div className=" h-8 bg-[#e8effc] rounded-md">
                                    <Button
                                        className="bg-[#fff]"
                                        icon={<img src="/icons/fs.svg" />}
                                        type="link"
                                        htmlType="submit"
                                        block
                                    >
                                        {intl.formatMessage({ id: 'skill.run' })}
                                    </Button>
                                </div>
                            </div>
                            {/* <div className='w-28'>
                                <Button
                                    className='w-28'
                                    icon={<img src="/icons/fs.svg" />}
                                    type="primary"
                                    htmlType="submit">

                                </Button>
                            </div> */}
                        </div>
                    </Spin>
                </Form.Item>
                <div className="w-28">
                    {Skillinfo?.publish_status === 1 && Skillinfo?.is_creator === 1 ? (
                        <div>
                            <Button
                                type="primary"
                                htmlType="submit"
                                className="w-full"
                                onClick={Goamend}
                            >
                                {intl.formatMessage({ id: 'skill.amend' })}
                            </Button>
                        </div>
                    ) : (
                        <div>
                            <Button
                                type="primary"
                                htmlType="submit"
                                className="w-full"
                                onClick={AgentPublish}
                                disabled={Operationbentate == 'false' ? false : true}
                            >
                                {intl.formatMessage({ id: 'skill.publish' })}
                            </Button>
                        </div>
                    )}
                </div>
                <div className="h-[30px] w-1"></div>
            </Form>
        </div>
    );
};
export default skillFourthly;
