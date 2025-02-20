import { GetagentInfo } from '@/api/agents';
import { BASE_URL } from '@/api/request';
import { CURRENT_NODE_ID } from '@/components/WorkFlow/config';
import {
    ArrowLeftOutlined,
    CodeOutlined,
    DesktopOutlined,
    FileDoneOutlined,
    FileTextOutlined,
} from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import type { MenuProps } from 'antd';
import { Button, Form, Menu, message } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
import AgentsFirst from './components/AgentsFirst';
import AgentsFourthly from './components/AgentsFourthly';
import AgentsSecond from './components/AgentsSecond';

type MenuItem = Required<MenuProps>['items'][number];

const Agents: React.FC = () => {
    const intl = useIntl();
    const childRef = useRef<any>(null);
    const [Ffromref] = Form.useForm();
    const [Tformref] = Form.useForm();
    const [Sformref] = Form.useForm();
    const [Fourthlyref] = Form.useForm();

    const [Detaillist, setDetaillist] = useState(null); // Agent detail information
    const [repository, setRepository] = useState(null); // Step one repository selected list id
    const [Fourthly_select_list, setFourthly_select_list] = useState(null); // Step four array parameters
    const [Fourthly_config_id, setFourthly_config_id] = useState(null); // Step four top-left corner id
    const [Fourthly_abilities_list, setFourthly_abilities_list] = useState(null); // ability_id list
    const [Operationbentate, setOperationbentate] = useState(null); // Operation status
    const [pageKey, pageKeyfun] = useState<string>('1'); // Step highlight
    const [callwordlist, setCallwordlist] = useState(null); // Step four call word list
    const items: MenuItem[] = [
        {
            key: '1',
            icon: <FileDoneOutlined />,
            label: intl.formatMessage({ id: 'agent.menu.basicsetup' }),
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                // background: pageKey == '3' ? 'rgba(27,100,243,0.1)' : '#FAFAFA',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '500',
                color: pageKey == '1' ? '#1B64F3' : '#213044',
            },
        },
        {
            key: '2',
            icon: <CodeOutlined />,
            label: intl.formatMessage({ id: 'agent.menu.Capacityoutput' }),
            disabled:Detaillist && Detaillist.app.attrs_are_visible === 0,
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                // background: pageKey == '3' ? 'rgba(27,100,243,0.1)' : '#FAFAFA',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '500',
                color: pageKey == '2' ? '#1B64F3' : '#213044',
            },
        },
        {
            key: '4',
            icon: <FileTextOutlined />,
            label: intl.formatMessage({ id: 'agent.menu.operation' }),
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                // background: pageKey == '3' ? 'rgba(27,100,243,0.1)' : '#FAFAFA',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '500',
                color: pageKey == '3' ? '#1B64F3' : '#213044',
            },
        },
    ];
    useEffect(() => {
        getAgent();
    }, []);
   
    const getAgent = async () => {
        let params = new URLSearchParams(window.location.search);
        console.log(params.get('type'));
        const res = await GetagentInfo(params.get('app_id'), params.get('type'));
        const data = res.data;
        if(res.data.agent_dataset_relation_list && res.data.agent_dataset_relation_list.length){
            const repositoryID = res.data.agent_dataset_relation_list.map((item: any) => {
                return item.dataset_id;
            });
            setRepository(repositoryID);
        }
        setDetaillist(res.data);
        setOperationbentate(
            res.data.agent.publish_status === 0 && res.data.is_creator === 1 ? 'false' : 'true',
        );
        if (res.data.agent.publish_status === 1) {
            message.warning(intl.formatMessage({ id: 'agent.message.listwarning' }), 5);
        }
       
        Ffromref.setFieldsValue(objecttoarray(data.agent.input_variables));
        
        if(res.data.agent_abilities_list){
            const user = res.data.agent_abilities_list.map((item: any) => {
                return item.status == 1 ? { ...item, status: true } : { ...item, status: false };
            });
            Sformref.setFieldsValue({
                users: !user[0] ? [{ agent_ability_id: 0, name: '', content: '', status: true }] : user,
            });

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
        }       
        if(data.m_configurations_list){
            setFourthly_select_list(
                data.m_configurations_list.map((item: any) => {
                    return { value: item.m_config_id, label: item.m_name };
                }),
            );
        }
       
        setFourthly_config_id(data.agent.m_config_id);
        if(data.agent_abilities_list){
            const newabilitieslist = data.agent_abilities_list.filter((item: any, i: any) => {
                return item.status === 1;
            });
            setFourthly_abilities_list(
                selectlistdata(newabilitieslist).concat([
                    { value: 0, label: intl.formatMessage({ id: 'agent.allability' }) },
                ]),
            );
        }

    };
  
    const objecttoarray = (obj?: any) => {
        console.log(!!obj && !!obj.properties, 'obj');
        const codeData = {
            users:
                !!obj && !!obj.properties
                    ? Object.values(obj.properties).map((item: any) => {
                          return {
                              name: item.name,
                              type: item.type,
                              content: item.display_name,
                              status: item.required,
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
  
    const returnList = () => {
        SkillMenuClick({
            key: pageKey,
            keyPath: [],
            item: undefined,
            domEvent: undefined,
        });
        history.back();
    };
   
    const SkillMenuClick: MenuProps['onClick'] = e => {
        console.log(Detaillist.agent.obligations, '1111', Sformref.getFieldsValue().users);
        if (pageKey == '1') {
            const wordlist = Ffromref.getFieldsValue().users.map((item: any) => {
                return { value: `<<${CURRENT_NODE_ID}.inputs.${item.name}>>`, label: item.name };
            });
            Fourthlyref.setFieldsValue(Ffromref.getFieldsValue());
            setCallwordlist(wordlist);
        }
        pageKeyfun(e.key);
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
                            {intl.formatMessage({ id: 'agent.back' })}
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
                    Detaillist.app.enable_api === 1 &&
                    Detaillist.app.publish_status === 1 ? (
                        <div
                            className="w-full h-[40px] rounded-lg text-[#000] hover:bg-[#f0f0f0] p-[12px] pl-[16px] cursor-pointer"
                            onClick={() => {
                                window.open(BASE_URL + Detaillist.app.api_url);
                            }}
                        >
                            <div className="mr-[20px]">
                                <DesktopOutlined className="mr-2" />
                                {intl.formatMessage({ id: 'agent.visit' })}API
                            </div>
                        </div>
                    ) : null}
                </div>
            </div>
            <div
                className="flex flex-col  "
                style={{
                    height: 'calc(100vh - 56px)',
                    width: 'calc(100vw - 230px)',
                    overflowY: 'scroll',
                    scrollbarWidth: 'none',
                }}
            >
                <div
                    className="px-[30px] "
                    style={{ overflowX: 'auto', minWidth: '960px', height: '100%' }}
                >
                    <div className="w-full flex justify-center mt-[30px]">
                        <div className="flex items-center  w-[900px]">
                            <div className="mr-[10px] w-[16px] h-[16px]">
                                <img src="/icons/flag.svg" alt="" className="w-[16px] h-[16px]" />
                            </div>
                            <div className="mr-[6px] text-lg text-[#213044] font-medium">
                                {Detaillist ? Detaillist.creator_nickname : ''}
                                {intl.formatMessage({ id: 'agent.agents' })}
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
                        <AgentsFirst
                            Ffromref={Ffromref}
                            Detaillist={Detaillist}
                            repository={repository}
                            Operationbentate={Operationbentate}
                            Fourthly_config_id={Fourthly_config_id}
                            Fourthly_select_list={Fourthly_select_list}
                        />
                    </div>
                    <div
                        style={{
                            display: pageKey === '2' ? 'flex' : 'none',
                            height: 'calc(100vh - 146px)',
                            justifyContent: 'center',
                        }}
                    >
                        <AgentsSecond Detaillist={Detaillist} Sformref={Sformref} />
                    </div>
                    <div
                        style={{
                            display: pageKey === '4' ? 'flex' : 'none',
                            height: 'calc(100vh - 146px)',
                            justifyContent: 'center',
                        }}
                    >
                        <AgentsFourthly
                            Detaillist={Detaillist}
                            setDetaillist={setDetaillist}
                            Fourthly_select_list={Fourthly_select_list}
                            Fourthly_config_id={Fourthly_config_id}
                            setFourthly_config_id={setFourthly_config_id}
                            Fourthlyref={Fourthlyref}
                            Fourthly_abilities_list={Fourthly_abilities_list}
                            Operationbentate={Operationbentate}
                            callwordlist={callwordlist}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};
export default Agents;
