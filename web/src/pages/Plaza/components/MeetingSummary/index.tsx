import React, { memo, useEffect, useRef, useState } from 'react';
import useChatroomStore from '@/store/chatroomstate'
import DraggablePanel from '@/components/Panel/DraggablePanel';
import type { MenuProps } from 'antd';
import { Empty,Input,Button,Dropdown,Form,Spin} from 'antd';
import { getWorkFlowStartCondition } from '@/api/workflow';
import {AppstoreAddOutlined,VerticalLeftOutlined,VerticalRightOutlined,InfoCircleOutlined} from '@ant-design/icons'
import { useIntl } from '@umijs/max';
import SelectAppDom from '../CreationChatRoom/selectApp'
import Graphic from '@/components/Graphic';
import { getMeetingsummary,getMeetingOrientation,getMeetingSummaryHistory } from '@/api/plaza';
import useSocketStore from '@/store/websocket';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import { ProForm } from '@ant-design/pro-components';
import { RenderConfirm } from '@/components/WorkFlow/components/RunForm/RenderConfirm';
import { RenderInput } from '@/components/WorkFlow/components/RunForm/RenderInput';
import {runWorkFlow } from '@/api/workflow';

const SummaryHistoryDom=memo((object:any)=>{
    const summaryHistory = object.list
    return(
        <>
            <div className='px-4'>
                {
                    summaryHistory&&summaryHistory.length?summaryHistory.map(item=>(
                        item?.source_run?
                            <div className='pt-[16px] border-b-[1px] border-color-[#eee]' key={item.source_run.id}>
                               {/* <div className='pb-[12px]'>
                                    <div className='text-[16px] font-[600]'>总结时间:</div>
                                    <div className='text-[14px] pt-[6px] px-[12px]'>{item.source_run.created_time}</div>
                               </div> */}
                               <div className='pb-[12px]'>
                                    <div className='text-[16px] font-[600] pb-[8px]'>总结内容:</div>
                                    <div className='px-[12px]'>
                                        <ReactMarkdown  rehypePlugins={[rehypeHighlight]}>
                                            {item?.source_run?.summary}
                                        </ReactMarkdown>
                                    </div>
                               </div>
                                
                            </div>
                        :<></>
                    )):<></>
                }
            </div>
        </>
    )
}
)
const RevisionsSummaryContent:React.FC<{id:any,runid:any,revisionsFn:any,setShow:any}>=params=>{
    let {runid,id,revisionsFn,setShow}=params
    const intl = useIntl();
    const [summaryContent,setSummaryContent] = useState('');
    const [revisions,setRevisions] = useState('');
    const [spinShow,setSpinShow] = useState(false);
    const meetingSummary = useSocketStore(state=>state.flowMessage);
    useEffect(()=>{
        let mettingSummary  =  meetingSummary.filter(item=>item.data.app_run_id == runid && item.type.indexOf('generate_meeting_summary')!==-1);
        if(mettingSummary.length!=0){
            const outputs = mettingSummary[mettingSummary.length-1]?.data?.exec_data?.outputs?.value;
            if(outputs){
              setSummaryContent(outputs)
              setShow(true)
              setSpinShow(false)
            }
        }        
     },[meetingSummary])
    return(
        <div className='pb-[16px]'>
            <div className='text-[16px] font-[600] pt-[12px]'>{intl.formatMessage({ id: `app.summary.title` })}</div>
            <div className='text-[14px] pt-[12px] leading-[23px] px-[8px]'>
                {summaryContent?
                    <div className={`max-h-[400px]  relative ${!spinShow?'overflow-y-auto':'overflow-hidden'}`}>
                        <ReactMarkdown  rehypePlugins={[rehypeHighlight]}>
                            {summaryContent}
                        </ReactMarkdown>
                        {spinShow?<div className='absolute top-0 left-0 w-full h-full flex items-center justify-center bg-[rgba(255,255,255,0.5)]'>
                            <Spin size="large" />
                        </div>:<></>}
                    </div>
                    :
                    <div className='min-h-[120px] flex items-center justify-center'><Spin size="large" /></div>}    
            </div>
            <div className='pt-[12px]'>
                <Input.TextArea onChange={(e)=>{setRevisions(e.target.value)}} value={revisions}  disabled={!summaryContent} rows={4} placeholder={intl.formatMessage({id:'app.summary.placeholder'})}></Input.TextArea>
            </div>
            <div className='flex pt-[12px] gap-x-[4px]'>
                <Button
                    type="primary"
                    disabled={!summaryContent || !revisions}
                    className="bg-[#1B64F3] rounded-[4px] w-[88px] h-[40px] flex-1"
                    onClick={()=>{
                        revisionsFn(id,{
                            'app_run_id':String(runid),
                            'corrected_parameter':revisions
                        })
                        setRevisions('')
                        setSpinShow(true)
                        setShow('')
                    }}
                >
                    {intl.formatMessage({ id: `app.summary.submitText` })}
                </Button>
            </div>
        </div>
    )
}
const RevisionsMeetingSummary = memo(RevisionsSummaryContent);

