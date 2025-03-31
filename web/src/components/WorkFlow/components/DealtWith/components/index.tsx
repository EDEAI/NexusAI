import { updateDealtWith } from '@/api/workflow';
import { BlockEnum } from '@/components/WorkFlow/types';
import useSocketStore from '@/store/websocket';
import { memo, useCallback, useEffect, useRef } from 'react';
import Container from './Container';
import CustomContent from './CustomContent';
import HumanContent from './HumanContent';
import LLMContent from './LLMContent';
import { useDealtWithState } from './hooks';

interface DealtWithProps {
  onSubmit?: (execId: string) => void;
  onClose?: () => void;
}

const DealtWith = memo(({ onSubmit, onClose }: DealtWithProps) => {
  const dealtWithData = useSocketStore(state => state.dealtWithData);
  const setDealtWithData = useSocketStore(state => state.setDealtWithData);
  const flowMessage = useSocketStore(state => state.flowMessage);
  
  // Reference to track if correction has been submitted
  const submitSuccessRef = useRef(false);
  // Reference to store the returned execId after submission
  const submitExecIdRef = useRef('');
  
  const {
    show,
    setShow,
    dealtWithInfo,
    execId,
    setExecId,
    buttonLoading,
    setButtonLoading,
    delHumanMessage,
    submitPrompt,
    confirmDealtWith,
    getHumanMessage,
  } = useDealtWithState(dealtWithData);

  const handleSubmitPrompt = useCallback((values: any) => {
    setButtonLoading(true);
    // When submitting LLM correction content, don't automatically close the page
    updateDealtWith(execId, values).then(res => {
      if (res.code === 0) {
        // Only delete the message, but don't close the page
        delHumanMessage(execId);
        setButtonLoading(false);
        // Mark submission as successful, save new execId for monitoring
        submitSuccessRef.current = true;
        if (res.data && res.data.exec_id) {
          submitExecIdRef.current = res.data.exec_id;
          // Immediately update the current execId to the newly returned execId
          setExecId(res.data.exec_id);
        }
      }
    });
  }, [delHumanMessage, execId, setButtonLoading, setExecId]);

  // Effect to monitor correction results
  useEffect(() => {
    // If correction has been submitted and we have a new execId
    if (submitSuccessRef.current && submitExecIdRef.current) {
      // Find a message in flowMessage that matches the new execId
      const newLLMResult = flowMessage.find(
        item => item?.data?.node_exec_data?.node_exec_id === submitExecIdRef.current
      );
      
      // If a matching message is found, get the latest information
      if (newLLMResult) {
        getHumanMessage(submitExecIdRef.current);
        // Reset flag to avoid duplicate fetches
        submitSuccessRef.current = false;
      }
    }
  }, [flowMessage, getHumanMessage]);

  const handleConfirmDealtWith = useCallback(() => {
    // Use the latest execId for confirmation
    const currentExecId = submitExecIdRef.current || execId;
    
    confirmDealtWith(currentExecId).then(res => {
      if (res.code === 0) {
        setShow(false);
        delHumanMessage(currentExecId);
        setDealtWithData(null);
        onSubmit?.(currentExecId);
        // Reset submission status
        submitSuccessRef.current = false;
        submitExecIdRef.current = '';
      }
    });
  }, [confirmDealtWith, delHumanMessage, execId, onSubmit, setDealtWithData, setShow]);

  const handleHumanUpdate = useCallback((execId: string, options: any) => {
    return updateDealtWith(execId, options).then(res => {
      if (res.code === 0) {
        setShow(false);
        delHumanMessage(execId);
        setDealtWithData(null);
        onSubmit?.(execId);
      }
      return res;
    });
  }, [delHumanMessage, onSubmit, setDealtWithData, setShow]);

  const handleCustomUpdate = useCallback((execId: string, options: any) => {
    return updateDealtWith(execId, options).then(res => {
      if (res.code === 0) {
        setShow(false);
        delHumanMessage(execId);
        setDealtWithData(null);
        onSubmit?.(execId);
      }
      return res;
    });
  }, [delHumanMessage, onSubmit, setDealtWithData, setShow]);

  const renderContent = useCallback(() => {
    const nodeType = dealtWithInfo?.node_type;
    if (nodeType === BlockEnum.Human) {
      return (
        <HumanContent
          dealtWithInfo={dealtWithInfo}
          dealtWithData={dealtWithData}
          execId={execId}
          buttonLoading={buttonLoading}
          onSubmit={handleSubmitPrompt}
          onUpdate={handleHumanUpdate}
        />
      );
    } else if (
      nodeType === BlockEnum.LLM ||
      nodeType === BlockEnum.Agent ||
      nodeType === BlockEnum.TaskGeneration
    ) {
      return (
        <LLMContent
          dealtWithInfo={dealtWithInfo}
          dealtWithData={dealtWithData}
          execId={execId}
          buttonLoading={buttonLoading}
          onSubmit={handleSubmitPrompt}
          onUpdate={handleHumanUpdate}
        />
      );
    }
    return (
      <CustomContent
        dealtWithInfo={dealtWithInfo}
        dealtWithData={dealtWithData}
        execId={execId}
        buttonLoading={buttonLoading}
        onSubmit={handleSubmitPrompt}
        onUpdate={handleCustomUpdate}
      />
    );
  }, [
    buttonLoading,
    dealtWithData,
    dealtWithInfo,
    execId,
    handleSubmitPrompt,
    handleHumanUpdate,
    handleCustomUpdate,
  ]);

  return (
    <Container
      dealtWithData={dealtWithData}
      setDealtWithData={setDealtWithData}
      show={show}
      setShow={setShow}
      execId={execId}
      dealtWithInfo={dealtWithInfo}
      buttonLoading={buttonLoading}
      onConfirm={handleConfirmDealtWith}
      onClose={onClose}
    >
      {renderContent()}
    </Container>
  );
});

export default DealtWith;

export { default as Container } from './Container';
export { default as CustomContent } from './CustomContent';
export { default as HumanContent } from './HumanContent';
export { default as LLMContent } from './LLMContent';
export * from './hooks';
export * from './types';
export * from './utils'; 