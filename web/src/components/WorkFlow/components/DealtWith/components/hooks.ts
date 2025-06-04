import { getDealtWithInfo, updateDealtWith } from '@/api/workflow';
import { Prompt } from '@/py2js/prompt';
import { ArrayVariable, createVariableFromObject, Variable } from '@/py2js/variables';
import useSocketStore from '@/store/websocket';
import { useRequest } from 'ahooks';
import { useCallback, useEffect, useRef, useState } from 'react';
import { UPLOAD_FILES_KEY } from '../../../config';
import { DealtWithData, DealtWithInfo } from './types';

export const useDealtWithState = (dealtWithData: DealtWithData | null) => {
  const [show, setShow] = useState(false);
  const [dealtWithInfo, setDealtWithInfo] = useState<DealtWithInfo | null>(null);
  const [execId, setExecId] = useState<string>('');
  const [buttonLoading, setButtonLoading] = useState(false);
  const [promptHumanId, setPromptHumanId] = useState<string>('');
  const flowMessage = useSocketStore(state => state.flowMessage);
  const setFlowMessage = useSocketStore(state => state.setFlowMessage);
  const processingRef = useRef(false);

  const { loading, runAsync } = useRequest(getDealtWithInfo, {
    manual: true,
  }) as { loading: boolean; runAsync: (id: string) => Promise<any> };

  useEffect(() => {
    setShow(!!dealtWithData);
    const id = dealtWithData?.data?.node_exec_data?.node_exec_id || dealtWithData?.exec_id || '';
    setExecId(id);
    if (id) {
      getHumanMessage(id);
    }
    return () => {
      setShow(false);
    };
  }, [dealtWithData]);

  const getHumanMessage = useCallback((id: string) => {
    if (loading || processingRef.current) return;
    
    processingRef.current = true;
    runAsync(id).then(res => {
      if (res && res.data) {
        setDealtWithInfo(res.data);
        if (id !== promptHumanId) {
          setButtonLoading(false);
          setPromptHumanId(id);
        }
      }
      processingRef.current = false;
    }).catch(() => {
      processingRef.current = false;
    });
  }, [loading, promptHumanId, runAsync]);

  const lastMsgIdRef = useRef<string | null>(null);
  const lastExecIdRef = useRef<string | null>(null);
  
  useEffect(() => {
    if (!execId || !flowMessage.length) return;
    if (execId === lastExecIdRef.current) return;
    
    lastExecIdRef.current = execId;
    
    const newHumanMessage = flowMessage.find(
      item => item?.data?.node_exec_data?.node_exec_id === execId
    );
    
    if (newHumanMessage) {
      const msgId = newHumanMessage.id || newHumanMessage.data?.node_exec_data?.node_exec_id;
      
      if (msgId && msgId !== lastMsgIdRef.current) {
        lastMsgIdRef.current = msgId;
        getHumanMessage(execId);
      }
    }
  }, [flowMessage, execId, getHumanMessage]);

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

  const submitPrompt = useCallback((values: any) => {
    setButtonLoading(true);
    
    return updateDealtWith(execId, {
      correct_prompt:values.correct_prompt|| new Prompt('', values.prompt, ''),
      operation:values.operation!==undefined?values.operation:1,
      outputs: dealtWithInfo?.outputs || null,
    });
  }, [execId, dealtWithInfo]);

  const confirmDealtWith = useCallback((targetExecId?: string) => {
    // Prioritize the passed execId, if not present use the state execId
    const idToUse = targetExecId || execId;
    
    return updateDealtWith(idToUse, {
      operation: 0,
      outputs: dealtWithInfo?.outputs || null,
    });
  }, [execId, dealtWithInfo]);

  const submitHumanContent = useCallback((values: any, inputVar: any, inputsArr: any[]) => {
    const input = createVariableFromObject(inputVar);
    if (inputsArr.length > 0) {
      const variables = Object.entries(values).filter(([key]) =>
        key.startsWith('variables.'),
      );
      variables.forEach(([key, value]) => {
        if (input.properties) {
          input.properties[key.replace('variables.', '')].value = value;
        }
      });
    }
    
    const freeFile = new ArrayVariable(UPLOAD_FILES_KEY, 'array[number]');
    values.file &&
      values.file.forEach((x: any) => {
        const fileVariable = new Variable(
          x.uid,
          'number',
          x?.response?.data?.file_id || 0,
        );
        freeFile.addValue(fileVariable);
      });
    input.addProperty(UPLOAD_FILES_KEY, freeFile);

    const knowledge_base_mapping = dealtWithInfo?.node_graph?.data?.knowledge_base_mapping || {
      input: {},
      output: {},
    };
    
    Object.entries(values).forEach(([key, value]) => {
      if (key.startsWith('dataset.')) {
        if (!knowledge_base_mapping.input[UPLOAD_FILES_KEY]) {
          knowledge_base_mapping.input[UPLOAD_FILES_KEY] = {};
        }
        knowledge_base_mapping.input[UPLOAD_FILES_KEY][key.replace('dataset.', '')] = value;
      }
    });
    
    return updateDealtWith(execId, {
      operation: 0,
      inputs: input,
      outputs: null,
      correct_prompt: null,
      knowledge_base_mapping,
    });
  }, [execId, dealtWithInfo]);

  const submitCustomOutput = useCallback((outputsValue: string) => {
    try {
      const outputs = JSON.parse(outputsValue);
      return updateDealtWith(execId, {
        outputs: Array.isArray(outputs) ? outputs[0] : outputs,
      });
    } catch (error) {
      return Promise.reject(error);
    }
  }, [execId]);

  return {
    show,
    setShow,
    dealtWithInfo,
    execId,
    setExecId,
    buttonLoading,
    setButtonLoading,
    getHumanMessage,
    delHumanMessage,
    submitPrompt,
    confirmDealtWith,
    submitHumanContent,
    submitCustomOutput
  };
}; 