/*
 * @LastEditors: biz
 */

export interface FileToUpload {
    name: string;
    variable_name: string;
    id: number;
    file_name?: string | null;
    file_path?: string | null;
    required?: boolean;
    accept?: string;
    maxSize?: number;
    description?: string;
    accepted_types?: string[];
}

export interface UploadedFileInfo {
    uploadId: string;
    fileName: string;
    fileId: string | number;
    variableName: string;
    status: 'uploading' | 'completed' | 'error';
    progress?: number;
    errorMessage?: string;
}

export interface FileUploadData {
    name: string;
    url?: string;
    size: number;
    type: string;
    uid: string;
    status: 'done' | 'uploading' | 'error';
    error?: string;
}

export type FileUploadResultMap = Record<string, FileUploadData>; 