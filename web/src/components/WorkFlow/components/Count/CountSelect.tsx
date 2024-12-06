/*
 * @LastEditors: biz
 */
import { Select, SelectProps } from 'antd';
import { memo, useMemo } from 'react';

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
const Count = {
    Equals: {
        label: '=',
        value: '=',
        name: '',
    },
    NotEqual: {
        label: '≠',
        value: '!=',
        name: '',
    },
    GreaterThan: {
        label: '>',
        value: '>',
        name: '',
    },
    LessThan: {
        label: '<',
        value: '<',
        name: '',
    },
    GreaterThanOrEqualTo: {
        label: '≥',
        value: '>=',
        name: '',
    },
    LessThanOrEqualTo: {
        label: '≤',
        value: '<=',
        name: '',
    },
    IsNull: {
        label: '',
        value: 'is None',
        name: '',
    },
    IsNotNull: {
        label: '',
        value: 'is not None',
        name: '',
    },
};

const transformEnumToOptions = (enumObj: CountType): Option[] => {
    return Object.entries(enumObj).map(([key, value]) => ({
        label: `${value.label}`,
        value: value.value as string,
    }));
};
type CustomSelectProps = {
    type?: 'number' | 'string';
    onChange?: (value) => void;
};

const CountSelect: React.FC<SelectProps & CustomSelectProps> = memo(props => {
    const { type, onChange, value, ...restProps } = props;
    const options = useMemo(
        () => transformEnumToOptions(type && type == 'string' ? Conditions : Count),
        [],
    );

    const handleChange = (findValue: string) => {
        const findOptions = type && type == 'string' ? Conditions : Count;
        Object.entries(findOptions).forEach(([key, value]) => {
            if (value.value == findValue) {
                onChange && onChange(value);
            }
        });
    };
    return (
        <Select
            {...props}
            value={value.value}
            options={options}
            onChange={handleChange}
            placeholder=""
        />
    );
});

export default CountSelect;
