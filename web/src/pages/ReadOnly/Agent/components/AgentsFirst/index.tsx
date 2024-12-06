import { GetdatasetList } from '@/api/agents';
import Callword from '@/components/callword';
import { useIntl } from '@umijs/max';
import { Form, Input, Radio, Select, Switch } from 'antd';
import React, { useEffect, useState } from 'react';

const { TextArea } = Input;
interface ChildProps {
    Detaillist: any;
    repository: any;
    Operationbentate: any;
    Ffromref: any;
    Fourthly_config_id: any;
    Fourthly_select_list: any;
}
const AgentsFirst: React.FC<ChildProps> = ({
    Detaillist,
    repository,
    Operationbentate,
    Ffromref,
    Fourthly_config_id,
    Fourthly_select_list,
}) => {
    const intl = useIntl();
    const [dataset, setDataset] = useState([]);
    useEffect(() => {
        getDataset();
    }, []);

    const getDataset = async () => {
        const res = await GetdatasetList();
        setDataset(
            res.data.data.map((item: any) => {
                return { value: item.dataset_id, label: item.name };
            }),
        );
    };
    const readed = {
        readOnly: true,
    };
    const disabled = {
        disabled: true,
    };
    return (
        <div style={{ height: '100%', width: '900px', marginBottom: '30px' }}>
            <div className="flex align-center justify-between mt-[30px]">
                <div className="text-base font-medium mb-[30px] text-[#333333]">
                    {intl.formatMessage({ id: 'agent.menu.basicsetup' })}
                </div>
            </div>
            <div className="w-full">
                <Form
                    name="dynamic_form_nest_item"
                    style={{ width: 900 }}
                    autoComplete="off"
                    form={Ffromref}
                >
                    <Form.List name="users">
                        {(fields, { add, remove }) => (
                            <>
                                <Form.Item className="mb-[30px]">
                                    <div className="text-[#555555] text-xs">
                                        <div className="font-medium  mb-[15px]">
                                            {intl.formatMessage({ id: 'agent.appname' })}
                                        </div>
                                        <div className="w-full p-3.5 flex font-normal items-center bg-[#F7F7F7] rounded-lg">
                                            <div>
                                                {Detaillist &&
                                                    Detaillist.app &&
                                                    Detaillist.app.name}
                                                &nbsp;
                                            </div>
                                            <div className="">
                                                {Operationbentate === 'true'
                                                    ? intl.formatMessage({
                                                          id: 'agent.cannotmodify',
                                                      })
                                                    : ''}
                                            </div>
                                        </div>
                                    </div>
                                </Form.Item>
                                <Form.Item className="mb-[30px]">
                                    <div className="text-[#555555] text-xs">
                                        <div className="font-medium  mb-[15px]">
                                            {intl.formatMessage({ id: 'agent.appdescription' })}
                                        </div>
                                        <div className="w-full p-3.5 flex font-normal items-center bg-[#F7F7F7] rounded-lg">
                                            {Detaillist &&
                                                Detaillist.app &&
                                                Detaillist.app.description}
                                        </div>
                                    </div>
                                </Form.Item>
                                <Form.Item className="mb-[30px]">
                                    <div>
                                        <div className="mb-[30px]">
                                            <div className="mb-[15px] text-[#555555] text-xs">
                                                <Callword
                                                    className="font-medium"
                                                    name={intl.formatMessage({
                                                        id: 'agent.teamvisibility',
                                                    })}
                                                    title={intl.formatMessage({
                                                        id: 'agent.explain.teamvisibility',
                                                    })}
                                                />
                                            </div>
                                            <Switch
                                                {...disabled}
                                                size="small"
                                                checked={
                                                    Detaillist && Detaillist.app.is_public === 1
                                                        ? true
                                                        : false
                                                }
                                            />
                                        </div>
                                        <div className="mb-[30px]  font-medium">
                                            <div className="mb-[15px] text-[#555555] text-xs">
                                                {intl.formatMessage({ id: 'agent.APIswitch' })}
                                            </div>
                                            <Switch
                                                {...disabled}
                                                size="small"
                                                checked={
                                                    Detaillist && Detaillist.app.enable_api === 1
                                                        ? true
                                                        : false
                                                }
                                            />
                                        </div>
                                        <div className="font-medium">
                                            <div className="mb-[15px] text-[#555555] text-xs">
                                                {intl.formatMessage({ id: 'agent.filesupload' })}
                                            </div>
                                            <Switch
                                                {...disabled}
                                                size="small"
                                                checked={
                                                    Detaillist &&
                                                    Detaillist.agent.allow_upload_file == 1
                                                        ? true
                                                        : false
                                                }
                                            />
                                        </div>
                                    </div>
                                </Form.Item>
                                <Form.Item className="mb-[30px]">
                                    <div>
                                        <div className="mb-[15px] text-[#555555] text-xs font-medium">
                                            {intl.formatMessage({ id: 'agent.LLMmodel' })}
                                        </div>
                                        <Select
                                            {...disabled}
                                            aria-readonly="true"
                                            style={{ width: 270 }}
                                            variant="filled"
                                            value={Fourthly_config_id}
                                            options={Fourthly_select_list}
                                        />
                                    </div>
                                </Form.Item>
                                <Form.Item className="mb-[30px]" name={'obligations'}>
                                    <div className="w-full">
                                        <div className="mb-[15px] text-[#555555] text-xs">
                                            <Callword
                                                name={intl.formatMessage({
                                                    id: 'agent.functiondescription',
                                                })}
                                                title={intl.formatMessage({
                                                    id: 'agent.explain.function',
                                                })}
                                            />
                                        </div>
                                        <TextArea
                                            {...disabled}
                                            value={
                                                Detaillist &&
                                                Detaillist.agent &&
                                                Detaillist.agent.obligations
                                            }
                                            variant="filled"
                                            autoSize={{ minRows: 8, maxRows: 10 }}
                                        />
                                    </div>
                                </Form.Item>
                                <div className="mb-[11px] text-xs font-bold flex justify-between items-center">
                                    <div className="text-[#555555] text-xs">
                                        <Callword
                                            className="font-medium"
                                            name={intl.formatMessage({ id: 'agent.inputvariable' })}
                                            title={intl.formatMessage({
                                                id: 'agent.explain.inputvariable',
                                            })}
                                        />
                                    </div>
                                </div>
                                <div className="w-full flex justify-start items-center text-xs font-medium px-2.5 text-[#555555] h-12 bg-[#F7F7F7] rounded-t-lg">
                                    <div className="w-[300px] ml-[10px]">
                                        {intl.formatMessage({ id: 'agent.variable.name' })}
                                    </div>
                                    <div className="w-[300px]">
                                        {intl.formatMessage({ id: 'agent.variable.display' })}
                                    </div>
                                    <div className="w-[230px]">
                                        {intl.formatMessage({ id: 'agent.variable.type' })}
                                    </div>
                                    <div className="w-[70px]">
                                        {intl.formatMessage({ id: 'agent.variable.required' })}
                                    </div>
                                </div>
                                <div className="mb-[30px]">
                                    {Ffromref &&
                                        Ffromref.getFieldValue('users') &&
                                        Ffromref.getFieldValue('users').map(
                                            (item: any, index: number) => {
                                                return (
                                                    <div className="w-full h-20 flex justify-start  px-2.5 border-b border-x pt-7 last:rounded-b-lg">
                                                        <Form.Item className="m-0">
                                                            <Input
                                                                value={item.name}
                                                                {...disabled}
                                                                placeholder={intl.formatMessage({
                                                                    id: 'agent.variable.name',
                                                                })}
                                                                className="w-[280px] mr-[20px]"
                                                            />
                                                        </Form.Item>
                                                        <Form.Item className="m-0">
                                                            <Input
                                                                value={item.content}
                                                                {...disabled}
                                                                placeholder={intl.formatMessage({
                                                                    id: 'agent.variable.display',
                                                                })}
                                                                className="w-[270px] mr-[20px]"
                                                            />
                                                        </Form.Item>
                                                        <Form.Item className="mr-[80px] m-0">
                                                            <Select
                                                                {...disabled}
                                                                style={{ width: '150px' }}
                                                                value={item.type}
                                                                defaultValue={'string'}
                                                                options={[
                                                                    {
                                                                        value: 'string',
                                                                        label: 'string',
                                                                    },
                                                                    {
                                                                        value: 'number',
                                                                        label: 'number',
                                                                    },
                                                                ]}
                                                            />
                                                        </Form.Item>
                                                        <Form.Item className="w-12 mr-14 m-0 ">
                                                            <Switch
                                                                checked={item.status}
                                                                {...disabled}
                                                                size="small"
                                                            />
                                                        </Form.Item>
                                                    </div>
                                                );
                                            },
                                        )}
                                </div>
                                <Form.Item className="mb-[30px]">
                                    <div className="text-[#555555] text-xs mb-[15px]">
                                        <Callword
                                            className="font-medium"
                                            name={intl.formatMessage({
                                                id: 'agent.associatedknowledgebase',
                                            })}
                                            title={intl.formatMessage({
                                                id: 'agent.explain.associatedknowledgebase',
                                            })}
                                        />
                                    </div>
                                    <Select
                                        {...disabled}
                                        size="large"
                                        mode="tags"
                                        style={{ width: '100%' }}
                                        placeholder={intl.formatMessage({
                                            id: 'agent.pleaseselect',
                                        })}
                                        value={repository}
                                        variant="filled"
                                        options={dataset}
                                    />
                                </Form.Item>
                                <Form.Item className="mb-[30px]">
                                    <div className="">
                                        <div className="text-[#555555] text-xs mb-[15px]">
                                            {' '}
                                            {intl.formatMessage({
                                                id: 'agent.defaultoutputformat',
                                            })}
                                        </div>
                                        <Radio.Group
                                            {...disabled}
                                            value={
                                                Detaillist && Detaillist.agent.default_output_format
                                            }
                                        >
                                            <Radio value={1}>
                                                <div className="text-[#555555] text-xs font-normal">
                                                    text
                                                </div>
                                            </Radio>
                                            <Radio value={2}>
                                                <div className="text-[#555555] text-xs font-normal">
                                                    json
                                                </div>
                                            </Radio>
                                            <Radio value={3}>
                                                <div className="text-[#555555] text-xs font-normal">
                                                    code
                                                </div>
                                            </Radio>
                                        </Radio.Group>
                                    </div>
                                </Form.Item>
                            </>
                        )}
                    </Form.List>
                    <div className="h-[30px] w-1"></div>
                </Form>
            </div>
        </div>
    );
};
export default AgentsFirst;
