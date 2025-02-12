/*
 * @LastEditors: biz
 */
import { BASE_URL } from '@/api/request';
import Log from '@/pages/WorkSpace/Log';
import {
    ArrowLeftOutlined,
    ContainerOutlined,
    DesktopOutlined,
    EditOutlined,
    PieChartOutlined,
    SettingOutlined,
} from '@ant-design/icons';
import { ProForm, ProFormSwitch } from '@ant-design/pro-components';
import { history } from '@umijs/max';
import { useUpdateEffect } from 'ahooks';
import type { MenuProps } from 'antd';
import { Menu, Popover } from 'antd';
import React, { useRef, useState } from 'react';
import { useIntl } from 'umi';
import useSaveWorkFlow from '../../saveWorkFlow';
import useStore from '../../store';

type MenuItem = Required<MenuProps>['items'][number];

const WorkFlowLeftMenu: React.FC = () => {
    const intl = useIntl();
    const [collapsed, setCollapsed] = useState(true);
    const setWorkflowEditInfo = useStore(state => state.setWorkflowEditInfo);
    const workFlowInfo = useStore(state => state.workFlowInfo);
    const setSelect = useStore(state => state.setSelect);
    const [activeKey, setActiveKey] = useState('1');
    const [canToApi, setCanToApi] = useState(false);
    const saveWorkFlow = useSaveWorkFlow();
    const ref = useRef(null);
    const content = () => {
        return (
            <div className="">
                <div className="w-[240px]  ">
                    <ProForm
                        formRef={ref}
                        submitter={{ render: () => null }}
                        onValuesChange={onFormChange}
                        layout="horizontal"
                    >
                        <ProFormSwitch
                            name="is_public"
                            label={intl.formatMessage({
                                id: 'component.label.teamVisible',
                                defaultMessage: '',
                            })}
                        ></ProFormSwitch>
                        <ProFormSwitch
                            tooltip={
                                workFlowInfo?.app?.publish_status != '1'
                                    ? {
                                          title: intl.formatMessage({
                                              id: 'component.tooltip.publishWorkflowFirst',
                                              defaultMessage: '',
                                          }),
                                      }
                                    : null
                            }
                            formItemProps={{
                                className:'mb-0'
                            }}
                            disabled={workFlowInfo?.app?.publish_status != '1'}
                            name="enable_api"
                            label="API"
                        ></ProFormSwitch>
                    </ProForm>
                </div>
            </div>
        );
    };
    const items: MenuItem[] = [
        {
            key: '4',
            icon: <ArrowLeftOutlined />,
            label: intl.formatMessage({
                id: 'component.menu.backToPreviousPage',
                defaultMessage: '',
            }),
        },
        {
            key: '0',
            icon: workFlowInfo?.isProd ? (
                <SettingOutlined />
            ) : (
                <Popover
                    content={content}
                    trigger="click"
                    forceRender={true}
                    placement="rightTop"
                    title={intl.formatMessage({
                        id: 'component.menu.setting',
                        defaultMessage: '',
                    })}
                >
                    <SettingOutlined />
                </Popover>
            ),
            label: intl.formatMessage({ id: 'component.menu.setting', defaultMessage: '' }),
            disabled: workFlowInfo?.isProd,
        },
        {
            key: '1',
            icon: <PieChartOutlined />,
            label: intl.formatMessage({ id: 'component.menu.arrange', defaultMessage: '' }),
        },
        {
            key: '2',
            icon: <DesktopOutlined />,
            label: intl.formatMessage({
                id: 'component.menu.accessAPI',
                defaultMessage: 'API',
            }),
            title: !canToApi
                ? intl.formatMessage({
                      id: 'component.tooltip.enableAPIFirst',
                      defaultMessage: 'API',
                  })
                : intl.formatMessage({ id: 'component.menu.accessAPI', defaultMessage: 'API' }),
            disabled: !canToApi,
        },
        {
            key: '3',
            icon: <ContainerOutlined />,
            label: intl.formatMessage({ id: 'component.menu.log', defaultMessage: '' }),
        },
    ];
    useUpdateEffect(() => {
        if (workFlowInfo) {
            const is_public = workFlowInfo?.app?.is_public;
            const enable_api = workFlowInfo?.app?.enable_api;
            const formRender = {};

            formRender.is_public = !!is_public;
            formRender.enable_api = workFlowInfo?.app?.publish_status == '1' ? !!enable_api : false;
            console.log(formRender);

            setCanToApi(formRender.enable_api);
            ref?.current?.setFieldsValue(formRender);
        }
    }, [workFlowInfo]);
    const onFormChange = (item, all) => {
        console.log(item, all);
        apiChange(all.enable_api);
        setWorkflowEditInfo(all);
        setTimeout(saveWorkFlow, 300);
    };

    const apiChange = value => {
        setCanToApi(!!value);
    };
    const onItemClick = e => {
        switch (e.key) {
            case '4':
                history.go(-1);
                break;
            case '0':
                break;
            case '2':
                window.open(BASE_URL + workFlowInfo?.app?.api_url, '_blank');
                break;

            default:
                setSelect('');
                setActiveKey(e.key);
        }
        // if (e.key == '0') {
        //     // setActiveKey('-1');
        // } else if (e.key == '2') {
        //     // setActiveKey(e.key);
        //     window.open(BASE_URL + workFlowInfo?.app?.api_url, '_blank');
        // } else {
        //     setActiveKey(e.key);
        // }
    };
    return (
        <>
            <div className={`absolute left-[calc(100%+26px)] -top-4  z-20 ${activeKey === '3' ? ' !-left-[14px]' : ''}`}>
                <Menu
                    defaultSelectedKeys={['1']}
                    selectedKeys={[activeKey]}
                    className="w-10 rounded-md"
                    mode="vertical"
                    inlineCollapsed={collapsed}
                    items={items}
                    onClick={onItemClick}
                />
                {activeKey == '0' && (
                    <div className="absolute top-0 left-full ml-2">
                        <div className="w-[240px] bg-white rounded-md p-4 border border-gray-200">
                            <ProForm
                                formRef={ref}
                                submitter={{ render: () => null }}
                                onValuesChange={onFormChange}
                                layout="horizontal"
                            >
                                <ProFormSwitch
                                    name="is_public"
                                    label={intl.formatMessage({
                                        id: 'component.label.teamVisible',
                                        defaultMessage: '',
                                    })}
                                ></ProFormSwitch>
                                <ProFormSwitch
                                    disabled={!workFlowInfo?.app?.api_url}
                                    name="enable_api"
                                    label="API"
                                ></ProFormSwitch>
                            </ProForm>
                        </div>
                    </div>
                )}
            </div>
            {activeKey == '3' && (
                <div
                    className="fixed right-0 top-[56px] pl-12 pt-4 pr-2 bg-white z-10"
                    style={{ height: `calc(100vh - 56px)` }}
                >
                    <div className="bg-white rounded-md h-full">
                        <Log></Log>
                    </div>
                </div>
            )}
        </>
    );
};

export default WorkFlowLeftMenu;
