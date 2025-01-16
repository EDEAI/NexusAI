import React, { memo, useEffect, useRef, useState } from 'react';
import type { MenuProps } from 'antd';
import { Button,Dropdown,Tag} from 'antd';
import { getWorkFlowStartCondition , runWorkFlow } from '@/api/workflow';
import {AppstoreAddOutlined,InfoCircleOutlined} from '@ant-design/icons'
import { useIntl } from '@umijs/max';
import SelectAppDom from '../../CreationChatRoom/selectApp'
import Graphic from '@/components/Graphic';
import { getMeetingOrientation } from '@/api/plaza';
import { ProForm } from '@ant-design/pro-components';
import { RenderConfirm } from '@/components/WorkFlow/components/RunForm/RenderConfirm';
import { RenderInput } from '@/components/WorkFlow/components/RunForm/RenderInput';
import SlateEditor from '@/components/WorkFlow/components/Editor/SlateEditor';
import { CURRENT_NODE_ID } from '@/components/WorkFlow/config';
import { createPromptFromObject } from '@/py2js/prompt.js';
import { PutagentRun } from '@/api/agents';
import useUserStore from '@/store/user';
import useSocketStore from '@/store/websocket';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';

interface params {
    id:any;
    runid:any;
    setBoxLoading:any;
    scrollDom:any;
    setinputShow:any;
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

const RunsMeetingSummary:React.FC<params>=(params)=>{
    const intl = useIntl();
    const {runid,id,setBoxLoading,scrollDom,setinputShow} = params
    const [currentVariate,setcurrentVariate] = useState(null)
    const [confirmNodes,setConfirmNodes] = useState(null)
    const [selectedType,setSelectedType] = useState('agent')
    const [selectApp,setSelectApp] = useState({
        type:'agent',
        checkItem:[],
        show:false
    })
    const [currentVariateArray,setcurrentVariateArray] = useState([])
    const [fourthly_prompt, setFourthly_prompt] = useState('');
    const [runStart,setRunStart] = useState(false)
    const [runData,setRunData]=useState(null)
    const [backData,setbackData]=useState(null)
    const [putsmd,setPutsMd]=useState('')
    const appId = useRef('');
    const originalVariate = useRef(null)
    const RunsId= useRef('')
    
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);

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
        setcurrentVariate(null)
        setSelectApp(pre=>{return {...pre,checkItem:params.checkItem}})
        setSelectedType(selectApp.type)
        getWorkFlowStart(params.checkItem[0].app_id,selectApp.type)
        appId.current = params.checkItem[0].app_id;
        setTimeout(()=>{
            scrollDom.current.scrollTo({top: scrollDom.current.scrollHeight});
        },300)
    }
    const setpercentage = (item: any) => {
        if (item.completed_progress) {
            return parseInt(item.completed_progress.slice(0, -1));
        } else {
            return false;
        }
    };
    const Editorrunchange = (value: any) => {
        const promptObj = {
            user: {
                value: serialize(value),
            },
        };
        setFourthly_prompt(new createPromptFromObject(promptObj));
    };
    const serialize = (nodes: any) => {
        return nodes
            .map((node: any) => {
                if (node.type === 'mention') {
                    return node.id;
                } else if (node.children) {
                    return serialize(node.children);
                } else {
                    return node.text;
                }
            })
            .join('');
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
        
        let res = await runWorkFlow(appId.current,params);
        
        if(res.code == 0){
            RunsId.current=res?.data?.app_run_id
            setRunStart(true)
        }
    };
    const agentRun=async(e)=>{
        setBoxLoading(true)
        let keys = Object.keys(e);
        keys.forEach(item=>{
            if(originalVariate.current.properties[item]){
                originalVariate.current.properties[item].value = e[item]
            }
        })
        let res = await PutagentRun({
            agent_id: selectApp.checkItem[0].agent_id,
            ability_id: 0,
            input_dict: originalVariate.current,
            prompt: fourthly_prompt,
            data_source_run_id:RunsId.current
        });
        if(res.code == 0){
            setPutsMd(res.data.outputs_md)
            setBoxLoading(false)
            // setRunStart(true)
        }
    }

    // useEffect(()=>{
    //     if(runboxShow){
    //         setSelectApp({type:'agent',checkItem:[],show:false})
    //         setcurrentVariate(null);
    //     }
    // },[runboxShow])

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
                    if(selectedType=='agent'){
                        let newArr = prokeys.map((item: any) => { return { value: `<<${CURRENT_NODE_ID}.inputs.${item}>>`, label: item }})
                        setcurrentVariateArray(newArr)
                    }
                }
                setinputShow(false)
                setBoxLoading(false)
            }
        }  
    },[flowMessage])


    return (
        <>
            {
                <div className={`pt-[24px]  border-[#ddd]`} style={{minHeight:selectApp?.checkItem?.length?scrollDom?.current?.offsetHeight:'100%'}} >
                    <div className='text-[14px] font-[500] flex item-center'>
                        <div className='flex-1'>{intl.formatMessage({ id: `app.summary.Runapp` })}</div>
                        <div className='px-[10px]'>
                            {!runStart && !putsmd?<Dropdown menu={{items}}>
                                <AppstoreAddOutlined className='transition cursor-pointer text-[#999] text-[18px] hover:text-[#1B64F3]'/>
                            </Dropdown> 
                            :<></>}
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
                                   

                                    {!runStart && currentVariate!=null ? 
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
                                        onFinish={(e)=>{
                                            selectedType=='workflow'?workflowRun(e):agentRun(e)
                                        }}
                                    >
                                        <div className='py-[6px]'>
                                            <RenderInput data={currentVariate}/>
                                        </div>
                                        
                                        {selectedType=='workflow'?
                                            <RenderConfirm data={confirmNodes} />
                                            :
                                            <div className='h-[150px] overflow-y-auto border border-color-[#eee] py-[4px] px-[11px] mb-[8px]'>
                                                <SlateEditor  
                                                    onChange={value => {Editorrunchange(value)}}
                                                    options={currentVariateArray} >
                                                </SlateEditor>
                                            </div>
                                        }
                                    </ProForm>:<></>}

                                    {
                                        putsmd? 
                                            <div className='max-h-[400px] overflow-y-auto mt-[16px]'>
                                                <div className='p-[12px]  bg-[#F7F7F7] leading-[22px]'>
                                                    <ReactMarkdown  rehypePlugins={[rehypeHighlight]}>
                                                        {putsmd}
                                                    </ReactMarkdown>
                                                </div>
                                            </div>
                                        :<></>

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

export default memo(RunsMeetingSummary)