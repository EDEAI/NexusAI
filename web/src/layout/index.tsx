/*
 * @LastEditors: biz
 */

import AgentCreate from '@/components/AgentCreate';
import SkillCreate from '@/components/SkillCreate';
import DealtWithForLog from '@/components/WorkFlow/components/DealtWith/DealtWithForLog';
import RunPanelLog from '@/components/WorkFlow/nodes/RunPanelLog';
import RunWorkFlow from '@/components/WorkFlow/RunWorkFlow';
import React from 'react';

interface PlazaProps {
    children: React.ReactNode;
}

const PageWrap: React.FC<PlazaProps> = ({ children }) => {
    return (
        <div className="layout ">
            <div>{children}</div>

            <RunPanelLog></RunPanelLog>
            <DealtWithForLog></DealtWithForLog>
            <RunWorkFlow></RunWorkFlow>
            <AgentCreate></AgentCreate>
            <SkillCreate></SkillCreate>
        </div>
    );
};

export default PageWrap;
