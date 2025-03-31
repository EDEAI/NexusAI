/*
 * @LastEditors: biz
 */
import { updateDealtWith } from '@/api/workflow';
import useUserStore from '@/store/user';
import useSocketStore from '@/store/websocket';
import { memo, useCallback } from 'react';
import { BlockEnum } from '../../types';
import { Container, CustomContent, HumanContent, LLMContent, useDealtWithState } from './components';

interface DealtWithForLogNewProps {
  onSubmit?: (execId: string) => void;
}


export default memo(({ onSubmit }: DealtWithForLogNewProps) => {
  const dealtWithData = useUserStore(state => state.dealtWithData);
  const setDealtWithData = useUserStore(state => state.setDealtWithData);
  const setPrevConfirmDealtWith = useUserStore(state => state.setPrevConfirmDealtWith);
  const setSubmitPromptId = useUserStore(state => state.setSubmitPromptId);
  
  const {
    show,
    setShow,
    dealtWithInfo,
    execId,
    buttonLoading,
    setButtonLoading,
    delHumanMessage,
    submitPrompt,
    confirmDealtWith,
  } = useDealtWithState(dealtWithData);

  const handleSubmitPrompt = useCallback((values: any) => {
    setButtonLoading(true);
    submitPrompt(values).then(res => {
      if (res.code === 0) {
        setShow(false);
        setSubmitPromptId(execId);
        setPrevConfirmDealtWith(dealtWithData);
        setDealtWithData(null);
        onSubmit?.(execId);
      }
    });
  }, [dealtWithData, execId, onSubmit, setPrevConfirmDealtWith, setButtonLoading, setDealtWithData, setShow, setSubmitPromptId, submitPrompt]);

  const handleConfirmDealtWith = useCallback(() => {
    confirmDealtWith().then(res => {
      if (res.code === 0) {
        setShow(false);
        setSubmitPromptId(execId);
        delHumanMessage(execId);
        setPrevConfirmDealtWith(dealtWithData);
        setDealtWithData(null);
      }
    });
  }, [confirmDealtWith, dealtWithData, delHumanMessage, execId, setPrevConfirmDealtWith, setDealtWithData, setShow, setSubmitPromptId]);

  const handleUpdate = useCallback((execId: string, options: any) => {
    return updateDealtWith(execId, options).then(res => {
      if (res.code === 0) {
        setShow(false);
        setSubmitPromptId(execId);
        setPrevConfirmDealtWith(dealtWithData);
        setDealtWithData(null);
      }
      return res;
    });
  }, [dealtWithData, setPrevConfirmDealtWith, setDealtWithData, setShow, setSubmitPromptId]);

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
          onUpdate={handleUpdate}
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
          onUpdate={handleUpdate}
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
        onUpdate={handleUpdate}
      />
    );
  }, [
    buttonLoading,
    dealtWithData,
    dealtWithInfo,
    execId,
    handleSubmitPrompt,
    handleUpdate,
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
      onClose={() => {
        setShow(false);
        setDealtWithData(null);
      }}
    >
      {renderContent()}
    </Container>
  );
}); 