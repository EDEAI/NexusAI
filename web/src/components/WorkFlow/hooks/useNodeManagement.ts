/*
 * @LastEditors: biz
 */
import { useState } from 'react';

const useNodeManagement = () => {
    const [nodes, setNodes] = useState([]);

    const addNode = newNode => {
        setNodes(prevNodes => [...prevNodes, newNode]);
    };

    return { nodes, addNode };
};

export default useNodeManagement;
