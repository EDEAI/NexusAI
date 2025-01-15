/*
 * @LastEditors: biz
 */
import { ProForm } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { memo } from 'react';
import { TextareaRunName } from '../Form/Input';
import { RenderConfirm } from './RenderConfirm';
import { RenderInput } from './RenderInput';

interface RunFormProps {
    loading?: boolean;
    onFinish: (values: any) => Promise<void>;
    data?: any;
}

const RunForm = memo(({ loading, onFinish, data }: RunFormProps) => {
    const intl = useIntl();

    return (
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
            loading={loading}
            onFinish={onFinish}
        >
            <TextareaRunName name={'description'} />
            <RenderInput data={data?.data?.start_node?.data?.input?.properties} />
            <RenderConfirm data={data?.data?.need_confirm_nodes} />
        </ProForm>
    );
});

export default RunForm;
