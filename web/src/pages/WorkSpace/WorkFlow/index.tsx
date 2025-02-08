/*
 * @LastEditors: biz
 */
import WorkFlowLeftMenu from '@/components/WorkFlow/components/Menu/WorkFlowLeftMenu';
import WorkFlow from '@/components/WorkFlow';
import React from 'react';

const WorkSpace: React.FC = () => {
    return (
        <div style={{ height: `calc(100vh - 56px)` }} className="w-full relative overflow-x-auto">
             {/* <WorkFlowLeftMenu></WorkFlowLeftMenu> */}
            <WorkFlow />

        </div>
    );
};
export default WorkSpace;
