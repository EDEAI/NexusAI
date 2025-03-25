import Callword from '@/components/callword';
import Variable from '@/components/WorkFlow/components/Variable';
import { useIntl } from '@umijs/max';
import { Form, Input, Select, Switch } from 'antd';
import React, { useEffect } from 'react';

const { TextArea } = Input;
interface ChildProps {
    FirstValue: (value: any) => void;
    FirstSkillref: any;
    Skillinfo: any;
    setSkillInfo: any;
    Operationbentate: any;
}
const SkillFirst: React.FC<ChildProps> = ({
    FirstValue,
    FirstSkillref,
    Skillinfo,
    setSkillInfo,
    Operationbentate,
}) => {
    const intl = useIntl();
    useEffect(() => {}, []);
    const readed = {
        readOnly: true,
    };
    const disabled = {
        disabled: true,
    };
    return (
        <div style={{ height: '100%' }}>
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
                style={{ width: 900 }}
                autoComplete="off"
                form={FirstSkillref}
            >
                {Skillinfo && Skillinfo.attrs_are_visible == 0 ? (
                    <>
                        <Form.Item className="mb-[30px]">
                            <div className="text-[#555555] text-xs font-medium  mb-[15px]">
                                {intl.formatMessage({ id: 'skill.appname' })}
                            </div>
                            <div className="text-[#555555] w-full my-2 p-[15px] flex text-xs  items-center bg-[#F7F7F7] rounded-lg">
                                <div>{Skillinfo && Skillinfo.name}&nbsp;</div>
                                <div className="">
                                    {Operationbentate === 'true'
                                        ? intl.formatMessage({ id: 'skill.toast.waring' })
                                        : ''}
                                </div>
                            </div>
                        </Form.Item>
                        <Form.Item className="mb-[30px]">
                            <div className="text-[#555555] text-xs  mb-[15px]">
                                {intl.formatMessage({ id: 'skill.appdescription' })}
                            </div>
                            <div className="text-[#555555] w-full my-2 p-[15px] flex text-xs  items-center bg-[#F7F7F7] rounded-lg">
                                {Skillinfo && Skillinfo.description}
                            </div>
                        </Form.Item>
                    </>
                ) : (
                    <>
                        <Form.Item className="mb-[30px]">
                            <div className="text-[#555555] text-xs font-medium  mb-[15px]">
                                {intl.formatMessage({ id: 'skill.appname' })}
                            </div>
                            <div className="text-[#555555] w-full my-2 p-[15px] flex text-xs  items-center bg-[#F7F7F7] rounded-lg">
                                <div>{Skillinfo && Skillinfo.name}&nbsp;</div>
                                <div className="">
                                    {Operationbentate === 'true'
                                        ? intl.formatMessage({ id: 'skill.toast.waring' })
                                        : ''}
                                </div>
                            </div>
                        </Form.Item>
                        <Form.Item className="mb-[30px]">
                            <div className="text-[#555555] text-xs  mb-[15px]">
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
                                {...disabled}
                                size="small"
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
                                {...disabled}
                                size="small"
                                checked={
                                    Skillinfo && Skillinfo.attrs_are_visible == 1 ? true : false
                                }
                            />
                        </Form.Item>
                        {Skillinfo?.input_variables && (
                                <div className="mb-[30px]">
                                    <Variable
                                    readonly
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
                                        variableTypes={['string', 'number', 'json']}
                                        variables={Object.values(
                                            Skillinfo?.input_variables?.properties || {},
                                        )}
                                        // onChange={handleVariableChange}
                                    />
                                </div>
                            )}
                        {/* <div className="mb-[15px] text-xs font-bold flex justify-between items-center">
                            <div className="text-[#555555] text-xs font-medium">
                                <Callword
                                    name={intl.formatMessage({ id: 'skill.inputvariable' })}
                                    title={intl.formatMessage({
                                        id: 'skill.Callword.inputvariable',
                                    })}
                                />
                            </div>
                        </div> */}
                        {/* <div className="w-full flex justify-start items-center text-xs font-medium px-2.5 text-[#555555] h-12 bg-[#F7F7F7]  rounded-t-lg">
                            <div className="w-[300px] ml-2.5">
                                {intl.formatMessage({ id: 'skill.variable.name' })}
                            </div>
                            <div className="w-[300px]">
                                {intl.formatMessage({ id: 'skill.variable.display' })}
                            </div>
                            <div className="w-[230px]">
                                {intl.formatMessage({ id: 'skill.variable.type' })}
                            </div>
                            <div className="w-[70px]">
                                {intl.formatMessage({ id: 'skill.variable.required' })}
                            </div>
                        </div> */}
                        {/* <div>
                            {FirstSkillref &&
                                FirstSkillref.getFieldValue().users &&
                                FirstSkillref.getFieldValue().users.map(
                                    (item: any, index: number) => {
                                        return (
                                            <div
                                                className="w-full h-20 flex justify-start  px-2.5 border-b border-x pt-7 last:rounded-b-lg"
                                                key={index}
                                            >
                                                <Form.Item
                                                    className="m-0"
                                                    rules={[
                                                        { required: true, message: '' },
                                                        {
                                                            pattern: /^[a-zA-Z0-9_]+$/,
                                                            message: '',
                                                        },
                                                    ]}
                                                >
                                                    <Input
                                                        {...disabled}
                                                        value={item.name}
                                                        className="w-[280px] mr-[20px]"
                                                    />
                                                </Form.Item>
                                                <Form.Item
                                                    className="m-0"
                                                    rules={[{ required: true, message: '' }]}
                                                >
                                                    <Input
                                                        {...disabled}
                                                        value={item.content}
                                                        className="w-[270px] mr-[20px]"
                                                    />
                                                </Form.Item>
                                                <Form.Item className=" mr-[80px] m-0">
                                                    <Select
                                                        {...disabled}
                                                        style={{ width: '150px' }}
                                                        defaultValue={'string'}
                                                        value={item.type}
                                                        options={[
                                                            { value: 'string', label: 'String' },
                                                            { value: 'number', label: 'Number' },
                                                            { value: 'json', label: 'Object' },
                                                        ]}
                                                    />
                                                </Form.Item>
                                                <Form.Item className="w-12 mr-14 m-0">
                                                    <Switch
                                                        {...disabled}
                                                        size="small"
                                                        checked={item.status}
                                                    />
                                                </Form.Item>
                                            </div>
                                        );
                                    },
                                )}
                        </div> */}
                        <div className="h-[30px] w-1"></div>
                    </>
                )}
            </Form>
        </div>
    );
};
export default SkillFirst;
