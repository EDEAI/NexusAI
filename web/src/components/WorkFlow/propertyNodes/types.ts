/*
 * @LastEditors: biz
 */
import { BlockEnum, PropertyNodeEnum } from '../types';

export interface PropertyNodeData {
    title: string;
    entitle: string;
    desc: string;
    descTools: string;
    endescTools: string;
    propertyType: PropertyNodeEnum;
    targetNodeTypes: BlockEnum[];
    outputInfo?: {
        key: string;
        type: string;
        base: boolean;
    };
}

export interface PropertyNodeConfig {
    node: any;
    panel: any;
    icon: PropertyNodeEnum;
    title: string;
    entitle: string;
    base: {
        type: PropertyNodeEnum;
        data: PropertyNodeData;
    };
}

export type PropertyNodeCustomType = {
    [key in PropertyNodeEnum]: PropertyNodeConfig;
}; 