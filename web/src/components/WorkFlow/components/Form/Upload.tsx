/*
 * @LastEditors: biz
 */
import { getUploadUrl } from '@/api/createkb';
import { InboxOutlined } from '@ant-design/icons';
import { ProFormUploadDragger, ProFormUploadDraggerProps } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { message } from 'antd';
import type { ReactNode } from 'react';

interface UploadDraggerProps {
    name?: string;
    required?: boolean;
    accept?: string;
    multiple?: boolean;
    maxSize?: number;
    label?: string;
    extra?: ReactNode;
}

export const UploadDragger = ({
    label = null,
    name = 'file',
    required = false,
    accept = '.txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv,.jpg,.png,.jpeg',
    multiple = true,
    maxSize = 15,
    extra,
}: UploadDraggerProps) => {
    const intl = useIntl();

    const uploadProps: ProFormUploadDraggerProps = {
        icon: <InboxOutlined />,
        label,
        extra,
        title: intl.formatMessage({ id: 'workflow.uploadFileText' }),
        description: intl.formatMessage({ id: 'workflow.uploadFileDes' }),
        accept,
        name,
        required,
        rules: required ? [{ required: true, message: intl.formatMessage({ id: 'workflow.isRequire' }) }] : undefined,
        fieldProps: {
            listType: 'picture',
            name: 'file',
            multiple,
            headers: {
                Authorization: `Bearer ${localStorage.getItem('token')}`,
            },
            action: getUploadUrl,
            beforeUpload(file) {
                const isLtMaxSize = file.size / 1024 / 1024 < maxSize;
                
                if (!isLtMaxSize) {
                    message.error(intl.formatMessage({ id: 'workflow.uploadFileErrorText' }));
                }
                return isLtMaxSize;
            },
        },
    };

    return <ProFormUploadDragger {...uploadProps} />;
}; 
