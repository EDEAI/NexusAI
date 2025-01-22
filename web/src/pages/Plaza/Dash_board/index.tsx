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
import { Button, Col, Empty, Row, Spin,Tooltip,Tag } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
import { history } from 'umi';
import {useBacklogList} from  '@/hooks/useBacklogList'
// import Menus from '../components/Menus/index';

// Subtitle
const SubTitle :React.FC<{subtitle:any}> = parmas => {
    let {subtitle} = parmas
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
const ProgressContainer :React.FC<{progressObj:any}> = parmas => {
    let {progressObj} = parmas
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
const OperationButton :React.FC<{operationObj:any}> = parmas => {
    let {operationObj} = parmas;
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
const Addbtn :React.FC<{bindAdd: any,type:any}> = parmas => {
    let {bindAdd,type} = parmas;
    return (
        <>
            {
                <div onClick={bindAdd}>
                    <a
                        style={{ color: '#0077ED', fontSize: '0' }}
                        className="flex items-center  gap-x-[5px]"
                    >
                        <img src="/icons/plaza_add.svg" className="w-[16px] h-[16px] shrink-0" />
                        <span className="text-[#1B64F3]" style={{ fontSize: '12px' }}>
                            {type}
                        </span>
                    </a>
                </div>
            }
        </>
    );
};
const EmptyDom :React.FC<{}> = parmas =>{
    const intl = useIntl();
    return(
        <div className="flex items-center h-full justify-center">
            <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={intl.formatMessage({
                    id: 'app.dashboard.None',
                })}
            ></Empty>
        </div>
    )
}

interface BlockParmas{
    data?:any,
    keyName?:any
}
// Backlogs
const Backlogs :React.FC<BlockParmas> = parmas =>{
    // const {data} = parmas;
    const {data,loading}=useBacklogList()
    const intl = useIntl();
    // const renamedData = data.map((item:any)=>({
    //     'app_name':item.app_name,
    //     'app_run_id':item.app_run_id,
    //     'icon':item.icon,
    //     'icon_background':item.icon_background,
    //     'need_human_confirm':item.need_human_confirm,
    //     'node_exec_data':{
    //         'node_name':item.node_name,
    //         'node_id':item.node_execution_id,
    //         'node_exec_id':item.exec_id
    //     },
    //     'exec_id':item.exec_id,
    //     'run_name':item.app_run_name,
    //     'mode':item.mode
    // }))
    // const [backData,setbackData]  = useState(renamedData);
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    const setRunId = useUserStore(state => state.setRunId);
    // const submitPromptId = useUserStore(state => state.submitPromptId);
    
    // const confirmConcat = (backlogs: any, list: any) => {
    //     const seenExecIds  = new Set();
    //     const combined = [...list.reverse(), ...backlogs];
    //     const result = combined.filter((item) => {
    //         const execId = item.node_exec_data?.node_exec_id || item.exec_id;
    //         if(!item.exec_id && item.node_exec_data?.node_exec_id){
    //             item.exec_id = item.node_exec_data?.node_exec_id
    //         }
    //         if (!execId) {
    //             return false;
    //         }

    //         if (seenExecIds.has(execId)) {
    //             return false;
    //         }

    //         seenExecIds.add(execId);
    //         return true;
    //     });
        
    //     return result.reverse();
    // };
    
    // // const setWebsocktdata = async () => {
    // //     let backlogs = flowMessage?.filter(item => item.type == 'workflow_need_human_confirm').map(({ data }) => data)?.filter(item => item.type !== 1);
      
    // //     if(backlogs && backlogs.length){
    // //         setbackData(confirmConcat(backlogs,backData))
    // //     }
    // // };
    // //websockt
    // // const flowMessage = useSocketStore(state => state.flowMessage);
    // // useEffect(() => {
    // //     setWebsocktdata();
    // // }, [flowMessage]);
    // useEffect(()=>{
    //     if(submitPromptId){
    //         setbackData((pre:any)=>{
    //             return pre.map((item:any)=>({
    //                 ...item,
    //                 'need_human_confirm':item.node_exec_data.node_exec_id == submitPromptId?0:item.need_human_confirm
    //             }))
    //         })
    //     }
        
    // },[submitPromptId])
    return (
        <>
            {data && data.list.length ? 
                    <div
                    className={`cardbox`}
                    style={{ overflowY: 'auto', height: '100%', overflowX: 'hidden' }}
                >
                    <Row gutter={[30,0]}>
                        {data.list.map((item: any, index: any) => (
                            <Col key={index} className="graphicHoverbox" span="24">
                                <Graphic
                                    icon={item.icon}
                                    title={ item.node_name && <SubTitle subtitle={{app_name:item.app_name,node_name:item.node_name}} /> }
                                    textDetails={item.app_run_name}
                                    handleClick={() => {
                                        if(item.need_human_confirm == 0){
                                            return
                                        }
                                        setDealtWithData(item);
                                        setRunId(null);
                                        setRunPanelLogRecord(false);
                                    }}
                                    backlogTips={<div className='flex items-center'>
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
                                                <CheckCircleOutlined className="text-[#52C41C]" />
                                            </Tooltip>
                                        )}
                                    </div>}
                                ></Graphic>
                            </Col>
                        ))}
                    </Row>
                </div>
            :<EmptyDom></EmptyDom>}
        </>

    )
}
// My Agent and Organization Agents
const Agent :React.FC<BlockParmas> = parmas =>{
    const  {data,keyName} = parmas;
    return (
        <div
            className={`cardbox`}
            style={{ overflowY: 'auto', height: '100%', overflowX: 'hidden' }}
        >
            <Row gutter={[30,0]}>
                {data.map((item: any, index: any) => (
                    <Col key={index} className="graphicHoverbox" span="12">
                        <Graphic
                            icon={item.icon}
                            title={item.name}
                            textDetails={item.description}
                            handleClick={() => {
                                // jumpDetails(index);
                                if(keyName == 'my_agent'){
                                    history.push(`/Agents?app_id=${item.app_id}&type=false`);
                                }else{
                                    history.push(`/ReadOnlyAgent?app_id=${item.app_id}&type=true`);
                                }
                            }}
                            // iconType={'robot_icon'}
                        ></Graphic>
                    </Col>
                ))}
            </Row>
        </div>

    )
}
// Workflow and OrganizationWorkflows
const Workflow :React.FC<BlockParmas> = parmas =>{
    let  {data,keyName} = parmas
    return (
        <div
            className={`cardbox`}
            style={{ overflowY: 'auto', height: '100%', overflowX: 'hidden' }}
        >
            <Row gutter={[30,0]}>
                {data.map((item: any, index: any) => (
                    <Col key={index} className="graphicHoverbox" span="12">
                            <Graphic
                                icon={item.icon}
                                title={item.name}
                                textDetails={item.description}
                                handleClick={() => {
                                    if(keyName == 'my_workflow'){
                                        history.push(`/workspace/workflow?app_id=${item.app_id}&type=false`);
                                    }else{
                                        history.push(`/workspace/workflow?app_id=${item.app_id}&type=true`);
                                    }
                                }}
                                operation={<OperationButton operationObj={item}></OperationButton>}
                                iconType={
                                    keyName == 'my_workflow'
                                        ? item.publish_status == 0
                                            ? 'play_disable_icon'
                                            : 'play_icon'
                                        : ''
                                }
                            ></Graphic>
                    </Col>
                ))}
            </Row>
        </div>

    )
}
// Run Logs
const RunLogs :React.FC<BlockParmas> = parmas =>{
    let  {data} = parmas;
    const intl = useIntl();
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    const setRunId = useUserStore(state => state.setRunId);
    const [runData,setRunData] = useState(data);
    const progressConcat = (progress: any, list: any) => {
        const map = new Map();
        list.reverse().forEach((item: any) => {
            map.set(item.app_run_id, item);
        });
        progress.forEach((item: any) => {
            map.set(item.app_run_id, item); // Use the key attribute value as the key to store each object in the map
        });
        return Array.from(map.values()).reverse();
    };
    const setpercentage = (item: any) => {
        if (item.completed_progress) {
            return parseInt(item.completed_progress.slice(0, -1));
        } else {
            return false;
        }
    };
    const setWebsocktdata = async () => {
        let progress = flowMessage?.filter(item => item.type == 'workflow_run_progress').map(({ data }) => data);
        if(progress && progress.length){
            setRunData(progressConcat(progress,runData))
        }
    };
    //websockt
    const flowMessage = useSocketStore(state => state.flowMessage);
    useEffect(() => {setWebsocktdata();}, [flowMessage]);
    
    return (
        <>
            {runData && runData.length?
                <div
                    className={`cardbox px-[10px]`}
                    style={{ overflowY: 'auto', height: '100%', overflowX: 'hidden' }}
                >
                    <Row gutter={[30,20]}>
                        {runData.map((item: any, index: any) => (
                            <Col key={index} className="graphicHoverbox" span="24">
                                    <Graphic
                                        status={item.status}
                                        icon={item.icon}
                                        title={
                                            <div className='items-center gap-x-[8px] inline-flex justify-end w-full'>
                                                <span className='flex-1 truncate'>{item.app_runs_name || item.run_name}</span>
                                                {item.status==2?1:0}
                                                {item?.need_human_confirm==1?<Tag className=' text-[12px] flex items-center justify-center margin-0' color="blue">{intl.formatMessage({id:'app.summaryhistory.tag'})}</Tag>:<></>}
                                            </div>
                                        }
                                        textDetails={
                                            <ProgressContainer progressObj={item}></ProgressContainer>
                                        }
                                        handleClick={() => {
                                            setRunPanelLogRecord(item);
                                            setRunId(null);
                                            setDealtWithData(false);
                                        }}
                                        progress={item.percentage || setpercentage(item)}
                                    ></Graphic>
                            </Col>
                        ))}
                    </Row>
                </div>
            :<EmptyDom></EmptyDom>}
        </>
    )
}

// CONTENT LIST
interface contentListparmas{
    item?:any,
    data?:any
}
const ContentList : React.FC<contentListparmas> = params =>{
    let {item,data} = params;
    const isEmptyDom = (data:any,components:any) =>{ 
        return data && data.length ? components : <EmptyDom></EmptyDom>
    }
    let components = {
        'backlogs':(e:any)=><Backlogs data={e.data}></Backlogs>,
        'my_agent':(e:any)=>isEmptyDom(data,<Agent data={e.data} keyName='my_agent'></Agent>),
        'my_workflow':(e:any)=>isEmptyDom(data,<Workflow data={e.data} keyName='my_workflow'></Workflow>),
        'workflow_log':(e:any)=><RunLogs data={e.data}></RunLogs>,
        'more_agent':(e:any)=>isEmptyDom(data,<Agent data={e.data}></Agent>),
        'more_workflow':(e:any)=>isEmptyDom(data,<Workflow data={e.data}></Workflow>),
    }
    return(
        <>
            { components[item.key]({data})}
        </>
    )
}
// View all button
const MoreList : React.FC<{ item?: any }> = parmas => {
    let {item} = parmas;
    const intl = useIntl();
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
interface MoreOrAddparmas{
    item?:any,
    setIsModalOpen?:any,
    setCreationType?:any
}
const MoreOrAdd :React.FC<MoreOrAddparmas> = parmas => {
    const intl = useIntl();
    let {item,setIsModalOpen,setCreationType} = parmas
    const Addel = () => {
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
            <MoreList item={item}></MoreList>
        </div>
    );
};
// Main body
const Coldom : React.FC = () => {
    const intl = useIntl();
// Card configuration file
    const cardList = [
        {
            title: intl.formatMessage({ id: 'app.dashboard.backlog' }),
            key: 'backlogs',
            substitle: true,
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
    const [closeLoading, setcloseLoading] = useState(true);
    const [contntList,setContntList] = useState({})
    // Has retrieved list
    const isLoad = useRef(false);
    // Get list
    const getCardList = async () => {
        let res = await getIndex();
        if (res.code == 0) {
            let data = res.data;
            setContntList(data)
            isLoad.current = true;
            setcloseLoading(true);
        }
    };
    useEffect(()=>{
        if(!isLoad.current)getCardList();
    },[])

    return (
        <>
            {closeLoading &&
                cardList.map((item: any, index: any) => (
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
                        <div
                            className="bg-[#fff] rounded-[8px] w-[100%] h-[100%]"
                            style={{ boxShadow: '0px 2px 4px 0px rgba(0,0,0,0.05)' }}
                        >
                            <div className="text-[14px] p-[20px] text-[#213044] flex">
                                <span className="flex-1 font-[500] text-[#213044]">
                                    {item.title}
                                </span>
                                <span>
                                    {
                                        <MoreOrAdd 
                                            item={item}
                                            setIsModalOpen={setIsModalOpen}
                                            setCreationType={setCreationType}
                                        />
                                    }
                                </span>
                            </div>
                            <div
                                className="pt-[5px] pb-[20px] px-[10px]"
                                style={{ height: 'calc(100% - 62px)' }}
                            >   
                                {contntList[item.key] ? <ContentList item={item} data={contntList[item.key]} ></ContentList> :<></>}                          
                            </div>
                        </div>
                    </Col>
                ))
            }
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
