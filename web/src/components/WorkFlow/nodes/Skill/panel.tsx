/*
 * @LastEditors: biz
 */
import { getSkillInfo } from '@/api/workflow';
import { ProForm, ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useLatest } from 'ahooks';
import { Collapse, Typography } from 'antd';
import _ from 'lodash';
import { memo, useRef, useState } from 'react';
import CodeEditor from '../../components/Editor/CodeEditor';
import {
    SwitchManualConfirmation,
    SwitchWaitForAllPredecessors,
} from '../../components/Form/Switch';
import { SelectVariable } from '../../components/Form/Select';
import useNodeIdUpdate from '../../hooks/useNodeIdUpdate';
import useStore from '../../store';
import { AppNode } from '../../types';
import { resetFormNodes } from '../../utils/resetFormNodes';
export default memo(({ node }: { node: AppNode }) => {
    const [nodeInfo, setNodeInfo] = useState(_.cloneDeep(node));
    const intl = useIntl();
    const formRef = useRef(null);
    const updateNode = useStore(state => state.updateNode);
    const updateNodeData = useStore(state => state.updateNodeData);
    const getVariables = useStore(state => state.getOutputVariables);
    const state = useLatest(nodeInfo);
    const [inputList, setInputList] = useState([]);

    // const getVariables = useVariables();
    const [editorOptions, setEditorOptions] = useState([]);
    useNodeIdUpdate((nodeId, upNode) => {
        if (!upNode) return;
        skillInfo();
        setNodeInfo(upNode);
        // const fieldNames = Object.keys(formRef.current.getFieldsValue());
        // fieldNames.forEach((e) => {
        //     formRef.current.setFieldsValue({ [e]: nodeInfo.data[e] });
        // });
        console.log('node', upNode);

        const rest = resetFormNodes(formRef, upNode);
        setTimeout(() => {
            rest();
        }, 100);
        const vars = getVariables(upNode.id).filter(item=>item.createVar.type!= 'file');
        setEditorOptions(vars);
    });

    const skillInfo = async () => {
        if (!node.data['baseData']?.app_id) return;
        let res;
        if (node?.data['infoData']) {
            res = {
                code: 0,
                data: node?.data['infoData'],
            };
        } else {
            res = await getSkillInfo(node.data['baseData']?.app_id);
        }

        if (res.code == 0) {
            updateNodeData(node.id, {
                infoData: res.data,
            });
            if (res.data?.input_variables?.properties) {
                setInputList(Object.values(res.data?.input_variables?.properties));
            }
        }
    };

    const setNodeChange = (addItem: { [key: string]: any }, allValues) => {
        updateNodeData(node.id, allValues);
    };
    function isValidJson(str) {
        try {
            console.log('str', str);

            return JSON.parse(str);
        } catch (e) {
            console.error(e);
            return false;
        }
    }
    //
    return (
        <>
            <div>
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
                    {inputList.map((item, index) => {
                        return (
                            <SelectVariable
                                key={index}
                                name={`variable.${item.name}`}
                                label={item.name}
                                showSearch
                                allowClear={false}
                                node={node}
                                options={editorOptions}
                            ></SelectVariable>
                        );
                    })}
                    <div className="user-form">
                        <SwitchManualConfirmation></SwitchManualConfirmation>
                        <SwitchWaitForAllPredecessors></SwitchWaitForAllPredecessors>
                    </div>
                </ProForm>
                <div className="w-full overflow-x-hidden">
                    <Collapse
                        className="-mx-4"
                        ghost
                        bordered={false}
                        expandIconPosition="end"
                        items={[
                            {
                                key: '0',
                                label: (
                                    <Typography.Title level={5}>
                                        {intl.formatMessage({
                                            id: 'workflow.label.skillConfiguration',
                                            defaultMessage: '',
                                        })}
                                    </Typography.Title>
                                ),
                                children: (
                                    <>
                                        <Typography.Title level={5}>
                                            {intl.formatMessage({
                                                id: 'workflow.label.code',
                                                defaultMessage: '',
                                            })}
                                        </Typography.Title>
                                        <div className="h-80">
                                            <CodeEditor
                                                language="python3"
                                                value={
                                                    nodeInfo?.data?.infoData?.code &&
                                                    isValidJson(
                                                        nodeInfo?.data?.infoData?.code || {},
                                                    )?.python3
                                                }
                                                readOnly
                                                onChange={() => {}}
                                                title={`python3`}
                                            ></CodeEditor>
                                        </div>
                                        <Typography.Title level={5} className="mt-4">
                                            {intl.formatMessage({
                                                id: 'workflow.label.output',
                                                defaultMessage: '',
                                            })}
                                        </Typography.Title>
                                        <div className="h-80">
                                            <CodeEditor
                                                language="python3"
                                                value={
                                                    nodeInfo?.data?.infoData?.output_variables &&
                                                    nodeInfo?.data?.infoData?.output_variables
                                                }
                                                readOnly
                                                isJSONStringifyBeauty
                                                onChange={() => {}}
                                                title={`python3`}
                                            ></CodeEditor>
                                        </div>
                                    </>
                                ),
                            },
                        ]}
                    ></Collapse>
                </div>
            </div>
        </>
    );
});
