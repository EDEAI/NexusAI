/*
 * @LastEditors: biz
 */
import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

interface MermaidChartProps {
    code: string;
    index: number;
}

const MermaidChart: React.FC<MermaidChartProps> = ({ code, index }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const chartId = `mermaid-chart-${index}-${Math.random().toString(36).substr(2, 9)}`;

    useEffect(() => {
        if (!containerRef.current) return;

        // Initialize mermaid
        mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: 'Arial, sans-serif',
            fontSize: 14,
        });

        const renderChart = async () => {
            try {
                const { svg } = await mermaid.render(chartId, code);
                if (containerRef.current) {
                    containerRef.current.innerHTML = svg;
                    debugger
                }
                
            } catch (error) {
                console.error('Mermaid rendering error:', error);
                if (containerRef.current) {
                    containerRef.current.innerHTML = `
                        <div class="p-4 text-red-500 bg-red-50 border border-red-200 rounded">
                            <p class="font-medium">图表渲染失败</p>
                            <p class="text-sm mt-1">${error.message}</p>
                        </div>
                    `;
                }
            }
        };

        renderChart();
    }, [code, chartId]);

    return (
        <div className="my-4 p-4 bg-white border border-gray-200 rounded-lg">
            <div 
                ref={containerRef} 
                className="flex justify-center items-center min-h-[200px]"
                id={chartId}
            />
        </div>
    );
};

export default MermaidChart; 