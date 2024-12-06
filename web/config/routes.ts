
export default [
    {
        path: '/user',
        layout: false,

        routes: [
            {
                name: 'login',
                path: '/user/login',
                component: './User/Login',
            },
            {
                name: 'register',
                path: '/user/register',
                component: './User/Register',
            },
        ],
    },
    {
        path: '/plaza',
        name: 'plaza',
        component: './Plaza/Dash_board',
    },
    {
        path: '/meeting',
        name: 'meeting',
        menu: false,
        component: './Plaza/Meeting',
    },
    {
        path: '/chat_room/:id',
        // path: '/chat_room',
        component: './Plaza/ChatRoom/index',
    },
    {
        path: '/workspace',
        name: 'workspace',
        component: './WorkSpace/index',
    },
    {
        path: '/workspace/workflow',
        name: 'workflow',
        component: './WorkSpace/WorkFlow',
        menu: false,
        menuRender: false,
    },
    {
        path: '/workspace/log',
        name: 'log',
        component: './WorkSpace/Log',
        menu: false,
        menuRender: false,
    },
    {
        path: '/creation',
        name: 'creation',

        component: './Creation/index',
    },
    {
        path: '/Agents',
        component: './Creation/Agents/index',
    },

    {
        path: '/Skill',
        component: './Creation/Skill/index',
    },
    {
        path: '/ReadOnlyAgent',
        component: './ReadOnly/Agent/index',
    },

    {
        path: '/ReadOnlySkill',
        component: './ReadOnly/Skill/index',
    },
    {
        path: '/',
        redirect: '/plaza ',
    },
    {
        path: '*',
        layout: false,
        component: './404',
    },
    {
        path: '/Createkb',
        name: 'createkb',
        menu: false,
        component: './Createkb',
        routes: [],
    },
];
