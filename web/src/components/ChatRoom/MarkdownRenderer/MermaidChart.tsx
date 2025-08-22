/*
 * @LastEditors: biz
 */
import { Button, Image } from 'antd';
import mermaid from 'mermaid';
import React, { useCallback, useEffect, useMemo, useState } from 'react';

interface MermaidChartProps {
    code: string;
    index: number;
}

const MermaidChart: React.FC<MermaidChartProps> = ({ code, index }) => {
    const [svgContent, setSvgContent] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [previewVisible, setPreviewVisible] = useState<boolean>(false);
    const [previewSrc, setPreviewSrc] = useState<string>('');

    // Generate stable chartId using code hash to avoid unnecessary re-renders
    const chartId = useMemo(() => {
        const codeHash = code.split('').reduce((a, b) => {
            a = (a << 5) - a + b.charCodeAt(0);
            return a & a;
        }, 0);
        return `mermaid-chart-${index}-${Math.abs(codeHash)}`;
    }, [code, index]);

    // Memoized mermaid config to avoid repeated initialization
    const mermaidConfig = useMemo(
        () => ({
            startOnLoad: false,
            theme: 'default' as const,
            securityLevel: 'loose' as const,
            fontFamily: 'Arial, sans-serif',
            fontSize: 14,
        }),
        [],
    );

    const renderChart = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);

            // Initialize mermaid with memoized config
            mermaid.initialize(mermaidConfig);

            const { svg } = await mermaid.render(chartId, code);
            setSvgContent(svg);
        } catch (error: any) {
            console.error('Mermaid rendering error:', error);
            setError(error.message || 'Unknown error occurred');
        } finally {
            setIsLoading(false);
        }
    }, [code, chartId, mermaidConfig]);

    useEffect(() => {
        renderChart();
    }, [renderChart]);

    // Prepare preview src (data URL) for Antd Image preview to avoid object URL access issues
    useEffect(() => {
        if (!svgContent) {
            setPreviewSrc('');
            return;
        }
        const dataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgContent)}`;
        setPreviewSrc(dataUrl);
    }, [svgContent]);

    // Memoized render content to avoid unnecessary re-renders
    const renderContent = useMemo(() => {
        if (isLoading) {
            return (
                <div className="flex justify-center items-center min-h-[200px] text-gray-500">
                    <div className="text-sm">Loading chart...</div>
                </div>
            );
        }

        if (error) {
            return (
                <div className="p-4 text-red-500 bg-red-50 border border-red-200 rounded">
                    <p className="font-medium">图表渲染失败</p>
                    <p className="text-sm mt-1">{error}</p>
                </div>
            );
        }

        if (svgContent) {
            return (
                <div className="relative">
                    <div
                        className="flex justify-center items-center min-h-[200px]"
                        dangerouslySetInnerHTML={{ __html: svgContent }}
                    />
                    {/* Preview trigger button */}
                    <Button
                        type="button"
                        aria-label="Open preview"
                        title="Open preview"
                        tabIndex={0}
                        onClick={() => setPreviewVisible(true)}
                        onKeyDown={e => {
                            if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                setPreviewVisible(true);
                            }
                        }}
                        className="absolute top-2 right-2 z-10 rounded-md bg-white/90 hover:bg-white text-gray-700 shadow px-2 py-1 text-xs border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                        Preview
                    </Button>

                    {/* Hidden Antd Image for fullscreen preview */}
                    {/* {previewSrc && ( */}
                    <div className="w-full">
                        <Image
                            style={{ display: 'none' }}
                            src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(
                                svgContent,
                            )}`}
                            width={'100%'}
                            
                            className="w-full"
                            preview={{
                                visible: previewVisible,
                                mask: false,
                                scaleStep: 0.25,
                                imageRender: (value) => {
                                    return <div className='bg-white w-full h-full flex justify-center items-center'>{value}</div>;
                                },
                                onVisibleChange: (value) => setPreviewVisible(value),
                            }}
                        />
                    </div>
                    {/* )} */}
                </div>
            );
        }

        return null;
    }, [isLoading, error, svgContent, previewVisible]);

    return (
        <div className="my-4 p-4 bg-white border border-gray-200 rounded-lg">{renderContent}</div>
    );
};

// Props comparison function for React.memo optimization
const arePropsEqual = (prevProps: MermaidChartProps, nextProps: MermaidChartProps): boolean => {
    return prevProps.code === nextProps.code && prevProps.index === nextProps.index;
};

export default React.memo(MermaidChart, arePropsEqual);
