/*
 * @LastEditors: biz
 */
import { getBacklogsList } from '@/api/workflow';
import useUserStore from '@/store/user';
import { SwapRightOutlined } from '@ant-design/icons';
import { usePagination, useSessionStorageState, useUpdateEffect } from 'ahooks';

import Headportrait from '@/components/headportrait';
import { headportrait } from '@/utils/useUser';
import { useIntl } from '@umijs/max';
import { Empty, Spin } from 'antd';
import { useRef } from 'react';
import { Title } from './TableTitle';
export default () => {
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const submitPromptId = useUserStore(state => state.submitPromptId);
    const intl = useIntl();
    const proListRef = useRef(null);

    const [pageNumber, setPageNumber] = useSessionStorageState('pageNumber');

    const showDealtWith = item => {
        console.log(item);
        setDealtWithData(item);
    };
    const getDetail = async ({ current, pageSize }) => {
        const res = await getBacklogsList({
            current,
            pageSize,
        });

        return {
            list: res.data.list,
            success: true,
            total: res.data.total_count,
        };
    };
    const { data, loading, pagination } = usePagination(getDetail, {
        defaultPageSize: 8,
    });
    useUpdateEffect(() => {
        if (proListRef.current) {
            proListRef.current.reload();
        }
    }, [submitPromptId]);

    return (
        <Spin spinning={loading}>
            <div style={{ height: 'calc(100vh - 596px)' }}>
                <Title
                    iconSrc="/icons/back_log.svg"
                    titleText={intl.formatMessage({ id: 'app.workflow.backlogs.title' })}
                    pagination={pagination}
                ></Title>

                <div
                    className="bg-white rounded-lg p-2.5 mt-4 overflow-y-auto h-full"
                    style={{ boxShadow: ` 0px 2px 4px 0px rgba(0,0,0,0.05)` }}
                >
                    {data?.list?.map((item, index) => {
                        item.type = 3;
                        return (
                            <div
                                key={item.exec_id}
                                onClick={() => {
                                    setDealtWithData(item);
                                    setRunPanelLogRecord(false);
                                }}
                                className="flex items-center gap-5 cursor-pointer duration-200 rounded-lg  p-2.5 hover:bg-[#fafafa]"
                            >
                                {/* <div className="relative size-10 p-2 bg-[#F4F8F1] rounded">
                                    <img
                                        src="/icons/creation/pitchgongzuoliu.svg"
                                        className="size-full"
                                    />
                                    <div
                                        style={{ boxShadow: `0px 0px 4px 0px rgba(0,0,0,0.1)` }}
                                        className="size-4 p-0.5 bg-white  absolute -right-2 -bottom-1"
                                    >
                                        <img
                                            className="size-full"
                                            src={`/icons/creation/${WORKFLOW_ICON.WorkFlow}.svg`}
                                            alt=""
                                        />
                                    </div>
                                </div> */}

                                <Headportrait
                                    Image={headportrait('single', item.icon)}
                                    // icon={`/icons/creation/${WORKFLOW_ICON.WorkFlow}.svg`}
                                ></Headportrait>
                                <div className="flex flex-col gap-1 truncate">
                                    <div>
                                        <span>{item.app_name}</span> <SwapRightOutlined />
                                        <span className="text-[#1B64F3]">{item.node_name}</span>
                                    </div>
                                    <div className="text-[#999999] text-xs truncate">
                                        {item.app_run_name}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                    {!loading && data?.list?.length === 0 && (
                        <div className="h-full flex items-center justify-center">
                            <Empty
                                image="/images/empty.svg"
                                description={intl.formatMessage({
                                    id: 'app.workflow.backlogs.empty',
                                })}
                            ></Empty>
                        </div>
                    )}
                </div>
            </div>
        </Spin>
    );
};
