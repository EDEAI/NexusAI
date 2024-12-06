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
