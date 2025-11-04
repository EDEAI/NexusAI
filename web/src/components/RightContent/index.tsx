/*
 * @LastEditors: biz
 */
import { setLang } from '@/api/workflow';
import { QuestionCircleOutlined } from '@ant-design/icons';
import { setLocale, SelectLang as UmiSelectLang, useIntl } from '@umijs/max';
import { message } from 'antd';
import { useUserInfo } from '@/hooks/useUserInfo';
import { mapLocaleToLanguage } from '@/utils/locale';

const LangIconLoaded = () => <img src="/icons/lang.svg" />;

export const SelectLang = () => {
    const { updateUserInfo, userInfo } = useUserInfo();
    const intl = useIntl();

    return (
        <UmiSelectLang
            key={`select-lang-${intl.locale}`}
            icon={<LangIconLoaded />}
            style={{
                padding: 4,
            }}
            onItemClick={async e => {
                const nextLocale = e?.key as string;
                const nextLanguage = mapLocaleToLanguage(nextLocale) || (nextLocale === 'zh-CN' ? 'zh' : 'en');

                try {
                    if (nextLanguage && userInfo?.language !== nextLanguage) {
                        await setLang(nextLanguage);
                        updateUserInfo({ language: nextLanguage });
                    }
                    setLocale(nextLocale, false);
                } catch (error) {
                    console.error('Failed to switch language', error);
                    message.error('Failed to switch language');
                }
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
