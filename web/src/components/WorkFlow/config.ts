/*
 * @LastEditors: biz
 */

import { BlockEnum } from './types';

export const EDGE_COLOR = {
    SELECT: '#875bf7',
    DEFAULT: '#b1b1b7',
    NODE_HOVER: '#2970ff',
};

export const HANDLE_COLOR = {
    DEFAULT: '#2970ff',
    DISABLE: '#875bf7',
};

export const UPLOAD_FILES_KEY = '4d6f7265-cde2-d0c7-c8cb-636f6d696e67';
export const CURRENT_NODE_ID = '536f6e67-bcab-cbd9-cfc0-4d6172637573';

export const NOT_RUN_NODE_TYPE = [
    BlockEnum.ConditionBranch,
    BlockEnum.Start,
    BlockEnum.End,
    BlockEnum.Human,
    BlockEnum.TaskExecution,
];

export enum WORKFLOW_ICON {
    WorkFlow = 'signgongzuoliu',
    Agent = 'pitchagent',
    Skill = 'signskill',
    Dataset = 'signzhishik',
    ChatRoom = 'chat_room',
}

export const NOT_SHOW_INPUT_RESULT_NODE = [BlockEnum.LLM, BlockEnum.End];
export const NOT_SHOW_OUTPUT_RESULT_NODE = [BlockEnum.Start];


export const NODE_COLOR={
    [BlockEnum.Start]:'#0765C2',
    [BlockEnum.End]: '#0765C2',

    [BlockEnum.CustomCode]: '#1AA3B3',
    [BlockEnum.TemplateConversion]: '#1AA3B3',

    [BlockEnum.TaskExecution]: '#209058',
    [BlockEnum.TaskGeneration]: '#209058',

    [BlockEnum.ConditionBranch]: '#E49B68',
    [BlockEnum.RequirementCategory]: '#E49B68',
    [BlockEnum.Retriever]: '#E49B68',

    [BlockEnum.Agent]: '#7967C8',
    [BlockEnum.Human]: '#2382DF',
    [BlockEnum.LLM]: '#AF68D0',
    [BlockEnum.VariableAggregation]: '#D569AF',
    [BlockEnum.Skill]: '#DBAF16',
    [BlockEnum.HttpRequest]: '#E086AB',
    [BlockEnum.Tool]: '#5A8852',
}
export const NODES_GROUP={
    custom:{
        name:'Custom',
        color:'#1AA3B3',
        nodes:[BlockEnum.CustomCode,BlockEnum.TemplateConversion]
    },
    task:{
        name:'Task',
        color:'#209058',
        nodes:[BlockEnum.TaskGeneration,BlockEnum.TaskExecution]
    },
    category:{
        name:'Category',
        color:'#E086AB',
        nodes:[BlockEnum.RequirementCategory,BlockEnum.ConditionBranch,BlockEnum.Retriever]
    },
    [BlockEnum.Start]:'#0765C2',
    [BlockEnum.End]: '#0765C2',
    
    [BlockEnum.Agent]: '#7967C8',
    [BlockEnum.Human]: '#2382DF',
    [BlockEnum.LLM]: '#AF68D0',
    [BlockEnum.VariableAggregation]: '#D569AF',
    [BlockEnum.Skill]: '#DBAF16',
    [BlockEnum.HttpRequest]: '#E086AB',
    [BlockEnum.Tool]: '#5A8852',

}