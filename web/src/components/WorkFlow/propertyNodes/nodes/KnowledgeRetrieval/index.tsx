import React from 'react';
import { Handle, Position } from 'reactflow';
import { PropertyNodeEnum } from '../../../types';
import { useIntl } from 'umi';

interface Props {
    data: {
        title: string;
        entitle: string;
        desc: string;
        selected?: boolean;
    };
    selected?: boolean;
}

const KnowledgeRetrieval: React.FC<Props> = ({ data, selected }) => {
    const intl = useIntl();
    const isEn = intl.locale === 'en-US';

    return (
        <div
            className={`px-2 py-1 rounded-md shadow-lg bg-white border-2 ${
                selected ? 'border-primary' : 'border-gray-200'
            }`}
        >
            <Handle
                type="target"
                position={Position.Left}
                className="w-3 h-3 rounded-full bg-gray-400"
            />
            <div className="flex items-center space-x-2">
                <div className="w-8 h-8 flex items-center justify-center bg-primary/10 rounded-md">
                    <i className="iconfont icon-knowledge text-primary text-xl" />
                </div>
                <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">
                        {isEn ? data.entitle : data.title}
                    </div>
                    {data.desc && (
                        <div className="text-xs text-gray-500">{data.desc}</div>
                    )}
                </div>
            </div>
            <Handle
                type="source"
                position={Position.Right}
                className="w-3 h-3 rounded-full bg-gray-400"
            />
        </div>
    );
};

export default KnowledgeRetrieval; 