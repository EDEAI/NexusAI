import { getWorkFlowLogList } from '@/api/workflow';
import useUserStore from '@/store/user';
import type { ProColumns } from '@ant-design/pro-components';
import { ProTable } from '@ant-design/pro-components';
import { useIntl, useSearchParams } from '@umijs/max';
import { useRef } from 'react';
export const waitTimePromise = async (time: number = 100) => {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve(true);
        }, time);
    });
};

export const waitTime = async (time: number = 100) => {
    await waitTimePromise(time);
};

type GithubIssueItem = {
    url: string;
    id: number;
    number: number;
    title: string;
    labels: {
        name: string;
        color: string;
    }[];
    state: string;
    comments: number;
    created_at: string;
    updated_at: string;
    closed_at?: string;
};

export default () => {
    const intl = useIntl();

    const columns: ProColumns<GithubIssueItem>[] = [
        {
            dataIndex: 'index',
            valueType: 'indexBorder',
            width: 48,
        },
        {
            title: intl.formatMessage({ id: 'workflow.toName', defaultMessage: '' }),
            dataIndex: 'app_runs_name',
            ellipsis: true,
            fieldProps: {
                onChange: value => {
                    formRef?.current?.submit();
                },
            },
        },
        {
            title: intl.formatMessage({ id: 'workflow.created_time', defaultMessage: '' }),
            dataIndex: 'created_time',
            ellipsis: true,
            width: 180,
            tooltip: intl.formatMessage({
                id: 'workflow.created_time_des',
                defaultMessage: intl.formatMessage({
                    id: 'workflow.created_time_des',
                    defaultMessage: '',
                }),
            }),
            search: false,
        },

        {
            disable: true,
            title: intl.formatMessage({ id: 'workflow.status', defaultMessage: '' }),
            dataIndex: 'app_runs_status',
            filters: true,
            onFilter: true,
            ellipsis: true,
            width: 120,
            valueType: 'select',
            fieldProps: {
                onChange: value => {
                    formRef?.current?.submit();
                },
            },

            valueEnum: {
                1: {
                    text: intl.formatMessage({ id: 'workflow.running', defaultMessage: '' }),
                    status: 'Processing',
                },
                2: {
                    text: intl.formatMessage({ id: 'workflow.runSc', defaultMessage: '' }),
                    status: 'Success',
                },
                3: {
                    text: intl.formatMessage({ id: 'workflow.runF', defaultMessage: '' }),
                    status: 'Error',
                },
            },
        },
        {
            title: `${intl.formatMessage({
                id: 'workflow.elapsed_time',
                defaultMessage: '',
            })}S`,
            dataIndex: 'elapsed_time',
            ellipsis: true,
            width: 100,
            tooltip: intl.formatMessage({
                id: 'workflow.run_time',
            }),
            search: false,
        },

        {
            title: 'Tokens',
            key: 'showTime',
            dataIndex: 'total_tokens',
            width: 100,
            hideInSearch: true,
        },
        {
            title: intl.formatMessage({ id: 'workflow.user' }),
            dataIndex: 'nickname',
            search: false,
            width: 120,
            ellipsis: true,
            key: 'user',
        },
    ];

    // const actionRef = useRef<ActionType>();
    const [searchParams] = useSearchParams();
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const appId = searchParams.get('app_id');
    const formRef = useRef(null);
    return (
        <div className="h-full w-screen pl-[60px] box-border">
            <div>
                <ProTable<GithubIssueItem>
                    columns={columns}
                    formRef={formRef}
                    // actionRef={actionRef}
                    form={{
                        submitter: false,
                    }}
                    cardBordered
                    style={{ height: 'calc(100% - 20px)' }}
                    scroll={{ y: 'calc(100vh - 380px)', x: '100%' }}
                    request={async (params, sort, filter) => {
                        console.log(params, sort, filter);

                        const res = await getWorkFlowLogList({
                            app_runs_name: '',
                            app_runs_status: 0,
                            ...params,
                            app_id: appId,
                        });
                        console.log(res);
                        // const uniqueData = _.uniqBy(res.data.list, 'app_runs_id');
                        return {
                            data: res.data.list,
                            success: true,
                            total: res.data.total_count,
                        };
                    }}
                    onRow={record => {
                        return {
                            onClick: () => {
                                console.log('Row clicked:', record);
                                setRunPanelLogRecord(record);
                            },
                        };
                    }}
                    editable={{
                        type: 'multiple',
                    }}
                    // columnsState={{
                    //     persistenceKey: 'pro-table-singe-demos',
                    //     persistenceType: 'localStorage',
                    //     defaultValue: {
                    //         option: { fixed: 'right', disable: true },
                    //     },
                    //     onChange(value) {
                    //         console.log('value: ', value);
                    //     },
                    // }}
                    rowKey="app_runs_id"
                    search={{
                        labelWidth: 'auto',
                    }}
                    options={{
                        setting: {
                            listsHeight: 600,
                        },
                    }}
                    pagination={{
                        pageSize: 12,
                        showSizeChanger: false,
                        // onChange: (page) => console.log(page),
                    }}
                    dateFormatter="string"
                    headerTitle={intl.formatMessage({
                        id: 'workflow.workflowLog',
                        defaultMessage: '',
                    })}
                />
            </div>
        </div>
    );
};
