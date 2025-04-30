import { GetdatasetList } from '@/api/agents';
import Callword from '@/components/callword';
import { findOption } from '@/components/WorkFlow/components/Form/Select';
import Variable from '@/components/WorkFlow/components/Variable';
import { useModelSelect } from '@/store/modelList';
import { useIntl } from '@umijs/max';
import { Button, Form, Input, Radio, Select, Switch, Tag } from 'antd';
import React, { useEffect, useState } from 'react';

const { TextArea } = Input;
interface ChildProps {
    FirstValue: (value: any) => void;
    Detaillist: any;
    setDetaillist: any;
    repository: any;
    setRepository: any;
    Newproperties: any;
    setNewproperties: any;
    Operationbentate: any;
    Ffromref: any;
    setFourthly_config_id: any;
    Fourthly_config_id: any;
    Fourthly_select_list: any;
    pageKeyfun: any;
    firstjudgingcondition: any;
    setAgentmunudisabled: any;
    agentmenudisabled: any;
    loading: boolean;
}

const AgentsFirst: React.FC<ChildProps> = ({
    loading,
    FirstValue,
    Detaillist,
    setDetaillist,
    repository,
    setRepository,
    Operationbentate,
    Ffromref,
    setFourthly_config_id,
    Fourthly_config_id,
    Fourthly_select_list,
    Newproperties,
    setNewproperties,
    pageKeyfun,
    firstjudgingcondition,
    setAgentmunudisabled,
    agentmenudisabled,
}) => {
    const intl = useIntl();
    const [dataset, setDataset] = useState([]);
    const [AgentsFirstData, setAgentsFirstData] = useState({
        agent_id: 0,
        data: {
            is_public: 1,
            enable_api: 0,
            obligations: null,
            input_variables: {},
            dataset_ids: [],
            attrs_are_visible: 1,
        },
    });
    useEffect(() => {
        getDataset();
    }, []);

    const FourthlySelect = (value: any) => {
        setFourthly_config_id(value);
        // setDetaillist({ ...Detaillist, agent: { ...Detaillist.agent, m_config_id: value } })
    };

    const obligations = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        // Detaillist.agent.obligations = e.target.value
        setAgentsFirstData({
            ...AgentsFirstData,
            data: { ...AgentsFirstData.data, obligations: e.target.value },
        });
        setDetaillist({
            ...Detaillist,
            agent: { ...Detaillist.agent, obligations: e.target.value },
        });
    };

    const hasDuplicateField = (array: any[], field: string) => {
        const uniqueValues = new Set();
        return array.some(item => {
            const value = item[field];
            return uniqueValues.has(value)
                ? uniqueValues.add(value)
                : uniqueValues.add(value) && false;
        });
    };

    const FirstTeam = (SwitchValue: boolean) => {
        setDetaillist({
            ...Detaillist,
            app: { ...Detaillist.app, is_public: SwitchValue ? 1 : 0 },
        });
        setAgentsFirstData({
            ...AgentsFirstData,
            data: { ...AgentsFirstData.data, is_public: SwitchValue ? 1 : 0 },
        });
    };

    const FirstAPI = (SwitchValue: boolean) => {
        setDetaillist({
            ...Detaillist,
            app: { ...Detaillist.app, enable_api: SwitchValue ? 1 : 0 },
        });
        setAgentsFirstData({
            ...AgentsFirstData,
            data: { ...AgentsFirstData.data, enable_api: SwitchValue ? 1 : 0 },
        });
    };
    const attrFirstAPI = SwitchValue => {
        setDetaillist({
            ...Detaillist,
            app: { ...Detaillist.app, attrs_are_visible: SwitchValue ? 1 : 0 },
        });
        setAgentsFirstData({
            ...AgentsFirstData,
            data: { ...AgentsFirstData.data, attrs_are_visible: SwitchValue ? 1 : 0 },
        });
    };

    const TPUpload = (checked: boolean) => {
        // AgentengineSet(null, checked ? 1 : 0)
        // setFourthly_config_id(checked ? 1 : 0)
        setDetaillist({
            ...Detaillist,
            agent: { ...Detaillist.agent, allow_upload_file: checked ? 1 : 0 },
        });
    };

    const handleChange = (value: any) => {
        setAgentsFirstData({
            ...AgentsFirstData,
            data: { ...AgentsFirstData.data, dataset_ids: value },
        });
        setRepository(value);
    };

    const getDataset = async () => {
        const res = await GetdatasetList();
        setDataset(
            res.data.data.map((item: any) => {
                return { value: item.dataset_id, label: item.name };
            }),
        );
    };

    const PutBaseUpdate = async () => {
        if (firstjudgingcondition()) {
        } else {
            pageKeyfun('2');
            setAgentmunudisabled({ ...agentmenudisabled, first: false, second: false });
        }
    };

    const overallRadiochange = (e: any) => {
        setDetaillist({
            ...Detaillist,
            agent: { ...Detaillist.agent, default_output_format: e.target.value },
        });
    };

    const handleVariableChange = (value: any) => {
        setDetaillist({
            ...Detaillist,
            agent: { ...Detaillist?.agent, input_variables: value.free },
        });
    };

    const { options, defaultValue } = useModelSelect();

    return (
        <div style={{ height: '100%', width: '100%', marginBottom: '30px' }}>
            <div className="flex align-center justify-between mt-[30px]">
                <div className="text-base font-medium mb-[30px] text-[#333333]">
                    {intl.formatMessage({ id: 'agent.menu.basicsetup' })}
                </div>
            </div>
            <div className="w-full">
                <Form
                    name="dynamic_form_nest_item"
                    // onFinish={nextStep}
                    style={{ width: '100%' }}
                    // labelCol={{ span: 24 }}
                    // wrapperCol={{ span: 24 }}
                    autoComplete="off"
                    form={Ffromref}
                >
                    <Form.Item className="mb-[30px]">
                        <div className="text-[#555555] text-xs">
                            <div className="font-medium  mb-[15px]">
                                {intl.formatMessage({ id: 'agent.appname' })}
                            </div>
                            <div className="w-full p-[15px] flex font-normal items-center bg-[#F7F7F7] rounded-lg">
                                <div>
                                    {Detaillist && Detaillist.app && Detaillist.app.name}
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
                            <div className="w-full p-[15px] flex font-normal items-center bg-[#F7F7F7] rounded-lg">
                                {Detaillist && Detaillist.app && Detaillist.app.description}
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
                                    size="small"
                                    onChange={FirstTeam}
                                    checked={
                                        Detaillist && Detaillist.app?.is_public === 1 ? true : false
                                    }
                                />
                            </div>
                            <div className="mb-[30px]  font-medium">
                                <div className="mb-[15px] text-[#555555] text-xs">
                                    <Callword
                                        className="font-medium"
                                        name={intl.formatMessage({
                                            id: 'agent.attrVisible',
                                        })}
                                        title={intl.formatMessage({
                                            id: 'agent.explain.attrVisible',
                                        })}
                                    />
                                </div>
                                <Switch
                                    size="small"
                                    onChange={attrFirstAPI}
                                    checked={Detaillist && Detaillist.app?.attrs_are_visible === 1}
                                />
                            </div>
                            <div className="mb-[30px]  font-medium">
                                <div className="mb-[15px] text-[#555555] text-xs">
                                    {intl.formatMessage({ id: 'agent.APIswitch' })}
                                </div>
                                <Switch
                                    size="small"
                                    onChange={FirstAPI}
                                    checked={Detaillist && Detaillist.app?.enable_api === 1}
                                    disabled={Detaillist?.app?.publish_status !== 1}
                                />
                            </div>
                            <div className="font-medium">
                                <div className="mb-[15px] text-[#555555] text-xs">
                                    {intl.formatMessage({ id: 'agent.filesupload' })}
                                </div>
                                <Switch
                                    size="small"
                                    onChange={TPUpload}
                                    checked={
                                        Detaillist && Detaillist.agent?.allow_upload_file == 1
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
                                <span className="text-[#E80000]">* </span>
                                {intl.formatMessage({ id: 'agent.LLMmodel' })}
                            </div>
                            <Select
                                placeholder={intl.formatMessage({
                                    id: 'agent.pleaseselect',
                                })}
                                // defaultValue="jack"
                                // style={{ width: 270 }}
                                value={
                                    Fourthly_config_id == 0
                                        ? intl.formatMessage({
                                              id: 'agent.pleaseselect',
                                          })
                                        : Fourthly_config_id
                                }
                                variant="filled"
                                onChange={FourthlySelect}
                                options={options}
                                optionRender={option => {
                                    return (
                                        <div title={JSON.stringify(option)}>
                                            {option.label}{' '}
                                            {option?.data?.support_image == 1 && (
                                                <Tag color="blue" className="text-xs">
                                                    {intl.formatMessage({
                                                        id: 'workflow.tag.imageUnderstanding',
                                                        defaultMessage: 'Image Understanding',
                                                    })}
                                                </Tag>
                                            )}
                                        </div>
                                    );
                                }}
                                labelRender={props => {
                                    return (
                                        <div>
                                            {props?.label}{' '}
                                            {findOption(props?.value, { options })?.support_image ==
                                                1 && (
                                                <Tag color="blue" className="text-xs">
                                                    {intl.formatMessage({
                                                        id: 'workflow.tag.imageUnderstanding',
                                                        defaultMessage: 'Image Understanding',
                                                    })}
                                                </Tag>
                                            )}
                                        </div>
                                    );
                                }}
                            />
                        </div>
                    </Form.Item>
                    <Form.Item className="mb-[30px]" name={'obligations'}>
                        <div className="w-full">
                            <div className="mb-[15px] text-[#555555] text-xs">
                                <Callword
                                    className="font-medium"
                                    required={true}
                                    name={intl.formatMessage({
                                        id: 'agent.functiondescription',
                                    })}
                                    title={intl.formatMessage({
                                        id: 'agent.explain.function',
                                    })}
                                />
                            </div>
                            <TextArea
                                onChange={obligations}
                                value={
                                    Detaillist && Detaillist.agent && Detaillist.agent.obligations
                                }
                                placeholder={`Agent${intl.formatMessage({
                                    id: 'agent.functiondescription',
                                })}`}
                                autoSize={{ minRows: 8, maxRows: 10 }}
                            />
                        </div>
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
                                                id: 'agent.inputvariable',
                                            })}
                                            title={intl.formatMessage({
                                                id: 'agent.explain.inputvariable',
                                            })}
                                        />
                                    </div>
                                }
                                variables={Object.values(
                                    Detaillist?.agent?.input_variables?.properties || {},
                                )}
                                onChange={handleVariableChange}
                            />
                        </div>
                    )}

                    {/* <div className="mb-[11px] text-xs font-bold flex justify-between items-center">
                        <div className="text-[#555555] text-xs">
                            <Callword
                                className="font-medium"
                                required={true}
                                name={intl.formatMessage({ id: 'agent.inputvariable' })}
                                title={intl.formatMessage({
                                    id: 'agent.explain.inputvariable',
                                })}
                            />
                        </div>
              
                    </div> */}

                    <Form.List name="users">
                        {(fields, { add, remove }) => (
                            <>
                                {/* <div className="w-full flex justify-start items-center text-xs font-medium px-2.5 text-[#555555] h-12 bg-[#F7F7F7] rounded-t-lg">
                                    <div className="w-[22%] mr-2 ml-[10px]">
                                        {intl.formatMessage({ id: 'agent.variable.name' })}
                                    </div>
                                    <div className="w-[25%] mr-2">
                                        {intl.formatMessage({ id: 'agent.variable.display' })}
                                    </div>
                                    <div className="w-[18%] mr-2">
                                        {intl.formatMessage({ id: 'agent.variable.type' })}
                                    </div>
                                    <div className="w-[15%] mr-2">
                                        {intl.formatMessage({ id: 'agent.variable.required' })}
                                    </div>
                                    <div className="w-[10%]">
                                        {intl.formatMessage({ id: 'agent.variable.operation' })}
                                    </div>
                                </div> */}
                                {/* <div className="mb-[30px]">
                                    {fields.map(({ key, name, ...restField }) => (
                                       
                                        <div className="w-full h-20 flex justify-start px-2.5 border-b border-x pt-7 last:rounded-b-lg">
                                            <Form.Item
                                                className="m-0 w-[22%] mr-2"
                                                {...restField}
                                                name={[name, 'name']}
                                                rules={[
                                                    {
                                                        required: true,
                                                        message: intl.formatMessage({
                                                            id: 'agent.rules.name',
                                                        }),
                                                    },
                                                    {
                                                        pattern: /^[a-zA-Z0-9_]+$/,
                                                        message: intl.formatMessage({
                                                            id: 'agent.rules.verifydescription',
                                                        }),
                                                    },
                                                ]}
                                            >
                                                <Input
                                                    placeholder={intl.formatMessage({
                                                        id: 'agent.variable.name',
                                                    })}
                                                    className="w-full"
                                                />
                                            </Form.Item>
                                            <Form.Item
                                                className="m-0 w-[25%] mr-2"
                                                {...restField}
                                                name={[name, 'content']}
                                                rules={[
                                                    {
                                                        required: true,
                                                        message: intl.formatMessage({
                                                            id: 'agent.rules.displayname',
                                                        }),
                                                    },
                                                ]}
                                            >
                                                <Input
                                                    placeholder={intl.formatMessage({
                                                        id: 'agent.variable.display',
                                                    })}
                                                    className="w-full"
                                                />
                                            </Form.Item>
                                            <Form.Item
                                                className="w-[18%] mr-2 m-0"
                                                {...restField}
                                                name={[name, 'type']}
                                            >
                                                <Select
                                                    defaultValue={'string'}
                                                    options={[
                                                        { value: 'string', label: 'string' },
                                                        { value: 'number', label: 'number' },
                                                    ]}
                                                />
                                            </Form.Item>
                                            <Form.Item
                                                className="w-[15%] mr-2 m-0 flex pl-[2%]"
                                                {...restField}
                                                name={[name, 'status']}
                                             
                                            >
                                                <Switch
                                                    size="small"
                                                 
                                                />
                                            </Form.Item>
                                            <Form.Item className="w-[10%] flex pl-[2%]">
                                                {Ffromref &&
                                                Ffromref.getFieldsValue().users.length > 1 ? (
                                                    <DeleteOutlined onClick={() => remove(name)} />
                                                ) : null}
                                            </Form.Item>
                                        </div>
                                      
                                    ))}
                                    <div
                                        onClick={() => add()}
                                        className="w-full p-2 mt-4  flex items-center gap-1 justify-center border  border-transparent  hover:border-dashed  hover:border-[#1B64F3] hover:text-[#1B64F3] cursor-pointer bg-[#F7F7F7] rounded-lg mb-4"
                                    >
                                        <PlusOutlined /> {intl.formatMessage({ id: 'agent.add' })}
                                    </div>
                                </div> */}

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
                                        size="large"
                                        mode="multiple"
                                        showSearch
                                        style={{ width: '100%',fontSize:'12px' }}
                                        placeholder={intl.formatMessage({
                                            id: 'agent.pleaseselect',
                                        })}
                                        
                                        value={repository}
                                        onChange={handleChange}
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
                                            value={
                                                Detaillist && Detaillist.agent.default_output_format
                                            }
                                            onChange={e => {
                                                overallRadiochange(e);
                                            }}
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
                    <div>
                        <Button
                            type="primary"
                            className="mr-[20px]"
                            onClick={() => {
                                PutBaseUpdate();
                            }}
                        >
                            {intl.formatMessage({ id: 'agent.btn.nextstep' })}
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
export default AgentsFirst;
