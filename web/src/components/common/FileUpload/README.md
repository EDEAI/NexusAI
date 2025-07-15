# FileUpload Component

A reusable file upload component based on Ant Design Upload, supporting drag & drop upload, multiple file upload, file type restrictions, and more.

## Features

- 🚀 Drag & drop upload support
- 📁 Multiple file batch upload
- 🎯 File type restrictions
- 📏 File size limitations
- 🔄 Upload progress display
- 🌐 Internationalization support
- 🎨 Custom styling
- 📋 Upload state management

## Basic Usage

```tsx
import FileUpload from '@/components/common/FileUpload';
import { getUploadUrl } from '@/api/upload';

const MyComponent = () => {
  const [fileList, setFileList] = useState([]);

  const handleUploadChange = (info) => {
    setFileList(info.fileList);
  };

  return (
    <FileUpload
      action={getUploadUrl}
      fileList={fileList}
      onChange={handleUploadChange}
    />
  );
};
```

## API

### FileUploadProps

| Property | Description | Type | Default |
| --- | --- | --- | --- |
| onChange | Callback for file upload status change | `(info: any) => void` | - |
| fileList | Current file list | `any[]` | `[]` |
| action | Upload URL | `string \| ((file: any) => string) \| ((file?: any) => Promise<string>)` | - |
| headers | Request headers | `Record<string, string>` | `{ Authorization: 'Bearer token' }` |
| disabled | Whether to disable the upload | `boolean` | `false` |
| multiple | Whether to support multiple file selection | `boolean` | `true` |
| accept | Accepted file types | `string` | `".txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv"` |
| maxSize | Maximum file size (MB) | `number` | `15` |
| showUploadList | Whether to show upload list | `boolean` | `false` |
| className | Custom CSS class name | `string` | `''` |
| height | Component height | `string \| number` | `'200px'` |
| timeout | Timeout duration (milliseconds) | `number` | `300000` |
| fileTypeIcons | File type icon configuration | `Array<{src: string, alt?: string}>` | Default icon config |
| children | Custom upload area content | `React.ReactNode` | - |
| dragText | Custom drag text | `string` | - |
| limitText | Custom upload limit text | `string` | - |

### FileUploadRef

| Method | Description | Type |
| --- | --- | --- |
| reset | Reset the upload component | `() => void` |

## Usage Examples

### Basic Upload

```tsx
import FileUpload from '@/components/common/FileUpload';

const BasicUpload = () => {
  const [fileList, setFileList] = useState([]);

  return (
    <FileUpload
      action="/api/upload"
      fileList={fileList}
      onChange={(info) => setFileList(info.fileList)}
    />
  );
};
```

### Custom File Type and Size Limits

```tsx
<FileUpload
  action="/api/upload"
  accept=".jpg,.png,.pdf"
  maxSize={10}
  fileList={fileList}
  onChange={handleChange}
/>
```

### Using Ref to Reset Component

```tsx
import { useRef } from 'react';

const UploadWithReset = () => {
  const uploadRef = useRef();
  
  const handleReset = () => {
    uploadRef.current?.reset();
  };

  return (
    <>
      <FileUpload
        ref={uploadRef}
        action="/api/upload"
        fileList={fileList}
        onChange={handleChange}
      />
      <Button onClick={handleReset}>Reset</Button>
    </>
  );
};
```

### Custom Upload Area Content

```tsx
<FileUpload
  action="/api/upload"
  fileList={fileList}
  onChange={handleChange}
>
  <div className="custom-upload-content">
    <Icon type="cloud-upload" style={{ fontSize: 48 }} />
    <p>Click or drag files to this area to upload</p>
  </div>
</FileUpload>
```

### Complete Configuration Example

```tsx
<FileUpload
  action="/api/upload"
  fileList={fileList}
  onChange={handleChange}
  headers={{
    'Authorization': 'Bearer your-token',
    'X-Custom-Header': 'value'
  }}
  accept=".doc,.docx,.pdf,.txt"
  maxSize={20}
  multiple={true}
  height="300px"
  timeout={600000}
  disabled={false}
  showUploadList={false}
  dragText="Drag documents here to upload"
  limitText="Supports DOC, PDF, TXT formats, single file no more than 20MB"
  fileTypeIcons={[
    { src: "/icons/doc.svg", alt: "Word" },
    { src: "/icons/pdf.svg", alt: "PDF" },
    { src: "/icons/txt.svg", alt: "Text" }
  ]}
/>
```

## Internationalization Configuration

The component uses the following internationalization keys:

```typescript
{
  'common.upload.success': 'Upload successful',
  'common.upload.error': 'Upload failed',
  'common.upload.error.fileSize': 'File size cannot exceed {maxSize}MB',
  'common.upload.starting': 'Starting upload',
  'common.upload.fileSize': 'File size',
  'common.upload.error.serverResponse': 'Server response error',
  'common.upload.error.httpStatus': 'HTTP status error',
  'common.upload.error.network': 'Network error',
  'common.upload.error.timeout': 'Upload timeout',
  'common.upload.error.cancelled': 'Upload cancelled',
  'common.upload.instruction.dragOrClick': 'Drag files here or click to upload',
  'common.upload.instruction.uploadLimit': 'Supports batch upload, single file no more than {maxSize}MB'
}
```

## Important Notes

1. Ensure the correct `action` upload URL is provided
2. Configure appropriate `headers` as needed, especially authentication information
3. Set reasonable `maxSize` to avoid uploading oversized files
4. Use the `fileList` property for controlled mode to ensure state synchronization
5. Use `ref` to get component instance and call `reset` method to reset component state 