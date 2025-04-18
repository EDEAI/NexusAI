/*
 * @LastEditors: biz
 */
import { runWorkFlow } from '@/api/workflow';
import { ArrayVariable, ObjectVariable, Variable } from '@/py2js/variables';
import useSocketStore from '@/store/websocket';
import { useIntl } from '@umijs/max';
import { message } from 'antd';
import _ from 'lodash';
import { useCallback, useState } from 'react';
import { UPLOAD_FILES_KEY } from '../../../config';
import useStore from '../../../store';
import { BlockEnum } from '../../../types';
import { RunPanelData, RunResultInfo } from './types';
import useSaveWorkFlow from '../../../saveWorkFlow';

export const useRunPanelState = () => {
  const intl = useIntl();
  const runPanelShow = useStore(state => state.runPanelShow);
  const setRunPanelShow = useStore(state => state.setRunPanelShow);
  const setDealtWithData = useSocketStore(state => state.setDealtWithData);
  const setFlowMessage = useSocketStore(state => state.setFlowMessage);
  const flowMessage = useSocketStore(state => state.flowMessage);
  const [hasResult, setHasResult] = useState(false);
  const [runResultInfo, setRunResultInfo] = useState<RunResultInfo | null>(null);
  const [runList, setRunList] = useState<RunPanelData[]>([]);
  const [tabKey, setTabKey] = useState('1');
  const [endRun, setEndRun] = useState<RunPanelData | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Use the existing useSaveWorkFlow hook from the project
  const saveWorkFlow = useSaveWorkFlow();

  const runResult = useCallback((e) => {
    setRunList([]);
    setRunResultInfo(e.data);
    setHasResult(true);
    setTabKey('4');
  }, []);

  const processRunList = useCallback(() => {
    if (!runResultInfo?.app_run_id) return;

    const humanList = flowMessage.filter(item => {
      return (
        item.type === 'workflow_need_human_confirm' &&
        item.data.app_run_id === runResultInfo?.app_run_id
      );
    });

    let list = flowMessage
      .filter(item => {
        return (
          item.type === 'workflow_run_debug' &&
          item.data.app_run_id === runResultInfo?.app_run_id
        );
      })
      .map(item => {
        return {
          ...item,
          human: humanList.some(x => {
            return (
              x.data.node_exec_data.node_exec_id === item.data.node_exec_data.node_exec_id ||
              x.data.node_exec_data.first_task_exec_id === item.data.node_exec_data.node_exec_id
            );
          }),
        };
      });

    // Build hierarchical structure
    let runList = list.filter(x => {
      if (x.data?.node_exec_data?.parent_exec_id) {
        const index = list.findIndex(
          y => y.data.node_exec_data.node_exec_id === x.data.node_exec_data.parent_exec_id
        );
        if (index > -1) {
          if (!list[index]['children']) {
            list[index]['children'] = [];
          }
          list[index]['children'].push(x);
        }
        return false;
      }
      return true;
    });

    // Merge data with same node_exec_id
    const mergeData = (items: RunPanelData[]): RunPanelData[] => {
      return items.filter((x, i) => {
        const findMeIndex = items.findIndex(
          y =>
            y.data?.node_exec_data?.node_exec_id === x.data?.node_exec_data?.first_task_exec_id ||
            y.data?.node_exec_data?.node_exec_id === x.data?.node_exec_data?.node_exec_id
        );
        
        if (items[i]?.['children']?.length) {
          items[i]['children'] = mergeData(items[i]['children'] as RunPanelData[]);
        }
        
        if (findMeIndex > -1 && findMeIndex < i) {
          items[findMeIndex].data = x.data;
          return false;
        }
        
        return true;
      });
    };

    runList = mergeData(runList);

    // Filter duplicates
    runList = runList.filter((x, i) => {
      const findMeIndex = runList.findIndex(
        y =>
          y.data?.node_exec_data?.node_exec_id === x.data?.node_exec_data?.first_task_exec_id ||
          y.data?.node_exec_data?.node_exec_id === x.data?.node_exec_data?.node_exec_id
      );
      
      if (findMeIndex > -1 && findMeIndex < i) {
        runList[findMeIndex].data = x.data;
        return false;
      }
      
      return true;
    });

    // Find end run
    const foundEndRun = runList.find(x => x?.data?.status === 2);
    if (foundEndRun) {
      setEndRun(runList[runList.length - 1]);
    }

    setRunList(runList);
  }, [flowMessage, runResultInfo]);

  const runWorkflow = useCallback(async (value: any) => {
    const storeState = useStore.getState();
    const { nodes, app_id, getOutputVariables } = storeState;
    
    if (!app_id) {
      message.error(intl.formatMessage({ id: 'workflow.noAppId' }));
      return null;
    }
    
    if (!nodes || nodes.length === 0) {
      message.error(intl.formatMessage({ id: 'workflow.noNodes' }));
      return null;
    }
    
    const findEnd = nodes.find(x => x.type === BlockEnum.End);
    if (!findEnd) {
      message.error(intl.formatMessage({ id: 'workflow.notEnd', defaultMessage: '' }));
      return null;
    }

    setLoading(true);
    
    try {
      // Use the save function obtained from useSaveWorkFlow
      const saveResult = await saveWorkFlow();
      if (!saveResult) {
        setLoading(false);
        message.error(intl.formatMessage({ id: 'workflow.saveFailed' }));
        return null;
      }
      
      // Return error if there's no first node
      if (!nodes[0]?.id) {
        setLoading(false);
        message.error(intl.formatMessage({ id: 'workflow.noStartNode' }));
        return null;
      }
      
      // Build input variables object
      const input = new ObjectVariable('input_var');
      const vals = getOutputVariables(nodes[0].id);
      
      // Process variables
      for (const key in value) {
        if (key.startsWith('var.')) {
          const varName = key.replace('var.', '');
          const val = vals.find(x => x.createVar.name === varName);
          if (val) {
            const variable = new Variable(varName, val.createVar.type, value[key]);
            input.addProperty(varName, variable);
          }
        }
      }
      
      // Process files
      const freeFile = new ArrayVariable(UPLOAD_FILES_KEY, 'array[number]');
      if (value.file && Array.isArray(value.file)) {
        value.file.forEach((x: any) => {
          const fileId = x?.response?.data?.file_id || 0;
          if (fileId) {
            const fileVariable = new Variable(x.uid, 'number', fileId);
            freeFile.addValue(fileVariable);
          }
        });
      }
      input.addProperty(UPLOAD_FILES_KEY, freeFile);
      
      // Process knowledge base mapping
      const knowledge_base_mapping = (nodes[0]?.data && 'knowledge_base_mapping' in nodes[0].data) 
        ? nodes[0].data.knowledge_base_mapping 
        : { input: {}, output: {} };
      
      Object.entries(value).forEach(([key, val]) => {
        if (key.startsWith('dataset.')) {
          if (!knowledge_base_mapping.input[UPLOAD_FILES_KEY]) {
            knowledge_base_mapping.input[UPLOAD_FILES_KEY] = {};
          }
          knowledge_base_mapping.input[UPLOAD_FILES_KEY][key.replace('dataset.', '')] = val;
        }
      });

      // Build run parameters
      const params = {
        run_name: value.run_name || `Run-${new Date().toISOString()}`,
        inputs: input,
        run_type: 0,
        node_confirm_users: {},
        knowledge_base_mapping,
      };

      // Call run API
      const res = await runWorkFlow(app_id, params);
      setLoading(false);
      
      if (res?.code !== 0) {
        message.error(res?.message || intl.formatMessage({ id: 'workflow.runFailed' }));
        return null;
      }
      
      return res;
    } catch (err) {
      setLoading(false);
      console.error('Error running workflow:', err);
      message.error(
        err instanceof Error 
          ? err.message 
          : intl.formatMessage({ id: 'workflow.runFailed' })
      );
      return null;
    }
  }, [intl, setLoading, saveWorkFlow]);

  return {
    runPanelShow,
    setRunPanelShow,
    setDealtWithData,
    setFlowMessage,
    flowMessage,
    hasResult,
    setHasResult,
    runResultInfo,
    setRunResultInfo,
    runList,
    setRunList,
    tabKey,
    setTabKey,
    endRun,
    setEndRun,
    loading,
    setLoading,
    runResult,
    processRunList,
    runWorkflow,
  };
}; 