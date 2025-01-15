import { createTag, deleteTag, updateTag } from '@/api/workflow';
import { useTagStore } from '@/store/tags';
import { CheckOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { useDebounce, useMount } from 'ahooks';
import {
    Button,
    Input,
    Modal,
    Popconfirm,
    Select,
    SelectProps,
    Tag,
    Typography,
    message,
} from 'antd';
import Fuse from 'fuse.js';
import type { CustomTagProps } from 'rc-select/lib/BaseSelect';
import { memo, useCallback, useEffect, useMemo, useState } from 'react';
import { EditableItem } from './DivEditable';

const { Paragraph } = Typography;

// Types
interface TagSearchProps extends SelectProps {
    children?: React.ReactNode;
    modes?: number;
    showAddButton?: boolean;
    listStyle?: 'vertical' | 'horizontal';
    [key: string]: any;
}

const TagSearch: React.FC<TagSearchProps> = memo(({ children, showAddButton = true, ...props }) => {
    const intl = useIntl();
    const { modes = 0 } = props;
    const [openAddTag, setOpenAddTag] = useState(false);
    const [keyword, setKeyword] = useState('');

    const { tags, loading, fetchTags } = useTagStore();

    // Memoized API calls
    const getTags = useCallback(async () => {
        try {
            await fetchTags();
        } catch (error) {
            message.error(
                intl.formatMessage({
                    id: 'error.fetchTags',
                    defaultMessage: 'Failed to fetch tags',
                }),
            );
        }
    }, [intl, fetchTags]);

    const debouncedKeyword = useDebounce(keyword, { wait: 300 });

    const filteredOptions = useMemo(() => {
        return tags
            .filter(tag => {
                if (!debouncedKeyword) return true;
                const stringValue = String(tag.name).toLowerCase();
                return stringValue.includes(debouncedKeyword.toLowerCase());
            })
            .map(tag => ({
                label: tag.name,
                value: tag.id,
                data: tag,
            }));
    }, [tags, debouncedKeyword]);

    useEffect(() => {
        if (!debouncedKeyword) {
            getTags();
        }
    }, [debouncedKeyword, getTags]);

    const createTagHandler = useCallback(
        async (name: string) => {
            if (!name.trim()) {
                message.warning(
                    intl.formatMessage({
                        id: 'addTag.emptyName',
                        defaultMessage: 'Tag name cannot be empty',
                    }),
                );
                return;
            }

            try {
                const res = await createTag(name, modes);
                if (res.code === 0) {
                    setKeyword('');
                    await fetchTags();
                    props?.onTagChange?.();
                    message.success(
                        intl.formatMessage({
                            id: 'addTag.success',
                            defaultMessage: 'Tag created successfully',
                        }),
                    );
                } else {
                    throw new Error(res.message || 'Failed to create tag');
                }
            } catch (error) {
                message.error(
                    intl.formatMessage({
                        id: 'error.createTag',
                        defaultMessage: 'Failed to create tag',
                    }),
                );
            }
        },
        [modes, intl, props?.onTagChange, fetchTags],
    );

    const deleteTagHandler = useCallback(
        async (tag_id: string | number) => {
            try {
                const res = await deleteTag(String(tag_id));
                if (res.code === 0) {
                    fetchTags();
                    message.success(
                        intl.formatMessage({
                            id: 'deleteTag.success',
                            defaultMessage: 'Tag deleted successfully',
                        }),
                    );
                } else {
                    throw new Error(res.message || 'Failed to delete tag');
                }
            } catch (error) {
                message.error(
                    intl.formatMessage({
                        id: 'error.deleteTag',
                        defaultMessage: 'Failed to delete tag',
                    }),
                );
            }
        },
        [intl, fetchTags],
    );

    const updateTagHandler = useCallback(
        async (id: string | number, name: string) => {
            try {
                const res = await updateTag(id, name);
                if (res.code === 0) {
                    fetchTags();
                    message.success(
                        intl.formatMessage({
                            id: 'updateTag.success',
                            defaultMessage: 'Tag updated successfully',
                        }),
                    );
                } else {
                    throw new Error(res.message || 'Failed to update tag');
                }
            } catch (error) {
                message.error(
                    intl.formatMessage({
                        id: 'error.updateTag',
                        defaultMessage: 'Failed to update tag',
                    }),
                );
            }
        },
        [intl, fetchTags],
    );

    // Mount effect
    useMount(() => {
        getTags();
    });

    // Modal content component
    const ModalContent = useMemo(
        () => (
            <div className="flex flex-wrap gap-2">
                <Input
                    suffix={
                        <PlusOutlined
                            onClick={() => keyword.trim() && createTagHandler(keyword)}
                            className={`cursor-pointer mx-1 ${
                                !keyword.trim() ? 'text-gray-300' : ''
                            }`}
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
                        e.preventDefault();
                        if (keyword.trim()) {
                            createTagHandler(keyword);
                        }
                    }}
                />
                {filteredOptions.map(item => (
                    <div
                        key={item.value}
                        className="p-0.5 cursor-pointer border border-gray-300 text-gray-600 hover:border-[#1B64F3] rounded-md flex flex-wrap items-center transition-all duration-300"
                    >
                        <div className="pl-3 pr-1">
                            <EditableItem
                                maxLength={10}
                                onUpdate={async newName => {
                                    try {
                                        await updateTagHandler(item.value, newName);
                                        fetchTags();
                                        props?.onTagChange?.();
                                    } catch (error) {
                                        message.error(
                                            intl.formatMessage({
                                                id: 'error.updateTag',
                                                defaultMessage: 'Failed to update tag',
                                            }),
                                        );
                                    }
                                }}
                            >
                                {item.label}
                            </EditableItem>
                        </div>
                        {(item.data as any).reference_count === 0 ? (
                            <Button
                                onClick={() => deleteTagHandler(item.value)}
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
                                })} ${(item.data as any).reference_count} ${intl.formatMessage({
                                    id: 'addTag.deleteConfirmation2',
                                })}`}
                                onConfirm={() => deleteTagHandler(item.value)}
                                okText={intl.formatMessage({
                                    id: 'addTag.confirm',
                                    defaultMessage: 'Confirm',
                                })}
                                cancelText={intl.formatMessage({
                                    id: 'addTag.cancel',
                                    defaultMessage: 'Cancel',
                                })}
                            >
                                <Button type="text" icon={<DeleteOutlined />} />
                            </Popconfirm>
                        )}
                    </div>
                ))}
            </div>
        ),
        [
            filteredOptions,
            keyword,
            intl,
            createTagHandler,
            deleteTagHandler,
            updateTagHandler,
            fetchTags,
            props?.onTagChange,
        ],
    );

    return (
        <div className="flex items-center gap-1">
            <Modal
                title={intl.formatMessage({ id: 'addTag.addTag', defaultMessage: 'Add Tag' })}
                className="z-[999]"
                open={openAddTag}
                onCancel={() => setOpenAddTag(false)}
                onOk={() => {
                    if (keyword.trim()) {
                        createTagHandler(keyword);
                    }
                    setOpenAddTag(false);
                }}
                okButtonProps={{ disabled: !keyword.trim() }}
                bodyProps={{
                    className: 'min-h-[200px] pt-4',
                }}
            >
                {ModalContent}
            </Modal>

            {showAddButton && (
                <Button
                    onClick={() => setOpenAddTag(true)}
                    type="text"
                    className="shrink-0"
                    icon={<PlusOutlined className="cursor-pointer mr-1" />}
                    aria-label={intl.formatMessage({
                        id: 'addTag.button',
                        defaultMessage: 'Add new tag',
                    })}
                />
            )}

            <TagSelect
                className="!w-[160px]"
                options={filteredOptions}
                loading={loading}
                onCreateTag={name => {
                    createTagHandler(name);
                }}
              
                {...props}
            />
        </div>
    );
});

interface TagSelectProps extends SelectProps {
    tagColor?: string;
    onCreateTag?: (name: string) => void;
    listStyle?: 'vertical' | 'horizontal';
}

interface SelectOption {
    label: string;
    value: string | number;
    data?: any;
}

export const TagSelect: React.FC<TagSelectProps> = memo(props => {
    const intl = useIntl();
    const { tagColor, listStyle = 'vertical' } = props;
    const { disabled, onCreateTag, ...restProps } = props;
    const [inputValue, setInputValue] = useState('');
    const [selectedTags, setSelectedTags] = useState<SelectOption[]>([]);

    useEffect(() => {
        if (restProps.options) {
            if (restProps.value) {
                const values = Array.isArray(restProps.value) ? restProps.value : [restProps.value];
                const selected = (restProps.options as SelectOption[]).filter(option =>
                    values.includes(option.value),
                );
                setSelectedTags(selected);
            } else if (restProps.defaultValue && !selectedTags.length) {
                const defaultValues = Array.isArray(restProps.defaultValue)
                    ? restProps.defaultValue
                    : [restProps.defaultValue];

                const selected = (restProps.options as SelectOption[]).filter(option =>
                    defaultValues.includes(option.value),
                );
                setSelectedTags(selected);
            }
        } else if (!restProps.value && !restProps.options) {
            setSelectedTags([]);
        }
    }, [restProps.value, restProps.options, restProps.defaultValue]);

    const handleChange = (values: (string | number)[] | null) => {
        if (!values) {
            setSelectedTags([]);
            props.onChange?.([]);
            return;
        }

        const newSelectedTags =
            (restProps.options as SelectOption[])?.filter(option =>
                values.includes(option.value),
            ) || [];
        setSelectedTags(newSelectedTags);
        props.onChange?.(values);
    };

    const tagRender = (props: CustomTagProps) => {
        const { label } = props;
        const onPreventMouseDown = (event: React.MouseEvent<HTMLSpanElement>) => {
            event.preventDefault();
            event.stopPropagation();
        };
        return (
            <Tag
                color={tagColor || 'blue'}
                onMouseDown={onPreventMouseDown}
                style={{ marginInlineEnd: 4 }}
            >
                {label}
            </Tag>
        );
    };

    const fuse = useMemo(() => {
        const options = {
            keys: ['label'],
            threshold: 0.3,
            includeScore: true,
        };
        return new Fuse((restProps.options || []) as SelectOption[], options);
    }, [restProps.options]);

    const filteredOptions = useMemo(() => {
        if (!inputValue) {
            return restProps.options || [];
        }

        const searchResults = fuse.search(inputValue);
        return searchResults.map(result => result.item);
    }, [inputValue, fuse, restProps.options]);

    const dropdownRender = (menu: React.ReactElement) => (
        <div className="p-1">
            <div
                className={`max-h-[300px] overflow-auto ${
                    listStyle === 'horizontal' ? 'flex flex-wrap gap-1' : ''
                }`}
            >
                {filteredOptions.map(option => (
                    <div
                        key={option.value}
                        className={`
                            flex items-center justify-between cursor-pointer rounded hover:bg-gray-100
                            ${
                                selectedTags.some(tag => tag.value === option.value)
                                    ? 'bg-blue-50'
                                    : ''
                            }
                            ${
                                listStyle === 'horizontal'
                                    ? 'px-2 py-0.5 border border-gray-200'
                                    : 'px-2 py-1.5'
                            }
                        `}
                        onClick={() => {
                            const isSelected = selectedTags.some(tag => tag.value === option.value);
                            const newSelectedTags = isSelected
                                ? selectedTags.filter(tag => tag.value !== option.value)
                                : [...selectedTags, option];
                            setSelectedTags(newSelectedTags);
                            handleChange(newSelectedTags.map(tag => tag.value));
                        }}
                    >
                        <span className="mr-2">{option.label}</span>
                        {selectedTags.some(tag => tag.value === option.value) && (
                            <CheckOutlined className="text-blue-500" />
                        )}
                    </div>
                ))}
            </div>
            {onCreateTag &&
                inputValue &&
                !filteredOptions.some(option => option.label === inputValue) && (
                    <div
                        className="flex items-center gap-2 px-2 py-2 mt-1 cursor-pointer hover:bg-gray-100 border-t"
                        onClick={() => {
                            if (inputValue.trim()) {
                                onCreateTag(inputValue.trim());
                                setInputValue('');
                            }
                        }}
                    >
                        <PlusOutlined className="text-blue-500" />
                        <span>
                            {intl.formatMessage(
                                { id: 'addTag.createTag', defaultMessage: 'Create tag: {tag}' },
                                { tag: inputValue },
                            )}
                        </span>
                    </div>
                )}
        </div>
    );

    return (
        <Select<SelectOption>
            mode="multiple"
            size="middle"
            showSearch
            tokenSeparators={[',']}
            searchValue={inputValue}
            onSearch={setInputValue}
            value={selectedTags.map(tag => tag.value)}
            onClear={() => {
                setSelectedTags([]);
                props.onChange?.([]);
            }}
            onKeyDown={e => {
                if (e.key === 'Enter') {
                    if (inputValue && inputValue.trim()) {
                        const tags = inputValue
                            .split(',')
                            .map(tag => tag.trim())
                            .filter(Boolean);
                        tags.forEach(tag => {
                            onCreateTag?.(tag);
                        });
                        setInputValue('');
                    }
                }
            }}
            placeholder={intl.formatMessage({
                id: 'addTag.pleaseSelect',
                defaultMessage: 'Please select',
            })}
            maxTagCount="responsive"
            onChange={handleChange}
            tagRender={tagRender}
            dropdownRender={dropdownRender}
            options={restProps.options || []}
            disabled={disabled}
            open={disabled ? false : restProps.open}
            {...restProps}
            
        />
    );
});

type TagRender = SelectProps['tagRender'];

export default memo(TagSearch);
