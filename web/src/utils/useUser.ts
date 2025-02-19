import { getModelList } from '@/api/workflow';
let llm_model_list = [];

export const userinfodata = (type: string, values?: any): any => {
    if (type === 'SET') {
        localStorage.setItem('userInfo', JSON.stringify(values));
    } else if (type === 'GET') {
        return JSON.parse(localStorage.getItem('userInfo'));
    } else if (type === 'REMOVE') {
        localStorage.removeItem('userInfo');
    }
};

export const headportrait = (type: string, headId?: number): any => {


    const profilephoto = [
        {
            id: 1,
            image: '/icons/headportrait/Android.svg',
        },
        {
            id: 2,
            image: '/icons/headportrait/Viewprocess.svg',
        },
        {
            id: 3,
            image: '/icons/headportrait/map.svg',
        },
        {
            id: 4,
            image: '/icons/headportrait/consultingfee.svg',
        },
        {
            id: 5,
            image: '/icons/headportrait/science.svg',
        },
        {
            id: 6,
            image: '/icons/headportrait/leaf.svg',
        },
        {
            id: 7,
            image: '/icons/headportrait/travel.svg',
        },
        {
            id: 8,
            image: '/icons/headportrait/aircraft.svg',
        },
        {
            id: 9,
            image: '/icons/headportrait/mainprocess.svg',
        },
        {
            id: 10,
            image: '/icons/headportrait/subprocess.svg',
        },
        {
            id: 11,
            image: '/icons/headportrait/python.svg',
        },
        {
            id: 12,
            image: '/icons/headportrait/SQL.svg',
        },
    ];
    if (type === 'single') {
        const A = profilephoto.filter((item: any, index: Number) => {
            return item.id == headId;
        });
        return A[0] ? A[0].image : '/icons/headportrait/Android.svg';

    } else if (type === 'all') {
        return profilephoto;
    }
};


export const creationsearchdata = (
    type: string,
    optionsModalId?: Number,
    searchType?: Boolean,
    fuzzySearchName?: string,
): any => {
    if (type === 'SET') {
        const data = {
            optionsModalId: optionsModalId
                ? optionsModalId
                : sessionStorage.getItem('creationsearchdata')
                ? JSON.parse(sessionStorage.getItem('creationsearchdata'))?.optionsModalId
                : 6,
            searchType: searchType ? searchType : false,
            // fuzzySearchName: fuzzySearchName  ? fuzzySearchName : JSON.parse(sessionStorage.getItem('creationsearchdata')).fuzzySearchName,
        };
        sessionStorage.setItem('creationsearchdata', JSON.stringify(data));
    } else if (type === 'GET') {
        const data = {
            optionsModalId: 6,
            searchType: false,
        };
        let returnData = null;
        try {
            returnData = JSON.parse(sessionStorage.getItem('creationsearchdata')) || data;
        } catch (e) {}
        return returnData;
    }
};


export const createappdata = (type: string, data?: any): any => {
    if (type === 'SET') {
        sessionStorage.setItem('createappdata', JSON.stringify(data));
    } else if (type === 'GET') {
        return JSON.parse(sessionStorage.getItem('createappdata') || '{}');
    }
};


export const agentdefault = (): any => {
    return new Promise(async (reslvoe: any) => {
        let data = {
            code: 0,
            detail: '',
            data: {
                app: {
                    app_id: 0,
                    user_id: 33,
                    name: createappdata('GET').name,
                    description: createappdata('GET').description,
                    icon: createappdata('GET').mode,
                    icon_background: '',
                    is_public: 1,
                    enable_api: 0,
                    publish_status: 0,
                    created_time: '',
                    status: 1,
                    api_url: '',
                },
                agent: {
                    agent_id: 0,
                    user_id: 33,
                    obligations: null,
                    input_variables: null,
                    auto_match_ability: 0,
                    default_output_format: 1,
                    m_config_id: 0,
                    allow_upload_file: 0,
                    publish_status: 0,
                    published_time: null,
                    created_time: '',
                    status: 1,
                },
                agent_dataset_relation_list: [],
                agent_abilities_list: [],
                m_configurations_list: [],
                is_creator: 1,
                creator_nickname: '',
                attrs_are_visible:1
            },
        };
        const res = await getModelList();
        data.data.m_configurations_list = res.data.data;
        reslvoe(data);
    });
};


export const skilldefault = (): any => {
    const data = {
        code: 0,
        detail: 'success',
        data: {
            id: 0,
            team_id: 1,
            user_id: 0,
            app_id: 0,
            name: createappdata('GET').name,
            description: createappdata('GET').description,
            config: null,
            input_variables: null,
            dependencies: null,
            code: null,
            output_type: 1,
            output_variables: null,
            publish_status: 0,
            published_time: null,
            created_time: '',
            updated_time: '',
            status: 1,
            is_public: 1,
            is_creator: 1,
            nickname: '',
            attrs_are_visible:1,
        },
    };
    return data;
};

export const getlist = async () => {
    // const res = await getModelList();
    // console.log(res.data.data, 'res')
    // llm_model_list = res.data.data
};
