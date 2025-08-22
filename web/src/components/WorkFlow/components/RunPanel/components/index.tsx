/*
 * @LastEditors: biz
 */
import { memo } from 'react';
import { useRunPanelState } from './hooks';
import Container from './Container';
import DetailContent from './DetailContent';
import InputContent from './InputContent';
import TrackContent from './TrackContent';
import { useIntl } from '@umijs/max';
import { useUpdateEffect } from 'ahooks';
import { Spin } from 'antd';

const RunPanel = memo(() => {
  const intl = useIntl();
  const {
    runPanelShow,
    setRunPanelShow,
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
    setDealtWithData,
    flowMessage,
    setFlowMessage,
    isPaused,
    showPauseResume,
    handlePauseResume,
  } = useRunPanelState();
  
  // Process run list updates
  useUpdateEffect(() => {
    processRunList();
  }, [flowMessage, runResultInfo]);
  
  return (
    <Container
      runPanelShow={runPanelShow}
      setRunPanelShow={setRunPanelShow}
      title={intl.formatMessage({ id: 'workflow.run' })}
      showPauseResume={showPauseResume}
      isPaused={isPaused}
      onPauseResume={handlePauseResume}
      tabItems={[
        {
          label: intl.formatMessage({ id: 'workflow.inputs' }),
          key: '1',
          children: (
            <InputContent 
              loading={loading} 
              onRunResult={runResult}
            />
          ),
        },
        {
          label: intl.formatMessage({ id: 'workflow.result' }),
          key: '3',
          disabled: !endRun,
          children: (
            <DetailContent 
              endRun={endRun} 
            />
          ),
        },
        {
          label: intl.formatMessage({ id: 'workflow.backTo' }),
          key: '4',
          disabled: !hasResult,
          children: (
            <div>
              {runList && runList.length > 0 ? (
                <TrackContent
                  key="track-content"
                  runList={runList}
                  flowMessage={flowMessage}
                  setDealtWithData={setDealtWithData}
                  setFlowMessage={setFlowMessage}
                />
              ) : (
                <div className="text-center justify-center items-center flex">
                  <Spin />
                </div>
              )}
            </div>
          ),
        },
      ]}
      activeKey={tabKey}
      onTabChange={setTabKey}
    />
  );
});

export default RunPanel;

export { default as Container } from './Container';
export { default as InputContent } from './InputContent';
export { default as DetailContent } from './DetailContent';
export { default as TrackContent } from './TrackContent';
export * from './hooks';
export * from './types';
export * from './utils';