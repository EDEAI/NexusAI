/*
 * @LastEditors: biz
 */
import { ProForm, ProFormDependency, ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useLatest, useMount } from 'ahooks';
import _ from 'lodash';
import { memo, useRef, useState } from 'react';
import {
    SwitchImportToKnowledgeBase,
    SwitchRequiresUpload,
    SwitchWaitForAllPredecessors,
} from '../../components/Form/Switch';
import Variable from '../../components/Variable';
import useStore from '../../store';
import { AppNode } from '../../types';
import { resetFormNodes } from '../../utils/resetFormNodes';
export default memo(({ node }: { node: AppNode }) => {
    const [nodeInfo, setNodeInfo] = useState(_.cloneDeep(node));
    const intl = useIntl();
    const formRef = useRef(null);
    const updateNode = useStore(state => state.updateNode);
    const updateNodeData = useStore(state => state.updateNodeData);
    const datasetData = useStore(state => state.datasetData);
    const state = useLatest(nodeInfo);
    const [variables, setVariables] = useState([]);
    useMount(() => {
        setNodeInfo(node);
        // const fieldNames = Object.keys(formRef.current.getFieldsValue());
        // fieldNames.forEach((e) => {
        //     formRef.current.setFieldsValue({ [e]: nodeInfo.data[e] });
        // });
        const reset = resetFormNodes(formRef, node);
        setTimeout(() => {
            reset();
        }, 200);
    });
    const variableChange = (e: any) => {
        setVariables(e);
        setNodeChange({ ['variables']: e });
    };

    const setNodeChange = (addItem: { [key: string]: any }) => {
        updateNodeData(node.id, addItem);
    };

    return (
        <>
            <div>
                <Variable
                    variables={nodeInfo.data['variables']?.value || []}
                    onChange={variableChange}
                    variableTypes={['string', 'number', 'file']}
                ></Variable>

                <ProForm
                    formRef={formRef}
                    submitter={{
                        render: () => null,
                    }}
                    autoFocusFirstInput={false}
                    omitNil={false}
                    layout="horizontal"
                    className="pt-5"
                    onValuesChange={setNodeChange}
                >
                    <div className="user-form">
                        <SwitchRequiresUpload></SwitchRequiresUpload>

                        <SwitchWaitForAllPredecessors></SwitchWaitForAllPredecessors>

                        <SwitchImportToKnowledgeBase></SwitchImportToKnowledgeBase>
                    </div>

                    <ProFormDependency name={['import_to_knowledge_base']}>
                        {({ import_to_knowledge_base }) => {
                            return (
                                import_to_knowledge_base && (
                                    <>
                                        {variables?.value?.map((item, index) => {
                                            return (
                                                <ProFormSelect
                                                    key={index}
                                                    name={`import_to_knowledge_base.${item.name}`}
                                                    label={
                                                        item.name
                                                    }
                                                    options={datasetData?.list || []}
                                                ></ProFormSelect>
                                            );
                                        })}
                                    </>
                                )
                            );
                        }}
                    </ProFormDependency>
                </ProForm>
            </div>
        </>
    );
});
