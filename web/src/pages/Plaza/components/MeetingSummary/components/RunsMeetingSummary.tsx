import React, { memo, useRef, useState } from 'react';
import type { MenuProps } from 'antd';
import { Button,Dropdown} from 'antd';
import {AppstoreAddOutlined} from '@ant-design/icons'
import { useIntl } from '@umijs/max';
import SelectAppDom from '../../CreationChatRoom/selectApp'
import RunsSummaryAgent from './RunsSummaryAgent';
import RunsSummaryWorkflow from './RunsSummaryWorkflow';
interface params {
    id:any;
    runid:any;
    setBoxLoading:any;
    scrollDom:any;
    setinputShow:any;
}

const RunsMeetingSummary:React.FC<params>=(params)=>{
    const intl = useIntl();
    const {runid,id,setBoxLoading,scrollDom,setinputShow} = params
    const selectedType = useRef('agent')
    const appId = useRef('');
    const [isRun,setisRun] = useState(false);
    const [selectApp,setSelectApp] = useState({
        type:'agent',
        checkItem:[],
        show:false
    })
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
    const popupClose=()=>{
        setSelectApp(pre=>{return {...pre,show:false}})
    }
    const popupSave=params=>{
        setBoxLoading(true)
        setSelectApp(pre=>{return {...pre,checkItem:params.checkItem}})
        selectedType.current = selectApp.type
        appId.current = params.checkItem[0].app_id;
        // setTimeout(()=>{
        //     scrollDom.current.scrollTo({top: scrollDom.current.scrollHeight});
        // },300)
    }

    return (
        <>
            {
                <div className={`pt-[24px]  border-[#ddd]`} style={{minHeight:selectApp?.checkItem?.length?scrollDom?.current?.offsetHeight:'100%'}} >
                    <div className='text-[14px] font-[500] flex item-center'>
                        <div className='flex-1'>{intl.formatMessage({ id: `app.summary.Runapp` })}</div>
                        <div className='px-[10px]'>
                            {isRun?<Dropdown menu={{items}}>
                                <AppstoreAddOutlined className='transition cursor-pointer text-[#999] text-[18px] hover:text-[#1B64F3]'/>
                            </Dropdown> 
                            :<></>}
                        </div>
                    </div>
                    <div>
                        {
                            selectApp?.checkItem?.length?
                                <>
                                {
                                    selectedType.current=='agent'?
                                    <RunsSummaryAgent 
                                        id={id} 
                                        appId={appId.current}
                                        selectApp={selectApp}
                                        runid={runid}
                                        setBoxLoading={setBoxLoading}
                                        scrollDom={scrollDom}
                                        setinputShow={setinputShow}
                                        setisRun={setisRun}/>
                                    :<RunsSummaryWorkflow
                                        id={id} 
                                        appId={appId.current}
                                        selectApp={selectApp}
                                        runid={runid}
                                        setBoxLoading={setBoxLoading}
                                        scrollDom={scrollDom}
                                        setinputShow={setinputShow}
                                        setisRun={setisRun}/>
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
                    selectedType.current == selectApp.type?selectApp.checkItem:[]
                }  
                zIndex={99}
                radio={true}
            />
        </>
    )
}

export default memo(RunsMeetingSummary)