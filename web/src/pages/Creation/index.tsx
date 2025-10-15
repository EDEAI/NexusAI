import { DeleteOutlined, EditOutlined, SearchOutlined, SettingOutlined } from '@ant-design/icons';
import {
    Button,
    Card,
    Col,
    Input,
    message,
    Modal,
    Popover,
    Radio,
    Row,
    Spin,
    Typography,
} from 'antd';
import React, { useEffect, useState } from 'react';
// import {Ellipsis} from '@ant-design/pro-components';
import { DeleteCreation, GetChatroom, PutappsUpdate } from '@/api/creation';
import { bindTag } from '@/api/workflow';
import Headportrait from '@/components/headportrait';
import Scroll from '@/components/InfiniteScroll';
import TagSearch, { TagSelect } from '@/components/TagSearch';
import { useTagStore } from '@/store/tags';
import useUserStore, { UPDATE_NOTIFICATIONS } from '@/store/user';
import { createappdata, creationsearchdata, getlist, headportrait } from '@/utils/useUser';
import { useIntl } from '@umijs/max';
import moment from 'moment';
import { history } from 'umi';
import CreationModal from '../../components/creationModal';
import AddCreation from './components/AddCreation';
import Profilephoto from './components/profilephoto';
import { usePermissions } from '@/hooks/usePermissions';
import { PERMISSION_IDS } from '@/utils/permissions';
const { Text, Paragraph } = Typography;

