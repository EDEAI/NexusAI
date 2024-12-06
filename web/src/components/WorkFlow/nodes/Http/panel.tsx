/*
 * @LastEditors: biz
 */
import {
    ProForm,
    ProFormDependency,
    ProFormDigit,
    ProFormRadio,
    ProFormSelect,
    ProFormText,
} from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount } from 'ahooks';
import { Collapse } from 'antd';
import { memo, useRef, useState } from 'react';
import EditorTable from '../../components/Editor/EditorTable';
import WrapperEditor from '../../components/Editor/WrapperEditor';
import {
    SwitchManualConfirmation,
    SwitchWaitForAllPredecessors,
} from '../../components/Form/Switch';
import useStore from '../../store';
import { AppNode } from '../../types';
import { resetFormNodes } from '../../utils/resetFormNodes';

type PromptItem = {
    serializedContent: string;
    value: object;
};
interface Prompt {
    system: PromptItem;
    user: PromptItem;
    assistant: PromptItem;
}
const httpOptions = [
    {
        label: 'GET',
        value: 'GET',
    },
    {
        label: 'POST',
        value: 'POST',
    },
    {
        label: 'PUT',
        value: 'PUT',
    },
    {
        label: 'OPTIONS',
        value: 'OPTIONS',
    },
    {
        label: 'DELETE',
        value: 'DELETE',
    },
    {
        label: 'PATCH',
        value: 'PATCH',
    },
    {
        label: 'HEAD',
        value: 'HEAD',
    },
];
const bodyOptions = [
    {
        label: 'none',
        value: 'none',
    },
    {
        label: 'form-data',
        value: 'form-data',
    },
    {
        label: 'x-www-form-urlencoded',
        value: 'x-www-form-urlencoded',
    },
    {
        label: 'raw text',
        value: 'raw-text',
    },
    {
        label: 'JSON',
        value: 'json',
    },
];
export default memo(({ node }: { node: AppNode }) => {
    const formRef = useRef(null);
    const intl = useIntl();
    const updateNodeData = useStore(state => state.updateNodeData);
    const [headers, setHeaders] = useState([]);
    const [params, setParams] = useState([]);
    const [body_data, setBodyTable] = useState([]);
    const [editor, setEditor] = useState([]);
    const [editorLoading, setEditorLoading] = useState(false);
    const [showToken, setShowToken] = useState(false);
    useMount(() => {
        resetFormNodes(formRef, node, ['cont_timeout', 'read_timeout', 'write_timeout']);

        setEditorLoading(true);
        if (node.data['headers']) {
            setHeaders(node.data['headers']);
        }
        if (node.data['params']) {
            setParams(node.data['params']);
        }
        if (node.data['body_data']) {
            setBodyTable(node.data['body_data']);
        }
        if (node.data['editor']) {
            setEditor(node.data['editor']);
        }

        setTimeout(() => {
            setEditorLoading(false);
        }, 500);
    });

    // useUpdateEffect(() => {
    //     // setUpdateEditor(() => updateEditor + 1);

    // }, [node.id]);

    const setNodeChange = (addItem: { [key: string]: any }) => {
        console.log(addItem);
        if (editorLoading) return;
        updateNodeData(node.id, addItem);
    };
    const editorTableChange = (key, value) => {
        if (editorLoading) return;
        updateNodeData(node.id, { [key]: value });
    };

    return (
        <>
            <div className="pt-4">
                <ProForm
                    submitter={{
                        render: () => null,
                    }}
                    initialValues={{
                        body_type: 'none',
                    }}
                    autoFocusFirstInput={false}
                    omitNil={false}
                    formRef={formRef}
                    layout="horizontal"
                    onValuesChange={setNodeChange}
                >
                    <div className="flex justify-between">
                        <div className="">
                            {intl.formatMessage({
                                id: 'workflow.label.api',
                                defaultMessage: 'API',
                            })}
                        </div>
                        <div>
                            {/* <Button
                type="text"
                className="text-xs"
                onClick={() => setShowToken(true)}
                icon={<SettingOutlined></SettingOutlined>}
            >
                {intl.formatMessage({ id: 'workflow.button.auth', defaultMessage: '' })}
            </Button> */}
                        </div>
                    </div>
                    <div className="flex gap-2 w-full">
                        <ProFormSelect
                            allowClear={false}
                            name="method"
                            options={httpOptions}
                        ></ProFormSelect>
                        <div className="flex-1">
                            <ProFormText name="url"></ProFormText>
                        </div>
                    </div>
                    <div className="py-2">
                        {intl.formatMessage({
                            id: 'workflow.label.headers',
                            defaultMessage: 'HEADERS',
                        })}
                    </div>
                    <EditorTable
                        value={headers}
                        onChange={e => editorTableChange('headers', e)}
                    ></EditorTable>
                    <div className="py-2">
                        {intl.formatMessage({
                            id: 'workflow.label.params',
                            defaultMessage: 'PARAMS',
                        })}
                    </div>
                    <EditorTable
                        value={params}
                        onChange={e => editorTableChange('params', e)}
                    ></EditorTable>
                    <div className="mt-4">
                        <ProFormRadio.Group
                            name="body_type"
                            label={
                                <span className="">
                                    {intl.formatMessage({
                                        id: 'workflow.label.body',
                                        defaultMessage: 'BODY',
                                    })}
                                </span>
                            }
                            options={bodyOptions}
                        />
                    </div>

                    <ProFormDependency name={['body_type']}>
                        {({ body_type }) => {
                            switch (body_type) {
                                case 'form-data':
                                case 'x-www-form-urlencoded':
                                    return (
                                        <EditorTable
                                            value={body_data}
                                            onChange={e => editorTableChange('body_data', e)}
                                        ></EditorTable>
                                    );
                                case 'raw-text':
                                case 'json':
                                    return (
                                        <WrapperEditor
                                            placeholder={intl.formatMessage({
                                                id: 'workflow.placeholder.bodyContent',
                                                defaultMessage: `${body_type}， @`,
                                            })}
                                            title={body_type}
                                            value={editor}
                                            onChange={e => editorTableChange('editor', e)}
                                        ></WrapperEditor>
                                    );

                                default:
                                    break;
                            }
                            return <></>;
                        }}
                    </ProFormDependency>
                    <div className="pt-4 user-form">
                        <SwitchWaitForAllPredecessors></SwitchWaitForAllPredecessors>
                        <SwitchManualConfirmation></SwitchManualConfirmation>
                    </div>
                    <div className="w-full overflow-x-hidden">
                        <Collapse
                            className="-mx-4"
                            ghost
                            bordered={false}
                            expandIconPosition="end"
                            items={[
                                {
                                    key: '0',
                                    forceRender: true,
                                    label: (
                                        <span className="">
                                            {intl.formatMessage({
                                                id: 'workflow.label.timeoutSettings',
                                                defaultMessage: '',
                                            })}
                                        </span>
                                    ),
                                    children: (
                                        <>
                                            <ProFormDigit
                                                tooltip={{
                                                    title: intl.formatMessage({
                                                        id: 'workflow.tooltip.connectTimeout',
                                                        defaultMessage:
                                                            '（）',
                                                    }),
                                                    placement: 'right',
                                                    overlayClassName: 'custom-overlay',
                                                }}
                                                fieldProps={{
                                                    suffix: intl.formatMessage({
                                                        id: 'workflow.suffix.seconds',
                                                        defaultMessage: '',
                                                    }),
                                                }}
                                                name="connect_timeout"
                                                label={
                                                    <span className="">
                                                        {intl.formatMessage({
                                                            id: 'workflow.label.connectTimeout',
                                                            defaultMessage: '',
                                                        })}
                                                    </span>
                                                }
                                            />
                                            <ProFormDigit
                                                tooltip={{
                                                    title: intl.formatMessage({
                                                        id: 'workflow.tooltip.readTimeout',
                                                        defaultMessage:
                                                            '（）',
                                                    }),
                                                    placement: 'right',
                                                    overlayClassName: 'custom-overlay',
                                                }}
                                                fieldProps={{
                                                    suffix: intl.formatMessage({
                                                        id: 'workflow.suffix.seconds',
                                                        defaultMessage: '',
                                                    }),
                                                }}
                                                name="read_timeout"
                                                label={
                                                    <span className="">
                                                        {intl.formatMessage({
                                                            id: 'workflow.label.readTimeout',
                                                            defaultMessage: '',
                                                        })}
                                                    </span>
                                                }
                                            />
                                            <ProFormDigit
                                                tooltip={{
                                                    title: intl.formatMessage({
                                                        id: 'workflow.tooltip.writeTimeout',
                                                        defaultMessage:
                                                            '（）',
                                                    }),
                                                    placement: 'right',
                                                    overlayClassName: 'custom-overlay',
                                                }}
                                                fieldProps={{
                                                    suffix: intl.formatMessage({
                                                        id: 'workflow.suffix.seconds',
                                                        defaultMessage: '',
                                                    }),
                                                }}
                                                name="write_timeout"
                                                label={
                                                    <span className="">
                                                        {intl.formatMessage({
                                                            id: 'workflow.label.writeTimeout',
                                                            defaultMessage: '',
                                                        })}
                                                    </span>
                                                }
                                            />
                                        </>
                                    ),
                                },
                            ]}
                        ></Collapse>
                    </div>
                </ProForm>
            </div>
            {/* <Modal open={showToken} title='' onCancel={()=>setShowToken(false)}>
                22222222222222222222222222222
            </Modal> */}
        </>
    );
});
