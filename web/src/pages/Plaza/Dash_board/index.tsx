// {/* <Coldom /> */}
import { getIndex } from '@/api/plaza';
import CreationModal from '@/components/creationModal';
import Footer from '@/components/Footer/index';
import Graphic from '@/components/Graphic';
import useUserStore from '@/store/user';
import useSocketStore from '@/store/websocket';
import { creationsearchdata } from '@/utils/useUser';
import { SwapRightOutlined,CheckCircleOutlined,ExclamationCircleOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Button, Col, Empty, Row, Spin,Tooltip } from 'antd';
import { useEffect, useRef, useState } from 'react';
import { history } from 'umi';
// import Menus from '../components/Menus/index';

// Subtitle
const SubTitle = ({ subtitle }) => {
    let titleClassName = `pl-[10px] text-[#1B64F3] text-[12px] ${subtitle.need_human_confirm==1||subtitle.need_human_confirm==undefined ? 'text-[#1B64F3]' : 'text-[#808183] '}`
    return (
        <div className="pr-4">
            <div className="truncate w-full">
                <span className="pr-[10px] text-[#666666] text-[12px]">{subtitle.app_name}</span>
                <SwapRightOutlined />
                <span className={titleClassName}>
                    {subtitle.node_name || subtitle.node_exec_data?.node_name}
                </span>
            </div>
        </div>
    );
};
// Progress bar subtitle
const ProgressContainer = ({ progressObj }) => {
    const setEntime = () => {
        return parseFloat(progressObj.elapsed_time).toFixed(6);
    };
    const setCurrentTime = (time: any) => {
        let date = new Date(time);
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const seconds = date.getSeconds().toString().padStart(2, '0');
        return <>{`${year}.${month}.${day} ${hours}:${minutes}:${seconds}`}</>;
    };
    return (
        <div className="inline-flex gap-x-4 justify-end max-w-[100%]">
            <div className="inline-flex gap-x-[20px] max-w-[100%]">
                <div className="truncate min-w-[70px]">
                    {progressObj.created_time && setCurrentTime(progressObj.created_time)}
                </div>
                <div className="truncate">{progressObj.apps_name || progressObj.app_name}</div>
                <div className="flex items-center gap-x-[7px] truncate min-w-[50px]">
                    <div
                        className={`shrink-0 rounded-full ${
                            progressObj.status == 1
                                ? 'bg-blue-600'
                                : progressObj.status == 2
                                ? 'bg-green-500'
                                : 'bg-red-500'
                        }`}
                        style={{ width: '3px', height: '3px' }}
                    ></div>
                    <div className="truncate">{setEntime()}S</div>
                </div>
            </div>
        </div>
    );
};
// Run button
const OperationButton = ({ operationObj }) => {
    const setRunId = useUserStore(state => state.setRunId);
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    return (
        <div className="inline-flex justify-end flex-1">
            <div className="inline-flex gap-x-[10px] items-center">
                <Button
                    type="primary"
                    size="small"
                    style={{ boxShadow: 'none', background: 'transparent', border: 'none' }}
                    disabled={operationObj.publish_status == 0}
                    icon={
                        <img
                            src={
                                operationObj.publish_status == 0
                                    ? '/icons/operation_disable_icon.svg'
                                    : '/icons/operation_icon.svg'
                            }
                        ></img>
                    }
                    onClick={e => {
                        e.stopPropagation();
                        setRunPanelLogRecord(false);
                        setDealtWithData(false);
                        setRunId(operationObj.app_id);
                        return false;
                    }}
                ></Button>
            </div>
        </div>
    );
};
// Add
const Addbtn = (Fn: any) => {
    return (
        <>
            {
                <div onClick={Fn.bindAdd}>
                    <a
                        style={{ color: '#0077ED', fontSize: '0' }}
                        className="flex items-center  gap-x-[5px]"
                    >
                        {/* <PlusOutlined style={{ paddingRight: '5px', fontSize: '12px' }} /> */}
                        <img src="/icons/plaza_add.svg" className="w-[16px] h-[16px] shrink-0" />
                        <span className="text-[#1B64F3]" style={{ fontSize: '12px' }}>
                            {Fn.type}
                        </span>
                    </a>
                </div>
            }
        </>
    );
};
// List
const BlockList = ({ blocklsit, item, blockIndex }) => {
// Navigate to details
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    const setRunId = useUserStore(state => state.setRunId);
    const jumpDetails = (i: any) => {
        switch (item.key) {
            case 'my_agent':
                history.push(`/Agents?app_id=${item.list[i].app_id}&type=false`);
                break;
            case 'more_agent':
                history.push(`/ReadOnlyAgent?app_id=${item.list[i].app_id}&type=true`);
                break;
            case 'my_workflow':
                history.push(`/workspace/workflow?app_id=${item.list[i].app_id}&type=false`);
                break;
            case 'more_workflow':
                history.push(`/workspace/workflow?app_id=${item.list[i].app_id}&type=true`);
                break;
            case 'workflow_log':
                // history.push(`/workspace/workflow?app_id=${item.list[blockIndex].app_id}&type=true`);
                setRunPanelLogRecord(item.list[i]);
                setRunId(null);
                setDealtWithData(false);
                break;
            case 'backlogs':
                // history.push(`/workspace/workflow?app_id=${item.list[blockIndex].app_id}&type=true`);
                if(item.list[i].need_human_confirm == 0){
                    return
                }
                setDealtWithData(item.list[i]);
                setRunId(null);
                setRunPanelLogRecord(false);
                break;
            default:
                break;
        }
    };
    const setpercentage = (i: any) => {
        if (i.completed_progress) {
            return parseInt(i.completed_progress.slice(0, -1));
        } else {
            return false;
        }
    };
    return (
        <div
            className={`${item.key == 'workflow_log' ? 'px-[10px] cardbox' : 'cardbox'}`}
            style={{ overflowY: 'auto', height: '100%', overflowX: 'hidden' }}
        >
            <Row gutter={[30, item.key == 'workflow_log' ? 20 : 0]}>
                {blocklsit.map((i: any, index: any) => (
                    <Col key={index} className="graphicHoverbox" span={item.biserial ? 12 : 24}>
                        {item.key == 'backlogs' && (
                            <Graphic
                                icon={i.icon}
                                title={
                                    (i.node_name && <SubTitle subtitle={i} />) ||
                                    (i.node_exec_data.node_name && <SubTitle subtitle={i} />)
                                }
                                textDetails={i.app_run_name || i.run_name}
                                handleClick={() => {
                                    jumpDetails(index);
                                }}
                                lineClamp={1}
                                backlogTips={item.needHuman(i)}
                                // iconType={'workflow_icon'}
                            ></Graphic>
                        )}
                        {(item.key == 'my_agent' || item.key == 'more_agent') && (
                            <Graphic
                                icon={i.icon}
                                title={i.name}
                                textDetails={i.description}
                                handleClick={() => {
                                    jumpDetails(index);
                                }}
                                lineClamp={1}
                                // iconType={'robot_icon'}
                            ></Graphic>
                        )}
                        {(item.key == 'my_workflow' || item.key == 'more_workflow') && (
                            <Graphic
                                icon={i.icon}
                                title={i.name}
                                textDetails={i.description}
                                handleClick={() => {
                                    jumpDetails(index);
                                }}
                                lineClamp={1}
                                operation={<OperationButton operationObj={i}></OperationButton>}
                                iconType={
                                    item.key == 'my_workflow'
                                        ? i.publish_status == 0
                                            ? 'play_disable_icon'
                                            : 'play_icon'
                                        : ''
                                }
                            ></Graphic>
                        )}
                        {item.key == 'workflow_log' && (
                            <Graphic
                                status={i.status}
                                icon={i.icon}
                                title={i.app_runs_name || i.run_name}
                                textDetails={
                                    <ProgressContainer progressObj={i}></ProgressContainer>
                                }
                                handleClick={() => {
                                    jumpDetails(index);
                                }}
                                lineClamp={1}
                                progress={i.percentage || setpercentage(i)}
                                // iconType={'workflow_icon'}
                            ></Graphic>
                        )}

                        {/* <Graphic
                            icon={i.icon}
                            title={i.name || i.app_run_name || i.run_name || i.app_name || i.app_runs_name}
                            textDetails={i.description || i.created_time || (i.node_name && <SubTitle subtitle={i}/>) || (i.node_exec_data?.node_name && <SubTitle subtitle={i}/>)}
                            subtitle={IsSubTitle(item, i)}
                            handleClick={()=>{jumpDetails(index)}}
                            lineClamp={1}
                            // iconType={}
                        ></Graphic> */}
                    </Col>
                ))}
            </Row>
        </div>
    );
};
// More list button
const MoreList = ({ item, intl }: any) => {
    const jumpMoreList = () => {
        const optionsModalId = item.key == 'my_agent' || item.key == 'more_agent' ? 1 : 2;
        const searchType = item.key == 'more_agent' || item.key == 'more_workflow' ? true : false;
        creationsearchdata('SET', optionsModalId, searchType);

        history.push(`/creation`);
    };
    return (
        <div onClick={jumpMoreList}>
            {item.key !== 'backlogs' && item.key !== 'workflow_log' ? (
                <a
                    className="flex items-center gap-x-[5px]"
                    style={{ color: '#0077ED', fontSize: '0' }}
                >
                    <img src="/icons/plaza_view.svg" className="w-[16px] h-[16px]" />
                    <span className="text-[#1B64F3]" style={{ fontSize: '12px' }}>
                        {intl.formatMessage({ id: 'app.dashboard.title_button_2' })}
                    </span>
                    {/* <DoubleRightOutlined style={{ paddingLeft: '5px', fontSize: '12px' }}></DoubleRightOutlined> */}
                </a>
            ) : (
                <></>
            )}
        </div>
    );
};
// More list and add new
const MoreOrAdd = (item: any, setIsModalOpen: any, setCreationType: any, intl: any) => {
    const Addel = () => {
        // console.log(item);
        let addCreationTyp =
            item.key == 'my_agent'
                ? { name: 'Agent', path: 'Agents', apps_mode: 1 }
                : { name: 'WorkFlow', path: 'workspace/workflow', apps_mode: 2 };
        setCreationType((pre: any) => {
            return {
                ...pre,
                ...addCreationTyp,
            };
        });
        setIsModalOpen(true);
    };
    let typeName =
        item.key == 'my_agent'
            ? intl.formatMessage({ id: 'app.dashboard.title_button_1.1' })
            : item.isAdd
            ? intl.formatMessage({ id: 'app.dashboard.title_button_1.2' })
            : '';
    return (
        <div className="flex gap-x-[30px] items-center">
            {item.isAdd && <Addbtn bindAdd={Addel} type={item.isAdd && typeName}></Addbtn>}
            <MoreList item={item} intl={intl}></MoreList>
        </div>
    );
};
// Main body
const Coldom = () => {
    const intl = useIntl();
// Card configuration file
    const cardList = [
        {
            title: intl.formatMessage({ id: 'app.dashboard.backlog' }),
            key: 'backlogs',
            substitle: true,
            needHuman:(item:any)=>{
                return (
                    <div className='flex items-center'>
                        {item.need_human_confirm==1||item.need_human_confirm==undefined ? (
                            <Tooltip
                                title={intl.formatMessage({
                                    id: 'app.workflow.needHumanConfirm',
                                })}
                            >
                                <ExclamationCircleOutlined className="text-[#1B64F3]" />
                            </Tooltip>
                        ) : (
                            <Tooltip
                                title={intl.formatMessage({
                                    id: 'app.workflow.noHumanConfirm',
                                })}
                            >
                                <CheckCircleOutlined className="text-[#808183]" />
                            </Tooltip>
                        )}
                    </div>
                )
            },
        },
        {
            title: intl.formatMessage({ id: 'app.dashboard.myagent' }),
            key: 'my_agent',
            isAdd: true, // Has add button
            biserial: true, // Is double column
        },
        {
            title: intl.formatMessage({ id: 'app.dashboard.workflow' }),
            key: 'my_workflow',
            isAdd: true,
            biserial: true,
        },
        {
            title: intl.formatMessage({ id: 'app.dashboard.run_log' }),
            key: 'workflow_log',
            progress: true, // Progress bar subtitle
        },
        {
            title: intl.formatMessage({ id: 'app.dashboard.team_agent' }),
            key: 'more_agent',
            biserial: true,
        },
        {
            title: intl.formatMessage({ id: 'app.dashboard.team_workflow' }),
            key: 'more_workflow',
            biserial: true,
        },
    ];
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [CreationType, setCreationType] = useState({});
    // Data list
    const [colstate, setColstate] = useState(cardList);
    // Card loading
    // const [cardLoading, setCardLoading] = useState(false);
    const [closeLoading, setcloseLoading] = useState(false);
    // Has retrieved list
    const isLoad = useRef(false);
    // Get list
    const getCardList = async () => {
        let res = await getIndex();
        if (res.code == 0) {
            let data = res.data;
            isLoad.current = true;
            setColstate(prev => {
                return prev.map((x: any) => {
                    return {
                        ...x,
                        list: data[x.key],
                    };
                });
            });
            setcloseLoading(true);
        }
    };
    const progressConcat = (progress: any, list: any) => {
        const map = new Map();
        list.reverse().forEach((item: any) => {
            map.set(item['app_run_id'], item);
        });
        progress.forEach((item: any) => {
            map.set(item['app_run_id'], item); // Use the key attribute value as the key to store each object in the map
        });
        return Array.from(map.values()).reverse();
    };
    const confirmConcat = (backlogs: any, list: any) => {
        const map = new Map();
        list.reverse().forEach((item: any) => {
            map.set(item.exec_id, item);
        });
        backlogs.forEach((item: any) => {
            item.exec_id = item.node_exec_data?.node_exec_id;
            if (item.node_exec_data?.node_exec_id) {
                map.set(item.exec_id, item); // Use the key attribute value as the key to store each object in the map
            }
        });
        return Array.from(map.values()).reverse();
    };
    const setWebsocktdata = async () => {
        if (!isLoad.current) {
            await getCardList();
        }
        let backlogs = flowMessage
            ?.filter(item => item.type == 'workflow_need_human_confirm')
            .map(({ data }) => data)
            ?.filter(item => item.type !== 1);

        let progress = flowMessage
            ?.filter(item => item.type == 'workflow_run_progress')
            .map(({ data }) => data);
            
        if ((backlogs && backlogs.length) || (progress && progress.length)) {
            setColstate(pre => {
                return pre.map((item: any) => {
                    return item.list
                        ? {
                              ...item,
                              list:
                                  item.key == 'backlogs'
                                      ? confirmConcat(backlogs, item.list)
                                      : item.key == 'workflow_log'
                                      ? progressConcat(progress, item.list)
                                      : item.list,
                          }
                        : {
                              ...item,
                          };
                });
            });
        }
    };
    //websockt
    const flowMessage = useSocketStore(state => state.flowMessage);
    useEffect(() => {
        setWebsocktdata();
    }, [flowMessage]);
    const submitPromptId = useUserStore(state => state.submitPromptId);
    useEffect(() => {
        if (submitPromptId) {
            setColstate(pre => {
                return pre.map((item: any) => {
                    return item.key == 'backlogs'
                        ? {
                              ...item,
                              list: item.list?.filter(
                                  (item: any) => item.exec_id != submitPromptId,
                              ),
                          }
                        : {
                              ...item,
                          };
                });
            });
        }
    }, [submitPromptId]);
    return (
        <>
            {closeLoading &&
                colstate.map((item: any, index: any) => (
                    <Col
                        span={8}
                        key={index}
                        xs={24}
                        sm={24}
                        md={24}
                        lg={12}
                        xl={8}
                        style={{ height: 'calc(50% - 20px)' }}
                    >
                        {/* <div style={{height:'calc(50% - 10px)'}}></div> */}
                        <div
                            className="bg-[#fff] rounded-[8px] w-[100%] h-[100%]"
                            style={{ boxShadow: '0px 2px 4px 0px rgba(0,0,0,0.05)' }}
                        >
                            <div className="text-[14px] p-[20px] text-[#213044] flex">
                                <span className="flex-1 font-[500] text-[#213044]">
                                    {item.title}
                                </span>
                                <span>
                                    {MoreOrAdd(item, setIsModalOpen, setCreationType, intl)}
                                </span>
                            </div>
                            <div
                                className="pt-[5px] pb-[20px] px-[10px]"
                                style={{ height: 'calc(100% - 62px)' }}
                            >
                                {item.list && item.list.length ? (
                                    <BlockList
                                        blocklsit={item.list}
                                        item={item}
                                        blockIndex={index}
                                    ></BlockList>
                                ) : (
                                    <div className="flex items-center h-full justify-center">
                                        <Empty
                                            image={Empty.PRESENTED_IMAGE_SIMPLE}
                                            description={intl.formatMessage({
                                                id: 'app.dashboard.None',
                                            })}
                                        ></Empty>
                                    </div>
                                )}
                            </div>
                        </div>
                        {/* <Card
                        title={item.title}
                        loading={cardLoading}
                        hoverable={true}
                        extra={MoreOrAdd(item,setIsModalOpen,setCreationType)}
                        style={{ width: '100%',height:'100%'}}
                        styles={{body:{padding:'5px 10px 20px 10px',height:'calc(100% - 62px)'},header:{border:0,fontSize:'14px',padding:'20px 20px',color:'#213044',}}}
                    >
                        {item.list && item.list.length ? (
                            <BlockList
                                blocklsit={item.list}
                                item={item}
                                blockIndex={index}
                            ></BlockList>
                        ) : (
                            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE}></Empty>
                        )}
                    </Card> */}
                    </Col>
                ))}
            {!closeLoading && (
                <div
                    className="w-full h-full flex items-center justify-center "
                    style={{ height: 'calc(100vh - 300px)' }}
                >
                    <Spin size="large" />
                </div>
            )}
            <CreationModal
                setIsModalOpen={setIsModalOpen}
                isModalOpen={isModalOpen}
                ModalType={false}
                CreationType={CreationType}
            />
        </>
    );
};

const Plaza: React.FC = () => {

    return (
        <div
            className="overflow-auto"
            style={{ height: 'calc(100vh - 56px)', maxHeight: 'calc(100vh - 56px)' }}
        >
            <div
                className="px-[30px] pb-[10px] flex flex-col pt-[30px]"
                style={{
                    width: '100%',
                    height: 'calc(100vh - 92px)',
                    maxHeight: 'calc(100vh - 92px)',
                    margin: '0 auto',
                }}
            >
                {/* <Menus keys="dash_board" path="/meeting"></Menus> */}
                <div className="flex-1" style={{ minHeight: 0 }}>
                    <Row
                        gutter={[20, 20]}
                        className="h-full"
                        style={{ overflowX: 'hidden', alignContent: 'flex-start' }}
                    >
                        <Coldom></Coldom>
                    </Row>
                </div>
            </div>
            <Footer></Footer>
        </div>
    );
};

export default Plaza;
