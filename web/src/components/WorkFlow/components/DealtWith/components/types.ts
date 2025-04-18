export interface DealtWithData {
  data?: {
    node_exec_data?: {
      node_exec_id?: string;
      node_type?: string;
    };
  };
  exec_id?: string;
}

export interface DealtWithInfo {
  node_type?: string;
  inputs?: any;
  outputs?: any;
  correct_llm_history?: any[];
  node_graph?: {
    data?: {
      title?: string;
      desc?: string;
      input?: any;
      requires_upload?: boolean;
      import_to_knowledge_base?: {
        input?: any;
      };
      knowledge_base_mapping?: {
        input: Record<string, any>;
        output: Record<string, any>;
      };
    };
  };
}


export interface LLMSubmitData {
  correct_prompt: {
    system?: { value: string };
    user: { value: string };
    assistant?: { value: string };
  };
  operation: number;
  outputs: any;
}

export interface ContentProps {
  dealtWithInfo: DealtWithInfo | null;
  dealtWithData: DealtWithData | null;
  execId: string;
  buttonLoading: boolean;
  onSubmit: (values: LLMSubmitData | any) => void;
  onUpdate: (execId: string, options: any) => Promise<any>;
}

export interface ContainerProps {
  dealtWithData: DealtWithData | null;
  setDealtWithData: (data: DealtWithData | null) => void;
  show: boolean;
  setShow: (show: boolean) => void;
  execId: string;
  dealtWithInfo: DealtWithInfo | null;
  buttonLoading: boolean;
  onConfirm?: (execId: string) => void;
  onClose?: () => void;
  children?: React.ReactNode;
} 