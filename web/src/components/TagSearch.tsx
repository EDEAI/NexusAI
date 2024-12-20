/*
 * @LastEditors: biz
 */
import { createTag as ApiCreateTag, getTagList } from '@/api/workflow';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useMount } from 'ahooks';
import { Button, Input, Modal, Select, SelectProps } from 'antd';
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
        // setTagList(res);
        getTags();
    });

    const getTags = async () => {
        const res = await getTagList(modes);
        if (res.code == 0) {
            setTagList(res.data);
        }
    };

    const createTag = async (name: string) => {
        const res = await ApiCreateTag(name, modes);
        console.log(res);
        if (res.code == 0) {
            // setTagList([
            //     {
            //         label: name,
            //         value: name,
            //     },
            //     ...tagList,
            // ]);
            getTags();
        }
    };

    return (
        <div className="flex items-center gap-1">
            <Modal
                title="Add Tag"
                className="z-[999]"
                open={openAddTag}
                onCancel={() => setOpenAddTag(false)}
                onOk={() => setOpenAddTag(false)}
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
                        return (
                            <div className=" p-0.5 cursor-pointer border border-gray-300 text-gray-600 hover:border-[#1B64F3] rounded-md flex flex-wrap items-center">
                                <div className="px-3">{item.name}</div>
                                <Button type="text" icon={<DeleteOutlined />}></Button>
                            </div>
                        );
                    })}
                </div>
            </Modal>
            <Button
                onClick={() => setOpenAddTag(true)}
                type='text'
                className='shrink-0'
                icon={<PlusOutlined className="cursor-pointer mr-1" />}
            ></Button>
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
