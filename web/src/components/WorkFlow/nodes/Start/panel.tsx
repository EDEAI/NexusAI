/*
 * @LastEditors: biz
 */
/*
 * @LastEditors: biz
 */
import { ProForm, ProFormDependency, ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useLatest, useMount } from 'ahooks';
import _ from 'lodash';
import { memo, useRef, useState } from 'react';
import { SwitchGroup } from '../../components/Form/Switch';
import Variable from '../../components/Variable';
import useStore from '../../store';
import { AppNode } from '../../types';
import { resetFormNodes } from '../../utils/resetFormNodes';
export default memo(({ node }: { node: AppNode }) => {
    const intl = useIntl();
    const [nodeInfo, setNodeInfo] = useState(_.cloneDeep(node));

    const formRef = useRef(null);
    const updateNode = useStore(state => state.updateNode);
    const datasetData = useStore(state => state.datasetData);
    const updateNodeData = useStore(state => state.updateNodeData);
    const state = useLatest(nodeInfo);
    const [variables, setVariables] = useState([]);
    useMount(() => {
        setNodeInfo(node);
      
        const reset = resetFormNodes(formRef, node);
        setTimeout(() => {
            reset();
        }, 200);
    });
    const variableChange = (e: any) => {
        setVariables(e);
        setNodeChange({ ['variables']: e }, { ['variables']: e });
    };

    const setNodeChange = (addItem: { [key: string]: any }, allVal) => {
        console.log(allVal, addItem);

        updateNodeData(node.id, allVal);
    };

    return (
        <>
            <div>
                <Variable
                    variables={nodeInfo.data['variables']?.value || []}
                    onChange={variableChange}
                ></Variable>

                <ProForm
                    formRef={formRef}
                    submitter={{
                        render: () => null,
                    }}
                    omitNil={false}
                    layout="horizontal"
                    className=""
                    onValuesChange={setNodeChange}
                >
                    <SwitchGroup
                        fields={['requires_upload', 'import_to_knowledge_base']}
                    ></SwitchGroup>

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
                                                        intl.formatMessage({
                                                            id: 'workflow.label.variable',
                                                            defaultMessage: '',
                                                        }) + item.name
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
