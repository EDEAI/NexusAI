/*
 * @LastEditors: biz
 */

import LLMNode from '@/py2js/nodes/llm.js';
import StartNode from '@/py2js/nodes/start.js';
import { createPromptFromObject } from '@/py2js/prompt.js';

import { Edge } from '@/py2js/edges.js';
import _ from 'lodash';
import { AppNode, BlockEnum } from '../types';

export function customFreeNode(node: AppNode) {
    console.log('createNode', node);

    const { data, type, position, id } = _.cloneDeep(node);
    const createObj = {
        title: data['title'] || '',
        desc: data['desc'] || '',
        position,
        original_node_id: id || null,
    };
    delete data['title'];
    delete data['desc'];
    switch (type) {
        case BlockEnum.Start:
            return new StartNode({
                ...createObj,
                input: data['input'] || null,
                requires_upload: data['requires_upload'] || false,
            });
        case BlockEnum.Agent:
            return new StartNode({
                ...createObj,
                input: data['input'] || null,
                requires_upload: data['requires_upload'] || false,
            });
        case BlockEnum.LLM:
            return new LLMNode({
                ...createObj,
            });
        default:
            break;
    }

    // console.error('：', type, node);
}

export function customFreeEdge(source, target) {
    const edge = {
        id: `${source}-${target}`,
        source: source,
        target: target,
    };
    return new Edge(0, source, target, null, null, false, 0, null, edge.id);
}

export function getNodePosition(currentNode) {
    const x = currentNode.position.x + currentNode.measured.width + 30;
    const y = currentNode.position.y;
    return { x, y };
}

export function createPrompt(promptObj) {
    return createPromptFromObject(promptObj);
}
