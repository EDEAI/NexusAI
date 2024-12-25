/*
 * @LastEditors: biz
 */
import { CaretRightFilled } from '@ant-design/icons';
import { useIntl, useSearchParams } from '@umijs/max';
import { NodeProps } from '@xyflow/react';
import { useHover, useUpdateEffect } from 'ahooks';
import { Button, Tooltip, Typography } from 'antd';
import React, { cloneElement, forwardRef, memo, useRef } from 'react';
import UserCon from '../../components/UserCon';
import { EDGE_COLOR, NOT_RUN_NODE_TYPE } from '../../config';
import useStore from '../../store';
import { BlockEnum } from '../../types';
import { NodeCustom } from '../nodeDisperse';
const { Text } = Typography;
export default memo(
    forwardRef((props: NodeProps & { children: any }) => {
        const { children, data, type } = props;
        const intl = useIntl();
        if (!data || typeof data !== 'object') {
            return null;
        }
        const icon = NodeCustom[type as keyof typeof NodeCustom]?.icon || 'default';
        const title = data.title as string;
        const desc = data.desc as string;
        const [searchParams] = useSearchParams();
        const publishStatus = searchParams.get('type') == 'true';
        const setSelect = useStore(state => state.setSelect);
        const updateEdgeColors = useStore(state => state.updateEdgeColors);
        const getInputVariables = useStore(state => state.getInputVariables);
        const setRunPanelNodeShow = useStore(state => state.setRunPanelNodeShow);
        const nodeRef = useRef(null);
        const nodeHover = useHover(nodeRef);
        useUpdateEffect(() => {
            if (nodeHover) {
                // #2970ff
                updateEdgeColors(props.id, EDGE_COLOR.NODE_HOVER);
            } else {
                updateEdgeColors(props.id);
            }
        }, [nodeHover]);

        const runNode = () => {
            setTimeout(() => {
                setRunPanelNodeShow(props);
            }, 500);
        };
        return (
            <>
                <div
                    className={`pl-2  w-[270px] pr-4 bg-white rounded-md border-2 ${
                        props.data['selected'] ? 'border-blue-400' : 'border-transparent'
                    } hover:shadow-lg`}
                    ref={nodeRef}
                >
                    {!publishStatus &&
                        nodeHover &&
                        !NOT_RUN_NODE_TYPE.includes(props.type as BlockEnum) && (
                            <div className="absolute top-1 right-1">
                                <Tooltip
                                    title={intl.formatMessage({
                                        id: 'workflow.tooltip.runNode',
                                        defaultMessage: '',
                                    })}
                                >
                                    <Button
                                        onClick={runNode}
                                        icon={<CaretRightFilled></CaretRightFilled>}
                                    ></Button>
                                </Tooltip>
                            </div>
                        )}
                    <div>
                        <UserCon title={title} icon={data?.baseData?.icon || data.icon || icon}></UserCon>

                        {desc && (
                            <div className="px-1 py-2">
                                <Text
                                    ellipsis={{ tooltip: desc }}
                                    className=" text-xs text-slate-500 break-all"
                                >
                                    {desc}
                                </Text>
                            </div>
                        )}
                        <div className="">
                            {React.Children.map(children, child =>
                                cloneElement(child, { nodeHover }),
                            )}
                        </div>
                    </div>
                </div>
            </>
        );
    }),
);
