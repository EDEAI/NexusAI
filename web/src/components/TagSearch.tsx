/*
 * @LastEditors: biz
 */
import { createTag as ApiCreateTag, getTagList } from '@/api/workflow';
import { PlusOutlined } from '@ant-design/icons';
import { useMount } from 'ahooks';
import { Input, Modal, Select, SelectProps } from 'antd';
import { memo, useState } from 'react';

interface TagSearchProps extends SelectProps {
    children?: React.ReactNode;

    modes?: number;
    [key: string]: any;
}

const TagSearch: React.FC<TagSearchProps> = ({ children, ...props }) => {
    const { modes = 0 } = props;
    const [openAddTag, setOpenAddTag] = useState(false);
    const [tagList, setTagList] = useState<SelectProps['options']>([
        {
            label: 'All',
            value: 'All',
        },
    ]);

    useMount(async () => {
        const res = await getTagList(modes);
        // setTagList(res);
    });

    const createTag = async (name: string) => {
        const res = await ApiCreateTag(name, modes);
        console.log(res);
        if (res.code == 0) {
            setTagList([
                {
                    label: name,
                    value: name,
                },
                ...tagList,
            ]);
        }
    };

    const AddTag = () => {
        return (
            <Modal
                title="Add Tag"
                className="z-[999]"
                open={openAddTag}
                bodyProps={{
                    className: 'min-h-[200px] pt-4',
                }}
            >
                <div className="flex flex-wrap gap-2">
                    <Input
                        suffix={<PlusOutlined className="cursor-pointer mx-1" />}
                        onPressEnter={e => {
                            console.log('enter', e);
                            createTag(e.target.value);
                            // e.target.form.submit();
                        }}
                    ></Input>
                    {tagList.map(item => {
                        return <div>13113</div>;
                    })}
                </div>
            </Modal>
        );
    };

    return (
        <div className="flex items-center gap-1">
            <AddTag />
            <PlusOutlined onClick={() => setOpenAddTag(true)} className="cursor-pointer mr-1" />
            <Select
                mode="multiple"
                size="middle"
                placeholder="Please select"
                onChange={() => {}}
                style={{ width: '100%' }}
                options={tagList}
                {...props}
            />
        </div>
    );
};

export default memo(TagSearch);
