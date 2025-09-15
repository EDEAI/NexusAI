/*
 * @LastEditors: biz
 */
export interface RunPanelData {
  data?: {
    app_run_id?: string;
    node_exec_data?: {
      node_exec_id?: string;
      node_type?: string;
      node_name?: string;
      inputs?: any;
      outputs?: any;
      outputs_md?: string;
      status?: number;
      elapsed_time?: number;
      file_list?: any[];
      prompt_data?: any;
      parent_exec_id?: string;
      first_task_exec_id?: string;
    };
    status?: number;
    error?: string;
    elapsed_time?: number;
    total_tokens?: number;
    completion_tokens?: number;
    created_time?: string;
    actual_completed_steps?: string;
  };
  type?: string;
  human?: boolean;
  children?: RunPanelData[];
  finished_time?: string;
}

export interface RunResultInfo {
  app_run_id?: string;
  [key: string]: any;
}

export interface ContentProps {
  runList: RunPanelData[];
  flowMessage: any[];
  setDealtWithData: (data: any) => void;
  setFlowMessage: (message: any[]) => void;
}

export interface InputContentProps {
  onRunResult: (res: any) => void;
  loading?: boolean;
  onCancelSchedule?: (taskId: number) => void;
  appId?: number;
  workflowId?: number;
}

export interface DetailContentProps {
  endRun: RunPanelData | null;
}

export interface ContainerProps {
  runPanelShow: boolean;
  setRunPanelShow: (show: boolean) => void;
  title: string;
  tabItems: {
    label: string;
    key: string;
    disabled?: boolean;
    children: React.ReactNode;
  }[];
  activeKey: string;
  onTabChange: (key: string) => void;
  children?: React.ReactNode;
  showPauseResume?: boolean;
  isPaused?: boolean;
  onPauseResume?: () => void;
}