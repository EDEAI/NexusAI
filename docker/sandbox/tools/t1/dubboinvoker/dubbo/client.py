# -*- coding: utf-8 -*-
"""
/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
"""

import logging
import time
from typing import Any, List, Optional

from dubbo.common.exceptions import RegisterException
from dubbo.connection.connections import connection_pool

logger = logging.getLogger('python-dubbo')

class DubboClient(object):
    """
    用于实现dubbo调用的客户端
    """

    def __init__(self, interface, version='', dubbo_version='2.4.10', host=None):
        """
        :param interface: 接口名，例如：com.qianmi.pc.es.api.EsProductQueryProvider
        :param version: 接口的版本号，例如：1.0.0，默认为1.0.0
        :param dubbo_version: dubbo的版本号，默认为2.4.10
        :param host: 远程主机地址，用于绕过zookeeper进行直连，例如：172.21.4.98:20882
        """
        if not host:
            raise RegisterException('host至少需要填入一个')

        logger.debug('Created client, interface={}, version={}'.format(interface, version))

        self.__interface = interface
        self.__version = version
        self.__dubbo_version = dubbo_version

        self.__host = host

    def call(self, method, args=(), param_types=None, timeout=None):
        """
        执行远程调用
        :param method: 远程调用的方法名
        :param args: 方法参数
                    1. 对于没有参数的方法，此参数不填；
                    2. 对于只有一个参数的方法，直接填入该参数；
                    3. 对于有多个参数的方法，传入一个包含了所有参数的列表；
                    4. 当前方法参数支持以下类型：
                        * bool
                        * int
                        * long
                        * float
                        * double
                        * java.lang.String
                        * java.lang.Object
        :param param_types: 参数类型列表，如['int', 'java.lang.String']
        :param timeout: 请求超时时间（秒），不设置则不会超时
        :return:
        """
        if not isinstance(args, (list, tuple)):
            args = [args]

        host = self.__host

        request_param = {
            'dubbo_version': self.__dubbo_version,
            'version': '',
            'path': self.__interface,
            'method': method,
            'arguments': args,
            'context': None
        }
        
        # 如果提供了参数类型信息，添加到请求参数中
        if param_types:
            request_param['parameter_types'] = param_types

        logger.debug('Start request, host={}, params={}'.format(host, request_param))
        start_time = time.time()
        result = connection_pool.get(host, request_param, timeout)
        cost_time = int((time.time() - start_time) * 1000)
        logger.debug('Finish request, host={}, params={}'.format(host, request_param))
        logger.debug('Request invoked, host={}, params={}, result={}, cost={}ms, timeout={}s'.format(
            host, request_param, result, cost_time, timeout))
        return result
