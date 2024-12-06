/*
 * @LastEditors: biz
 */
import { ProFormTextArea } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
export const TextareaRunName = ({ name }) => {
    const intl = useIntl();
    return (
        <ProFormTextArea
            label={intl.formatMessage({ id: 'workflow.toName' })}
            required
            rules={[
                {
                    required: true,
                    message: intl.formatMessage({ id: 'workflow.toNameRequire' }),
                },
            ]}
            name={name}
            fieldProps={{
                maxLength: 50,
            }}
            placeholder={intl.formatMessage({ id: 'workflow.toInput' })}
        />
    );
};
