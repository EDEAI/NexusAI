/*
 * @LastEditors: biz
 */
import { getModelList } from '@/api/workflow';
import { ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useRequest } from 'ahooks';
import useStore from '../../store';

export const SelectModelConfigId = ({ name, form }) => {
    const intl = useIntl();
    // const { data, loading } = useRequest(
    //     () =>
    //         getModelList().then(res => {
    //             const safeModels = Array.isArray(res?.data?.data) ? res.data.data : [];

    //             const options = safeModels.map(supplier => ({
    //                 label: supplier.supplier_name,
    //                 options: Array.isArray(supplier.model_list) ? supplier.model_list.map(model => ({
    //                     label: model.model_name,
    //                     value: model.model_config_id,
    //                 })) : []
    //             }));

    //             let defaultValue;
    //             for (const supplier of safeModels) {
    //                 if (Array.isArray(supplier.model_list)) {
    //                     const defaultModel = supplier.model_list.find(model => model.model_default_used === 1);
    //                     if (defaultModel) {
    //                         defaultValue = defaultModel.model_config_id;
    //                         break;
    //                     }
    //                 }
    //             }

    //             return {
    //                 options,
    //                 defaultValue
    //             };
    //         }),
    //     {
    //         cacheKey: 'workFlowCacheModelConfigId',
    //         cacheTime: 160 * 1000,
    //     },
    // );
    const data = useStore(state => state.modelOptionsData);
    return (
        <div className='min-h-8'>
           {
            //  !loading && (
                <ProFormSelect
                    allowClear={false}
                    options={data?.options || []}
                    name={name}
                    initialValue={data?.defaultValue}
                    label={intl.formatMessage({
                        id: 'workflow.label.selectModel',
                        defaultMessage: '',
                    })}
                ></ProFormSelect>
                // )
           }
        </div>
    );
};
