/*
 * @LastEditors: biz
 */
import { getModelList } from '@/api/workflow';
import { ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useRequest } from 'ahooks';

export const SelectModelConfigId = ({ name, form }) => {
    const intl = useIntl();
    const { data, loading } = useRequest(
        () =>
            getModelList().then(res => {
                return (
                    res?.data?.data?.map(x => ({
                        ...x,
                        label: x.model_name,
                        value: x.model_config_id,
                    })) || []
                );
            }),
        {
            cacheKey: 'workFlowCacheModelConfigId',
            cacheTime: 60 * 1000,
        },
    );
    console.log(form);

    // useMount(()=>{
    //     console.log(form?.current?.getFieldValue,data,!form?.current?.getFieldValue?.(name));

    //     if (form?.current?.getFieldValue&&data && data.length > 0 && !form?.current?.getFieldValue?.(name)) {
    //         form?.current?.setFieldsValue({ [name]: data[0].value });
    //         debugger
    //     }
    // })
    return (
        <div className='min-h-8'>
           {
             !loading && (
                <ProFormSelect
                    allowClear={false}
                    options={data || []}
                    name={name}
                    initialValue={data?.[0]?.value || null}
                    label={intl.formatMessage({
                        id: 'workflow.label.selectModel',
                        defaultMessage: '',
                    })}
                ></ProFormSelect>
                )
           }
        </div>
    );
};
