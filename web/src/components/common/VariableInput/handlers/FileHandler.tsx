/*
 * @LastEditors: biz
 */
import React from 'react';
import { Typography } from 'antd';
import { UploadDragger } from '../../../WorkFlow/components/Form/Upload';
import type { TypeHandlerProps } from '../types';

const FileHandler: React.FC<TypeHandlerProps> = ({
  variable,
  disabled = false,
  readonly = false,
  fileConfig,
}) => {
  const defaultFileConfig = {
    accept: '.txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv,.jpg,.png,.jpeg',
    maxSize: 15,
    multiple: false,
    ...fileConfig,
  };

  return (
    <div>
      {variable.display_name && (
        <Typography.Title level={5}>
          {variable.display_name}
          {variable.required && <span className="text-red-500 ml-1">*</span>}
        </Typography.Title>
      )}
      <UploadDragger
        name={variable.name}
        required={variable.required}
        accept={defaultFileConfig.accept}
        multiple={defaultFileConfig.multiple}
        maxSize={defaultFileConfig.maxSize}
      />
    </div>
  );
};

export default FileHandler; 