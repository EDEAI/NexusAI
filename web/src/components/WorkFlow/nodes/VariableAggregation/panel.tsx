/*
 * @LastEditors: biz
 */
import { ProForm, ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useUpdateEffect } from 'ahooks';
import { Tag } from 'antd';
import { memo, useRef } from 'react';
import { SelectVariable } from '../../components/Form/Select';
import useStore from '../../store';
import { AppNode } from '../../types';
import { resetFormNodes } from '../../utils/resetFormNodes';



export default memo(({ node }: { node: AppNode }) => {
    const formRef = useRef(null);
    const intl = useIntl();
    const getVariables = useStore(state => state.getOutputVariables);
    const updateNodeData = useStore(state => state.updateNodeData);
    useMount(() => {
        // const fieldNames = Object.keys(formRef.current.getFieldsValue());
        // fieldNames.forEach(e => {
        //     formRef.current.setFieldsValue({ [e]: node.data[e] });
        // });

        const reset = resetFormNodes(formRef, node);
        setTimeout(() => {
            reset();
        }, 200);
    });

    useUpdateEffect(() => {}, [node.id]);

    const setNodeChange = (addItem: { [key: string]: any }, allValues) => {
        updateNodeData(node.id, allValues);
    };

    const tagRender = props => {
        const { label, value, closable, onClose } = props;
        const onPreventMouseDown = (event: React.MouseEvent<HTMLSpanElement>) => {
            event.preventDefault();
            event.stopPropagation();
        };
        return (
            <Tag
                // color={'red'}
                onMouseDown={onPreventMouseDown}
                closable={closable}
                onClose={onClose}
                style={{ marginInlineEnd: 4 }}
            >
                {label}
            </Tag>
        );
    };
    //
    return (
        <>
            <div className="pt-4">
                <ProForm
                    submitter={{
                        render: () => null,
                    }}
                    omitNil={false}
                    formRef={formRef}
                    autoFocusFirstInput={false}
                    onValuesChange={setNodeChange}
                >
                    <SelectVariable
                        name="variables_list"
                        allowClear={false}
                        fieldProps={{
                            showSearch: true,
                        }}
                        label={intl.formatMessage({
                            id: 'workflow.label.selectAggregationVariables',
                            defaultMessage: '',
                        })}
                        mode="multiple"
                        node={node}
                    ></SelectVariable>

                    {!getVariables(node.id)?.length && (
                        <div className="-mt-10">
                            {intl.formatMessage({
                                id: 'workflow.message.setVariablesFirst',
                                defaultMessage: '',
                            })}
                        </div>
                    )}
                </ProForm>
            </div>
        </>
    );
});
