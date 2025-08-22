import { useCallback } from 'react';
import Fuse from 'fuse.js';
import { getLocale } from '@umijs/max';
import { UseNodeSearchOptions } from './types';

export const useNodeSearch = (options: UseNodeSearchOptions = {}) => {
    const {
        nodeSearchThreshold = 0.3,
        toolSearchThreshold = 0.4,
    } = options;

    const lang = getLocale() === 'en-US' ? 'en_US' : 'zh_Hans';

    const searchNodesByKeyword = useCallback(
        (nodes: any[], keyword: string) => {
            if (!keyword) return nodes;

            const fuse = new Fuse(nodes, {
                keys: ['data.title', 'type', 'data.desc'],
                threshold: nodeSearchThreshold,
                includeScore: true,
            });

            const results = fuse.search(keyword);
            return results.map(result => result.item);
        },
        [nodeSearchThreshold],
    );

    const searchToolsByKeyword = useCallback(
        (tools: any[], keyword: string) => {
            if (!keyword) return tools;

            // Flatten tools for better search experience
            const flattenedTools = tools.map(category => ({
                ...category,
                tools: category.tools?.map((tool: any) => ({
                    ...tool,
                    categoryName: category.identity?.label?.[lang],
                    categoryIcon: category.identity?.icon,
                })),
            }));

            const fuse = new Fuse(flattenedTools, {
                keys: [
                    'identity.label.zh_Hans',
                    'identity.label.en_US',
                    'identity.description.zh_Hans',
                    'identity.description.en_US',
                    'tools.identity.label.zh_Hans',
                    'tools.identity.label.en_US',
                    'tools.description.human.zh_Hans',
                    'tools.description.human.en_US',
                ],
                threshold: toolSearchThreshold,
                includeScore: true,
                useExtendedSearch: true,
            });

            const results = fuse.search(keyword);

            return results
                .map(result => ({
                    ...result.item,
                    tools: result.item.tools,
                }))
                .filter(item => item.tools.length > 0);
        },
        [lang, toolSearchThreshold],
    );

    const searchWorkflowsByKeyword = useCallback(
        (workflows: any[], keyword: string) => {
            if (!keyword) return workflows;

            const fuse = new Fuse(workflows, {
                keys: ['data.title', 'data.desc', 'baseData.name', 'baseData.description'],
                threshold: nodeSearchThreshold,
                includeScore: true,
            });

            const results = fuse.search(keyword);
            return results.map(result => result.item);
        },
        [nodeSearchThreshold],
    );

    return {
        searchNodesByKeyword,
        searchToolsByKeyword,
        searchWorkflowsByKeyword,
        lang,
    };
};



