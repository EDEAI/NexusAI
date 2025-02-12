/*
 * @LastEditors: biz
 */
import { BlockEnum, PropertyNodeEnum } from '../types';
import { PropertyNodeConfig, PropertyNodeCustomType } from './types';
import KnowledgeRetrieval from './nodes/KnowledgeRetrieval';
import KnowledgeRetrievalPanel from './nodes/KnowledgeRetrieval/panel';

export const PropertyNodeCustom: PropertyNodeCustomType = {
    [PropertyNodeEnum.KnowledgeRetrieval]: {
        node: KnowledgeRetrieval,
        panel: KnowledgeRetrievalPanel,
        icon: PropertyNodeEnum.KnowledgeRetrieval,
        title: '知识库检索',
        entitle: 'Knowledge Retrieval',
        base: {
            type: PropertyNodeEnum.KnowledgeRetrieval,
            data: {
                title: '知识库检索',
                entitle: 'Knowledge Retrieval',
                desc: '',
                descTools: '从知识库中检索相关内容以增强节点的处理能力',
                endescTools: 'Retrieve relevant content from knowledge base to enhance node processing capabilities',
                propertyType: PropertyNodeEnum.KnowledgeRetrieval,
                targetNodeTypes: [BlockEnum.LLM, BlockEnum.Agent],
                outputInfo: {
                    key: 'knowledge',
                    type: 'array',
                    base: true,
                },
            },
        },
    },
};

export const getBasePropertyNode = (type?: PropertyNodeEnum): PropertyNodeConfig | PropertyNodeCustomType => {
    if (type) {
        return PropertyNodeCustom[type];
    }
    return PropertyNodeCustom;
}; 