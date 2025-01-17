/*
 * @LastEditors: biz
 */
import { BASE_URL } from '@/api/request';
import { exportWorkflow, importWorkflow, publishWorkFlow } from '@/api/workflow';
import { ExportOutlined, PlayCircleOutlined, SyncOutlined } from '@ant-design/icons';
import { useIntl, useSearchParams } from '@umijs/max';
import { Button, message, UploadProps } from 'antd';
import moment from 'moment';
import { memo } from 'react';
import useSaveWorkFlow from '../saveWorkFlow';
import useStore from '../store';

export default memo(() => {
    const intl = useIntl();
    const [searchParams] = useSearchParams();
    const setWorkFlowInfo = useStore(state => state.setWorkFlowInfo);
    const workFlowInfo = useStore(state => state.workFlowInfo);
    const setRunPanelShow = useStore(state => state.setRunPanelShow);
    const publishStatus = searchParams.get('type') == 'true';
    const saveWorkFlow = useSaveWorkFlow();
    const [messageApi, contextHolder] = message.useMessage();
    const publish = async () => {
        await saveWorkFlow()
        const appId = searchParams.get('app_id');
        publishWorkFlow(appId).then(res => {
            console.log(res);
            if (res.code == 0) {
                setWorkFlowInfo({
                    ...workFlowInfo,
                    app: {
                        ...workFlowInfo?.app,
                        publish_status: '1',
                    },
                });
                messageApi.open({
                    type: 'success',
                    content: intl.formatMessage({
                        id: 'workflow.releaseSuc',
                    }),
                });
            }
        });
    };

    const runFlow = () => {
        setRunPanelShow(true);
    };

    const importData = async () => {
        const appId = searchParams.get('app_id');
        const res = await importWorkflow(appId);
    };

    const exportData = async () => {
        const appId = searchParams.get('app_id');
        const fileName = workFlowInfo?.app?.name || 'workflow';
        const formattedTime = moment().format('YYYY_MM_DD-HH_mm_ss');
        exportWorkflow(appId, publishStatus == true ? 1 : 0).then(res => {
            const blob = new Blob([res], { type: 'text/yaml' });

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${fileName}_${formattedTime}.yml`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    };
    const props: UploadProps = {
        name: 'file',
        fileList: null,
        action: BASE_URL + '/v1/workflow/import',
        accept: '.yml',
        multiple: false,
        headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
    };
    return (
        <div className="fixed right-2 top-16 flex gap-2">
            {!publishStatus && (
                <div  className="flex gap-2">
                    <Button type="primary" onClick={publish}>
                        {intl.formatMessage({ id: 'workflow.release' })}
                    </Button>
                    <Button icon={<PlayCircleOutlined />} onClick={runFlow}>
                        {intl.formatMessage({ id: 'workflow.run' })}
                    </Button>
                    <Button icon={<SyncOutlined />} type="dashed" onClick={saveWorkFlow}>
                        {intl.formatMessage({ id: 'workflow.save' })}
                    </Button>
                </div>
            )}

            {/* <Upload {...props}>
            <Button icon={<SyncOutlined />} type="dashed" onClick={importData}>
                {intl.formatMessage({ id: 'workflow.import', defaultMessage: '' })}
            </Button>
            </Upload> */}
            <Button icon={<ExportOutlined />} type="dashed" onClick={exportData}>
                {intl.formatMessage({ id: 'workflow.export', defaultMessage: '' })}
            </Button>
            {contextHolder}
        </div>
    );
});
