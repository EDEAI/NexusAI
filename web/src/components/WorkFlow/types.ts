/*
 * @LastEditors: biz
 */
import { Nodes } from '@/py2js/nodes/base.js';
import {
    Node as BaseNode,
    BuiltInNode,
    Edge,
    OnConnect,
    OnEdgesChange,
    OnInit,
    OnNodesChange,
} from '@xyflow/react';

type AppNodeData = {
    title: string;
    desc?: string;
    input?: string;
    level?: number;
    [key: string]: any;
};
export type AppNode =
    | (BaseNode & {
          type: BlockEnum;
          data: AppNodeData;
          level?: number;
      })
    | BuiltInNode;

export type Viewport = {
    x: number;
    y: number;
    zoom: number;
};
type CustomEdge = Edge & {
    level?: number;
    [key: string]: any;
};

export type AppState = {
    nodes: AppNode[];
    edges: CustomEdge[];
    workFlowInfo: object;
    freeNodes: Nodes;
    agentData: any;
    skillData: any;
    selectedNode: AppNode;
    toolData: any;
    modelData: any;
    datasetData: any;
    preventScrolling: boolean;
    app_id: string;
    runPanelShow: boolean;
    viewport: Viewport;
    runPanelNodeShow: boolean | AppNode;
    dealtWithData: any;
    handleList: any;
    workflowEditInfo: any;
    showChildNode: any;
    teamDatasetData: any;
    getNode: (nodeId: string) => AppNode;
    setShowChildNode: (value: any) => void;
    setWorkflowEditInfo: (value: any) => void;
    addHandleList: (list: any) => void;
    setHandleList: (list: any) => void;
    setDealtWithData: (value: any) => void;
    setRunPanelNodeShow: (value: boolean | AppNode) => void;
    setViewPort: (value: Viewport) => void;
    getModelData: () => any;
    setRunPanelShow: (value: boolean) => void;
    setWorkFlowInfo: (value: any) => void;
    setAppId: (value: string) => void;
    setPreventScrolling: (value: boolean) => void;
    addNode: (node: AppNode) => void;
    setAgentData: (data: any) => void;
    setSkillData: (data: any) => void;
    setToolData: (data: any) => void;
    setTeamDatasetData: (data: any) => void;
    setDatasetData: (data: any) => void;
    resetNodes: () => void;
    transformWorkFlow: () => {
        nodes: AppNode[];
        edges: CustomEdge[];
        freeNodes: any;
        freeEdges: any;
    };
    flowSetLevel: () => {
        nodes: AppNode[];
        edges: CustomEdge[];
        getNodeLevel: (string) => number;
        getEdgeLevel: (string) => number;
    };
    getAllConnectedElements: (nodeId: string, direction?: 'target' | 'source') => any;
    getOutputVariables: (nodeId: string, variable?: string) => any[];
    getInputVariables: (nodeId: string) => {
        inputs: any;
        context: any;
    };
    updateEdgeColors: (nodeId: string, color?: string) => void;
    createNode: (createType: NodeCreate['createType'], data?: object) => AppNode;
    setSelect: (nodeId: string, update?: boolean) => void;
    getSelectedNode: () => AppNode;
    updateNodeFromId: (nodeId: string, newNodeData: Partial<AppNode>) => void;
    updateNode: (newNode: AppNode) => void;
    updateNodeData: (nodeId: string, newData: Partial<AppNodeData>) => void;
    onNodesChange: OnNodesChange<AppNode>;
    onEdgesChange: OnEdgesChange;
    onConnect: OnConnect;
    onInit: OnInit;
    setNodes: (nodes: AppNode[]) => void;
    setEdges: (edges: Edge[]) => void;
    updateNodeColor: (nodeId: string, color: string) => void;
    nodeTypes: {};
    connectionLineStyle: {};
    defaultViewport: Viewport;
    onDrop: (event: React.DragEvent) => void;
    onDragOver: (event: React.DragEvent) => void;
    setNodeTypes: (nodeTypes: {}) => void;
    setConnectionLineStyle: (style: {}) => void;
    setDefaultViewport: (viewport: Viewport) => void;
    setOnDrop: (onDrop: (event: React.DragEvent) => void) => void;
    setOnDragOver: (onDragOver: (event: React.DragEvent) => void) => void;
};

export interface NodeCreate {
    createType: BlockEnum;
    position?: { x: number; y: number };
}

export enum BlockEnum {
    Start = 'start',
    End = 'end',
    Agent = 'agent',
    Answer = 'answer',
    Human = 'human',
    Retriever = 'retriever',
    LLM = 'llm',
    VariableAggregation = 'variable_aggregation',
    TemplateConversion = 'template_conversion',
    ConditionBranch = 'condition_branch',
    RequirementCategory = 'requirement_category',
    KnowledgeRetrieval = 'knowledge-retrieval',
    QuestionClassifier = 'question-classifier',
    IfElse = 'if-else',
    CustomCode = 'custom_code',
    Skill = 'skill',
    TemplateTransform = 'template-transform',
    HttpRequest = 'http_request',
    TaskExecution = 'recursive_task_execution',
    TaskGeneration = 'recursive_task_generation',
    Tool = 'tool',
    ParameterExtractor = 'parameter-extractor',
    Iteration = 'iteration',
}
export enum Conditions {
    Contains = '',
    DoesNotContain = '',
    StartsWith = '',
    EndsWith = '',
    Is = '',
    IsNot = '',
    IsEmpty = '',
    IsNotEmpty = '',
}
export enum Count {
    Equals = '=',
    NotEqual = '!=',
    GreaterThan = '>',
    LessThan = '<',
    GreaterThanOrEqualTo = '>=',
    LessThanOrEqualTo = '<=',
    Plus = '+',
    Minus = '-',
    Asterisk = '*',
    Slash = '/',
    Percent = '%',
    Increment = '++',
    Decrement = '--',
    LogicalAND = '&&',
    LogicalOR = '||',
    LogicalNOT = '!',
    BitwiseAND = '&',
    BitwiseOR = '|',
    BitwiseXOR = '^',
    BitwiseNOT = '~',
    LeftShift = '<<',
    RightShift = '>>',
    UnsignedRightShift = '>>>',
    PlusEquals = '+=',
    MinusEquals = '-=',
    MultiplyEquals = '*=',
    DivideEquals = '/=',
    ModulusEquals = '%=',
    BitwiseANDEquals = '&=',
    BitwiseOREquals = '|=',
    BitwiseXOREquals = '^=',
    LeftShiftEquals = '<<=',
    RightShiftEquals = '>>=',
    UnsignedRightShiftEquals = '>>>=',
    TernaryOperator = '?:',
}
export interface LLMNodeData {
    model_config_id?: number;
    prompt?: object | null;
    requires_upload?: boolean;
    wait_for_all_predecessors?: boolean;
    task_splitting?: boolean;
    manual_confirmation?: boolean;
    import_to_knowledge_base?: boolean;
    knowledge_base_mapping?: { [key: string]: number };
    originalNodeId?: string | null;
}