const RunsSummaryContent:React.FC<{id:any,runid:any,runboxShow:any,setBoxLoading:any,scrollDom:any}>=params=>{
    const intl = useIntl();
    const {runboxShow,runid,id,setBoxLoading,scrollDom} = params
    const [currentVariate,setcurrentVariate] = useState(null)
    const [confirmNodes,setConfirmNodes] = useState(null)
    const [selectedType,setSelectedType] = useState('agent')
    const [selectApp,setSelectApp] = useState({
        type:'agent',
        checkItem:[],
        show:false
    })
    const [runData,setRunData]=useState([])
    const appId = useRef('');
    const originalVariate = useRef(null)
    const RunsId= useRef('')
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
    const items:MenuProps['items'] = [
        {
            key: '1',
            label: (
                <div className='hover:text-[#1B64F3]' onClick={
                    ()=>{
                        setSelectApp(pre=>{return {...pre,type:'agent',show:true}})
                    }
                }>{intl.formatMessage({id:'app.summary.SelectAgent'})}</div>
            ),
        },
        {
            key: '2',
            label: (
                <div className='hover:text-[#1B64F3]' onClick={
                    ()=>{
                        setSelectApp(pre=>{return {...pre,type:'workflow',show:true}})
                    }
                }>{intl.formatMessage({id:'app.summary.SelectWorkflow'})}</div>
            ),
        },
    ]
    const getMeetingOrientationfn = async(id:any,data:any)=>{
        let resData = await getMeetingOrientation(id,data); 
        if(resData?.code == 0){
            RunsId.current=resData?.data?.app_run_id
        }
    }
    const getWorkFlowStart = async(appid,type)=>{
        if(type!='agent'){
            let resData = await getWorkFlowStartCondition(appid);
            if(resData.code == 0){
                setConfirmNodes(resData?.data?.need_confirm_nodes);
            }
        }
        getMeetingOrientationfn(id,{
            app_id:appid,
            app_run_id:runid,
            status:1,
            corrected_parameter:'',
        })
    }
    const popupClose=()=>{
        setSelectApp(pre=>{return {...pre,show:false}})
    }
    const popupSave=params=>{
        setBoxLoading(true)
        setSelectApp(pre=>{return {...pre,checkItem:params.checkItem}})
        setSelectedType(selectApp.type)
        getWorkFlowStart(params.checkItem[0].app_id,selectApp.type)
        appId.current = params.checkItem[0].app_id;
        setTimeout(()=>{
            scrollDom.current.scrollTo({top: scrollDom.current.scrollHeight});
        },200)
    }
    const setpercentage = (item: any) => {
        if (item.completed_progress) {
            return parseInt(item.completed_progress.slice(0, -1));
        } else {
            return false;
        }
    };
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
    const setWebsocktdata = async () => {
        let progress = flowMessage?.filter(item => item.type == 'workflow_run_progress').map(({ data }) => data);
        if(progress && progress.length){
            setRunData(progressConcat(progress,runData))
            console.log(runData);
            
        }
    };
    useEffect(()=>{
        if(runboxShow){
            setSelectApp({type:'agent',checkItem:[],show:false})
        }
    },[runboxShow])
    const flowMessage = useSocketStore(state=>state.flowMessage);
    useEffect(()=>{
        setWebsocktdata();
        let runSummary  =  flowMessage.filter(item=>item.data.app_run_id == runid && item.type.indexOf('generate_meeting_action_items')!==-1);
        if(runSummary.length != 0){
            const outputs = runSummary[runSummary.length-1]?.data?.exec_data?.outputs?.value;
            if(outputs){
                let object = JSON.parse(outputs);
                originalVariate.current = object
                let prokeys = Object.keys(object.properties);
                if(prokeys.length){
                    setcurrentVariate(object.properties)
                }
                setBoxLoading(false)
            }
        }  
    },[flowMessage])

    return (
        <>
            {
                runboxShow?
                    <div className={`pt-[24px]  border-[#ddd] ${selectApp?.checkItem?.length?'h-full':''}`}  >
                        <div className='text-[14px] font-[500] flex item-center'>
                            <div className='flex-1'>{intl.formatMessage({ id: `app.summary.Runapp` })}</div>
                            <div className='px-[10px]'>
                                <Dropdown menu={{items}}>
                                    <AppstoreAddOutlined className='transition cursor-pointer text-[#999] text-[18px] hover:text-[#1B64F3]'/>
                                </Dropdown> 
                            </div>
                        </div>
                        <div>
                            {
                                selectApp?.checkItem?.length?
                                    <>
                                        <div className='py-[6px]'>
                                            <Graphic
                                                icon={selectApp?.checkItem[0]?.icon}
                                                title={selectApp?.checkItem[0]?.name}
                                                textDetails={selectApp?.checkItem[0]?.description}
                                                iconType={selectedType=='agent'?'robot_icon':'workflow_icon'}
                                                handleClick={() => {}}
                                            />
                                        </div>
                                        <ProForm
                                            submitter={{
                                                resetButtonProps: false,
                                                submitButtonProps: {
                                                    className: 'w-full',
                                                },
                                                searchConfig: {
                                                    submitText: intl.formatMessage({
                                                        id: 'workflow.button.run',
                                                    }),
                                                },
                                            }}
                                            onFinish={ async(e)=>{

                                                let keys = Object.keys(e);
                                                let node_confirm_users = {};
                                                keys.forEach(item=>{
                                                    if(originalVariate.current.properties[item]){
                                                        originalVariate.current.properties[item].value = e[item]
                                                    }
                                                    if(confirmNodes){
                                                        confirmNodes.forEach(citem=>{
                                                            if(citem.node_id == item){
                                                                node_confirm_users[item] = e[item]
                                                            }
                                                        })
                                                    }
                                                })
                                                let params = {inputs:originalVariate.current,node_confirm_users,run_name:`chatroom-${id}-run-${RunsId.current}-driven`,run_type:1}
                                                
                                                let res = await runWorkFlow(appId.current,params);
                                                

                                                
                                            }}
                                        >
                                            <div className='py-[6px]'>
                                                <RenderInput data={currentVariate}/>
                                            </div>
                                            <RenderConfirm data={confirmNodes} />
                                        </ProForm>
                                        {
                                            runData.length?
                                                <div>
                                                    {
                                                        runData.map((item,index)=>(
                                                            <div className='pt-[10px]' key={index}>
                                                                <div className='py-[12px]'>
                                                                    <div className='flex gap-x-[6px] items-center'><div><InfoCircleOutlined className='text-[#1B64F3] text-[16px]'/></div><span>{intl.formatMessage({id:'app.summary.backlogTips'})}</span></div>
                                                                </div>
                                                                <Graphic
                                                                    status={item.status}
                                                                    icon={item.icon}
                                                                    title={item.run_name}
                                                                    textDetails={
                                                                        <ProgressContainer progressObj={item}></ProgressContainer>
                                                                    }
                                                                    handleClick={() => {
                                                                        // setRunPanelLogRecord(item);
                                                                        // setRunId(null);
                                                                        // setDealtWithData(false);
                                                                    }}
                                                                    progress={0 || setpercentage(item)}
                                                                ></Graphic>
                                                            </div>
                                                        ))
                                                    }
                                                </div>
                                            :<></>
                                            
                                        }
                                        
                                    </>
                                :
                                <div className='flex gap-x-[20px] min-h-[70px] items-center px-[20px]'>
                                    <Button className='flex-1 text-[14px]' onClick={
                                        ()=>{
                                            setSelectApp(pre=>{return {...pre,type:'agent',show:true}})
                                        }
                                    }
                                    >
                                        <img
                                            src={`/icons/robot_icon.svg`}
                                            alt=""
                                            className="w-[14px] h-[14px]"
                                        />
                                        {intl.formatMessage({id:'app.summary.SelectAgent'})}
                                    </Button>
                                    <Button className='flex-1 text-[14px]'onClick={ 
                                        ()=>{
                                            setSelectApp(pre=>{return {...pre,type:'workflow',show:true}})
                                        }
                                    } >
                                        <img
                                            src={`/icons/workflow_icon.svg`}
                                            alt=""
                                            className="w-[14px] h-[14px]"
                                        />
                                        {intl.formatMessage({id:'app.summary.SelectWorkflow'})}
                                    </Button>
                                </div>
                            }
                        </div>
                        
                    </div>
                :<></>
            }
            <SelectAppDom 
                show={selectApp.show} 
                nodetype={selectApp.type} 
                popupClose={popupClose} 
                popupSave={popupSave} 
                checkList={
                    selectedType == selectApp.type?selectApp.checkItem:[]
                }  
                zIndex={99}
                radio={true}
            />
        </>
    )
}
const RunsMeetingSummary = memo(RunsSummaryContent)

