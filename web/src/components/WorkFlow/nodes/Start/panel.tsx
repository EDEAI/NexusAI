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
import { memo, useEffect, useRef, useState } from 'react';
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
    const [variables, setVariables] = useState<any>(node?.data?.variables || { value: [] });
    useMount(() => {
        setNodeInfo(node);
      
        const reset = resetFormNodes(formRef, node);
        setTimeout(() => {
            reset();
        }, 200);
    });
    useEffect(() => {
        setNodeInfo(_.cloneDeep(node));
    }, [node]);

    useEffect(() => {
        setVariables(node?.data?.variables || { value: [] });
    }, [node?.data?.variables]);

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
                    variables={variables?.value || []}
                    variableTypes={['string', 'number', 'file']}
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
                        fields={['import_to_knowledge_base']}
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
