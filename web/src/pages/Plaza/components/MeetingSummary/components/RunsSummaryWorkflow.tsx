import React, { FC, memo, useEffect, useRef, useState } from 'react';
import {Tag} from 'antd';
import { getWorkFlowStartCondition , runWorkFlow } from '@/api/workflow';
import {InfoCircleOutlined} from '@ant-design/icons'
import { useIntl } from '@umijs/max';
import Graphic from '@/components/Graphic';
import { getMeetingOrientation } from '@/api/plaza';
import { ProForm } from '@ant-design/pro-components';
import { RenderConfirm } from '@/components/WorkFlow/components/RunForm/RenderConfirm';
import { RenderInput } from '@/components/WorkFlow/components/RunForm/RenderInput';
import useUserStore from '@/store/user';
import useSocketStore from '@/store/websocket';

interface params {
    id:any;
    appId:any;
    selectApp:any;
    runid:any;
    setBoxLoading:any;
    scrollDom:any;
    setinputShow:any;
    setisRun:any
}
// Progress bar subtitle
const ProgressContainer :React.FC<{progressObj:any}> = memo((parmas) => {
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
});

const RunsWorkFlow:FC<params>=(params) =>{
    const {selectApp,runid,setBoxLoading,setinputShow,appId,id,setisRun}=params;
    const intl = useIntl();
    const RunsId= useRef('');
    const originalVariate = useRef(null)
    const [runData,setRunData]=useState(null)
    const [runStart,setRunStart] = useState(false)
    const [currentVariate,setcurrentVariate] = useState(null)
    const [confirmNodes,setConfirmNodes] = useState(null)
    const [backData,setbackData]=useState(null)
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const workflowRun=async(e)=>{
        setBoxLoading(true)
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
        let params = {inputs:originalVariate.current,node_confirm_users,run_name:`chatroom-${id}-run-${RunsId.current}-driven`,run_type:1,data_source_run_id:RunsId.current}
        
        let res = await runWorkFlow(appId,params);
        
        if(res.code == 0){
            RunsId.current=res?.data?.app_run_id
            setRunStart(true)
            setisRun(false)
        }
    };
    const setWebsocktdata = async () => {
        let progress = flowMessage?.filter(item => item.type == 'workflow_run_progress' && item.data.app_run_id == RunsId.current).map(({ data }) => data);
        if(progress && progress.length){
            let obj = progress[progress.length-1]
            setRunData(obj);
            setBoxLoading(false)
        }
    };
    const backlogSetWebsocktdata = async () => {
        let backDatas = flowMessage?.filter(item => item.type == 'workflow_need_human_confirm' && item.data.app_run_id == RunsId.current);     
        
        let backlogs = backDatas.map(({ data,need_human_confirm }) => ({data,need_human_confirm}))?.filter(item => item.data.type !== 1)
            
        if(backlogs && backlogs.length){
            let data = backlogs[backlogs.length-1].data
            data.exec_id = data?.node_exec_data?.node_exec_id
            setbackData(backlogs[backlogs.length-1])
            setBoxLoading(false)
        }
    };
    const setpercentage = (item: any) => {
        if (item.completed_progress) {
            return parseInt(item.completed_progress.slice(0, -1));
        } else {
            return false;
        }
    };
    const getMeetingOrientationfn = async(id:any,data:any)=>{
        let resData = await getMeetingOrientation(id,data); 
        if(resData?.code == 0){
            RunsId.current=resData?.data?.app_run_id
        }
    }
    const getWorkFlowStart = async()=>{
    
        
        let resData = await getWorkFlowStartCondition(appId);
        if(resData.code == 0){
            setConfirmNodes(resData?.data?.need_confirm_nodes);
        }
        getMeetingOrientationfn(id,{
            app_id:appId,
            app_run_id:runid,
            status:1,
            corrected_parameter:'',
        })
    }
    useEffect(()=>{
        if(selectApp && selectApp.checkItem.length){
            setisRun(true)
            getWorkFlowStart()
        }
    },[selectApp])
    const flowMessage = useSocketStore(state=>state.flowMessage);
    useEffect(()=>{
        setWebsocktdata();
        backlogSetWebsocktdata();
        let runSummary  =  flowMessage.filter(item=>item.data.app_run_id == runid && item.type.indexOf('generate_meeting_action_items')!==-1);
        if(runSummary.length != 0){
            const outputs = runSummary[runSummary.length-1]?.data?.exec_data?.outputs?.value;
            if(outputs){
                let object = JSON.parse(outputs);
                originalVariate.current = object
                let prokeys = Object.keys(object.properties);
                if(prokeys.length){
              
                    
                    setcurrentVariate(object.properties);
                }
                setinputShow(false)
                setBoxLoading(false)
            }
        }  
    },[flowMessage])
    return (
        <div>
            <div className='py-[6px]'>
                <Graphic
                    icon={selectApp?.checkItem[0]?.icon}
                    title={selectApp?.checkItem[0]?.name}
                    textDetails={selectApp?.checkItem[0]?.description}
                    iconType='workflow_icon'
                    avatar={selectApp?.checkItem[0]?.avatar}
                    handleClick={() => {}}
                />
            </div>
            {!runStart && currentVariate!=null? 
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
                    onFinish={workflowRun}
                >
                    <div className='py-[6px]'>
                        <RenderInput data={currentVariate}/>
                    </div>
                    <RenderConfirm data={confirmNodes} />
                </ProForm>
                :<>
                    {currentVariate!=null?<div>
                        <div className='text-[16px] color-[#000] font-[600] py-[12px]'>{intl.formatMessage({id:'app.summaryhistory.input'})}:</div>
                        {Object.values(currentVariate).map((item:any)=>(
                            <div className='pb-[10px]'>
                                    <div className='pb-[8px] font-[600]'>{item.display_name || item.name}</div>
                                    
                                <div className='py-[4px] px-[11px] text-[14px] leading-[1.5] '>{item.value}</div>
                            </div>
                        ))}
                    </div>:<></>}
                </>
            }
            
            {backData &&  backData.need_human_confirm != 0?
                <div className='pt-[12px]'>
                    <div className='flex gap-x-[6px] items-center h-[20px] cursor-pointer' onClick={()=>{setDealtWithData(backData.data)}}>
                        <div><InfoCircleOutlined className='text-[#1B64F3] text-[16px]'/></div>
                        <span>{intl.formatMessage({id:'app.summary.backlogTips'})}</span>
                    </div>
                </div>:<></>
            } 
            {
                runData?
                    <div className='pt-[10px]'>       
                        <Graphic
                            status={runData.status}
                            icon={runData.icon}
                            title={
                                <div className='items-center gap-x-[8px] inline-flex justify-end w-full'>
                                    <span className='flex-1 truncate'>{runData.run_name}</span>
                                    {runData.need_human_confirm==1?<Tag className=' text-[12px] flex items-center justify-center margin-0' color="blue">{intl.formatMessage({id:'app.summaryhistory.tag'})}</Tag>:<></>}
                                </div>
                            }
                            textDetails={
                                <ProgressContainer progressObj={runData}></ProgressContainer>
                            }
                            handleClick={() => {
                                setRunPanelLogRecord(runData);
                            }}
                            progress={0 || setpercentage(runData)}
                        ></Graphic>
                    </div>
                :<></>
            }
        </div>
    )
}

export default memo(RunsWorkFlow)