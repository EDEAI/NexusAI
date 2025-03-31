/*
 * @LastEditors: biz
 */
import {
  Alert,
  Collapse,
  Tag,
  Tooltip,
  Typography,
  message,
  Space
} from 'antd';
import { useIntl } from '@umijs/max';
import { memo, useCallback } from 'react';
import {
  CheckCircleOutlined,
  LoadingOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import CodeEditor from '../../Editor/CodeEditor';
import FileDownloadList from '@/components/common/FileDownloadList';
import useSaveWorkFlow from '../../../saveWorkFlow';
import { updateDealtWith } from '@/api/workflow';
import _ from 'lodash';
import { BlockEnum } from '../../../types';
import { ContentProps, RunPanelData } from './types';
import { NOT_SHOW_INPUT_RESULT_NODE, NOT_SHOW_OUTPUT_RESULT_NODE } from '../../../config';
import { getTagColor, isValidJsonString, formatJsonString } from './utils';

const { Panel } = Collapse;
const { Text } = Typography;

const TrackContent = memo(({ runList, flowMessage, setDealtWithData, setFlowMessage }: ContentProps) => {
  const intl = useIntl();
  const saveWorkFlow = useSaveWorkFlow();

  const delHumanMessage = useCallback((id: string) => {
    const newFlowMessage = flowMessage.filter(
      item =>
        !(
          item?.data?.node_exec_data?.node_exec_id === id &&
          item?.type === 'workflow_need_human_confirm'
        ),
    );
    setFlowMessage(newFlowMessage);
  }, [flowMessage, setFlowMessage]);

  const NodeChildren = useCallback((item: RunPanelData) => {
    const nodeInfo = item?.data?.node_exec_data;
    
    if (!nodeInfo) return null;

    const nodeType = nodeInfo.node_type as unknown as BlockEnum;

    if (nodeType === BlockEnum.Human) {
      if (item.human) {
        return (
          <div>{intl.formatMessage({ id: 'workflow.toBackLogs' })}</div>
        );
      }
      return (
        <Alert
          message={intl.formatMessage({
            id: 'workflow.checkedBackLogsMessage',
          })}
          type="success"
          className="text-green-700"
        />
      );
    }

    if (nodeInfo.status === 3 || (nodeInfo.status === 2 && item?.children)) {
      return (
        <div className="flex flex-col gap-2 w-full overflow-hidden">
          {nodeInfo?.prompt_data?.length > 0 && (
            <div className="h-80 w-full overflow-hidden">
              <CodeEditor
                language="python3"
                value={nodeInfo?.prompt_data}
                readOnly
                isJSONStringifyBeauty
                onChange={() => {}}
                title={intl.formatMessage({
                  id: 'workflow.historyPrompt',
                })}
              />
            </div>
          )}
          {nodeInfo.inputs && !NOT_SHOW_INPUT_RESULT_NODE.includes(nodeType) && (
            <div className="h-80 w-full overflow-hidden">
              <CodeEditor
                language="python3"
                value={nodeInfo?.inputs}
                readOnly
                isJSONStringifyBeauty
                onChange={() => {}}
                title={intl.formatMessage({
                  id: 'workflow.inputs',
                })}
              />
            </div>
          )}
          {item?.children && (
            <div className="w-full overflow-hidden">
              <TrackContent 
                runList={item?.children} 
                flowMessage={flowMessage}
                setDealtWithData={setDealtWithData}
                setFlowMessage={setFlowMessage}
              />
            </div>
          )}
          {nodeInfo.outputs && !NOT_SHOW_OUTPUT_RESULT_NODE.includes(nodeType) && (
            <div className="h-80 w-full overflow-hidden">
              <CodeEditor
                language="python3"
                value={nodeInfo?.outputs}
                mdValue={nodeInfo?.outputs_md}
                readOnly
                isJSONStringifyBeauty
                onChange={() => {}}
                title={intl.formatMessage({
                  id: 'workflow.outputs',
                })}
              />
            </div>
          )}

          {nodeInfo.file_list && nodeInfo.file_list.length > 0 && (
            <div className="w-full overflow-hidden">
              <FileDownloadList 
                files={nodeInfo.file_list} 
                title={intl.formatMessage({ id: 'skill.downloadFiles' })}
                className="w-full"
              />
            </div>
          )}
        </div>
      );
    } else if (nodeInfo.status === 4) {
      return (
        <Alert
          message={
            item?.data?.error ||
            intl.formatMessage({ id: 'workflow.nodeRunError' })
          }
          type="error"
          className="text-red-700 break-all"
        />
      );
    }

    return null;
  }, [intl, flowMessage, setDealtWithData, setFlowMessage]);

  const NodeExtra = useCallback((item: RunPanelData) => {
    const nodeInfo = item?.data?.node_exec_data;
    
    if (!nodeInfo) return null;

    const nodeType = nodeInfo?.node_type as unknown as BlockEnum;
    
    if (item.human) {
      if (nodeInfo?.status === 4) {
        return (
          <Tooltip
            title={intl.formatMessage({
              id: 'workflow.nodeRunErrorDes',
            })}
          >
            <Tag
              icon={<SyncOutlined spin />}
              color="error"
              className="mr-0"
              onClick={async e => {
                e.stopPropagation();
                await saveWorkFlow();
                updateDealtWith(
                  item.data?.node_exec_data?.node_exec_id || '',
                  {},
                ).then(async res => {
                  if (res.code === 0) {
                    delHumanMessage(
                      item.data?.node_exec_data?.node_exec_id || '',
                    );
                  }
                });
              }}
            >
              {intl.formatMessage({ id: 'workflow.resetRun' })}
            </Tag>
          </Tooltip>
        );
      }
      return (
        <Tooltip
          title={intl.formatMessage({ id: 'workflow.clickToBackLogs' })}
        >
          <Tag
            icon={<SyncOutlined spin />}
            color="processing"
            className="mr-0"
            onClick={e => {
              e.stopPropagation();
              setDealtWithData(item);
            }}
          >
            {intl.formatMessage({ id: 'workflow.backlogs' })}
          </Tag>
        </Tooltip>
      );
    }

    if (nodeType === BlockEnum.Human) {
      return (
        <Tag
          icon={<CheckCircleOutlined />}
          color="success"
          className="mr-0"
        >
          {intl.formatMessage({ id: 'workflow.checkedBackLogs' })}
        </Tag>
      );
    }
    
    if (nodeInfo?.status === 2) {
      return <LoadingOutlined />;
    }
    
    if (nodeInfo?.status === 3) {
      return (
        <>
          <span>
            {_.clamp(
              item?.data?.node_exec_data?.elapsed_time || 0,
              0.00001,
              999999,
            ).toFixed(5)}
            S
          </span>
          <CheckCircleOutlined className="text-green-400" />
        </>
      );
    } else if (nodeInfo?.status === 4) {
      return <span className="text-red-500">ERROR</span>;
    }

    return null;
  }, [intl, delHumanMessage, setDealtWithData, saveWorkFlow]);

  return (
    <div className="grid gap-2 w-full overflow-hidden">
      {runList?.map((item, index) => {
        const nodeInfo = item?.data?.node_exec_data;
        if (!nodeInfo) return null;
        
        return (
          <Collapse
            key={index}
            defaultActiveKey={
              item?.children?.length && nodeInfo.status === 2 ? '1' : '2'
            }
            className="w-full overflow-hidden"
            items={[
              {
                key: '1',
                label: (
                  <div className="flex items-center gap-2 w-full">
                    <div className="bg-gray-300 size-7 rounded-md flex justify-center items-center flex-shrink-0">
                      {item.data?.node_exec_data?.node_type ? (
                        <img
                          src={`/icons/${item.data.node_exec_data.node_type}.svg`}
                          className="size-6"
                          alt=""
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                          }}
                        />
                      ) : (
                        <div className="size-6"></div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0 overflow-hidden text-ellipsis">
                      <div className="truncate">{item.data?.node_exec_data?.node_name || 'Unnamed Node'}</div>
                      <div className="truncate text-xs text-gray-500">{item.finished_time}</div>
                    </div>
                    <div className="flex-shrink-0">
                      {NodeExtra(item) || <span></span>}
                    </div>
                  </div>
                ),
                children: (
                  <div className="w-full overflow-hidden">
                    {NodeChildren(item) || null}
                  </div>
                ),
              },
            ]}
          />
        );
      })}
    </div>
  );
});

export default TrackContent; 