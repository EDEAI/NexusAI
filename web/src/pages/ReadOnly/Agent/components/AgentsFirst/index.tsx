import { GetdatasetList } from '@/api/agents';
import Callword from '@/components/callword';
import Variable from '@/components/WorkFlow/components/Variable';
import { useIntl } from '@umijs/max';
import { Form, Input, Radio, Select, Switch } from 'antd';
import React, { useEffect, useState } from 'react';
import Avatar from '@/components/ChatAvatar';

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
        <div style={{ height: '100%', width: '100%', marginBottom: '30px' }}>
            <div className="flex align-center justify-between mt-[30px]">
                <div className="text-base font-medium mb-[30px] text-[#333333]">
                    {intl.formatMessage({ id: 'agent.menu.basicsetup' })}
                </div>
            </div>
            <div className="w-full">
                <Form
                    name="dynamic_form_nest_item"
                    style={{ width: '100%' }}
                    autoComplete="off"
                    form={Ffromref}
                >
                    {Detaillist && Detaillist.app.attrs_are_visible === 0 ? (
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
                                </>
                            )}
                        </Form.List>
                    ) : (
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
                                                    {...disabled}
                                                    size="small"
                                                    checked={
                                                        Detaillist &&
                                                        Detaillist.app.attrs_are_visible === 1
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
                                                        Detaillist &&
                                                        Detaillist.app.enable_api === 1
                                                            ? true
                                                            : false
                                                    }
                                                />
                                            </div>
                                            <div className="font-medium">
                                                <div className="mb-[15px] text-[#555555] text-xs">
                                                    {intl.formatMessage({
                                                        id: 'agent.filesupload',
                                                    })}
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
                                    {/* <div className="mb-[11px] text-xs font-bold flex justify-between items-center">
                                        <div className="text-[#555555] text-xs">
                                            <Callword
                                                className="font-medium"
                                                name={intl.formatMessage({
                                                    id: 'agent.inputvariable',
                                                })}
                                                title={intl.formatMessage({
                                                    id: 'agent.explain.inputvariable',
                                                })}
                                            />
                                        </div>
                                    </div> */}
                                    {Detaillist?.agent?.input_variables && (
                                        <div className="mb-[30px]">
                                            <Variable
                                                readonly
                                                title={
                                                    <div  className="text-[#555555] text-xs">
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
                                                    Detaillist?.agent?.input_variables
                                                        ?.properties || {},
                                                )}
                                            />
                                        </div>
                                    )}

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
                                                    Detaillist &&
                                                    Detaillist.agent.default_output_format
                                                }
                                                options={[
                                                    {
                                                        value: 1,
                                                        label: 'text',
                                                    },
                                                    {
                                                        value: 2,
                                                        label: 'json',
                                                    },
                                                    {
                                                        value: 3,
                                                        label: 'code',
                                                    },
                                                ]}
                                            ></Radio.Group>
                                        </div>
                                    </Form.Item>
                                </>
                            )}
                        </Form.List>
                    )}
                    
                    {Detaillist && Detaillist.app.attrs_are_visible === 1 && Detaillist.agent.selected_skills && (
                        <Form.Item className="mb-[30px]">
                            <div className='text-[#555555] text-base mb-[15px]'>
                                {intl.formatMessage({ id: 'agent.mcp.resources' })}
                            </div>
                            <div className='pl-4'>
                                {Detaillist.agent.selected_skills && Detaillist.agent.selected_skills.length > 0 && (
                                    <div className="mb-[30px]">
                                        <div className="flex items-center mb-[15px]">
                                            <div className="text-[#555555] text-xs">
                                                <Callword
                                                    className="font-medium"
                                                    name={intl.formatMessage({ id: 'agent.selectSkills' })}
                                                    title={intl.formatMessage({ id: 'agent.explain.selectSkills' })}
                                                />
                                            </div>
                                        </div>
                                        <div className="flex flex-col gap-4 mb-4">
                                            {Detaillist.agent.selected_skills.map((skill: any) => (
                                                <div key={skill.app_id} className="flex items-center w-full p-2 bg-white rounded-lg shadow-sm">
                                                    <Avatar
                                                        rounded="6px"
                                                        data={skill}
                                                        bg={skill.icon_background}
                                                    />
                                                    <div className="flex flex-col ml-2 truncate">
                                                        <span className="text-sm font-medium text-[#333333]">{skill.name}</span>
                                                        <span className="text-xs text-[#666666] truncate">{skill.description}</span>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {Detaillist.agent.selected_workflows && Detaillist.agent.selected_workflows.length > 0 && (
                                    <div className="mb-[30px]">
                                        <div className="flex items-center mb-[15px]">
                                            <div className="text-[#555555] text-xs">
                                                <Callword
                                                    className="font-medium"
                                                    name={intl.formatMessage({ id: 'agent.selectWorkflows' })}
                                                    title={intl.formatMessage({ id: 'agent.explain.selectWorkflows' })}
                                                />
                                            </div>
                                        </div>
                                        <div className="flex flex-col gap-4 mb-4">
                                            {Detaillist.agent.selected_workflows.map((workflow: any) => (
                                                <div key={workflow.app_id} className="flex items-center w-full p-2 bg-white rounded-lg shadow-sm">
                                                    <Avatar
                                                        rounded="6px"
                                                        data={workflow}
                                                        bg={workflow.icon_background}
                                                    />
                                                    <div className="flex flex-col ml-2 truncate">
                                                        <span className="text-sm font-medium text-[#333333]">{workflow.name}</span>
                                                        <span className="text-xs text-[#666666] truncate">{workflow.description}</span>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                {
                                    !Detaillist.agent.selected_skills && !Detaillist.agent.selected_workflows && (
                                        <div className="text-[#555555] text-xs">
                                            {intl.formatMessage({ id: 'agent.noResources' })}
                                        </div>
                                    )
                                }
                            </div>
                        </Form.Item>
                    )}
                    
                    <div className="h-[30px] w-1"></div>
                </Form>
            </div>
        </div>
    );
};
export default AgentsFirst;

