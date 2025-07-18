/*
 * @LastEditors: biz
 */
import React, { useState, useEffect } from 'react';
import { MCPToolRuntimeData } from '../types/mcp';
import { FileToUpload, FileUploadData } from '../types/fileUpload';
import FileUploadItem from './FileUploadItem';
import { Button, message } from 'antd';
import { UploadedFile } from '@/hooks/useFileUpload';

interface FileUploadSectionProps {
    toolData: MCPToolRuntimeData;
    onFileUploadComplete: (resultArray: any[]) => void;
    onFileUploadError: (error: string) => void;
}

const FileUploadSection: React.FC<FileUploadSectionProps> = ({
    toolData,
    onFileUploadComplete,
    onFileUploadError,
}) => {
    const filesToUpload = toolData.files_to_upload || [];
    // { [variableName]: FileUploadData }
    const [uploadMap, setUploadMap] = useState<Record<string, FileUploadData>>({});

 
    const allRequiredUploaded = filesToUpload.every(
        (item) =>
            item.required === false ||
            (uploadMap[item.variable_name] && uploadMap[item.variable_name].status === 'done')
    );


    const handleItemChange = (variableName: string, fileData: FileUploadData | null) => {
        setUploadMap((prev) => {
            const next = { ...prev };
            
            if (fileData) {
                next[variableName] = fileData;
            } else {
                delete next[variableName];
            }
            return next;
        });
    };

    const buildMergedFilesToUpload = () => {
        return filesToUpload.map((item) => {
            const upload = uploadMap[item.variable_name];
            return {
                ...item,
                ...upload,
              
            };
        });
    };

    const handleComplete = () => {
        if (!allRequiredUploaded) {
            message.warning('Please upload all required files.');
            return;
        }
        
        const mergedFiles = buildMergedFilesToUpload();
        onFileUploadComplete(mergedFiles);
    };

    useEffect(() => {
   
        // if (allRequiredUploaded) onFileUploadComplete(uploadMap);
    }, [allRequiredUploaded, uploadMap, onFileUploadComplete]);

    return (
        <div className="mt-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
            <div className="mb-3">
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Required Files
                </h4>
            </div>
            {filesToUpload.length === 0 && (
                <div className="text-xs text-gray-500">No files required.</div>
            )}
            {filesToUpload.map((fileConfig) => (
                <FileUploadItem
                    key={fileConfig.variable_name}
                    fileConfig={fileConfig}
                    value={uploadMap[fileConfig.variable_name]}
                    onChange={(fileData) => handleItemChange(fileConfig.variable_name, fileData)}
                />
            ))}
            <Button
                type="primary"
                className="mt-2 w-full"
                disabled={!allRequiredUploaded}
                onClick={handleComplete}
            >
                Complete Upload
            </Button>
        </div>
    );
};

export default FileUploadSection; 