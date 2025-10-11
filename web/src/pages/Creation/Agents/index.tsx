import {
    GetagentInfo,
    PutagentAbilitiesset,
    PutagentBaseupdate,
    PutagentOutputset,
} from '@/api/agents';
import { PostappsCreate } from '@/api/creation';
import { BASE_URL } from '@/api/request';
import { CURRENT_NODE_ID } from '@/components/WorkFlow/config';
import { Variable as AgentsVariable, ObjectVariable } from '@/py2js/variables.js';
import { agentdefault, createappdata, createDefaultAgentInputVariables } from '@/utils/useUser';
import {
    ArrowLeftOutlined,
    CodeOutlined,
    DesktopOutlined,
    FileDoneOutlined,
    FileTextOutlined,
} from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import type { MenuProps } from 'antd';
import { Button, Form, Menu, message, Spin, Splitter } from 'antd';
import _ from 'lodash';
import React, { useEffect, useRef, useState } from 'react';
import { history } from 'umi';
import AgentsFirst from '../components/AgentsFirst';
import AgentsFourthly from '../components/AgentsFourthly';
import AgentsSecond from '../components/AgentsSecond';
import Chat from './Chat';
import Log from './Log';

type MenuItem = Required<MenuProps>['items'][number];

const Agents: React.FC = () => {
    const intl = useIntl();
    const childRef = useRef<any>(null);
    const [Ffromref] = Form.useForm();
    const [Tformref] = Form.useForm();
    const [Sformref] = Form.useForm();
    const [Fourthlyref] = Form.useForm();

    const [Detaillist, setDetaillist] = useState(null);
    const [Procedure, setProcedure] = useState(0);
    const [repository, setRepository] = useState(null);
    const [Newproperties, setNewproperties] = useState(null);
    const [agent_select_list, setAgent_select_list] = useState(null);
    const [agent_select_list_old, setAgent_select_list_old] = useState(null);
    const [Fourthly_select_list, setFourthly_select_list] = useState(null);
    const [Fourthly_config_id, setFourthly_config_id] = useState(null);
    const [AgentSpecial, setAgentSpecial] = useState(null);
    const [Fourthly_abilities_list, setFourthly_abilities_list] = useState(null);
    const [Operationbentate, setOperationbentate] = useState(null);
    const [pageKey, pageKeyfun] = useState<string>('1');
    const [callwordlist, setCallwordlist] = useState(null);
    const [fromdata, setFromdata] = useState(null);
    const [newagentid, setNewagentid] = useState(null);
    const [creationappid, setcreationappid] = useState(null);
    const [loading, setLoading] = useState(true);
    const [agentmenudisabled, setAgentmunudisabled] = useState({
        first: false,
        second: false,
        fourthly: false,
    });
    const items: MenuItem[] = [
        {
            key: '1',
            icon: <FileDoneOutlined />,
            label: intl.formatMessage({ id: 'agent.menu.basicsetup' }),
            disabled: agentmenudisabled.first,
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '500',
                lineHeight: '22px',
                color: pageKey == '1' ? '#1B64F3' : '#213044',
            },
        },
        {
            key: '2',
            disabled: agentmenudisabled.second,
            icon: <CodeOutlined />,
            label: intl.formatMessage({ id: 'agent.menu.Capacityoutput' }),
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                marginBottom: '10px',
                fontSize: '16px',
                lineHeight: '22px',
                fontWeight: '500',
                color: pageKey == '2' ? '#1B64F3' : '#213044',
            },
        },
        {
            key: '5',
            disabled: agentmenudisabled.fourthly,
            icon: <FileTextOutlined />,
            label: intl.formatMessage({ id: 'app.dashboard.run_log_agent' }),
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                marginBottom: '10px',
                fontSize: '16px',
                lineHeight: '22px',
                fontWeight: '500',
                color: pageKey == '5' ? '#1B64F3' : '#213044',
            },
        },
    ];
    const createDefaultInputVariables = () => {
        const defaultDisplayName = intl.formatMessage({
            id: 'agent.inputvariable.default.display',
        });
        const inputVariables = new ObjectVariable('input', '', '');
        const defaultVariable = new AgentsVariable(
            'default_var',
            'string',
            '',
            defaultDisplayName,
            true,
            48,
        );
        inputVariables.addProperty('default_var', defaultVariable);
        return inputVariables.toObject();
    };
    useEffect(() => {
        let params = new URLSearchParams(window.location.search);
        if (!params.get('app_id')) {
            setAgentmunudisabled({
                ...agentmenudisabled,
                first: false,
                second: true,
                fourthly: true,
            });
            setLoading(false);
        }
        getAgent();
    }, []);

    const getAgent = async (app_id?: any) => {
        let params = new URLSearchParams(window.location.search);
        if (!!params.get('from')) {
            setFromdata(params.get('from'));
        }
        let res = null;
        if (!!params.get('app_id') || !!app_id) {
            res = await GetagentInfo(app_id ? app_id : params.get('app_id'), params.get('type'));
            setcreationappid(res.data.app.app_id);
        } else {
            res = await agentdefault();
        }
        const data = res.data;
        if (
            !data.agent.input_variables ||
            _.isEmpty(data.agent.input_variables?.properties)
        ) {
            const defaultDisplayName = intl.formatMessage({
                id: 'agent.inputvariable.default.display',
            });
            data.agent.input_variables = createDefaultAgentInputVariables(
                defaultDisplayName,
            );
        }
        const repositoryID = res.data?.agent_dataset_relation_list?.map((item: any) => {
            return item.dataset_id;
        });
        setRepository(repositoryID);
        if (res.data.callable_items) {
            res.data.agent.selected_skills = [];
            res.data.agent.selected_workflows = [];
            res.data.callable_items.forEach((item: any) => {
                if (item.item_type == 1) {
                    res.data.agent.selected_skills.push({
                        ...item,
                        mode: 4,
                    });
                } else {
                    res.data.agent.selected_workflows.push({
                        ...item,
                        mode: 2,
                    });
                }
            });
        }
        setDetaillist(res.data);
        setOperationbentate(
            res.data.agent.publish_status === 0 && res.data.is_creator === 1 ? 'false' : 'true',
        );
        if (res.data.agent.publish_status === 1) {
            message.warning(intl.formatMessage({ id: 'agent.message.listwarning' }), 5);
        }

        Ffromref.setFieldsValue(objecttoarray(data.agent.input_variables));

        const user = res.data.agent_abilities_list.map((item: any) => {
            return item.status == 1 ? { ...item, status: true } : { ...item, status: false };
        });
        Sformref.setFieldsValue({
            users: !user[0]
                ? [{ agent_ability_id: 0, name: '', content: '', status: true, output_format: 0 }]
                : user,
        });

        setAgent_select_list(selectlistdata(data.agent_abilities_list));
        setAgent_select_list_old(selectlistdata(data.agent_abilities_list));
        const list = data.agent_abilities_list.filter((item: any) => {
            return item.output_format !== 0;
        });
        Tformref.setFieldsValue({
            users: list.map((item: any) => {
                return {
                    agent_ability_id: item.agent_ability_id,
                    output_format: item.output_format,
                };
            }),
        });

        Fourthlyref.setFieldsValue(objecttoarray(data.agent.input_variables));

        setFourthly_select_list(
            data.m_configurations_list.map((item: any) => {
                return {
                    value: item.m_config_id ? item.m_config_id : item.model_config_id,
                    label: item.m_name ? item.m_name : item.model_name,
                };
            }),
        );
        if (data.agent.m_config_id || data.agent.model_config_id) {
            setFourthly_config_id(
                data.agent.m_config_id ? data.agent.m_config_id : data.agent.model_config_id,
            );
        } else {
            setFourthly_config_id(data.m_configurations_list[0].model_config_id);
        }

        const newabilitieslist = data.agent_abilities_list.filter((item: any, i: any) => {
            return item.status === 1;
        });

        setFourthly_abilities_list(
            selectlistdata(newabilitieslist).concat([
                { value: 0, label: intl.formatMessage({ id: 'agent.allability' }) },
            ]),
        );
        setLoading(false);
    };

    const objecttoarray = (obj?: any) => {
        const codeData = {
            users:
                !!obj && !!obj.properties
                    ? Object.values(obj.properties).map((item: any) => {
                          return {
                              name: item.name,
                              type: item.type,
                              content: item.display_name,
                              status: item.required,
                              ...item,
                          };
                      })
                    : [
                          {
                              name: '',
                              content: '',
                              type: 'string',
                              agent_ability_id: 0,
                              output_format: 0,
                              status: 0,
                          },
                      ],
        };
        return codeData;
    };

    const selectlistdata = (list: any) => {
        return list.map((item: any) => {
            return { value: item.agent_ability_id, label: item.name };
        });
    };

    const handleValueFromChid = (value: any) => {
        AgentUpdate(value, 1);
        Fourthlyref.setFieldsValue(Ffromref.getFieldsValue());
    };

    const SecondValue = () => {
        getAgent();
    };

    const handleBack = (id: number) => {
        setProcedure(id);
    };
    const returnList = () => {
        history.back();
    };

    const firstjudgingcondition = () => {
        // const firstusers = Ffromref.getFieldsValue().users.filter((item: any) => {
        //     return !item || !item.name || !item.content;
        // });
        // if (!Ffromref.getFieldsValue().users[0]) {
        //     message.warning(intl.formatMessage({ id: 'agent.message.warning.variable' }));
        //     return true;
        // }
        // else
        if (!Detaillist.agent.input_variables) {
            message.warning(intl.formatMessage({ id: 'agent.message.warning.variable' }));
            return true;
        }
        if (_.isEmpty(Detaillist.agent.input_variables.properties)) {
            message.warning(intl.formatMessage({ id: 'agent.message.warning.variable' }));
            return true;
        }

        if (!Fourthly_config_id) {
            message.warning(intl.formatMessage({ id: 'agent.message.warning.LLM' }));
            return true;
        } else if (!Detaillist.agent.obligations) {
            message.warning(intl.formatMessage({ id: 'agent.message.warning.functiondescribe' }));
            return true;
        } else if (hasDuplicateField(Ffromref.getFieldsValue().users, 'name')) {
            message.warning(intl.formatMessage({ id: 'agent.message.warning.repetition' }));
            return true;
        }

        // else if (firstusers.length !== 0) {
        //     message.warning(intl.formatMessage({ id: 'agent.message.warning.completevariable' }));
        //     return true;
        // }
        return false;
    };

    const secondjudgingcondition = () => {
        const secondusersA = Sformref.getFieldsValue().users.filter((item: any) => {
            return !!item;
        });
        const secondusersB = secondusersA.filter((item: any) => {
            return !item.name || !item.content;
        });
        if (secondusersB.length !== 0) {
            if (
                secondusersB.length == 1 &&
                secondusersB[0].name == '' &&
                secondusersB[0].content == ''
            ) {
            } else {
                message.warning(
                    intl.formatMessage({ id: 'agent.message.warning.integritycapacity' }),
                );
                return true;
            }
        }
        return false;
    };

    const SkillMenuClick: MenuProps['onClick'] = e => {
        if (e?.key == '4') {
            const wordlist = Ffromref.getFieldsValue().users.map((item: any) => {
                return { value: `<<${CURRENT_NODE_ID}.inputs.${item.name}>>`, label: item.name };
            });
            setCallwordlist(wordlist);
        }
        pageKeyfun(e.key);
    };

    const agentupdata = () => {
        setLoading(true);
        let creationagentid = 0;
        return new Promise(resolve => {
            const handleAgentCreation = appId => {
                return GetagentInfo(appId, false)
                    .then(async value => {
                        creationagentid = value.data.agent.agent_id;

                        await agentfirst(creationagentid);

                        if (!creationappid) {
                            history.replace(`/Agents?app_id=${appId}&type=false`);
                        }

                        agentsecond(creationagentid).then(res => {
                            message.success(intl.formatMessage({ id: 'skill.conserve.success' }));
                            setTimeout(() => {
                                getAgent(appId);
                                if (!creationappid) {
                                    const createdData = {
                                        ...createappdata('GET'),
                                        app_id: appId,
                                    };
                                    createappdata('SET', createdData);
                                }
                            }, 1000);

                            setNewagentid(creationagentid);
                        });

                        return value;
                    })
                    .catch(() => {
                        return '';
                    });
            };

            if (!creationappid) {
                PostappsCreate(createappdata('GET'))
                    .then(res => {
                        setcreationappid(res.data.app_id);
                        handleAgentCreation(res.data.app_id)
                            .then(result => resolve(result))
                            .catch(err => {
                                console.error('Error during agent creation:', err);
                                resolve('');
                            });
                    })
                    .catch(err => {
                        console.error('Error creating app:', err);
                        setLoading(false);
                        resolve('');
                    });
            } else {
                handleAgentCreation(creationappid)
                    .then(result => resolve(result))
                    .catch(err => {
                        console.error('Error during agent update:', err);
                        resolve('');
                    });
            }
        });
    };

    const agentfirst = (agent_id: any, e?: any): Promise<void> => {
        return new Promise((resolve, reject) => {
            Ffromref.validateFields()
                .then(async value => {
                    //                 "callable_list": [
                    //     {
                    //       "app_id": 0,
                    //       "item_type": 0
                    //     }
                    //   ]
                    const callable_list = [
                        ...(Detaillist.agent.selected_skills || []),
                        ...(Detaillist.agent.selected_workflows || []),
                    ].map((item: any) => {
                        return {
                            app_id: item.app_id,
                            //1skill 2workflow
                            item_type: item.mode == 4 ? 1 : 2,
                        };
                    });

                    const putBasedata = {
                        agent_id: agent_id,
                        data: {
                            is_public: Detaillist.app.is_public,
                            enable_api: Detaillist.app.enable_api,
                            attrs_are_visible: Detaillist.app.attrs_are_visible,
                            obligations: Detaillist.agent.obligations,
                            input_variables: Detaillist.agent.input_variables
                                ? Detaillist.agent.input_variables
                                : arraytoobject(Ffromref.getFieldsValue()),
                            dataset_ids: repository,
                            m_config_id: Fourthly_config_id,
                            allow_upload_file: Detaillist.agent.allow_upload_file,
                            default_output_format: Detaillist.agent.default_output_format,
                            callable_list: callable_list,
                        },
                    };
                    if (Operationbentate == 'false') {
                        await AgentUpdate(putBasedata, 1);
                    }

                    Fourthlyref.setFieldsValue(Ffromref.getFieldsValue());

                    const wordlist =
                        Ffromref.getFieldsValue()?.users?.map((item: any) => {
                            return {
                                value: `<<${CURRENT_NODE_ID}.inputs.${item.name}>>`,
                                label: item.name,
                            };
                        }) || [];

                    setCallwordlist(wordlist);

                    if (e) {
                        pageKeyfun(e.key);
                    }

                    resolve();
                })
                .catch(err => {
                    reject(err);
                });
        });
    };

    const agentsecond = (agent_id: any): Promise<void> => {
        return new Promise((resolve, reject) => {
            const secondusersA = Sformref.getFieldsValue().users.filter((item: any) => {
                return !!item;
            });
            const agent_abilities = secondusersA.map((item: any) => {
                return {
                    ...item,
                    status: item.status == false ? 2 : 1,
                    agent_ability_id: item.agent_ability_id ? item.agent_ability_id : 0,
                    output_format: item.output_format ? item.output_format : 0,
                };
            });
            const params = {
                agent_id: agent_id,
                data: {
                    auto_match_ability: Detaillist.agent.auto_match_ability,
                    agent_abilities: agent_abilities,
                },
            };
            if (Operationbentate == 'false') {
                if (
                    agent_abilities.length == 1 &&
                    agent_abilities[0].name == '' &&
                    agent_abilities[0].content == ''
                ) {
                    setAgentmunudisabled({ first: false, second: false, fourthly: false });
                    // pageKeyfun('4');
                    resolve();
                } else {
                    PutagentAbilitiesset(params)
                        .then(res => {
                            if (res.code == 0) {
                                setAgentmunudisabled({
                                    first: false,
                                    second: false,
                                    fourthly: false,
                                });
                                // pageKeyfun('4');
                                resolve();
                            } else {
                                reject(new Error(`API call failed with code: ${res.code}`));
                            }
                        })
                        .catch(err => {
                            reject(err);
                        });
                }
            } else {
                resolve();
            }
        });
    };

    const AgentUpdate = async (values: any, id: number) => {
        if (Operationbentate === 'false') {
            const res =
                id === 1
                    ? await PutagentBaseupdate(values)
                    : id === 2
                    ? await PutagentAbilitiesset(values)
                    : await PutagentOutputset(values);
            if (res && res.code === 0) {
                setLoading(false);
            }
        }
        return true;
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

    const arraytoobject = (value: any) => {
        const input_variables = new ObjectVariable('input', '', '');
        value.users.forEach((item: any) => {
            const variable = new AgentsVariable(
                item.name,
                item.type ? item.type : 'string',
                item.value ? item.value : '',
                item.content,
                item.status,
            );
            input_variables.addProperty(item.name, variable);
        });
        return input_variables;
    };
    return (
        <div className=" flex bg-white" style={{ height: 'calc(100vh - 56px)' }}>
            <div className="flex flex-col w-[300px]" style={{ height: 'calc(100vh - 56px)' }}>
                <div className="flex w-full items-center bg-white px-[30px] pt-[30px] border-[#e5e7eb] border-solid border-r">
                    <Button
                        type="link"
                        shape="circle"
                        size="middle"
                        className=""
                        onClick={returnList}
                    >
                        <ArrowLeftOutlined />
                        <span className="text-sm font-medium text-[#213044]">
                            {fromdata == 'chat_room'
                                ? intl.formatMessage({ id: 'agent.back_meeting' })
                                : intl.formatMessage({ id: 'agent.back' })}
                        </span>
                    </Button>
                </div>
                <div className="w-full flex-1 px-[30px] py-[30px] bg-white border-[#e5e7eb] border-solid border-r">
                    <Menu
                        selectedKeys={[pageKey]}
                        onClick={SkillMenuClick}
                        style={{ width: '100%', borderInlineEnd: '1px solid rgba(0,0,0,0)' }}
                        defaultSelectedKeys={[pageKey]}
                        mode="inline"
                        items={items}
                    />
                    {Detaillist &&
                    Detaillist.app?.enable_api === 1 &&
                    Detaillist.app?.publish_status === 1 ? (
                        <div
                            className="w-full h-[40px] rounded-lg text-[#000] hover:bg-[#f0f0f0] p-[12px] pl-[16px] cursor-pointer"
                            onClick={async () => {
                                let params = new URLSearchParams(window.location.search);
                                let res = null;
                                if (params.get('app_id')) {
                                    res = await GetagentInfo(
                                        params.get('app_id'),
                                        params.get('type'),
                                    );
                                }
                                if (
                                    res != null &&
                                    res.data.app.enable_api === 1 &&
                                    res.data.app.publish_status === 1
                                ) {
                                    window.open(BASE_URL + Detaillist.app.api_url);
                                } else {
                                    message.warning(
                                        intl.formatMessage({ id: 'agent.save.and.click' }),
                                        5,
                                    );
                                }
                            }}
                        >
                            <div className="mr-[20px] text-base font-medium text-[#213044] -mt-1">
                                <DesktopOutlined className="mr-3" />
                                {intl.formatMessage({ id: 'agent.visit' })} API
                            </div>
                        </div>
                    ) : null}
                </div>
            </div>
            <div className="flex-1 relative w-[calc(100%-300px)]">
                <Splitter style={{ height: '100%', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }}>
                    <Splitter.Panel defaultSize="50%" min="40%" max="70%">
                        <Spin spinning={loading} size="large" className="mt-[112px] mr-4">
                            <div
                                className="flex flex-col"
                                style={{
                                    height: 'calc(100vh - 56px)',
                                    // width: 'calc(100vw - 230px)',
                                    overflowY: 'scroll',
                                    scrollbarWidth: 'none',
                                }}
                            >
                                <div
                                    className="px-[30px] "
                                    style={{ overflowX: 'auto', height: '100%' }}
                                >
                                    <div className="w-full flex justify-center  mt-[30px]">
                                        <div className="flex items-center w-full ">
                                            <div className="mr-[10px] w-[16px] h-[16px]">
                                                <img
                                                    src="/icons/flag.svg"
                                                    alt=""
                                                    className="w-[16px] h-[16px]"
                                                />
                                            </div>
                                            <div className="flex items-center">
                                                <div className="mr-[6px] text-lg text-[#213044] font-medium">
                                                    {createappdata('GET')?.app_id
                                                        ? intl.formatMessage({
                                                              id: 'agent.compile',
                                                          })
                                                        : intl.formatMessage({
                                                              id: 'agent.created',
                                                          })}{' '}
                                                    {intl.formatMessage({ id: 'agent' })}
                                                </div>
                                                {Detaillist?.app?.publish_status === 1 ? (
                                                    <div className="bg-[#1B64F3] px-[7px] text-[#fff] rounded font-normal text-xs flex items-center justify-center h-[18px]">
                                                        {intl.formatMessage({
                                                            id: 'agent.havepublished',
                                                        })}
                                                    </div>
                                                ) : (
                                                    <div className=" bg-[#EEE] px-[7px]  text-[#999] rounded font-normal text-xs flex items-center justify-center h-[18px]">
                                                        {intl.formatMessage({
                                                            id: 'agent.unpublish',
                                                        })}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <div
                                        style={{
                                            display: pageKey === '1' ? 'flex' : 'none',
                                            height: 'calc(100vh - 146px)',
                                            justifyContent: 'center',
                                        }}
                                    >
                                        {!loading && (
                                            <AgentsFirst
                                                FirstValue={handleValueFromChid}
                                                Ffromref={Ffromref}
                                                Detaillist={Detaillist}
                                                setDetaillist={setDetaillist}
                                                repository={repository}
                                                setRepository={setRepository}
                                                Newproperties={Newproperties}
                                                setNewproperties={setNewproperties}
                                                Operationbentate={Operationbentate}
                                                Fourthly_config_id={Fourthly_config_id}
                                                setFourthly_config_id={setFourthly_config_id}
                                                Fourthly_select_list={Fourthly_select_list}
                                                pageKeyfun={pageKeyfun}
                                                firstjudgingcondition={firstjudgingcondition}
                                                agentmenudisabled={agentmenudisabled}
                                                setAgentmunudisabled={setAgentmunudisabled}
                                            />
                                        )}
                                    </div>
                                    <div
                                        style={{
                                            display: pageKey === '2' ? 'flex' : 'none',
                                            height: 'calc(100vh - 146px)',
                                            justifyContent: 'center',
                                            position: 'sticky',
                                            top: '-150px',
                                        }}
                                    >
                                        <AgentsSecond
                                            SecondValue={SecondValue}
                                            Detaillist={Detaillist}
                                            setDetaillist={setDetaillist}
                                            Sformref={Sformref}
                                            Operationbentate={Operationbentate}
                                            handleBack={handleBack}
                                            pageKeyfun={pageKeyfun}
                                            SkillMenuClick={SkillMenuClick}
                                            secondjudgingcondition={secondjudgingcondition}
                                            agentupdata={agentupdata}
                                        />
                                    </div>
                                    <div
                                        style={{
                                            display: pageKey === '4' ? 'flex' : 'none',
                                            height: 'calc(100vh - 146px)',
                                            justifyContent: 'center',
                                        }}
                                    >
                                        <AgentsFourthly
                                            handleBack={handleBack}
                                            Detaillist={Detaillist}
                                            setDetaillist={setDetaillist}
                                            Fourthly_select_list={Fourthly_select_list}
                                            Fourthly_config_id={Fourthly_config_id}
                                            setFourthly_config_id={setFourthly_config_id}
                                            Fourthlyref={Fourthlyref}
                                            Fourthly_abilities_list={Fourthly_abilities_list}
                                            Operationbentate={Operationbentate}
                                            callwordlist={callwordlist}
                                            newagentid={newagentid}
                                        />
                                    </div>
                                </div>
                            </div>
                        </Spin>
                    </Splitter.Panel>
                    <Splitter.Panel>
                        <div>
                            <Chat
                                saveInfo={{
                                    firstjudgingcondition,
                                    secondjudgingcondition,
                                    agentupdata,
                                }}
                                operationbentate={Operationbentate}
                                data={{
                                    abilitiesList: Fourthly_abilities_list,
                                    detailList: Detaillist,
                                }}
                            />
                        </div>
                    </Splitter.Panel>
                    {pageKey == '5' && (
                        <div className="absolute bottom-0 left-0 right-0 bg-slate-50 w-full h-full z-10">
                            <Log agent_id={Detaillist.agent.agent_id}></Log>
                        </div>
                    )}
                </Splitter>
            </div>
        </div>
    );
};
export default Agents;
