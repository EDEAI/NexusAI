import React, { FC, memo, useEffect, useRef, useState } from 'react';
import { useIntl } from '@umijs/max';
import Graphic from '@/components/Graphic';
import { getMeetingOrientation } from '@/api/plaza';
import { ProForm } from '@ant-design/pro-components';
import { RenderInput } from '@/components/WorkFlow/components/RunForm/RenderInput';
import SlateEditor from '@/components/WorkFlow/components/Editor/SlateEditor';
import { CURRENT_NODE_ID } from '@/components/WorkFlow/config';
import { createPromptFromObject } from '@/py2js/prompt.js';
import { PutagentRun } from '@/api/agents';
import useSocketStore from '@/store/websocket';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';

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

const RunsAgent:FC<params>=(params) =>{
    const {selectApp,runid,setBoxLoading,setinputShow,appId,id,setisRun}=params;
    const intl = useIntl();
    const RunsId= useRef('');
    const slateEditorval = useRef('');
    const originalVariate = useRef(null);
    const [putsmd,setPutsMd]=useState('')
    const [currentVariate,setcurrentVariate] = useState(null);
    const [currentVariateArray,setcurrentVariateArray] = useState([])
    const [fourthly_prompt, setFourthly_prompt] = useState('');
    const flowMessage = useSocketStore(state=>state.flowMessage);
    const Editorrunchange = (value: any) => {
        slateEditorval.current = serialize(value)
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
            setisRun(false)
        }
    };
    const getMeetingOrientationfn = async(id:any,data:any)=>{
        let resData = await getMeetingOrientation(id,data); 
        if(resData?.code == 0){
            RunsId.current=resData?.data?.app_run_id
        }
    }    
    useEffect(()=>{
        if(selectApp && selectApp.checkItem.length){
            setisRun(true)
            getMeetingOrientationfn(id,{
                app_id:appId,
                app_run_id:runid,
                status:1,
                corrected_parameter:'',
            })
        }
    },[selectApp])
    useEffect(()=>{
        let runSummary  =  flowMessage.filter(item=>item.data.app_run_id == runid && item.type.indexOf('generate_meeting_action_items')!==-1);
        if(runSummary.length != 0){
            const outputs = runSummary[runSummary.length-1]?.data?.exec_data?.outputs?.value;
            if(outputs){
                let object = JSON.parse(outputs);
                originalVariate.current = object
                let prokeys = Object.keys(object.properties);
                if(prokeys.length){
                    setcurrentVariate(object.properties);
                    let newArr = prokeys.map((item: any) => { return { value: `<<${CURRENT_NODE_ID}.inputs.${item}>>`, label: item }})
                    setcurrentVariateArray(newArr)
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
                    iconType='robot_icon'
                    avatar={selectApp?.checkItem[0]?.avatar}
                    handleClick={() => {}}
                />
            </div>
            { currentVariate!=null ? 
                <ProForm
                    submitter={{
                        resetButtonProps: false,
                        submitButtonProps: {
                            className: 'w-full',
                            disabled: !slateEditorval.current
                        },
                        searchConfig: {
                            submitText: intl.formatMessage({
                                id: 'workflow.button.run',
                            }),
                        },
                    }}
                    onFinish={(e)=>{
                        agentRun(e)
                    }}
                >
                    <div className='py-[6px]'>
                        <RenderInput data={currentVariate}/>
                    </div>
                    <div className='h-[150px] overflow-y-auto border border-color-[#eee] py-[4px] px-[11px] mb-[8px]'>
                        <SlateEditor  
                            onChange={value => {Editorrunchange(value)}}
                            options={currentVariateArray} placeholder="请输入运行指令，输入@插入变量" >
                        </SlateEditor>
                    </div>
                </ProForm>:<></>
            }
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
        </div>
    )
}

export default memo(RunsAgent)