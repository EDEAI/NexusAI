/*
 * @LastEditors: biz
 */
import { CloseOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { useLatest, usePrevious } from 'ahooks';
import { Button } from 'antd';
import _ from 'lodash';
import { memo, useEffect, useState } from 'react';
import useStore from '../../store';
import CountItem from './CountItem';
interface CountWrapProps {
    options: any;
    type: string;
    index: number;
    updateIndex: number;
    onDel?: () => void;
    currentNode?: any;
    onChange?: (value: any) => void;
}
export default memo((props: CountWrapProps) => {
    const intl = useIntl();
    const { options, index, updateIndex, onDel, currentNode } = props;
    const [node, setNode] = useState(null);
    const [changeValue, setChangeValue] = useState([]);
    const [allCount, setAllCount] = useState([]);
    const selectedNode = useStore(state => state.getSelectedNode);
    const updateNodeData = useStore(state => state.updateNodeData);
    const prevChangeVal = usePrevious(changeValue);
    const lastChangeValue = useLatest(changeValue);
    useEffect(() => {
        // const currentNode = selectedNode();
        setAllCount(currentNode?.data?.count ?? []);
        if (currentNode?.data?.count) {
            setChangeValue(currentNode.data.count[index].list ?? []);
        }
        setNode(currentNode);
    }, [currentNode.data.count[index]]);


    const onAdd = () => {
        setChangeValue([...changeValue, {}]);
    };
    const delItem = delIndex => {
        setChangeValue(prev => {
            const currentPrev = prev.filter((_, index) => index !== delIndex);
            props?.onChange(currentPrev);
            return currentPrev;
        });
    };
    const onDelWrap = () => {
        setChangeValue([]);
        onDel?.();
    };

    const onChange = (value, changeIndex) => {
        setChangeValue(prev => {
            const newVal = prev.map((item, index) => {
                if (index === changeIndex) {
                    return value;
                }
                return item;
            });
            props?.onChange(newVal);
            return newVal;
        });
    };
    const changeType = () => {
        console.log(currentNode.data.count[index]);
        const oldCount = _.cloneDeep(currentNode.data.count);
        oldCount[index].type = currentNode.data.count[index].type == 'or' ? 'and' : 'or';
        updateNodeData(currentNode.id, {
            count: oldCount,
        });
    };
    return (
        <div className="p-2 rounded-md bg-slate-100">
            <div className="flex justify-between items-center">
                <div className="pb-2 font-bold text-m">{index == 0 ? 'IF' : 'ELSE-IF'}</div>

                {index > 0 && (
                    <Button type="text" onClick={onDelWrap} icon={<CloseOutlined />}></Button>
                )}
            </div>
            <div className="fade-in">
                <div className="flex flex-col gap-2 ">
                    {changeValue.map((item, smIndex) => (
                        <div className="relative flex flex-col gap-2">
                            <CountItem
                                key={smIndex}
                                index={smIndex}
                                value={item}
                                options={options}
                                onChange={val => onChange(val, smIndex)}
                                onDel={() => delItem(smIndex)}
                            />
                            {currentNode.data?.count[index]?.type &&
                                changeValue.length > 1 &&
                                smIndex != changeValue.length - 1 && (
                                    <div className=" z-10 w-full flex  items-center">
                                        <div
                                            onClick={changeType}
                                            className="py-1 shadow-sm flex items-center cursor-pointer border-blue-400 border text-blue-500 px-4 rounded-2xl !leading-none bg-white bold !text-sm"
                                        >
                                            {currentNode.data.count[index].type == 'or'
                                                ? 'OR'
                                                : 'AND'}
                                        </div>
                                    </div>
                                )}
                        </div>
                    ))}
                </div>
                <Button className="mt-4" onClick={onAdd} block>
                    {intl.formatMessage({
                        id: 'workflow.button.addComparison',
                        defaultMessage: '+ ',
                    })}
                </Button>
            </div>
        </div>
    );
});
