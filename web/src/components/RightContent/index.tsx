/*
 * @LastEditors: biz
 */
import { setLang } from '@/api/workflow';
import { QuestionCircleOutlined } from '@ant-design/icons';
import { setLocale, SelectLang as UmiSelectLang } from '@umijs/max';



const LangIconLoaded = () => <img src="/icons/lang.svg" />;

export const SelectLang = () => {
    return (
        <UmiSelectLang
            icon={<LangIconLoaded />}
            style={{
                padding: 4,
            }}
            onItemClick={e => {
                setLang(e.key === 'zh-CN' ? 'zh' : 'en').then(res => {
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
