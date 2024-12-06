/*
 * @LastEditors: biz
 */
import { Switch } from 'antd';
import React, { memo } from 'react';

interface Props extends Partial<React.ComponentProps<typeof Switch>> {
    className?: string;
    label?: string;
}

const AniSwitch = memo((props: Props) => {
    const { className, label, ...restProps } = props;
    return (
        <div className={className}>
            {label}
            {label && '：'}
            <Switch {...restProps} />
        </div>
    );
});

export default AniSwitch;
