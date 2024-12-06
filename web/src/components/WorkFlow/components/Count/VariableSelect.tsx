/*
 * @LastEditors: biz
 */
import { Select } from 'antd';
import { memo, useEffect, useState } from 'react';

type SelectOption = {
    label: string;
    value: string;
    options?: SelectOption[];
};

type GroupedSelectOption = {
    label: JSX.Element;
    title: string;
    options: {
        label: JSX.Element;
        value: string;
    }[];
};

const transformOptions = (options: SelectOption[]): GroupedSelectOption[] => {
    return options.map(group => {
        return {
            label: <span>{group.label}</span>,
            title: group.value,
            options:
                group.options?.map(item => ({
                    label: <span>{item.label}</span>,
                    value: item.value,
                })) || [],
        };
    });
};

interface CustomSelectProps {
    options: SelectOption[];
    placeholder: string;
    className: string;
    value: { value: string };
    onChange?: (value: SelectOption) => void;
}

const VariableSelect: React.FC<CustomSelectProps> = memo(
    ({ options, placeholder, value, className, onChange }) => {
        const [data, setData] = useState<GroupedSelectOption[]>([]);

        useEffect(() => {
            const transformedOptions = transformOptions(options);
            setData(transformedOptions);
        }, [options]);

        const handleSearch = (inputValue: string) => {
            const transformedOptions = transformOptions(options);
            const filteredOptions = transformedOptions
                .map(group => {
                    const filteredItems = group.options.filter(item =>
                        item.value.toLowerCase().includes(inputValue.toLowerCase()),
                    );
                    return {
                        ...group,
                        options: filteredItems,
                    };
                })
                .filter(group => group.options.length > 0); 

            setData(filteredOptions);
        };

        const handleChange = (value: string) => {
            for (const group of options) {
                for (const option of group.options) {
                    if (option.value === value) {
                        onChange?.(option);
                        return;
                    }
                }
            }
        };

        return (
            <Select
                options={data}
                value={value.value}
                showSearch
                // allowClear
                placeholder={placeholder}
                suffixIcon={null}
                className={className}
                onSearch={handleSearch}
                onChange={handleChange}
                notFoundContent={null}
                filterOption={false}
            />
        );
    },
);

export default VariableSelect;
