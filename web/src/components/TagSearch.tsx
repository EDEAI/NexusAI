import {
    createTag as apiCreateTag,
    deleteTag as apiDeleteTag,
    getTagList,
    updateTag,
} from '@/api/workflow';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { useMount } from 'ahooks';
import { Button, Input, Modal, Popconfirm, Select, SelectProps, Tag, Typography } from 'antd';

import { memo, useCallback, useEffect, useState } from 'react';
const { Paragraph } = Typography;

interface TagSearchProps extends SelectProps {
    children?: React.ReactNode;
    modes?: number;
    [key: string]: any;
}

const TagSearch: React.FC<TagSearchProps> = ({ children, ...props }) => {
    const intl = useIntl();
    const { modes = 0 } = props;
    const [openAddTag, setOpenAddTag] = useState(false);
    const [keyword, setKeyword] = useState('');
    const [tagList, setTagList] = useState<SelectProps['options']>([
        {
            label: intl.formatMessage({ id: 'addTag.all', defaultMessage: 'All' }),
            value: 'All',
        },
    ]);

    useMount(async () => {
        getTags();
    });

    const getTags = async () => {
        const res = await getTagList(modes);
        if (res.code == 0) {
            setTagList(
                res.data?.map(x => {
                    return {
                        ...x,
                        label: x.name,
                        value: x.id,
                    };
                }),
            );
        }
    };

    const createTag = async (name: string) => {
        const res = await apiCreateTag(name, modes);
        if (res.code == 0) {
            setKeyword('');
            getTags();
            props?.onTagChange?.();
        }
    };

    const deleteTag = async (tag_id: string) => {
        const res = await apiDeleteTag(tag_id);
        if (res.code == 0) {
            getTags();
        }
    };

    return (
        <div className="flex items-center gap-1">
            <Modal
                title={intl.formatMessage({ id: 'addTag.addTag', defaultMessage: 'Add Tag' })}
                className="z-[999]"
                open={openAddTag}
                onCancel={() => setOpenAddTag(false)}
                onOk={() => {
                    if (keyword != '') {
                        createTag(keyword);
                    }
                    setOpenAddTag(false);
                }}
                bodyProps={{
                    className: 'min-h-[200px] pt-4',
                }}
            >
                <div className="flex flex-wrap gap-2">
                    <Input
                        suffix={
                            <PlusOutlined
                                onClick={() => createTag(keyword)}
                                className="cursor-pointer mx-1"
                            />
                        }
                        placeholder={intl.formatMessage({
                            id: 'addTag.inputTagName',
                            defaultMessage: 'Enter tag name',
                        })}
                        maxLength={10}
                        value={keyword}
                        onChange={e => setKeyword(e.target.value)}
                        onPressEnter={e => {
                            createTag(e.target.value);
                        }}
                    />
                    {tagList.map(item => (
                        <div
                            key={item.id}
                            className="p-0.5 cursor-pointer border border-gray-300 text-gray-600 hover:border-[#1B64F3] rounded-md flex flex-wrap items-center"
                        >
                            <div className="pl-3 pr-1">
                                <EditableItem
                                    onUpdate={e => {
                                        console.log(e);

                                        updateTag(item.id, e).then(res => {
                                            getTags();
                                            props?.onTagChange?.();
                                        });
                                    }}
                                >
                                    {item.name}
                                </EditableItem>
                            </div>
                            {item.reference_count === 0 ? (
                                <Button
                                    onClick={() => deleteTag(item.id)}
                                    type="text"
                                    icon={<DeleteOutlined />}
                                />
                            ) : (
                                <Popconfirm
                                    title={intl.formatMessage({
                                        id: 'addTag.deleteTag',
                                        defaultMessage: 'Delete',
                                    })}
                                    description={`${intl.formatMessage({
                                        id: 'addTag.deleteConfirmation1',
                                    })} ${item.reference_count} ${intl.formatMessage({
                                        id: 'addTag.deleteConfirmation2',
                                    })}`}
                                    onConfirm={() => deleteTag(item.id)}
                                    okText={intl.formatMessage({
                                        id: 'addTag.confirm',
                                        defaultMessage: 'Confirm',
                                    })}
                                    cancelText={intl.formatMessage({
                                        id: 'addTag.cancel',
                                        defaultMessage: 'Cancel',
                                    })}
                                >
                                    <Button type="text" icon={<DeleteOutlined />}></Button>
                                </Popconfirm>
                            )}
                        </div>
                    ))}
                </div>
            </Modal>
            <Button
                onClick={() => setOpenAddTag(true)}
                type="text"
                className="shrink-0"
                icon={<PlusOutlined className="cursor-pointer mr-1" />}
            />

            <TagSelect
                className="!w-[160px]"
                options={tagList}
                // onChange={e => {
                //     props?.onChange?.(e);
                // }}
                {...props}
            ></TagSelect>
        </div>
    );
};

interface Tag {
    label: string;
    value: string;
}

interface UseTagsResult {
    tagList: Tag[];
    refreshTags: () => void;
}

export const useTags = (initialModes = 0) => {
    const [tagList, setTagList] = useState([]);
    const [modes, setModes] = useState(initialModes);

    const fetchTags = useCallback(async currentModes => {
        const res = await getTagList(currentModes);
        if (res.code === 0) {
            setTagList(
                res.data?.map(x => ({
                    ...x,
                    label: x.name,
                    value: x.id,
                })),
            );
        }
    }, []);

    useEffect(() => {
        fetchTags(modes);
    }, [modes, fetchTags]);

    const refreshTags = (newModes = 0) => {
        setModes(newModes);
        fetchTags(newModes);
    };

    return { tagList, refreshTags };
};

interface TagSelectProps extends SelectProps {}
export const TagSelect: React.FC<TagSelectProps> = memo(props => {
    const intl = useIntl();

    return (
        <Select
            mode="multiple"
            size="middle"
            placeholder={intl.formatMessage({
                id: 'addTag.pleaseSelect',
                defaultMessage: 'Please select',
            })}
            maxTagCount="responsive"
            onChange={e => {
                props?.onChange?.(e);
            }}
        
            tagRender={tagRender}
            options={props?.options || []}
            {...props}
        />
    );
});


type TagRender = SelectProps['tagRender'];
const tagRender: TagRender = props => {
    const { label, value, closable, onClose } = props;
    const onPreventMouseDown = (event: React.MouseEvent<HTMLSpanElement>) => {
        event.preventDefault();
        event.stopPropagation();
    };
    return (
        <Tag
            color={`blue`}
            onMouseDown={onPreventMouseDown}
            // closable={closable}
            // onClose={onClose}
            style={{ marginInlineEnd: 4 }}
        >
            {label}
        </Tag>
    );
};
export const EditableItem = ({ children, onUpdate, maxLength = 10 }) => {
    const handleInput = e => {
        const content = e.currentTarget.textContent;
        if (content.length > maxLength) {
            e.currentTarget.textContent = content.substring(0, maxLength);
        }
    };

    const handleBlur = e => {
        const newValue = e.currentTarget.textContent;
        onUpdate(newValue);
    };

    return (
        <div
            contentEditable
            onInput={handleInput}
            onBlur={handleBlur}
            suppressContentEditableWarning={true}
        >
            {children}
        </div>
    );
};

export default memo(TagSearch);
