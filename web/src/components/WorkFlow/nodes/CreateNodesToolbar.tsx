/*
 * @LastEditors: biz
 */
import { SearchOutlined } from '@ant-design/icons';
import { useMount } from 'ahooks';
import type { TabsProps } from 'antd';
import { Input, Tabs, Typography } from 'antd';
import { memo, useRef, useState } from 'react';
import UserCon from '../components/UserCon';
import useStore from '../store';
import { BlockEnum } from '../types';

import { getLocale, useIntl } from '@umijs/max';
import { NodeCustom } from './nodeDisperse';
interface CreateNodesToolbarProps {
    onSelect?: (e) => void;
    defaultActiveKey?: string;
    enabledIndexs?: Array<string>;
}

export default memo((props: CreateNodesToolbarProps) => {
    const baseNodes = Object.values(NodeCustom).filter(
        item =>
            ![BlockEnum.Start, BlockEnum.Agent, BlockEnum.Tool, BlockEnum.Skill].includes(
                item.icon,
            ),
    );
    const intl = useIntl();
    const lang = getLocale() == 'en-US' ? 'en_US' : 'zh_Hans';
    const tabItems: TabsProps['items'] = [
        {
            key: '1',
            label: intl.formatMessage({ id: 'workflow.node', defaultMessage: '' }),
            disabled: props?.enabledIndexs ? !props.enabledIndexs.includes('1') : false,
        },
        {
            key: '2',
            label: intl.formatMessage({ id: 'workflow.agent', defaultMessage: 'Agent' }),
            disabled: props?.enabledIndexs ? !props.enabledIndexs.includes('2') : false,
        },
        {
            key: '3',
            label: intl.formatMessage({ id: 'workflow.tool', defaultMessage: '' }),
            children: <div>{}</div>,
            disabled: props?.enabledIndexs ? !props.enabledIndexs.includes('3') : false,
        },
        {
            key: '4',
            label: intl.formatMessage({ id: 'workflow.skill', defaultMessage: '' }),
            disabled: props?.enabledIndexs ? !props.enabledIndexs.includes('4') : false,
        },
    ];
    const [searchNode, setSearchNode] = useState(baseNodes);

    const [tabIndex, setTabIndex] = useState(props?.defaultActiveKey || '1');
    const tools = useRef(null);

    const agentData = useStore(state => state.agentData);
    const agentList = [...(agentData?.team?.list || []), ...(agentData?.user?.list || [])];

    const skillData = useStore(state => state.skillData);
    const skillList = [...(skillData?.user?.list || []), ...(skillData?.team?.list || [])];
    const toolData = useStore(state => state.toolData);

    useMount(() => {
        setSearchNode(trandformData(props?.defaultActiveKey || '1'));
    });

    const trandformData = e => {
        let setData = null;
        if (e == '1') {
            setData = baseNodes;
        } else if (e == '2') {
            setData =
                agentList.map(item => {
                    return {
                        ...item,
                        title: item.name,
                        icon: BlockEnum.Agent,
                    };
                }) || [];
        } else if (e == '3') {
            setData = [];
        } else if (e == '4') {
            setData =
                skillList?.map(item => {
                    return {
                        ...item,
                        title: item.name,
                        icon: BlockEnum.Skill,
                    };
                }) || [];
        }
        return setData;
    };

    const onTabChange = e => {
        setTabIndex(e);
        setSearchNode(trandformData(e));
    };

    const search = (e: React.ChangeEvent<HTMLInputElement>) => {
        let searchFrom = trandformData(tabIndex);
        const searchNode = searchFrom.filter(item =>
            item.title.toLowerCase().includes(e.target.value.toLowerCase()),
        );
        searchNode.length && setSearchNode(searchNode);
    };

    return (
        <div
            ref={tools}
            className="p-2 w-[240px] pt-4 bg-white rounded-md cursor-pointer border border-blue-100"
        >
            <Input
                onChange={search}
                allowClear
                placeholder={intl.formatMessage({
                    id: 'workflow.searchNode',
                    defaultMessage: '',
                })}
                prefix={<SearchOutlined />}
            />
            {/* {useNodeId()} */}
            <Tabs
                defaultActiveKey={tabIndex}
                onChange={e => onTabChange(e)}
                items={tabItems}
            ></Tabs>
            <div style={{ maxHeight: 'calc(100vh - 500px)' }} className="overflow-y-auto">
                {tabIndex != '3'
                    ? searchNode.map((item, index) => (
                          <div
                              onClick={e => {
                                  e.stopPropagation();
                                  props.onSelect?.(item);
                              }}
                              className="hover:bg-slate-100 px-2 rounded"
                              key={index}
                          >
                              <UserCon key={index} title={item.title} icon={item.icon}></UserCon>
                          </div>
                      ))
                    : toolData?.list?.map(item => {
                          return (
                              <div>
                                  <div className="py-2">
                                      <Typography.Title level={5}>
                                          {item?.identity?.label[lang]}
                                      </Typography.Title>
                                  </div>
                                  <div>
                                      {item?.tools?.map((tool, toolIndex) => {
                                          return (
                                              <div
                                                  className="flex items-center gap-2 px-2 hover:bg-slate-100 "
                                                  onClick={e => {
                                                      e.stopPropagation();
                                                      props.onSelect?.({
                                                          item,
                                                          toolIndex,
                                                      });
                                                  }}
                                              >
                                                  <UserCon
                                                      key={toolIndex}
                                                      title={
                                                          tool?.identity?.label[lang] ||
                                                          intl.formatMessage({
                                                              id: 'workflow.tool',
                                                              defaultMessage: '',
                                                          })
                                                      }
                                                      icon={item?.identity?.icon}
                                                  ></UserCon>
                                              </div>
                                          );
                                      })}
                                  </div>
                              </div>
                          );
                      })}
            </div>
        </div>
    );
});
