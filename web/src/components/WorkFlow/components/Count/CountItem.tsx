/*
 * @LastEditors: biz
 */
import { CloseOutlined } from '@ant-design/icons';
import { useMount } from 'ahooks';
import { Button, Input } from 'antd';
import { memo, useEffect, useMemo, useState } from 'react';
import CountSelect from './CountSelect';
import VariableSelect from './VariableSelect';

type SelectOptionItem = {
    label: string;
    value: string;
    type: string;
};
export type SelectOption = {
    label: string;
    value: string;
    options?: SelectOptionItem[];
};

export interface CountProps {
    options: SelectOption[];
    onDel?: () => void;
    onChange?: (value: any) => void;
    value: any;
    index?: number;
}
interface Option {
    label: string;
    value: string;
}
type CountType = {
    [key: string]: { label: string; value: string; name: string };
};
const Conditions = {
    Equals: {
        label: '',
        value: '=',
        name: '',
    },
    NotEqual: {
        label: '',
        value: '!=',
        name: '',
    },
    Contains: {
        label: '',
        value: 'in',
        name: '',
    },
    DoesNotContain: {
        label: '',
        value: 'not in',
        name: '',
    },
    StartsWith: {
        label: '',
        value: 'startswith',
        name: '',
    },
    EndsWith: {
        label: '',
        value: 'endswith',
        name: '',
    },
    IsEmpty: {
        label: '',
        value: 'is None',
        name: '',
    },
    IsNotEmpty: {
        label: '',
        value: 'is not None',
        name: '',
    },
};
export default memo((props: CountProps) => {
    const { options, onDel, onChange, value, index } = props;

    const [changeValue, setChangeValue] = useState({});

    useMount(() => {
        if (value) {
            setChangeValue(value);
        }
    });

    const variableChange = value => {
        setChangeValue(prev => ({
            ...prev,
            variable: value,
        }));
    };

    const countChange = value => {
        setChangeValue(prev => ({
            ...prev,
            count: JSON.parse(JSON.stringify(value)),
        }));
    };

    const targetChange = e => {
        setChangeValue(prev => ({
            ...prev,
            target: e.target.value,
        }));
    };

    useEffect(() => {

        if (changeValue.isDelete) return;
        onChange?.(changeValue);
    }, [changeValue]);

    const handleDel = () => {
        value.variable = {};
        value.count = {};
        value.target = '';

        setChangeValue({ isDelete: true });
        onDel?.();
    };

    const transformEnumToOptions = (enumObj: CountType): Option[] => {
        return Object.entries(enumObj).map(([key, value]) => ({
            label: `${value.label}`,
            value: value.value as string,
        }));
    };

    const CountSelectOptions = useMemo(() => transformEnumToOptions(Conditions), []);
    return (
        <div className="flex gap-2">
            <VariableSelect
                options={options}
                value={value?.variable || {}}
                onChange={variableChange}
                placeholder=""
                className="w-32"
            />
            <CountSelect value={value?.count || {}} style={{ width: 100 }} onChange={countChange} />

            <Input
                style={{ maxWidth: 100 }}
                value={value?.target || ''}
                onChange={targetChange}
                placeholder=""
            ></Input>
            {index != undefined && index != 0 && (
                <Button className="shrink-0" onClick={handleDel} icon={<CloseOutlined />}></Button>
            )}
        </div>
    );
});
