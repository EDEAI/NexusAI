import { getModelList } from '@/api/workflow';
import { ObjectVariable, Variable as SkillVariable } from '@/py2js/variables.js';
let llm_model_list = [];

export const headportrait = (type: string, headId?: number): any => {


    const profilephoto = [
        {
            id: 1,
            image: '/icons/headportrait/human1.png',
        },
        {
            id: 2,
            image: '/icons/headportrait/human2.png',
        },
        {
            id: 3,
            image: '/icons/headportrait/human3.png',
        },
        {
            id: 4,
            image: '/icons/headportrait/human4.png',
        },
        {
            id: 5,
            image: '/icons/headportrait/human5.png',
        },
        {
            id: 6,
            image: '/icons/headportrait/human6.png',
        },
        {
            id: 7,
            image: '/icons/headportrait/human7.png',
        },
        {
            id: 8,
            image: '/icons/headportrait/human8.png',
        },
        {
            id: 9,
            image: '/icons/headportrait/human9.png',
        },
        {
            id: 10,
            image: '/icons/headportrait/human10.png',
        },
        {
            id: 11,
            image: '/icons/headportrait/human11.png',
        },
        {
            id: 12,
            image: '/icons/headportrait/human12.png',
        },
        {
            id: 13,
            image: '/icons/headportrait/human13.png',
        },
        {
            id: 14,
            image: '/icons/headportrait/human14.png',
        },
        {
            id: 15,
            image: '/icons/headportrait/human15.png',
        },
        {
            id: 16,
            image: '/icons/headportrait/Android.svg',
        },
        {
            id: 17,
            image: '/icons/headportrait/Viewprocess.svg',
        },
        {
            id: 18,
            image: '/icons/headportrait/map.svg',
        },
        {
            id: 19,
            image: '/icons/headportrait/consultingfee.svg',
        },
        {
            id: 20,
            image: '/icons/headportrait/science.svg',
        },
        {
            id: 21,
            image: '/icons/headportrait/leaf.svg',
        },
        {
            id: 22,
            image: '/icons/headportrait/travel.svg',
        },
        {
            id: 23,
            image: '/icons/headportrait/aircraft.svg',
        },
        {
            id: 24,
            image: '/icons/headportrait/mainprocess.svg',
        },
        {
            id: 25,
            image: '/icons/headportrait/subprocess.svg',
        },
        {
            id: 26,
            image: '/icons/headportrait/python.svg',
        },
        {
            id: 27,
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

    const input = new ObjectVariable('input_var', 'Input Object Variable');
    const exampleVariable = new SkillVariable('arg1', 'number', '', 'arg1',true );
    input.addProperty('arg1', exampleVariable); 

    const output = new ObjectVariable('output_var', 'Output Object Variable');
    const exampleVariable2 = new SkillVariable('result', 'number', '', 'result',true);
    output.addProperty('result', exampleVariable2);

    const code={
        python3:`def main(arg1: int) -> dict:
    return {
        "result": (arg1 + 2) * 3,
    }`
    }
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
            input_variables: input.toObject(),
            dependencies: null,
            code:JSON.stringify(code),
            output_type: 1,
            output_variables: output.toObject(),
            publish_status: 0,
            published_time: null,
            created_time: '',
            updated_time: '',
            status: 1,
            is_public: 1,
            is_creator: 1,
            nickname: '',
            attrs_are_visible: 1,
        },
    };
    return data;
};

export const getlist = async () => {
    // const res = await getModelList();
    // console.log(res.data.data, 'res')
    // llm_model_list = res.data.data
};
