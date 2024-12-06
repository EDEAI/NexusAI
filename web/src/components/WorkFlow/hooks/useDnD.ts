import { useCallback } from 'react';

const useDnD = screenToFlowPosition => {
    const handleDragOver = useCallback(event => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    const handleDrop = useCallback(
        event => {
            event.preventDefault();
            const data = event.dataTransfer.getData('application/reactflow');
            if (!data) return null;

            const { type, item } = JSON.parse(data);
            if (!type || !item) return null;

            const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
            return { position, type, item }; 
        },
        [screenToFlowPosition],
    );

    const onDnD = useCallback(
        callback => {
            const handleDropWithCallback = event => {
                const result = handleDrop(event);
                if (result) {
                    callback(result.position, result.type, result.item); 
                }
            };

            
            document.addEventListener('dragover', handleDragOver);
            document.addEventListener('drop', handleDropWithCallback);

           
            return () => {
                document.removeEventListener('dragover', handleDragOver);
                document.removeEventListener('drop', handleDropWithCallback);
            };
        },
        [handleDragOver, handleDrop],
    );

    return { onDnD };
};

export default useDnD;
