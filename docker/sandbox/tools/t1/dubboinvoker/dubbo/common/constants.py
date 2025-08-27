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

from dubbo.common.util import num_2_byte_list

# 服务端的响应码
response_status_message = {
    20: 'OK',
    30: 'CLIENT_TIMEOUT',
    31: 'SERVER_TIMEOUT',
    40: 'BAD_REQUEST',
    50: 'BAD_RESPONSE',
    60: 'SERVICE_NOT_FOUND',
    70: 'SERVICE_ERROR',
    80: 'SERVER_ERROR',
    90: 'CLIENT_ERROR'
}

# 32位整型的最大值
MAX_INT_32 = 2147483647
# 32位整型的最小值
MIN_INT_32 = -2147483648

# MAGIC_NUM(2) + FLAG(1) + STATUS(1)
DEFAULT_REQUEST_META = num_2_byte_list(0xdabbc200)

# 客户端对服务端发送的心跳的请求的头部
CLI_HEARTBEAT_REQ_HEAD = num_2_byte_list(0xdabbe2) + [0]
# 客户端对服务端发送的心跳的响应的头部
CLI_HEARTBEAT_RES_HEAD = num_2_byte_list(0xdabb2214)
# 心跳尾部
CLI_HEARTBEAT_TAIL = [0, 0, 0, 1] + num_2_byte_list(0x4e)

DUBBO_ZK_PROVIDERS = '/dubbo/{}/providers'
DUBBO_ZK_CONSUMERS = '/dubbo/{}/consumers'
DUBBO_ZK_CONFIGURATORS = '/dubbo/{}/configurators'

# 客户端检测与远程主机的连接是否超时的间隔
TIMEOUT_CHECK_INTERVAL = 0.03  # 30ms
# 连接最长允许的空闲时间
TIMEOUT_IDLE = 60
# 连接允许的最多的超时次数
TIMEOUT_MAX_TIMES = 3

# 数据的头部大小为16个字节
# 读取的数据类型：1 head; 2 error_body; 3 common_body;
# 头部信息不存在invoke_id，所以为None
DEFAULT_READ_PARAMS = 16, 1, None
