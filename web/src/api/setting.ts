/*
 * @LastEditors: biz
 */
import aniRequest from './request';

// Get model list
export const getSuppliersList = async () => {
    return await aniRequest<any>('/v1/supplier/suppliers_list', { method: 'GET' });
};

// Supplier approves a single model setting
export const postSuppliersAuthorize = async (data: any) => {
    const res = await aniRequest<any>('/v1/supplier/supplier_authorize', {
        method: 'POST',
        data: data,
    });
    return res;
};

// Supplier approves multiple model settings
export const postSwitchingModels = async (data: any) => {
    const res = await aniRequest<any>('/v1/supplier/switching_models', {
        method: 'POST',
        data: data,
    });
    return res;
};