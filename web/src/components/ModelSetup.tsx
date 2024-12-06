import Callword from '@/components/callword';
import { CaretDownOutlined, CaretUpOutlined, SettingOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import {
    Badge,
    Button,
    Input,
    InputNumber,
    message,
    Modal,
    Popconfirm,
    Select,
    Typography,
} from 'antd';
import React, { useEffect, useState } from 'react';
import { getSuppliersList, postSuppliersAuthorize, postSwitchingModels } from '../api/setting';
const { TextArea } = Input;
const { Paragraph, Text } = Typography;

export type TeamProps = {
    isModalOpen: boolean;
    setIsModalOpen: any;
};
const ModelSetup: React.FC<TeamProps> = ({ isModalOpen, setIsModalOpen }) => {
    const intl = useIntl();
    const [suppliers, setSuppliers] = useState<any>(null);
    const [modelslist, setModelslist] = useState<any>(null);
    const [isModalOpen2, setIsModalOpen2] = useState(false);
    const [modalsingledata, setModalSingleData] = useState<any>(null);
    // const Modeltypedata = [
    //     { id: 1, name: 'text-generation' },
    //     { id: 2, name: 'embeddings' },
    //     { id: 3, name: 'reranking' },
    //     { id: 4, name: 'speech2text' },
    //     { id: 5, name: 'tts' },
    //     { id: 6, name: 'text2img' },
    //     { id: 7, name: 'moderation' },
    // ]
    const [pulldownlistid, setPulldownlistid] = useState<any>(1);
    useEffect(() => {}, []);

    const findDefaultModelId = (data: any): number | null => {
        for (const supplier of data.suppliers) {
            for (const model of supplier.models) {
                if (model.model_default_used === 1) {
                    return model.model_id;
                }
            }
        }
        return null;
    };

    const changemodal = async (value: any, id: any) => {
        console.log(value, id, 'data');
        const data = {
            type: value.model_type,
            model_id: id,
        };
        const res = await postSwitchingModels(data);
        console.log(res, 'data');
        ModelSetupList(true);
    };

    const ModelSetupList = async (param: boolean) => {
        if (param) {
            const res = await getSuppliersList();

            setModelslist(res.data.models_list);
            const newdata = res.data.suppliers_list.map((item: any, index: any) => {
                return { ...item, listopen: false };
            });
            // console.log(newdata, 'newdata')
            setSuppliers(newdata);
        }
    };

    const handleCancel1 = () => {
        setIsModalOpen(false);
    };

    const handleOpenModal = (data: any) => {
        setIsModalOpen2(true);
        setModalSingleData(data);
        console.log(data, 'data');
    };

    const uniqueTypeSet = (data: any) => {
        const uniqueTypeSet = new Set(data.map(model => model.model_type));
        const filteredModels = data.filter(
            model =>
                uniqueTypeSet.has(model.model_type) &&

                !data
                    .slice(0, data.indexOf(model))
                    .some(prevModel => prevModel.model_type === model.model_type),
        );
        // const newtype = filteredModels.map((item: any, index: any) => { return item.model_type })
        // const newmodeldata = Modeltypedata.filter((item: any, index: any) => {
        //     return newtype.includes(item.id)
        // })
        // console.log(filteredModels, 'AASDA')
        return filteredModels;
    };

    const ChangePulldown = (id: any) => {
        // [{AAA:'bbb',type:false},{AAA:'ccc',type:false}]
        const newdata = suppliers;
        newdata[id].listopen = !newdata[id].listopen;
        setSuppliers(newdata);
        console.log(newdata, 'suppliers[id].listopen = !suppliers[id].listopenASD');
        // setSuppliers({...suppliers,[id]:{...suppliers[id],listopen:!suppliers[id].listopen}})
        if (id + 1 == pulldownlistid) {
            setPulldownlistid(0);
        } else {
            setPulldownlistid(id + 1);
        }
    };

    const InputChange = (e: any, index: any) => {
        console.log(typeof e, 'e');
        const newmodal = JSON.parse(JSON.stringify(modalsingledata));
        // if (newmodal.supplier_config[index].type == 'int' || newmodal.supplier_config[index].type == 'float') {
        //     // if(typeof e ==='number')
        //     newmodal.supplier_config[index].value = e
        // } else {
        //     newmodal.supplier_config[index].value = e
        // }
        newmodal.supplier_config[index].value = e;
        setModalSingleData(newmodal);
    };

    const handleSave = async () => {
        const data = {
            supplier_id: modalsingledata.supplier_id,
            config: modalsingledata.supplier_config,
        };
        const res = await postSuppliersAuthorize(data);
        if (res.code === 0) {
            message.success(
                intl.formatMessage({ id: 'user.saveSuccess', defaultMessage: '' }),
            );
            setIsModalOpen2(false);
            ModelSetupList(true);
        }
        console.log(res, 'data');
    };
    return (
        <div className="m-4">
            <Modal
                width={900}
                title={intl.formatMessage({ id: 'user.modelSettings', defaultMessage: '' })}
                open={isModalOpen}
                footer={false}
                onCancel={handleCancel1}
                afterOpenChange={ModelSetupList}
            >
                <div className="flex items-center justify-between mb-5 ">
                    <div className="text-xs font-medium">
                        {intl.formatMessage({ id: 'user.modelList', defaultMessage: '' })}
                    </div>
                    <div>
                        <Popconfirm
                            placement="bottomRight"
                            title=""
                            icon={null}
                            okText={intl.formatMessage({ id: 'user.save', defaultMessage: '' })}
                            onConfirm={() => {
                                message.success(
                                    intl.formatMessage({
                                        id: 'user.saveSuccess',
                                        defaultMessage: '',
                                    }),
                                );
                            }}
                            description={
                                <div>
                                    {modelslist
                                        ? modelslist.map((item: any, index: any) => {
                                              return (
                                                  <div className="mb-5">
                                                      <div className="mb-2.5">
                                                          <Callword
                                                              name={item.model_type_name}
                                                              title={item.help}
                                                          />
                                                      </div>
                                                      {/* <div>{findDefaultModelId(item) }</div> */}
                                                      <Select
                                                          // value={}
                                                          // value={findDefaultModel(item).model.model_id}
                                                          // value={
                                                          //     item.suppliers.map((item: any, index: any) => {
                                                          //         return item.models.filter((item: any, index: any) => {
                                                          //             return item.model_default_used === 1
                                                          //         })
                                                          //     })
                                                          // }
                                                          value={findDefaultModelId(item)}
                                                          style={{ width: 330 }}
                                                          variant="filled"
                                                          onChange={e => changemodal(item, e)}
                                                          options={
                                                              item.suppliers.map(
                                                                  (item: any, index: any) => {
                                                                      return {
                                                                          label: (
                                                                              <span>
                                                                                  {
                                                                                      item.supplier_name
                                                                                  }
                                                                              </span>
                                                                          ),
                                                                          options: item.models.map(
                                                                              (
                                                                                  item: any,
                                                                                  index: any,
                                                                              ) => {
                                                                                  return {
                                                                                      label: (
                                                                                          <span>
                                                                                              {
                                                                                                  item.model_name
                                                                                              }
                                                                                          </span>
                                                                                      ),
                                                                                      value: item.model_id,
                                                                                  };
                                                                              },
                                                                          ),
                                                                          // [
                                                                          //     { label: <span>Jack</span>, value: 'Jack' },
                                                                          //     { label: <span>Lucy</span>, value: 'Lucy' },
                                                                          // ],
                                                                      };
                                                                  },
                                                              )

                                                              // [
                                                              //     {
                                                              //         label: <span>man2ager</span>,
                                                              //         options: [
                                                              //             { label: <span>Jack</span>, value: 'Jack' },
                                                              //             { label: <span>Lucy</span>, value: 'Lucy' },
                                                              //         ],
                                                              //     },
                                                              //     {
                                                              //         label: <span>engineer</span>,
                                                              //         title: 'engineer',
                                                              //         options: [
                                                              //             { label: <span>Chloe</span>, value: 'Chloe' },
                                                              //             { label: <span>Lucas</span>, value: 'Lucas' },
                                                              //         ],
                                                              //     },
                                                              // ]
                                                          }
                                                      />
                                                  </div>
                                              );
                                          })
                                        : null}
                                </div>
                            }
                            // onConfirm={handleOk}
                            // okButtonProps={{ loading: confirmLoading }}
                            // onCancel={handleCancel}
                        >
                            <Button icon={<SettingOutlined />}>
                                {intl.formatMessage({
                                    id: 'user.systemModelSettings',
                                    defaultMessage: '',
                                })}
                            </Button>
                        </Popconfirm>
                    </div>
                </div>
                <div style={{ height: '520px', overflowY: 'scroll' }}>
                    {suppliers
                        ? suppliers.map((item: any, index: any) => {
                              return (
                                  <div
                                      key={index}
                                      className="w-full bg-[#F5F5F5] rounded mb-3.5"
                                      style={{ border: '1px solid #EEE' }}
                                  >
                                      <div className="flex  justify-between mb-3.5 mx-3.5 mt-5">
                                          <div className="">
                                              <div className="text-base font-medium text-[#213044]  mb-3.5">
                                                  {item.supplier_name}
                                              </div>
                                              <div className="flex items-center">
                                                  {uniqueTypeSet(item.models).map(
                                                      (item: any, index: any) => {
                                                          return (
                                                              <Text keyboard key={index}>
                                                                  {item.model_name}
                                                              </Text>
                                                          );
                                                      },
                                                  )}
                                              </div>
                                          </div>
                                          <div
                                              className=" w-32 rounded bg-[#FCFCFC] py-1.5 px-2.5"
                                              style={{
                                                  border: '1px solid #EBEBEB',
                                                  boxSizing: 'border-box',
                                              }}
                                          >
                                              <div className="flex justify-between mb-1">
                                                  <div>Api-KEY </div>
                                                  <div>
                                                      <Badge
                                                          color={
                                                              item.authorization == 1
                                                                  ? '#1FDC27'
                                                                  : '#d8d8d8'
                                                          }
                                                      />
                                                  </div>
                                              </div>
                                              <Button
                                                  icon={<SettingOutlined />}
                                                  size="small"
                                                  className="w-full"
                                                  onClick={() => {
                                                      handleOpenModal(item);
                                                  }}
                                              >
                                                  {intl.formatMessage({
                                                      id: 'user.settings',
                                                      defaultMessage: '',
                                                  })}
                                              </Button>
                                          </div>
                                      </div>
                                      <div className="w-full bg-[#FCFCFC] px-3.5 py-2.5">
                                          <div
                                              className="text-xs font-medium text-[#6C7280] cursor-pointer"
                                              onClick={() => {
                                                  ChangePulldown(index);
                                              }}
                                          >
                                              {item.models.length}
                                              {intl.formatMessage({
                                                  id: 'user.numberOfModels',
                                                  defaultMessage: '',
                                              })}
                                              {
                                                  // pulldownlistid == index + 1 ? <CaretUpOutlined /> : <CaretDownOutlined />
                                                  item.listopen ? (
                                                      <CaretUpOutlined />
                                                  ) : (
                                                      <CaretDownOutlined />
                                                  )
                                              }
                                          </div>
                                          <div
                                              className="bg-[#fff]  py-3.5 box-border rounded mt-2.5"
                                              style={{ display: item.listopen ? 'block' : 'none' }}
                                          >
                                              {item.models.map((item: any, index: any) => {
                                                  return (
                                                      <div
                                                          key={index}
                                                          className="flex justify-between items-center px-2.5 py-2.5 hover:bg-[#F7F7F7]"
                                                      >
                                                          <div>
                                                              <span className="mr-2.5">
                                                                  {item.model_name}
                                                              </span>
                                                              <Text keyboard key={index}>
                                                                  {/* {
                                                                    Modeltypedata.filter((value: any, index: any) => {
                                                                        return item.model_type == value.id
                                                                    })[0].name
                                                                } */}
                                                                  {item.model_type_name}
                                                              </Text>
                                                          </div>
                                                          <div>
                                                              <Badge
                                                                  color={
                                                                      item.model_default_used == 1
                                                                          ? '#1FDC27'
                                                                          : '#d8d8d8'
                                                                  }
                                                              />
                                                          </div>
                                                      </div>
                                                  );
                                              })}
                                          </div>
                                      </div>
                                  </div>
                              );
                          })
                        : null}
                </div>
            </Modal>

            <Modal
                width={500}
                // `${intl.formatMessage({id: 'user.name',defaultMessage: ''})}${modalsingledata ? modalsingledata.supplier_name : ''}`
                title={modalsingledata?.supplier_name}
                open={isModalOpen2}
                okText={intl.formatMessage({ id: 'user.save', defaultMessage: '' })}
                // footer={false}
                onOk={() => handleSave()}
                onCancel={() => setIsModalOpen2(false)}
            >
                <div>
                    {modalsingledata
                        ? modalsingledata.supplier_config.map((item: any, index: any) => {
                              return (
                                  <div className="mb-5">
                                      <div className="font-normal text-gray-600 mb-2.5">
                                          <Callword name={item.key} title={item.description} />
                                      </div>
                                      {item.type == 'selectable' ? (
                                          <div>
                                              <Select
                                                  defaultValue={item.value}
                                                  style={{ width: 460 }}
                                                  variant="filled"
                                                  onChange={e => InputChange(e, index)}
                                                  options={item.options.map(
                                                      (item: any, index: any) => {
                                                          return {
                                                              value: item.value,
                                                              label: item.display,
                                                          };
                                                      },
                                                  )}
                                              />
                                          </div>
                                      ) : item.type == 'int' || item.type == 'float' ? (
                                          <div>
                                              <InputNumber
                                                  min={0}
                                                  // max={999999999999999999999}
                                                  defaultValue={3}
                                                  variant="filled"
                                                  style={{ width: 460 }}
                                                  value={
                                                      item.value ? item.value : item.default_value
                                                  }
                                                  onChange={e => {
                                                      InputChange(e, index);
                                                  }}
                                              />
                                          </div>
                                      ) : (
                                          <div>
                                              {item.secret ? (
                                                  // <Input.Password
                                                  //     placeholder={item.description}
                                                  //     onChange={(e) => { InputChange(e.target.value, index) }}
                                                  //     value={item.value ? item.value : item.default_value}
                                                  //     style={{ width: 460 }}
                                                  //     variant="filled"
                                                  // />
                                                  <Input
                                                      placeholder={item.description}
                                                      style={{ width: 460 }}
                                                      variant="filled"
                                                      onChange={e => {
                                                          InputChange(e.target.value, index);
                                                      }}
                                                      value={
                                                          item.value
                                                              ? item.value
                                                              : item.default_value
                                                      }
                                                  />
                                              ) : (
                                                  <div>
                                                      <Input
                                                          placeholder={item.description}
                                                          style={{ width: 460 }}
                                                          variant="filled"
                                                          onChange={e => {
                                                              InputChange(e.target.value, index);
                                                          }}
                                                          value={
                                                              item.value
                                                                  ? item.value
                                                                  : item.default_value
                                                          }
                                                      />
                                                  </div>
                                              )}
                                          </div>
                                      )}
                                  </div>
                              );
                          })
                        : null}
                </div>
            </Modal>
        </div>
    );
};
export default ModelSetup;
