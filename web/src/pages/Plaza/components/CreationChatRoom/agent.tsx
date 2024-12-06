import { getList } from '@/api/plaza';
import Scroll from '@/components/InfiniteScroll';
import { headportrait } from '@/utils/useUser';
import { CloseOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Button, Col, Empty, Input, Row, Select } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
interface Agentparam {
    show?: any;
    popupClose?: any;
    popupSave?: any;
    checkList?: any;
    zIndex?: any;
}
const AgentContent: React.FC<Agentparam> = param => {
    let { show, popupClose, popupSave, checkList, zIndex = '' } = param;

    const intl = useIntl();
    // Selected agent
    const checkAgent = useRef([]);
    // Number of selected agents
    const [selectNumber, setSelectNumeber] = useState({
        my_agent: 0,
        more_agent: 0,
    });
    const [selectAgentType, setSelectAgentType] = useState('my_agent');
    // Whether more can be loaded
    const [ishasMore, setIshasMore] = useState(true);
    // Agent list
    const [agentList, setAgentList] = useState([]);
    // MyAgent list
    const [moreAgentList, setMoreAgentList] = useState([]);
    // Whether more can be loaded
    const [moreishasMore, setMoreIshasMore] = useState(true);
    // content
    const contentDom = useRef(null);
    // Agent request parameters
    const agentParameters = useRef({
        page: 1,
        page_size: 40,
        agent_search_type: 3,
        name: '',
    });
    // More agent request parameters
    const moreAgentParameters = useRef({
        page: 1,
        page_size: 40,
        agent_search_type: 2,
        name: '',
    });

    const isMyAagent = () => {
        if (selectAgentType == 'my_agent') {
            return agentList && agentList.length > 0 ? agentList : [];
        } else {
            return moreAgentList && moreAgentList.length > 0 ? moreAgentList : [];
        }
    };
    const handleChange = (value: string) => {
        setSelectAgentType(value);
    };
    const getAgentList = async (data: any, isInit = false) => {
        if (isInit) {
            data.page = 1;
        }
        let res = await getList('/v1/agent/agent_list', data);
        if (res.code == 0) {
            res.data.list.forEach((item: any) => {
                item.check = isCheckAagent(item);
            });

            if (data.agent_search_type == 3) {
                isInit
                    ? setAgentList([...res.data.list])
                    : setAgentList([...agentList, ...res.data.list]);
                setIshasMore(res.data.total_pages > agentParameters.current.page);
                selectAgentNumber('my_agent');
            } else {
                isInit
                    ? setMoreAgentList([...res.data.list])
                    : setMoreAgentList([...agentList, ...res.data.list]);
                setMoreIshasMore(res.data.total_pages > moreAgentParameters.current.page);
                selectAgentNumber('more_agent');
            }
        }
    };
    const setAgentInput = (e: any) => {
        if (selectAgentType == 'my_agent') {
            agentParameters.current.name = e.target.value;
            getAgentList(agentParameters.current, true);
        } else {
            moreAgentParameters.current.name = e.target.value;
            getAgentList(moreAgentParameters.current, true);
        }
    };
    const selectAgentNumber = (key: any) => {
        let myAgentNumber = checkAgent.current.filter(items => items.type == key).length;
        setSelectNumeber(pre => {
            pre[key] = myAgentNumber;
            return pre;
        });
    };
    const addCheckAgent = (type: any, item: any, index: any) => {
        item.type = type;
        let res = checkAgent.current.filter(items => items.agent_id == item.agent_id);
        checkAgent.current.forEach((item, index) => {
            if (item.agent_id == res[0]?.agent_id) {
                checkAgent.current.splice(index, 1);
            }
        });
        checkAgent.current = res.length ? [...checkAgent.current] : [...checkAgent.current, item];
        if (type == 'my_agent') {
            agentList.filter(i => {
                if (i.agent_id == item.agent_id) {
                    i.check = !i.check;
                }
            });
            setAgentList([...agentList]);
            selectAgentNumber('my_agent');
        } else {
            moreAgentList.filter(i => {
                if (i.agent_id == item.agent_id) {
                    i.check = !i.check;
                }
            });
            setMoreAgentList([...moreAgentList]);
            selectAgentNumber('more_agent');
        }
    };
    const isCheckAagent = (item: any) => {
        return checkAgent.current.filter(i => i.agent_id == item.agent_id).length;
    };
    // show popup
    // const showPopup = ()=>{
    //     contentDom.current.style='display:flex;opacity:1'
    // }
    
    const agentCancel = () => {
        // contentDom.current.style='opacity:0;display:none'
        popupClose();
        checkAgent.current = [];
        setMoreAgentList([]);
        setSelectAgentType('my_agent');
        setSelectNumeber({
            my_agent: 0,
            more_agent: 0,
        });
    };
   // Save popup
    const agentSave = () => {
        popupSave({
            checkAgent: checkAgent.current,
        });
        agentCancel();
    };
    useEffect(() => {
        if (show) {
            // showPopup()
            if (checkList.length) {
                checkAgent.current = checkList;
            }
            agentParameters.current.name = '';
            moreAgentParameters.current.name = '';

            getAgentList(agentParameters.current, true);

            getAgentList(moreAgentParameters.current, true);
        }
    }, [show]);

    return (
        <div
            ref={contentDom}
            style={zIndex ? { zIndex: zIndex } : { zIndex: 30 }}
            className='transition  w-full h-full fixed top-[0] left-[0] bg-[rgba(0,0,0,0.5)] flex items-center justify-center z-30"'
        >
            <div className="w-[980px] h-[646px] bg-[#fff] rounded-[6px] transition">
                <div className="flex flex-col h-full">
                    <div
                        className="text-[16px] flex items-center p-[20px]"
                        style={{ borderBottom: '1px solid #ebebeb' }}
                    >
                        <span className="flex-1 text-[14px] font-[500] text-[#213044]">
                            {intl.formatMessage({ id: 'app.check_agent_popup.title' })}
                        </span>
                        <CloseOutlined
                            className="text-[16px] cursor-pointer"
                            onClick={agentCancel}
                        />
                    </div>
                    <div className="p-[20px] pb-[0px] flex-1 min-h-[0]">
                        <div className="flex items-center pb-[20px]">
                            <span className="text-[#999]">
                                {intl.formatMessage({ id: 'app.check_agent_popup.chenck_text' })}：
                            </span>
                            <div className="flex items-center gap-x-[12px]">
                                <span className="text-[#213044] text-[14px]">
                                    {intl.formatMessage({ id: 'app.check_agent_popup.select_1' })}:{' '}
                                    {selectNumber['my_agent']}
                                </span>
                                <span className="text-[#213044] text-[14px]">
                                    {intl.formatMessage({ id: 'app.check_agent_popup.select_2' })}:{' '}
                                    {selectNumber['more_agent']}
                                </span>
                            </div>
                        </div>
                        <div className="flex gap-x-[20px] pb-[20px]">
                            <Select
                                defaultValue={intl.formatMessage({
                                    id: 'app.check_agent_popup.select_1',
                                })}
                                style={{ width: 148, background: '#F7F7F7' }}
                                size="large"
                                className="border-[#eee] text-[#213044] text-[12px] select_agent"
                                popupClassName="select_agent"
                                onChange={handleChange}
                                options={[
                                    {
                                        value: 'my_agent',
                                        label: intl.formatMessage({
                                            id: 'app.check_agent_popup.select_1',
                                        }),
                                    },
                                    {
                                        value: 'more_agent',
                                        label: intl.formatMessage({
                                            id: 'app.check_agent_popup.select_2',
                                        }),
                                    },
                                ]}
                            />
                            <Input
                                className="w-[320px] input_agent"
                                onPressEnter={setAgentInput}
                                size="large"
                                placeholder={intl.formatMessage({
                                    id: 'app.check_agent_popup.search',
                                })}
                                prefix={
                                    <img
                                        src="/icons/search_icon.svg"
                                        className="w-[16px] h-[16px] mr-[10px]"
                                    />
                                }
                            />
                        </div>
                        <div
                            className="overflow-y-auto"
                            id="agentScroll"
                            style={{ height: 'calc(100% - 100px)' }}
                        >
                            <Scroll
                                dataLength={
                                    selectAgentType == 'my_agent'
                                        ? agentList.length
                                        : moreAgentList.length
                                }
                                elid={'agentScroll'}
                                ishasMore={
                                    selectAgentType == 'my_agent' ? ishasMore : moreishasMore
                                }
                                upSlide={() => {
                                    getAgentList(
                                        selectAgentType == 'my_agent'
                                            ? agentParameters
                                            : moreAgentParameters,
                                    );
                                }}
                            >
                                <div className="w-full overflow-x-hidden">
                                    <Row gutter={[15, 15]}>
                                        {isMyAagent() && isMyAagent().length ? (
                                            isMyAagent().map((item: any, index: any) => (
                                                <Col span={6} key={item.agent_id}>
                                                    <div
                                                        className={`bg-[#fff] flex gap-x-[20px] p-[10px] cursor-pointer border-solid border-[1px] rounded-[4px] ${
                                                            !item.check
                                                                ? 'border-[#eee]'
                                                                : 'border-[#1B64F3]'
                                                        }`}
                                                        onClick={() => {
                                                            addCheckAgent(
                                                                selectAgentType,
                                                                item,
                                                                index,
                                                            );
                                                        }}
                                                    >
                                                        <div className="w-[40px] h-[40px] bg-[#F4F8F1] rounded-[6px] relative flex items-center justify-center shrink-0">
                                                            <img
                                                                src={headportrait(
                                                                    'single',
                                                                    item.icon,
                                                                )}
                                                                alt=""
                                                                className="w-[20px]  h-[20px]"
                                                            />
                                                            {/* <div className='w-[16px]  h-[16px] bg-[#fff] absolute bottom-[-2px] right-[-2px]'>
                                                                    <img src="/icons/robot_icon.svg" alt="" className='w-[12px]  h-[12px]'/>
                                                                </div> */}
                                                        </div>
                                                        <div className="flex flex-col gap-y-[5px] justify-center flex-1 min-w-[0]">
                                                            <div className="text-[#213044] text-[12px] font-[500] w-full truncate">
                                                                {item.name}
                                                            </div>
                                                            <div className="text-[#999] text-[12px] w-full truncate">
                                                                {item.description}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </Col>
                                            ))
                                        ) : (
                                            <div className="w-full h-[380px] flex justify-center items-center">
                                                <Empty
                                                    style={{ margin: '0px', fontSize: '16px' }}
                                                    imageStyle={{
                                                        width: '60px',
                                                        margin: '0 auto',
                                                        marginBottom: '2px',
                                                    }}
                                                    description={intl.formatMessage({
                                                        id: 'app.dashboard.None',
                                                    })}
                                                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                                                ></Empty>
                                            </div>
                                        )}
                                    </Row>
                                </div>
                                {/* Empty */}
                            </Scroll>
                        </div>
                    </div>
                    <div
                        className="p-[20px] flex gap-x-[20px] justify-end"
                        style={{ borderTop: '1px solid #e8e8e8' }}
                    >
                        <Button
                            className="text-[14px] text-[#213044] w-[88px] h-[40px]"
                            style={{ border: '1px solid #D8D8D8' }}
                            onClick={agentCancel}
                        >
                            {intl.formatMessage({ id: 'app.check_agent_popup.cancel' })}
                        </Button>
                        <Button
                            type="primary"
                            className="bg-[#1B64F3] rounded-[4px] w-[88px] h-[40px]"
                            htmlType="submit"
                            onClick={agentSave}
                        >
                            {intl.formatMessage({ id: 'app.check_agent_popup.save' })}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AgentContent;