const MeetingSummary:React.FC<{id:any}>= params =>{
    const {id} = params
    const [contentShow,setContentShow] = useState(false);
    const [summaryShow,setSummaryShow] = useState(false);
    const [runboxShow,setRunboxShow] = useState(false);
    const [summaryHistory,setSummaryHistory] = useState([]);
    const [roomId,setRoomId] = useState('')
    const [appRunId,setAppRunId] = useState('');
    const [packUp,setPackUp] = useState(false);
    const scrollDom = useRef(null)
    const [boxLoading,setBoxLoading] = useState(false)

    const getMeetingsummaryfn = async(id:any,data:any={
        "app_run_id":"",
        "corrected_parameter":""
    })=>{
        let resData = await getMeetingsummary(id,data); 
        if(resData?.code == 0){
            setContentShow(true);
            setSummaryShow(true)
            setAppRunId(resData?.data?.app_run_id)
            setTimeout(()=>{
                scrollDom.current.scrollTo({top: scrollDom.current.scrollHeight});
            },200)
        }
    }

    const getSummaryHistory=async()=>{
        let resData=await getMeetingSummaryHistory({
            'chatroom_id':id,
            'page':1,
            'page_size':9999
        })
        if(resData.code == 0){
            if(resData?.data?.list && resData?.data?.list?.length){
                setContentShow(true);
                setSummaryHistory(resData.data.list);
                setTimeout(()=>{
                    scrollDom.current.scrollTo({top: scrollDom.current.scrollHeight});
                })
            }
           
        }
    }
    
    useEffect(()=>{
        getSummaryHistory()
    },[id])

    const summaryParams = useChatroomStore(state=>state.summaryParams);
    const setSummaryParams = useChatroomStore(state=>state.setSummaryParams);
    useEffect(()=>{
        if(summaryParams && summaryParams.id){
            getMeetingsummaryfn(summaryParams.id)
            setRoomId(summaryParams.id)
            setSummaryParams({})
        }
    },[summaryParams])
    
    return (
        <>
            
            {
                contentShow ? 
                    <DraggablePanel
                        minWidth={400}
                        className={`relative h-full right-0 border-0 returned-0 px-[0] ${packUp?'translate-x-full flex-[0]':''}`}
                    >
                        {boxLoading?<div className='h-full w-full absolute top-0 left-0 flex justify-center items-center z-20 bg-[rgba(255,255,255,0.5)]'><Spin size="large" /></div>:<></>}
                        {
                            <>
                                <div onClick={()=>{ setPackUp(pre=>!pre)}} className={`
                                        ${!packUp?'right-[6px] top-[60px]':'right-[100%] top-[4px]' }
                                        fixed   w-[40px] h-[40px]  flex justify-center items-center cursor-pointer
                                    `}>
                                   {!packUp?<VerticalLeftOutlined className='text-[20px]'/>:<VerticalRightOutlined className='text-[20px]'/>}
                                </div>
                                <div className='h-full overflow-y-auto' ref={scrollDom}>
                                    {summaryHistory.length?<SummaryHistoryDom list={summaryHistory}/>:<></>}
                                    {
                                       summaryShow?<div className='w-full px-4 h-full'>
                                            <RevisionsMeetingSummary 
                                                id={roomId} 
                                                runid={appRunId} 
                                                revisionsFn={getMeetingsummaryfn}
                                                setShow={setRunboxShow}
                                            />
                                            <RunsMeetingSummary
                                                id={roomId} 
                                                runid={appRunId}
                                                runboxShow={runboxShow}
                                                setBoxLoading={setBoxLoading}
                                                scrollDom={scrollDom}
                                            />
                                        </div>:<></>
                                    }   
                                </div>
                            </>
                        }
                    </DraggablePanel>
                :<></>
            }
            
        </>
    )

}

export default memo(MeetingSummary)