/*
 * @LastEditors: biz
 */

import AgentCreate from '@/components/AgentCreate';
import DealtWithForLog from '@/components/WorkFlow/components/DealtWith/DealtWithForLog';
import RunPanelLog from '@/components/WorkFlow/nodes/RunPanelLog';
import RunWorkFlow from '@/components/WorkFlow/RunWorkFlow';
import React from 'react';

interface PlazaProps {
    children: React.ReactNode;
}

const PageWrap: React.FC<PlazaProps> = ({ children }) => {
    return (
        <div className="layout">
            <div>{children}</div>
            <DealtWithForLog></DealtWithForLog>
            <RunPanelLog></RunPanelLog>
            <RunWorkFlow></RunWorkFlow>
            <AgentCreate></AgentCreate>
        </div>
    );
};

export default PageWrap;
