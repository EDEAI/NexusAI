
import { getUploadUrl } from '@/api/createkb';
import { useIntl } from '@umijs/max';
import { message, Upload } from 'antd';
import './upload.css';

const { Dragger } = Upload;
const UploadView = ({ fun, createkbInfo }: any) => {
    const intl = useIntl();
    let uploads = {
        action: getUploadUrl,
        headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        onChange(info) {
            fun(info);
        },
        beforeUpload(file) {
            const isLt15M = file.size / 1024 / 1024 < 15;
            if (!isLt15M) {
                message.error(
                    intl.formatMessage({
                        id: 'createkb.fileLimit',
                        defaultMessage: '15M',
                    }),
                );
                return false;
            }
            return isLt15M;
        },
    };
    const props = {
        ...uploads,
        name: 'file',
        multiple: true,
        className: 'h-[200px]',
        showUploadList: false,
    };
    return (
        <>
            <Dragger
                {...props}
                listType="picture"
                className="flex flex-col items-center justify-center custom-dragger mt-[15px]"
                accept=".txt,.md,.pdf,.html,.xlsx,.xls,.docx,.csv"
                disabled={createkbInfo.type}
            >
                <div className="update p-[4px]">
                    <div className="flex items-center w-full justify-center">
                        <img src="/icons/word.svg" className="w-[42px] h-[42px] mx-3" />
                        <img src="/icons/txt.svg" className="w-[42px] h-[42px] mx-3" />
                        <img src="/icons/pdf.svg" className="w-[42px] h-[42px] mx-3" />
                        <img src="/icons/xlsx.svg" className="w-[42px] h-[42px] mx-3" />
                        <img src="/icons/md.svg" className="w-[42px] h-[42px] mx-3" />
                    </div>
                    <div className="mt-[10px] text-[#213044] text-sm">
                        {intl.formatMessage({
                            id: 'createkb.dragOrClick',
                            defaultMessage: '，',
                        })}
                    </div>
                    <div className="mt-[10px] text-[#999999] text-sm">
                        {intl.formatMessage({
                            id: 'createkb.uploadLimit',
                            defaultMessage: '10， 15MB',
                        })}
                    </div>
                </div>
            </Dragger>
        </>
    );
};

export default UploadView;
