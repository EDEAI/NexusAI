import { useIntl } from '@umijs/max';
import { history } from 'umi';
interface menusPops {
    keys?: string;
    path?: string;
}

//
const Menus: React.FC<menusPops> = (props: menusPops) => {
    const intl = useIntl();
    const items = [
        {
            label: intl.formatMessage({ id: 'app.dashboard.menu' }),
            key: 'dash_board',
            icon: (keys: any, key: any) => {
                return (
                    <img
                        src={`/icons/plaza_m1_c${keys == key ? '1' : '2'}.svg`}
                        className="w-[16px] h-[16px]"
                    ></img>
                );
            },
        },
        {
            label: intl.formatMessage({ id: 'app.chatroom_list.menu' }),
            key: 'meeting',
            icon: (keys: any, key: any) => {
                return (
                    <img
                        src={`/icons/plaza_m2_c${keys == key ? '1' : '2'}.svg`}
                        className="w-[16px] h-[16px]"
                    ></img>
                );
            },
        },
    ];
    const { keys, path } = props;

    const tabClick = (e: any) => {
        if (e !== keys) history.push(path);
    };

    return (
        <>
            <div className="flex gap-x-[20px] pt-[20px] pb-[20px]">
                {items.map((item: any, index: any) => (
                    <div
                        key={index}
                        className={`pt-[6px] pb-[6px] pl-[15px] pr-[15px] cursor-pointer rounded-[8px] items-center flex gap-x-[10px] ${
                            item.key == keys ? 'bg-[#fff] text-[#1B64F3]' : ''
                        }`}
                        onClick={() => {
                            tabClick(item.key);
                        }}
                    >
                        <span>{item.icon(keys, item.key)}</span>
                        <span className="text-[14px]">{item.label}</span>
                    </div>
                ))}
            </div>
        </>
    );
};

export default Menus;
