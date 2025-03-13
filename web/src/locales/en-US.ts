/*
 * @LastEditors: biz
 */
import agent from './en-US/agent';
import component from './en-US/component';
import createkb from './en-US/createkb';
import creation from './en-US/creation';
import globalHeader from './en-US/globalHeader';
import menu from './en-US/menu';
import pages from './en-US/pages';
import plaza from './en-US/plaza';
import pwa from './en-US/pwa';
import settingDrawer from './en-US/settingDrawer';
import settings from './en-US/settings';
import skill from './en-US/skill';
import user from './en-US/user';
import workflow from './en-US/workflow';

export default {
    'navBar.lang': 'Languages',
    'layout.user.link.help': 'Help',
    'layout.user.link.privacy': 'Privacy',
    'layout.user.link.terms': 'Terms',
    'app.preview.down.block': 'Download this page to your local project',
    'app.welcome.link.fetch-blocks': 'Get all block',
    'app.welcome.link.block-list': 'Quickly build standard, pages based on `block` development',
    ...globalHeader,
    ...menu,
    ...settingDrawer,
    ...settings,
    ...pwa,
    ...component,
    ...pages,
    ...workflow,
    ...creation,
    ...agent,
    ...createkb,
    ...user,
    ...skill,
    ...plaza,
    'skill.downloadFiles': 'Output Files',
    'skill.download': 'Download',
    'app.workflow.log.filter.all': 'All Logs',
    'app.workflow.log.filter.roundtable': 'Roundtable',
    'app.workflow.log.filter.agent': 'Agent',
    'app.workflow.log.filter.workflow': 'Workflow',
    'app.workflow.log.output.files': 'Output Files',
    'app.workflow.log.type.roundtable': 'Roundtable',
    'app.workflow.log.type.agent': 'Agent',
    'app.workflow.log.type.workflow': 'Workflow',
    'app.workflow.log.type.agent.simple': 'Agent',
    'app.workflow.log.type.workflow.simple': 'Workflow',
    'app.workflow.log.roundtable.guidance': 'Roundtable:{name} Guidance Execution',
    'app.workflow.log.guidance.execution': 'Guidance Execution {type}: {name}',
    'app.workflow.log.empty': 'No logs available',
    'app.chatroom.log.title': 'Guidance Log',
    'app.chatroom.log.name': 'Guidance Name',
    'workflow.created_time': 'Created Time',
    'workflow.finished_time': 'Finished Time',
    'workflow.elapsed_time': 'Elapsed Time',
    'workflow.status': 'Status',
    'workflow.running': 'Running',
    'workflow.runSc': 'Completed',
    'workflow.runF': 'Failed',
    'agent.log.output': 'Output Result',
    'agent.log.error': 'Error Message',
    'agent.log.run.failed': 'Run Failed',
    'agent.log.no.output': 'No Output',
    'agent.log.corrections': 'Correction Records',
    'app.workflow.log.title': 'Application Logs',
};
