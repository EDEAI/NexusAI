/*
 * @LastEditors: biz
 */

import { Footer } from '@/components';
import RunWorkFlow from '@/components/WorkFlow/RunWorkFlow';
import React from 'react';
import Backlogs from './components/Backlogs';
import RecentlyActive from './components/RecentlyActive';
import WorkFlowLog from './components/WorkFlowLog';
import './index.less';
const WorkSpace: React.FC = () => {
    return (
        <div
            style={{ height: `calc(100vh - 56px)` }}
            className="w-full p-[30px] flex flex-col gap-6 overflow-x-auto box-border"
        >
            <RecentlyActive></RecentlyActive>
            <div className="grid grid-cols-2 gap-6 flex-1">
                <Backlogs></Backlogs>
                <WorkFlowLog></WorkFlowLog>
            </div>
            <Footer></Footer>
            <RunWorkFlow></RunWorkFlow>
        </div>
    );
};

export default WorkSpace;