const { TextArea } = Input;
const Creation: React.FC = () => {
    const intl = useIntl();
    const { hasPermission } = usePermissions();
    const [CreationList, setCreationList] = useState(null);
    const [apppage, setAPPPage] = useState(1);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [CreationName, setCreationName] = useState('');
    const [CreationContent, setCreationContent] = useState('');
    const [CardData, setCardData] = useState(null);
    const [showTab, showTabfun] = useState(false);

    const [establishModal, setEstablishModal] = useState(false);
    const [CreationType, setcreationType] = useState({
        name: 'Agent',
        path: intl.formatMessage({ id: 'creation.agent' }),
        icon: '/icons/creation/agent.svg',
        pitchicon: '/icons/creation/pitchagent.svg',
        signicon: '/icons/creation/pitchagent.svg',
        apps_mode: 1,
    }); //1: agent 2: workflow 3: dataset 4: custom tool
    let optionsModal = [
        {
            apps_mode: 6,
            name: intl.formatMessage({ id: 'creation.all' }),
            path: 'Agents',
            icon: '/icons/creation/quanbu.svg',
            unselected: '/icons/creation/quanbu.svg',
            pitchicon: '/icons/creation/pitchquanbu.svg',
            signicon: '/icons/creation/pitchquanbu.svg',
        },
        {
            apps_mode: 1,
            name: intl.formatMessage({ id: 'creation.agent' }),
            path: 'Agents',
            icon: '/icons/creation/agent.svg',
            unselected: '/icons/creation/unselectedrobot.svg',
            pitchicon: '/icons/creation/pitchagent.svg',
            signicon: '/icons/creation/pitchagent.svg',
        },
        {
            apps_mode: 2,
            name: intl.formatMessage({ id: 'creation.workflow' }),
            path: 'workspace/workflow',
            icon: '/icons/creation/gongzuoliu1.svg',
            unselected: '/icons/creation/unselectedprocess.svg',
            pitchicon: '/icons/creation/pitchgongzuoliu.svg',
            signicon: '/icons/creation/signgongzuoliu.svg',
        },
        // {
        //     apps_mode: 3,
        //     name: intl.formatMessage({ id: 'creation.repository' }),
        //     path: 'Createkb',
        //     icon: '/icons/creation/zhishik1.svg',
        //     unselected: '/icons/creation/unselectedrepository.svg',
        //     pitchicon: '/icons/creation/pitchzhishik.svg',
        //     signicon: '/icons/creation/signzhishik.svg',
        // },
        {
            apps_mode: 4,
            name: intl.formatMessage({ id: 'creation.skill' }),
            path: 'Skill',
            icon: '/icons/creation/jienng1.svg',
            unselected: '/icons/creation/unselectedskill.svg',
            pitchicon: '/icons/creation/pitchskill.svg',
            signicon: '/icons/creation/signskill.svg',
        },
    ];
    if (location.pathname == '/knowledgebase') {
        optionsModal = [
            {
                apps_mode: 3,
                name: intl.formatMessage({ id: 'creation.repository' }),
                path: 'Createkb',
                icon: '/icons/creation/zhishik1.svg',
                unselected: '/icons/creation/unselectedrepository.svg',
                pitchicon: '/icons/creation/pitchzhishik.svg',
                signicon: '/icons/creation/signzhishik.svg',
            },
        ];
    }

    const [optionsModalId, setOptionsModalId] = useState(6);
    const [searchType, setSearchType] = useState(false);
    const [fuzzySearchName, setFuzzySearchName] = useState('');

    const [hasMore, setHasMore] = useState(false);
    const [Modetype, setModetype] = useState([
        {
            apps_mode: 1,
            name: intl.formatMessage({ id: 'creation.agent' }),
            path: 'Agents',
            readOnlypath: 'ReadOnlyAgent',
        },
        {
            apps_mode: 2,
            name: intl.formatMessage({ id: 'creation.workflow' }),
            path: 'workspace/workflow',
        },
        { apps_mode: 3, name: intl.formatMessage({ id: 'creation.repository' }), path: 'createkb' },
        {
            apps_mode: 4,
            name: intl.formatMessage({ id: 'creation.skill' }),
            path: 'Skill',
            readOnlypath: 'ReadOnlySkill',
        },
    ]); //1: agent 2: workflow 3: dataset 4: custom tool 5: chatroom
    const [loading, setLoading] = useState(true);
    const [opensetting, setOpensetting] = useState(-1);
    const [selectedTags, setSelectedTags] = useState<string[]>([]);
    const [lastCheck, setLastCheck] = useState(Date.now());
    const { shouldComponentUpdate, clearUpdateNotification } = useUserStore();
    const [showModelType, setShowModelType] = useState(true);
    const getChatRoomList = async (
        page?: any,
        searchTypedata?: any,
        apps_mode?: Number,
        apps_name?: string,
        slide?: Boolean,
        page_size?: Number,
        tag_ids?: string[],
    ) => {
        const parameter = {
            page: page ? page : apppage,
            page_size: 27,
            search_type: creationsearchdata('GET').searchType == true ? 2 : 1,
            apps_mode: creationsearchdata('GET').optionsModalId,
            apps_name: apps_name || apps_name == '' ? apps_name : fuzzySearchName,
            tag_ids: tag_ids ? tag_ids.join(',') : '',
        };
        setLoading(true);
        let res = await GetChatroom(parameter);
        setHasMore(true);
        if (slide) {
            setCreationList({ list: CreationList.list.concat(res.data.list) });
        } else {
            setCreationList(res.data);
        }
        // setHasMore(false)
        setLoading(false);
        if (res.data.list.length < 27) {
            setHasMore(false);
        }
    };

    useEffect(() => {
        getlist();

        if (location.pathname == '/knowledgebase') {
            let item = {
                apps_mode: 3,
                name: intl.formatMessage({ id: 'creation.repository' }),
                path: 'Createkb',
            };
            setShowModelType(false);

            appModalChange(item);
        } else {
            showTabfun(true);
            getChatRoomList(1, null);
        }
    }, []);

    const pageonChange = () => {
        setAPPPage(apppage + 1);
        getChatRoomList(apppage + 1, searchType, null, null, true);
    };

    const appModalChange = (value: any) => {
        setOptionsModalId(value.apps_mode);
        creationsearchdata(
            'SET',
            value.apps_mode,
            JSON.parse(creationsearchdata('GET').searchType),
        );
        getChatRoomList(1, searchType, value.apps_mode);
    };

    const appNameChange = (e: any) => {
        setFuzzySearchName(e.target.value);
        getChatRoomList(1, searchType, optionsModalId, e.target.value);
    };
    useEffect(() => {
        getChatRoomList(1, searchType, optionsModalId, fuzzySearchName, null, null, selectedTags);
    }, [selectedTags]);
    const handleCancel = () => {
        setIsModalOpen(false);
    };

    const handleOk = async () => {
        let param = {
            name: CreationName,
            description: CreationContent,
            app_id: CardData.app_id,
            mode: CardData.mode,
            icon: (CardData.id ? JSON.stringify(CardData.id) : CardData.icon) || '0',
            icon_background: '',
            avatar: CardData?.avatar || null,
        };

        try{
            let res = await PutappsUpdate(param);

        if (res.code == 0) {
            setIsModalOpen(false);
            getChatRoomList(1, searchType, null, null, null, apppage * 27);
        } else {
                setIsModalOpen(false);
            }
        } catch (error) {
            console.log(error);
            setIsModalOpen(false);
        }
    };

    const showModal = (data: any, i: any) => {
        setOpensetting(i);
        setIsModalOpen(true);
        setCreationName(data.name);
        setCreationContent(data.description);
        setCardData(data);
    };

    const IconName = (e: any) => {
        setCreationName(e.target.value);
    };

    const CreationContents = (e: any) => {
        setCreationContent(e.target.value);
    };

    const EntryDetails = (data: any) => {
        event.stopPropagation();
        createappdata('SET', { ...data, type: creationsearchdata('GET').searchType });
        const Type = Modetype.filter((item: any) => {
            return item.apps_mode === data.mode;
        });

        if ((data.mode === 1 || data.mode === 4) && creationsearchdata('GET').searchType == true) {
            history.push(
                `/${Type[0].readOnlypath}?app_id=${data.app_id ? data.app_id : data.apps_id}&type=${
                    creationsearchdata('GET').searchType
                }`,
            );
        } else {
            history.push(
                `/${Type[0].path}?app_id=${data.app_id ? data.app_id : data.apps_id}&type=${
                    creationsearchdata('GET').searchType
                }`,
            );
        }
    };

    const deleteShowModal = (data: any, i: any) => {
        setOpensetting(i);
        Modal.confirm({
            title: intl.formatMessage({ id: 'creation.modal.returnconfirm' }),
            content: intl.formatMessage({ id: 'creation.modal.deldescribe' }),
            onOk: async () => {
                let res = await DeleteCreation(data);
                if (res && res.code == 0) {
                    message.success(intl.formatMessage({ id: 'creation.modal.delsuccess' }));
                    getChatRoomList(1, null, null, null, null, apppage * 27);
                } else {
                    message.error(intl.formatMessage({ id: 'creation.modal.delerror' }));
                }
            },
            onCancel() {},
        });
    };

    const teamSwitch = (checked: any) => {
        // , name: checked.target.value === 'true' ? intl.formatMessage({ id: 'creation.team' }) : intl.formatMessage({ id: 'creation.individual' })
        const searchTypedata = JSON.parse(checked.target.value);
        setSearchType(searchTypedata);
        creationsearchdata('SET', null, searchTypedata);
        getChatRoomList(1, searchTypedata);
    };

    const creationshowModal = () => {
        const newtype = optionsModal.filter((value: any) => {
            return value.apps_mode == creationsearchdata('GET').optionsModalId;
        });
        if (location.pathname == '/knowledgebase') {
            setShowModelType(false);
        }
        setEstablishModal(true);
        
        // Check route-specific permissions
        if (location.pathname === '/knowledgebase') {
            // For knowledge base route, only allow knowledge base creation
            if (newtype[0]?.apps_mode === 3 && hasPermission(PERMISSION_IDS.CREATE_KNOWLEDGE_BASE)) {
                setcreationType(newtype[0]);
                return;
            }
            // If current selection is not knowledge base or no permission, set to knowledge base
            const kbType = optionsModal.find(option => option.apps_mode === 3);
            if (kbType) {
                setcreationType(kbType);
            }
            return;
        } else {
            // For creation route, only allow agent, workflow, skill creation
            if (newtype[0]?.apps_mode !== 6 && newtype[0]?.apps_mode !== 3) {
                const selectedType = newtype[0];
                const hasPermissionForType = 
                    (selectedType.apps_mode === 1 && hasPermission(PERMISSION_IDS.CREATE_AGENT)) ||
                    (selectedType.apps_mode === 2 && hasPermission(PERMISSION_IDS.CREATE_WORKFLOW)) ||
                    (selectedType.apps_mode === 4 && hasPermission(PERMISSION_IDS.CREATE_SKILL));
                
                if (hasPermissionForType) {
                    setcreationType(selectedType);
                    return;
                }
            }
            
            // Find the first type user has permission for (excluding knowledge base)
            const availableTypes = [
                { apps_mode: 1, permission: hasPermission(PERMISSION_IDS.CREATE_AGENT) },
                { apps_mode: 2, permission: hasPermission(PERMISSION_IDS.CREATE_WORKFLOW) },
                { apps_mode: 4, permission: hasPermission(PERMISSION_IDS.CREATE_SKILL) }
            ];
            
            const firstAvailableType = availableTypes.find(type => type.permission);
            
            if (firstAvailableType) {
                const typeConfig = optionsModal.find(option => option.apps_mode === firstAvailableType.apps_mode);
                setcreationType(typeConfig || {
                    name: 'Agent',
                    path: 'Agents',
                    icon: '/icons/creation/agent.svg',
                    pitchicon: '/icons/creation/pitchagent.svg',
                    signicon: '/icons/creation/pitchagent.svg',
                    apps_mode: 1,
                });
            } else {
                // Fallback to Agent if no permissions (shouldn't happen in normal flow)
                setcreationType({
                    name: 'Agent',
                    path: 'Agents',
                    icon: '/icons/creation/agent.svg',
                    pitchicon: '/icons/creation/pitchagent.svg',
                    signicon: '/icons/creation/pitchagent.svg',
                    apps_mode: 1,
                });
            }
        }
    };
    const setRunId = useUserStore(state => state.setRunId);
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    const toRunWorkFlow = item => {
        setRunId(item.app_id);
    };

    // const [tagList, setTagList] = useState<SelectProps['options']>([
    //     {
    //         label: 'All',
    //         value: 'All',
    //     },
    // ]);
    const { tags, fetchTags } = useTagStore();

    useEffect(() => {}, [optionsModalId]);

    useEffect(() => {
        const checkUpdate = () => {
            if (shouldComponentUpdate(UPDATE_NOTIFICATIONS.AGENT_LIST, lastCheck)) {
                const notification = useUserStore
                    .getState()
                    .updateNotifications.get(UPDATE_NOTIFICATIONS.AGENT_LIST);

                if (notification?.payload?.action === 'create') {
                    getChatRoomList(1, null);
                } else {
                    getChatRoomList(1, null);
                }

                setLastCheck(Date.now());

                clearUpdateNotification(UPDATE_NOTIFICATIONS.AGENT_LIST);
            }
            if (shouldComponentUpdate(UPDATE_NOTIFICATIONS.SKILL_LIST, lastCheck)) {
                const notification = useUserStore
                    .getState()
                    .updateNotifications.get(UPDATE_NOTIFICATIONS.SKILL_LIST);

                if (notification?.payload?.action === 'create') {
                    getChatRoomList(4, null);
                } else {
                    getChatRoomList(4, null);
                }

                setLastCheck(Date.now());

                clearUpdateNotification(UPDATE_NOTIFICATIONS.SKILL_LIST);
            }
        };

        const timer = setInterval(checkUpdate, 1000);
        return () => clearInterval(timer);
    }, [shouldComponentUpdate, lastCheck]);

    return (
        <div
            className=" pb-[10px] flex flex-col"
            style={{ height: 'calc(-60px + 100vh)', width: '100%', margin: '0 auto' }}
        >
            <div className="flex px-[30px] py-[20px] mx-[8px] items-center flex-wrap justify-between gap-2">
                <div className="flex items-center">
                    {showTab
                        ? optionsModal.map((item: any, i: number) => {
                              return (
                                  // <Button color="primary" variant="filled"
                                  // icon={ <img src={item.icon} alt="" />}
                                  // >
                                  //   {item.name}
                                  // </Button>
                                  <div
                                      onClick={() => {
                                          appModalChange(item);
                                      }}
                                      className="flex justify-center items-center h-8 rounded-lg mr-4 cursor-pointer px-[10px]"
                                      style={
                                          creationsearchdata('GET').optionsModalId == item.apps_mode
                                              ? { color: '#1B64F3', backgroundColor: '#ffffff' }
                                              : { color: '#9097a1' }
                                      }
                                  >
                                      <div className="mr-2">
                                          <img
                                              src={
                                                  creationsearchdata('GET').optionsModalId ==
                                                  item.apps_mode
                                                      ? item.pitchicon
                                                      : item.unselected
                                              }
                                              alt=""
                                          />
                                      </div>
                                      <div>{item.name}</div>
                                  </div>
                              );
                          })
                        : ''}
                </div>

                <div className="flex items-center flex-wrap">
                    <div className="min-w-[200px] mr-4">
                        {/* <Select
                            mode="multiple"
                            size='middle'
                            placeholder="Please select"
                            defaultValue={['a10', 'c12']}
                            onChange={()=>{}}
                            style={{ width: '100%' }}
                            options={tagList}
                        /> */}
                        <TagSearch
                            allowClear
                            modes={creationsearchdata('GET').optionsModalId}
                            placeholder={intl.formatMessage({
                                id: 'creation.placeholder.selectTags',
                            })}
                            onTagChange={() => {
                                fetchTags();
                            }}
                            onChange={e => {
                                setSelectedTags(e);
                            }}
                        ></TagSearch>
                    </div>
                    <div className=" mr-5">
                        <Radio.Group
                            onChange={teamSwitch}
                            defaultValue={JSON.stringify(creationsearchdata('GET').searchType)}
                        >
                            <Radio.Button value="true">
                                {intl.formatMessage({ id: 'creation.team' })}
                            </Radio.Button>
                            <Radio.Button value="false">
                                {intl.formatMessage({ id: 'creation.individual' })}
                            </Radio.Button>
                        </Radio.Group>
                    </div>
                    <Input
                        style={{ width: 300 }}
                        prefix={<SearchOutlined />}
                        placeholder={intl.formatMessage({ id: 'creation.placeholder.searchname' })}
                        variant="filled"
                        onChange={appNameChange}
                    />
                </div>
            </div>
            {/* <div className="flex justify-center w-screen"  > */}
            <Spin spinning={loading} size="large" className="mt-[112px]">
                <div id="Creation" style={{ overflowY: 'auto', height: 'calc(100vh - 128px)' }}>
                    {CreationList && CreationList.list && CreationList.list.length > 0 ? (
                        <Scroll
                            dataLength={CreationList.list.length}
                            elid={'Creation'}
                            ishasMore={hasMore}
                            upSlide={pageonChange}
                            isFooter={true}
                        >
                            <Row
                                gutter={[16, 8]}
                                wrap={true}
                                style={{ margin: 0 }}
                                className="px-[30px]"
                            >
                                <Col sm={24} md={12} lg={12} xl={8} xxl={6}>
                                    <AddCreation
                                        optionsModalId={creationsearchdata('GET').optionsModalId}
                                    />
                                </Col>
                                {CreationList && CreationList.list && CreationList.list.length
                                    ? CreationList.list.map((item: any, i: number) => (
                                          <Col
                                              className="gutter-row"
                                              sm={24}
                                              md={12}
                                              lg={12}
                                              xl={8}
                                              xxl={6}
                                              key={i}
                                          >
                                              <Card
                                                  // bordered={false}
                                                  className=" cursor-pointer transition shadow-lg shadow-gray-100 hover:shadow-gray-200"
                                                  style={{ marginTop: 10, minWidth: 300 }}
                                                  hoverable={false}
                                                  styles={{
                                                      body: { padding: '20px' },
                                                  }}
                                              >
                                                  <div>
                                                      <div onClick={() => EntryDetails(item)}>
                                                          <Card.Meta
                                                              // avatar={
                                                              //   <Headportrait
                                                              //     Image={headportrait('single', item.icon)}
                                                              //     icon={creationsearchdata('GET').optionsModalId === 6 ? optionsModal.filter((value: any) => value.apps_mode === item.mode)[0].signicon : null}
                                                              //   />
                                                              // }
                                                              title={[
                                                                  <div className="flex w-full">
                                                                      <div className="mr-[17px] shrink-0">
                                                                          <Headportrait
                                                                              Image={headportrait(
                                                                                  'single',
                                                                                  item.icon,
                                                                              )}
                                                                              avatar={item.avatar}
                                                                              icon={
                                                                                  creationsearchdata(
                                                                                      'GET',
                                                                                  )
                                                                                      .optionsModalId ===
                                                                                  6
                                                                                      ? optionsModal.filter(
                                                                                            (
                                                                                                value: any,
                                                                                            ) =>
                                                                                                value.apps_mode ===
                                                                                                item.mode,
                                                                                        )[0]
                                                                                            ?.signicon
                                                                                      : null
                                                                              }
                                                                          />
                                                                      </div>
                                                                      <div className="flex-1">
                                                                          <div className="flex items-center justify-between">
                                                                              {' '}
                                                                              {/* style={{width:'calc(100% - 50px)'}} 160px*/}
                                                                              <div
                                                                                  style={{
                                                                                      maxWidth:
                                                                                          '160px',
                                                                                  }}
                                                                                  className="text-sm text-[#213044] font-medium truncate"
                                                                              >
                                                                                  {/* {item.name} */}
                                                                                  <Text
                                                                                      ellipsis={{
                                                                                          tooltip:
                                                                                              item.name,
                                                                                      }}
                                                                                  >
                                                                                      {item.name}
                                                                                  </Text>
                                                                              </div>
                                                                              <div className=" leading-6 flex items-center justify-end text-xs font-normal text-[#999999]">
                                                                                  <div>
                                                                                      {intl.formatMessage(
                                                                                          {
                                                                                              id: 'creation.numberofcitation',
                                                                                          },
                                                                                      )}
                                                                                      :{' '}
                                                                                  </div>
                                                                                  <div className="text-[#1B64F3] ml-2">
                                                                                      {' '}
                                                                                      {item.execution_times
                                                                                          ? item.execution_times
                                                                                          : 0}
                                                                                  </div>
                                                                              </div>
                                                                          </div>

                                                                          <div className="flex items-center justify-between w-full text-xs font-normal text-[#999999]">
                                                                              <div className="text-xs font-normal text-[#999999] mt-[7px]">
                                                                                  {Modetype.map(
                                                                                      (
                                                                                          value: any,
                                                                                          i: any,
                                                                                      ) => {
                                                                                          return value.apps_mode ===
                                                                                              item.mode
                                                                                              ? value.name
                                                                                              : null;
                                                                                      },
                                                                                  )}
                                                                              </div>

                                                                              <div className=" flex items-center justify-end mt-[7px]">
                                                                                  <div className="max-w-[56px] mr-2 ">
                                                                                      <Text
                                                                                          ellipsis={{
                                                                                              tooltip:
                                                                                                  item.published_creator,
                                                                                          }}
                                                                                          className="text-base"
                                                                                      >
                                                                                          <div className=" text-[#999999] text-xs">
                                                                                              {
                                                                                                  item.published_creator
                                                                                              }
                                                                                          </div>
                                                                                      </Text>
                                                                                  </div>
                                                                                  <div>
                                                                                      {item.published_time ? (
                                                                                          <span className="text-[#1B64F3]">
                                                                                              {moment(
                                                                                                  item.published_time,
                                                                                              ).format(
                                                                                                  'YYYY-MM-DD HH:mm:ss',
                                                                                              )}{' '}
                                                                                              {intl.formatMessage(
                                                                                                  {
                                                                                                      id: 'creation.publish',
                                                                                                  },
                                                                                              )}
                                                                                          </span>
                                                                                      ) : item.mode !==
                                                                                        3 ? (
                                                                                          <div className="flex">
                                                                                              <img
                                                                                                  src="/icons/unpublish.svg"
                                                                                                  alt=""
                                                                                                  className="mr-[5px]"
                                                                                              />
                                                                                              {intl.formatMessage(
                                                                                                  {
                                                                                                      id: 'creation.unpublish',
                                                                                                  },
                                                                                              )}
                                                                                          </div>
                                                                                      ) : null}
                                                                                  </div>
                                                                              </div>
                                                                          </div>
                                                                      </div>
                                                                  </div>,
                                                              ]}
                                                              description={
                                                                  <div
                                                                      style={{
                                                                          height: 100,
                                                                          margin: '20px 0 20px 0',
                                                                      }}
                                                                  >
                                                                      <Paragraph
                                                                          ellipsis={{
                                                                              rows: 4,
                                                                              tooltip:
                                                                                  item.description,
                                                                          }}
                                                                          className="!mb-0"
                                                                      >
                                                                          <div
                                                                              style={{
                                                                                  color: '#999999',
                                                                              }}
                                                                          >
                                                                              {item.description}
                                                                          </div>
                                                                      </Paragraph>
                                                                      <div
                                                                          onClick={e => {
                                                                              e.stopPropagation();
                                                                          }}
                                                                          className="not_has_down_select hover:bg-gray-100 rounded-md"
                                                                      >
                                                                          {/* <Select
                                                                              mode="multiple"
                                                                              size="middle"
                                                                              variant="borderless"
                                                                              placeholder={intl.formatMessage(
                                                                                  {
                                                                                      id: 'addTag.pleaseSelect',
                                                                                      defaultMessage:
                                                                                          'Please select',
                                                                                  },
                                                                              )}
                                                                              maxTagCount="responsive"
                                                                              onChange={e => {}}

                                                                              style={{
                                                                                  width: '100%',
                                                                              }}
                                                                              options={tagList}
                                                                          /> */}
                                                                          <TagSelect
                                                                              onBlur={e => {
                                                                                  //   const changeList=item.changeTags||(item.tags.map(x=>x.id))
                                                                                  //   const removeList=item.tags.filter(x=>!changeList.some(y=>y==x.id)).map(x=>x.id)
                                                                                  //   if(removeList?.length){
                                                                                  //     unBindTag(removeList,item.app_id).then(res=>{
                                                                                  //         item.tags=item.changeTags
                                                                                  //     })
                                                                                  //   }
                                                                                  //   if(item.changeTags?.length){
                                                                                  bindTag(
                                                                                      item.changeTags,
                                                                                      [item.app_id],
                                                                                  );
                                                                                  //   }
                                                                              }}
                                                                              listStyle="horizontal"
                                                                              key={item.app_id}
                                                                              onChange={e => {
                                                                                  // const removeList=item.tags.filter(x=>!(e).some(y=>y==x.id)).map(x=>x.id||x)
                                                                                  // if(removeList?.length){
                                                                                  //     unBindTag(removeList,item.app_id).then(res=>{
                                                                                  //         item.tags=e
                                                                                  //     })
                                                                                  // }
                                                                                  item.changeTags =
                                                                                      e;

                                                                                  //   bindTag(e, [
                                                                                  //       item.app_id,
                                                                                  //   ]);
                                                                              }}
                                                                              placeholder={intl.formatMessage(
                                                                                  {
                                                                                      id: 'addTag.addTag',
                                                                                  },
                                                                              )}
                                                                              defaultValue={item.tags?.map(
                                                                                  item => item.id,
                                                                              )}
                                                                              maxTagCount={5}
                                                                              options={tags}
                                                                              className="!w-full"
                                                                              variant="borderless"
                                                                          ></TagSelect>
                                                                      </div>
                                                                  </div>
                                                              }
                                                          />
                                                      </div>
                                                      <div className="flex justify-between">
                                                          <div
                                                              className="flex items-center justify-start"
                                                              style={{ height: '24px' }}
                                                          >
                                                              {item.list && item.list.length ? (
                                                                  <Popover
                                                                      placement="bottomLeft"
                                                                      content={
                                                                          <div className=" overflow-auto">
                                                                              {item.list.map(
                                                                                  (
                                                                                      value: any,
                                                                                      i: number,
                                                                                  ) => {
                                                                                      return (
                                                                                          <div
                                                                                              className="w-80 flex items-center justify-start p-1.5 rounded-md  cursor-pointer hover:bg-[#fafafa]"
                                                                                              key={
                                                                                                  i
                                                                                              }
                                                                                              onClick={() =>
                                                                                                  EntryDetails(
                                                                                                      value,
                                                                                                  )
                                                                                              }
                                                                                          >
                                                                                              <div className="mr-3.5">
                                                                                                  <div className="w-[36px] h-[36px] bg-[#EDF3FE] rounded-lg mr-1.5 flex items-center justify-center ">
                                                                                                      <img
                                                                                                          src={headportrait(
                                                                                                              'single',
                                                                                                              value.icon,
                                                                                                          )}
                                                                                                          alt=""
                                                                                                      />
                                                                                                  </div>
                                                                                              </div>
                                                                                              <div>
                                                                                                  <div className="text-xs font-normal text-[#213044]">
                                                                                                      {
                                                                                                          value.name
                                                                                                      }
                                                                                                  </div>
                                                                                                  <div className="text-xs font-normal text-[#666]">
                                                                                                      {value?.mode ==
                                                                                                      1
                                                                                                          ? intl.formatMessage(
                                                                                                                {
                                                                                                                    id: 'workflow.agent',
                                                                                                                },
                                                                                                            )
                                                                                                          : value?.mode ==
                                                                                                            2
                                                                                                          ? intl.formatMessage(
                                                                                                                {
                                                                                                                    id: 'component.menu.workflow',
                                                                                                                },
                                                                                                            )
                                                                                                          : value?.mode ==
                                                                                                            3
                                                                                                          ? intl.formatMessage(
                                                                                                                {
                                                                                                                    id: 'component.menu.knowledgeBase',
                                                                                                                },
                                                                                                            )
                                                                                                          : intl.formatMessage(
                                                                                                                {
                                                                                                                    id: 'workflow.skill',
                                                                                                                },
                                                                                                            )}
                                                                                                  </div>
                                                                                              </div>
                                                                                          </div>
                                                                                      );
                                                                                  },
                                                                              )}
                                                                          </div>
                                                                      }
                                                                  >
                                                                      <div className="flex items-center justify-around text-xs font-normal">
                                                                          {intl.formatMessage({
                                                                              id: 'creation.relevancy.app',
                                                                          })}{' '}
                                                                          :
                                                                          {item.list
                                                                              .slice(0, 4)
                                                                              .map(
                                                                                  (
                                                                                      data: any,
                                                                                      i: number,
                                                                                  ) => {
                                                                                      return (
                                                                                          <div
                                                                                              key={
                                                                                                  i
                                                                                              }
                                                                                              className='ml-1.5'
                                                                                          >
                                                                                              {/* <div className="w-8 h-8 rounded-lg ml-1.5 flex items-center justify-center "> */}
                                                                                                  {/* <img
                                                                                                      src={headportrait(
                                                                                                          'single',
                                                                                                          data.icon,
                                                                                                      )}
                                                                                                      alt=""
                                                                                                  /> */}
                                                                                                  <Headportrait
                                                                                                      Image={headportrait(
                                                                                                          'single',
                                                                                                          data.icon,
                                                                                                      )}
                                                                                                      avatar={
                                                                                                          data.avatar
                                                                                                      }
                                                                                                      size='24'
                                                                                                      // icon={`/icons/creation/${WORKFLOW_ICON.WorkFlow}.svg`}
                                                                                                  ></Headportrait>
                                                                                              {/* </div> */}
                                                                                          </div>
                                                                                      );
                                                                                  },
                                                                              )}
                                                                          {item.list.length > 4 ? (
                                                                              <div className="w-8 h-8 bg-[#EDF3FE] rounded-lg ml-1.5 flex items-center justify-center ">
                                                                                  <img
                                                                                      src={
                                                                                          '/icons/more.svg'
                                                                                      }
                                                                                      alt=""
                                                                                  />
                                                                              </div>
                                                                          ) : null}
                                                                      </div>
                                                                  </Popover>
                                                              ) : null}
                                                          </div>
                                                          {item?.mode === 2 ? (
                                                              <div className="flex-1 flex justify-end items-center">
                                                                  {item?.publish_status == 1 ? (
                                                                      <img
                                                                          onClick={() =>
                                                                              toRunWorkFlow(item)
                                                                          }
                                                                          src="/icons/operation_icon.svg"
                                                                          className="mr-2"
                                                                      />
                                                                  ) : (
                                                                      <img
                                                                          src="/icons/operation_disable_icon.svg"
                                                                          className="mr-2"
                                                                      />
                                                                  )}
                                                              </div>
                                                          ) : null}
                                                          <div>
                                                              {!JSON.parse(
                                                                  creationsearchdata('GET')
                                                                      ?.searchType,
                                                              ) ? (
                                                                  <Popover
                                                                      placement="rightTop"
                                                                      open={
                                                                          opensetting == i
                                                                              ? true
                                                                              : false
                                                                      }
                                                                      onOpenChange={newopen => {
                                                                          setOpensetting(-1);
                                                                      }}
                                                                      mouseLeaveDelay={1}
                                                                      content={
                                                                          <div>
                                                                              <div>
                                                                                  <Button
                                                                                      type="link"
                                                                                      className="text-[#213044]"
                                                                                      onClick={() => {
                                                                                          showModal(
                                                                                              item,
                                                                                              -1,
                                                                                          );
                                                                                      }}
                                                                                  >
                                                                                      <EditOutlined />
                                                                                      {intl.formatMessage(
                                                                                          {
                                                                                              id: 'creation.redact',
                                                                                          },
                                                                                      )}
                                                                                  </Button>
                                                                              </div>
                                                                              <div>
                                                                                  <Button
                                                                                      type="link"
                                                                                      className="text-[#E12222]"
                                                                                      onClick={() =>
                                                                                          deleteShowModal(
                                                                                              item,
                                                                                              -1,
                                                                                          )
                                                                                      }
                                                                                  >
                                                                                      <DeleteOutlined />
                                                                                      {intl.formatMessage(
                                                                                          {
                                                                                              id: 'creation.delete',
                                                                                          },
                                                                                      )}
                                                                                  </Button>
                                                                              </div>
                                                                          </div>
                                                                      }
                                                                  >
                                                                      <div
                                                                          onMouseEnter={() => {
                                                                              setOpensetting(i);
                                                                          }}
                                                                          className="w-[26px] h-[26px] flex items-center justify-center"
                                                                      >
                                                                          <SettingOutlined
                                                                              key="setting"
                                                                              onClick={() => {
                                                                                  setOpensetting(i);
                                                                              }}
                                                                          />
                                                                      </div>
                                                                  </Popover>
                                                              ) : null}
                                                          </div>
                                                      </div>
                                                  </div>
                                              </Card>
                                          </Col>
                                      ))
                                    : null}
                            </Row>
                        </Scroll>
                    ) : CreationList && CreationList.list && CreationList.list.length == 0 ? (
                        <div className="w-full flex items-center flex-wrap justify-center mt-48">
                            <div className="w-full flex items-center justify-center mb-2.5">
                                <img src="/icons/default.svg" alt="" />
                            </div>
                            {fuzzySearchName && fuzzySearchName !== '' ? (
                                <div>“{fuzzySearchName}”</div>
                            ) : (
                                <div>
                                    <div className="w-full text-center mb-3 text-[#666] text-sm">
                                        {intl.formatMessage({ id: 'creation.margindescribe' })} ~
                                    </div>
                                    <div className="w-full text-center">
                                        {' '}
                                        <Button
                                            color="primary"
                                            disabled={(() => {
                                                if (location.pathname === '/knowledgebase') {
                                                    return !hasPermission(PERMISSION_IDS.CREATE_KNOWLEDGE_BASE);
                                                }
                                                // For creation route, only check agent, workflow, and skill permissions
                                                const currentModalId = creationsearchdata('GET').optionsModalId;
                                                if (currentModalId === 1) return !hasPermission(PERMISSION_IDS.CREATE_AGENT);
                                                if (currentModalId === 2) return !hasPermission(PERMISSION_IDS.CREATE_WORKFLOW);
                                                if (currentModalId === 4) return !hasPermission(PERMISSION_IDS.CREATE_SKILL);
                                                // For "All" tab (currentModalId === 6) in creation route, only check agent, workflow, and skill permissions
                                                return !(hasPermission(PERMISSION_IDS.CREATE_AGENT) || 
                                                        hasPermission(PERMISSION_IDS.CREATE_WORKFLOW) || 
                                                        hasPermission(PERMISSION_IDS.CREATE_SKILL));
                                            })()}
                                            className={(() => {
                                                if (location.pathname === '/knowledgebase') {
                                                    return !hasPermission(PERMISSION_IDS.CREATE_KNOWLEDGE_BASE) ? 'cursor-not-allowed opacity-50' : '';
                                                }
                                                // For creation route, only check agent, workflow, and skill permissions
                                                const currentModalId = creationsearchdata('GET').optionsModalId;
                                                let isDisabled = false;
                                                if (currentModalId === 1) isDisabled = !hasPermission(PERMISSION_IDS.CREATE_AGENT);
                                                else if (currentModalId === 2) isDisabled = !hasPermission(PERMISSION_IDS.CREATE_WORKFLOW);
                                                else if (currentModalId === 4) isDisabled = !hasPermission(PERMISSION_IDS.CREATE_SKILL);
                                                else isDisabled = !(hasPermission(PERMISSION_IDS.CREATE_AGENT) || 
                                                                   hasPermission(PERMISSION_IDS.CREATE_WORKFLOW) || 
                                                                   hasPermission(PERMISSION_IDS.CREATE_SKILL));
                                                return isDisabled ? 'cursor-not-allowed opacity-50' : '';
                                            })()}
                                            onClick={() => {
                                                creationshowModal();
                                            }}
                                        >
                                            {intl.formatMessage({ id: 'creation.addnewapp' })}
                                        </Button>{' '}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : null}
                </div>
            </Spin>
            <Modal
                title=""
                open={isModalOpen}
                okText={intl.formatMessage({ id: 'creation.conserve' })}
                onOk={handleOk}
                onCancel={handleCancel}
            >
                <div className="mb-[30px]">
                    <div className="mb-[15px]">
                        {CardData?.mode == 1
                            ? intl.formatMessage({ id: 'creation.agent' })
                            : CardData?.mode == 2
                            ? intl.formatMessage({ id: 'creation.workflow' })
                            : CardData?.mode == 3
                            ? intl.formatMessage({ id: 'creation.repository' })
                            : intl.formatMessage({ id: 'creation.skill' })}
                        {intl.formatMessage({ id: 'creation.appiconname' })}
                    </div>
                    <div className="flex items-center justify-around">
                        <Profilephoto CardData={CardData} setCardData={setCardData} />
                        <Input
                            showCount
                            maxLength={50}
                            placeholder={intl.formatMessage({ id: 'creation.placeholder.appname' })}
                            onChange={IconName}
                            value={CreationName}
                        />
                    </div>
                </div>
                <div className="mb-[30px]">
                    <div className="mb-[15px]">
                        {CardData?.mode == 1
                            ? intl.formatMessage({ id: 'creation.agent' })
                            : CardData?.mode == 2
                            ? intl.formatMessage({ id: 'creation.workflow' })
                            : CardData?.mode == 3
                            ? intl.formatMessage({ id: 'creation.repository' })
                            : intl.formatMessage({ id: 'creation.skill' })}
                        {intl.formatMessage({ id: 'creation.appdescribe' })}
                    </div>
                    <TextArea
                        showCount
                        maxLength={2000}
                        rows={4}
                        placeholder={intl.formatMessage({ id: 'creation.placeholder.appdescribe' })}
                        onChange={CreationContents}
                        value={CreationContent}
                    />
                </div>
            </Modal>
            <CreationModal
                setIsModalOpen={setEstablishModal} //Toggle modal switch
                isModalOpen={establishModal} //Toggle modal switch
                ModalType={showModelType} //Toggle button display
                CreationType={CreationType} //Card creation type { name: "Agent", path: "Agents", id: 1, }
                setcreationType={setcreationType} //Toggle card button type (optional)
                transformData={optionsModal.filter((item: any) => {
                    return item.apps_mode !== 6;
                })} //Total type of button toggle (optional)
            />
        </div>
        // </div>
    );
};
export default Creation;
