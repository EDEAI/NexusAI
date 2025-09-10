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


class DubboException(RuntimeError):
    pass


class DubboResponseException(DubboException):
    """
    dubbo服务端向客户端发送响应时所产生的异常
    """
    pass


class HessianTypeError(DubboException):
    """
    Hessian解码的时候发生了解析类型错误
    """
    pass


class RegisterException(DubboException):
    """
    与注册中心相关的异常
    """
    pass


class DubboRequestTimeoutException(DubboException):
    """
    dubbo请求超时异常
    """
    pass
