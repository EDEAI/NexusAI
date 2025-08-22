import { BlockEnum } from '@/components/WorkFlow/types';

export interface AppItemResponse {
    name: string;
    description: string;
    [key: string]: any;
}

export interface AppListResponse {
    code: number;
    data: {
        list: AppItemResponse[];
        [key: string]: any;
    };
    [key: string]: any;
}

export interface SearchNodeList {
    [BlockEnum.Agent]?: any;
    [BlockEnum.Skill]?: any;
    workflow?: any;
}

export interface CacheData {
    [key: string]: {
        data: any[];
        timestamp: number;
        params: FilterData;
    };
}

export interface FilterData {
    team: number;
    keyword: string;
    tag: any[];
}

export interface NodeItem {
    id: string;
    type: string;
    data: {
        title: string;
        desc: string;
        [key: string]: any;
    };
    baseData?: any;
    [key: string]: any;
}

export interface TabConfig {
    tabKey: 'node' | 'agent' | 'tool' | 'skill' | 'workflow';
    label: string;
    defaultMessage: string;
    type: 'normal' | 'tools' | 'workflow';
    key: string;
    getData: () => Promise<any[]> | any[];
}

export interface UseNodeListOptions {
    cacheExpiry?: number;
}

export interface UseNodeSearchOptions {
    nodeSearchThreshold?: number;
    toolSearchThreshold?: number;
}

export interface UseNodeTabsOptions {
    visibleTabs?: ('node' | 'agent' | 'tool' | 'skill' | 'workflow')[];
    defaultActiveTab?: string;
}



