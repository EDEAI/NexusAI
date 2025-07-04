/*
 * @LastEditors: biz
 */
/*
 * @LastEditors: biz
 */
import React, { createContext, useContext, useMemo, ReactNode } from 'react';
import { findOption } from '@/components/WorkFlow/components/Form/Select';
import { useModelSelect } from '@/store/modelList';

interface ModelImageSupportContextType {
    isImageSupportModel: (modelConfigId?: number | string) => boolean;
    getCurrentModelImageSupport: (modelConfigId?: number | string) => boolean;
}

const ModelImageSupportContext = createContext<ModelImageSupportContextType | undefined>(undefined);

interface ModelImageSupportProviderProps {
    children: ReactNode;
}

export const ModelImageSupportProvider: React.FC<ModelImageSupportProviderProps> = ({ children }) => {
    const { options } = useModelSelect();

    const contextValue = useMemo(() => {
        const isImageSupportModel = (modelConfigId?: number | string): boolean => {
            if (!modelConfigId || !options) return false;
            
            const modelOption = findOption(modelConfigId, { options });
            return modelOption?.support_image === 1;
        };

        const getCurrentModelImageSupport = (modelConfigId?: number | string): boolean => {
            return isImageSupportModel(modelConfigId);
        };

        return {
            isImageSupportModel,
            getCurrentModelImageSupport,
        };
    }, [options]);

    return (
        <ModelImageSupportContext.Provider value={contextValue}>
            {children}
        </ModelImageSupportContext.Provider>
    );
};

export const useModelImageSupport = (): ModelImageSupportContextType => {
    const context = useContext(ModelImageSupportContext);
    if (context === undefined) {
        throw new Error('useModelImageSupport must be used within a ModelImageSupportProvider');
    }
    return context;
};

export default ModelImageSupportContext; 