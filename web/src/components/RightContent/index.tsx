/*
 * @LastEditors: biz
 */
import { setLang } from '@/api/workflow';
import { QuestionCircleOutlined } from '@ant-design/icons';
import { setLocale, SelectLang as UmiSelectLang } from '@umijs/max';

export type SiderTheme = 'light' | 'dark';

export const SelectLang = () => {
    return (
        <UmiSelectLang
            style={{
                padding: 4,
            }}
            onItemClick={e => {
                setLang(e.key == 'zh-CN' ? 'zh' : 'en').then(res => {
                    setLocale(e.key);
                });
                return true;
            }}
        />
    );
};

export const Question = () => {
    return (
        <div
            style={{
                display: 'flex',
                height: 26,
            }}
            onClick={() => {}}
        >
            <QuestionCircleOutlined />
        </div>
    );
};
