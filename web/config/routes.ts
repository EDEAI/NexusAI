
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
            {
                name: 'forgot-password',
                path: '/user/forgot-password',
                component: './User/ForgotPassword/Step1',
            },
            {
                name: 'forgot-password-step2',
                path: '/user/forgot-password/step2',
                component: './User/ForgotPassword/Step2',
            },
            {
                name: 'forgot-password-step3',
                path: '/user/forgot-password/step3',
                component: './User/ForgotPassword/Step3',
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
        path: '/knowledgebase',
        name: 'knowledgebase',
        component: './Creation/index',
    },
    {
        name: 'role-management',
        path: '/role-management',
        component: './RoleManagement',
    },
    {
        name: 'role-create',
        path: '/role-management/create',
        component: './RoleManagement/Create',
    },
    {
        name: 'role-edit',
        path: '/role-management/edit/:id',
        component: './RoleManagement/Edit',
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
