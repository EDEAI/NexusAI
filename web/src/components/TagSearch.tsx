import {
    createTag as apiCreateTag,
    deleteTag as apiDeleteTag,
    getTagList,
    updateTag,
} from '@/api/workflow';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
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
import { memo, useCallback, useEffect, useMemo, useReducer, useState } from 'react';
import { EditableItem } from './DivEditable';

const { Paragraph } = Typography;

// Types
interface TagSearchProps extends SelectProps {
    children?: React.ReactNode;
    modes?: number;
    showAddButton?: boolean;
    [key: string]: any;
}

interface TagState {
    tagList: SelectProps['options'];
    loading: boolean;
    error: string | null;
}

// Action types
type TagAction =
    | { type: 'SET_TAGS'; payload: SelectProps['options'] }
    | { type: 'SET_LOADING'; payload: boolean }
    | { type: 'SET_ERROR'; payload: string | null };

// Reducer
const tagReducer = (state: TagState, action: TagAction): TagState => {
    switch (action.type) {
        case 'SET_TAGS':
            return { ...state, tagList: action.payload, error: null };
        case 'SET_LOADING':
            return { ...state, loading: action.payload };
        case 'SET_ERROR':
            return { ...state, error: action.payload, loading: false };
        default:
            return state;
    }
};

const TagSearch: React.FC<TagSearchProps> = memo(({ children, showAddButton = true, ...props }) => {
    const intl = useIntl();
    const { modes = 0 } = props;
    const [openAddTag, setOpenAddTag] = useState(false);
    const [keyword, setKeyword] = useState('');

    // Use reducer for complex state management
    const [state, dispatch] = useReducer(tagReducer, {
        tagList: [
            {
                label: intl.formatMessage({ id: 'addTag.all', defaultMessage: 'All' }),
                value: 'All',
            },
        ],
        loading: false,
        error: null,
    });

    const debouncedKeyword = useDebounce(keyword, 300);

    useEffect(() => {
        const filteredTags = state.tagList.filter(tag => {
            const stringValue = String(tag.label).toLowerCase();
            return stringValue.includes(debouncedKeyword.toLowerCase());
        });
        if (debouncedKeyword) {
            dispatch({ type: 'SET_TAGS', payload: filteredTags });
        } else {
            getTags();
        }
    }, [debouncedKeyword]);

    // Memoized API calls
    const getTags = useCallback(async () => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const res = await getTagList(modes);
            if (res.code === 0) {
                const formattedTags = res.data?.map(x => ({
                    ...x,
                    label: x.name,
                    value: x.id,
                }));
                dispatch({ type: 'SET_TAGS', payload: formattedTags });
            } else {
                throw new Error(res.message || 'Failed to fetch tags');
            }
        } catch (error) {
            dispatch({ type: 'SET_ERROR', payload: error.message });
            message.error(
                intl.formatMessage({
                    id: 'error.fetchTags',
                    defaultMessage: 'Failed to fetch tags',
                }),
            );
        } finally {
            dispatch({ type: 'SET_LOADING', payload: false });
        }
    }, [modes, intl]);

    const createTag = useCallback(
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
                dispatch({ type: 'SET_LOADING', payload: true });
                const res = await apiCreateTag(name, modes);
                if (res.code === 0) {
                    setKeyword('');
                    getTags();
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
            } finally {
                dispatch({ type: 'SET_LOADING', payload: false });
            }
        },
        [modes, intl, props?.onTagChange],
    );

    const deleteTag = useCallback(
        async (tag_id: string) => {
            try {
                dispatch({ type: 'SET_LOADING', payload: true });
                const res = await apiDeleteTag(tag_id);
                if (res.code === 0) {
                    getTags();
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
            } finally {
                dispatch({ type: 'SET_LOADING', payload: false });
            }
        },
        [intl],
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
                            onClick={() => keyword.trim() && createTag(keyword)}
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
                            createTag(keyword);
                        }
                    }}
                />
                {state.tagList.map(item => (
                    <div
                        key={item.id}
                        className="p-0.5 cursor-pointer border border-gray-300 text-gray-600 hover:border-[#1B64F3] rounded-md flex flex-wrap items-center transition-all duration-300"
                    >
                        <div className="pl-3 pr-1">
                            <EditableItem
                                maxLength={10}
                                onUpdate={async newName => {
                                    try {
                                        await updateTag(item.id, newName);
                                        getTags();
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
                                <Button type="text" icon={<DeleteOutlined />} />
                            </Popconfirm>
                        )}
                    </div>
                ))}
            </div>
        ),
        [state.tagList, keyword, intl, createTag, deleteTag],
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
                        createTag(keyword);
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
                options={state.tagList}
                loading={state.loading}
                {...props}
            />
        </div>
    );
});

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

// Add useTags hook back with improvements
export const useTags = (initialModes = 0) => {
    const intl = useIntl();
    const [modes, setModes] = useState(initialModes);
    const [state, dispatch] = useReducer(tagReducer, {
        tagList: [
            {
                label: intl.formatMessage({ id: 'addTag.all', defaultMessage: 'All' }),
                value: 'All',
            },
        ],
        loading: false,
        error: null,
    });

    const fetchTags = useCallback(
        async (currentModes: number) => {
            try {
                dispatch({ type: 'SET_LOADING', payload: true });
                const res = await getTagList(currentModes);
                if (res.code === 0) {
                    const formattedTags = res.data?.map(x => ({
                        ...x,
                        label: x.name,
                        value: x.id,
                    }));
                    dispatch({ type: 'SET_TAGS', payload: formattedTags });
                } else {
                    throw new Error(res.message || 'Failed to fetch tags');
                }
            } catch (error) {
                dispatch({ type: 'SET_ERROR', payload: error.message });
                message.error(
                    intl.formatMessage({
                        id: 'error.fetchTags',
                        defaultMessage: 'Failed to fetch tags',
                    }),
                );
            } finally {
                dispatch({ type: 'SET_LOADING', payload: false });
            }
        },
        [intl],
    );

    useEffect(() => {
        fetchTags(modes);
    }, [modes, fetchTags]);

    const refreshTags = useCallback((newModes = 0) => {
        setModes(newModes);
    }, []);

    return {
        tagList: state.tagList,
        loading: state.loading,
        error: state.error,
        refreshTags,
    };
};

export default memo(TagSearch);
