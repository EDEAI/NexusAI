/*
 * @LastEditors: biz
 */
import { BASE_URL } from '@/api/request';
import FileUpload, { FileUploadRef } from '@/components/common/FileUpload';
import { forwardRef } from 'react';

const UploadView = forwardRef<FileUploadRef, any>(({ fun, createkbInfo, fileList = [] }, ref) => {
    console.log('Upload component received fileList:', fileList.length, 'files');
    console.log('Upload fileList names:', fileList.map(f => f.name));
    
    return (
        <FileUpload
            ref={ref}
            action={`${BASE_URL}/v1/upload/upload_file`}
            fileList={fileList}
            onChange={fun}
            disabled={createkbInfo.type}
            accept=".txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv"
            maxSize={15}
            height="200px"
            timeout={300000}
            multiple={true}
            showUploadList={false}
            className="mt-[15px]"
            fileTypeIcons={[
                { src: "/icons/word.svg", alt: "Word" },
                { src: "/icons/txt.svg", alt: "TXT" },
                { src: "/icons/pdf.svg", alt: "PDF" },
                { src: "/icons/xlsx.svg", alt: "Excel" },
                { src: "/icons/md.svg", alt: "Markdown" }
            ]}
        />
    );
});

export default UploadView;
