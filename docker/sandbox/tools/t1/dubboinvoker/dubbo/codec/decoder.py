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

from datetime import datetime
from struct import unpack

from dubbo.common.exceptions import HessianTypeError, DubboException, DubboResponseException
from dubbo.common.constants import response_status_message

functions = {}


def ranges(*defined_ranges):
    """
    根据hessian协议，把处理方法交给其定义好的范围
    :param defined_ranges:
    :return:
    """

    def decorator(func):
        # 遍历所有的范围
        for defined_range in defined_ranges:
            if isinstance(defined_range, (tuple, list)):
                if not len(defined_range) == 2:
                    raise ValueError('Invalid range {}'.format(defined_range))
                nums = range(defined_range[0], defined_range[1] + 1)
                for num in nums:
                    functions[num] = func
            elif isinstance(defined_range, int):
                functions[defined_range] = func
            else:
                raise ValueError('Defined value {} illegal'.format(defined_ranges))

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)  # 原始方法正常执行

        return wrapper

    return decorator


class Response(object):
    """
    A class for parsing dubbo response body.
    All types can be parsed:
    * byte
    * boolean
    * int
    * long
    * double
    * string
    * object
    * class
    * generic type
    * list
    * map
    * date
    * null
    """

    def __init__(self, data):
        self.__data = data  # data是字节数组
        self.__index = 0
        self.types = []
        self.objects = []
        # 对于一个类来说，有path的地方就应该有field_name
        self.paths = []
        self.field_names = []

    def get_byte(self):
        """
        获取到头部的字节数据，只是获取并不移动指针
        :return:
        """
        return self.__data[self.__index]

    def length(self):
        """
        当前的字节长度
        :return:
        """
        return len(self.__data) - self.__index

    def read_byte(self):
        """
        读取一个字节并向后移动一位指针
        :return:
        """
        if self.__index >= len(self.__data):
            raise ValueError('Index {} bigger than data length {}'.format(self.__index, len(self.__data)))
        value = self.__data[self.__index]
        self.__index += 1
        return value

    def read_bytes(self, num):
        """
        读取n个字节并向后移动n位指针
        :param num:
        :return:
        """
        value = self.__data[self.__index:self.__index + num]
        self.__index += num
        return value

    @ranges(ord('T'), ord('F'))
    def read_boolean(self):
        """
        读取一个布尔类型
        :return:
        """
        value = self.read_byte()
        if value == ord('T'):
            return True
        elif value == ord('F'):
            return False
        else:
            raise HessianTypeError('illegal boolean value: {0}'.format(value))

    @ranges((0x80, 0xd7), ord('I'))
    def read_int(self):
        """
        读取一个整型数据
        :return:
        """
        value = self.read_byte()
        if 0x80 <= value <= 0xbf:
            result = value - 0x90
        elif 0xc0 <= value <= 0xcf:
            i = (value - 0xc8) << 8
            i |= self.read_byte()
            result = i
        elif 0xd0 <= value <= 0xd7:
            i = (value - 0xd4) << 16
            i |= self.read_byte() << 8
            i |= self.read_byte()
            result = i
        else:
            result = unpack('!i', self.read_bytes(4))[0]
        return result

    @ranges((0x5b, 0x5f), ord('D'))
    def read_double(self):
        """
        读取一个浮点类型
        :return:
        """
        value = self.read_byte()
        if value == 0x5b:
            result = 0.0
        elif value == 0x5c:
            result = 1.0
        elif value == 0x5d:
            result = float(unpack('!b', self.read_bytes(1))[0])
        elif value == 0x5e:
            result = float(unpack('!h', self.read_bytes(2))[0])
        elif value == 0x5f:
            result = float(unpack('!i', self.read_bytes(4))[0]) * 0.001
        elif value == ord('D'):
            result = float(unpack('!d', self.read_bytes(8))[0])
        else:
            raise HessianTypeError('{0} is not a float'.format(value))
        return result

    def _read_utf(self, length):
        """
        读取n个字符
        :param length:
        :return:
        """
        value = ''
        for i in range(length):
            ch = self.read_byte()
            if ch < 0x80:
                value += chr(ch)
            elif (ch & 0xe0) == 0xc0:
                ch1 = self.read_byte()
                value += chr(((ch & 0x1f) << 6) + (ch1 & 0x3f))
            elif (ch & 0xf0) == 0xe0:
                ch1 = self.read_byte()
                ch2 = self.read_byte()
                value += chr(((ch & 0x0f) << 12) + ((ch1 & 0x3f) << 6) + (ch2 & 0x3f))
            else:
                raise ValueError('Can\'t parse utf-8 char {}'.format(ch))
        return value.encode('utf-8')  # 将unicode转化为str类型

    @ranges((0x00, 0x1f), (0x30, 0x33), 0x52, ord('S'))
    def read_string(self):
        """
        读取一个字符串
        :return:
        """
        value = self.read_byte()
        string = ''
        while value == 'R':
            length = unpack('!h', self.read_bytes(2))[0]
            string += self._read_utf(length)
            value = self.read_byte()

        if value == ord('S'):
            length = unpack('!h', self.read_bytes(2))[0]
        elif 0x00 <= value <= 0x1f:
            length = value
        else:
            length = (value - 0x30) << 8 | self.read_byte()

        string += self._read_utf(length).decode('utf-8')
        return string

    @ranges((0x60, 0x6f), ord('O'))
    def read_object(self):
        """
        读取一个对象
        :return:
        """
        result = {}
        self.objects.append(result)
        value = self.read_byte()
        if 0x60 <= value <= 0x6f:
            ref = value - 0x60
        else:
            ref = self.read_int()
        field_names = self.field_names[ref]
        for field_name in field_names:
            field_value = self.read_next()
            result[field_name] = field_value

        path = self.paths[ref]
        if path == 'java.math.BigDecimal':
            result = float(result['value']) or 0
            self.objects[-1] = result
        elif path == 'java.math.BigInteger':
            result = int(result['value'])
            self.objects[-1] = result

        return result

    @ranges(ord('C'))
    def read_class(self):
        """
        读取一个类的类属性，主要是类名和类中的变量名
        :return:
        """
        self.read_byte()
        path = self.read_string()
        self.paths.append(path)

        field_length = self.read_int()
        field_names = []
        for i in range(field_length):
            field_names.append(self.read_string())
        self.field_names.append(field_names)
        return self.read_object()

    def read_type(self):
        """
        type代表了list或者map中泛型的类型，在Python中此类型无意义
        :return:
        """
        _type = self.read_next()
        if isinstance(_type, int):
            return self.types[_type]
        elif isinstance(_type, str):
            self.types.append(_type)
            return _type
        else:
            raise HessianTypeError('Unknown _type type for value: {0}'.format(_type))

    @ranges((0x70, 0x7f), (0x55, 0x58))
    def read_list(self):
        """
        读取一个列表
        :return:
        """
        result = []
        self.objects.append(result)
        value = self.read_byte()
        # 固定长度的有类型短小列表
        if 0x70 <= value <= 0x77:
            _type = self.read_type()  # type对于Python来说没有用处
            length = value - 0x70
            for i in range(length):
                result.append(self.read_next())
        # 固定长度的无类型短小列表
        elif 0x78 <= value <= 0x7f:
            length = value - 0x78
            for i in range(length):
                result.append(self.read_next())
        # 固定长度的有类型列表
        elif value == 0x56:
            _type = self.read_type()
            length = self.read_int()
            for i in range(length):
                result.append(self.read_next())
        # 固定长度的无类型列表
        elif value == 0x58:
            length = self.read_int()
            for i in range(length):
                result.append(self.read_next())
        # 可变长度的有类型列表
        elif value == 0x55:
            _type = self.read_type()
        # 可变长度的无类型列表
        elif value == 0x57:
            pass
        return result

    @ranges((0xd8, 0xff), (0x38, 0x3f), 0x59, ord('L'))
    def read_long(self):
        """
        读取一个long类型的数字
        :return:
        """
        value = self.read_byte()
        if 0xd8 <= value <= 0xef:
            result = value - 0xe0
        elif 0xf0 <= value <= 0xff:
            result = ((value - 0xf8) << 8) | self.read_byte()
        elif 0x38 <= value <= 0x3f:
            i = (value - 0x3c) << 16
            i |= self.read_byte() << 8
            i |= self.read_byte()
            result = i
        elif value == 0x59:
            result = unpack('!i', self.read_bytes(4))[0]
        elif value == ord('L'):
            result = unpack('!q', self.read_bytes(8))[0]
        else:
            raise HessianTypeError('{0} is not long type'.format(value))
        return result

    @ranges(ord('N'))
    def read_null(self):
        """
        读取一个None
        :return:
        """
        value = self.read_byte()
        if value == ord('N'):
            return None
        else:
            raise HessianTypeError('{0} is not null'.format(value))

    @ranges(ord('H'), ord('M'))
    def read_map(self):
        """
        读取一个dict
        :return:
        """
        value = self.read_byte()

        if value == ord('M') or value == ord('H'):
            result = {}
            self.objects.append(result)
            while self.get_byte() != ord('Z'):
                key = self.read_next()
                value = self.read_next()
                result[key] = value
            self.read_byte()  # 干掉最后一个'Z'字符
            return result
        else:
            raise HessianTypeError('{0} is not a map.'.format(value))

    @ranges(0x4a, 0x4b)
    def read_date(self):
        """
        读取一个date类型的值
        :return:
        """
        value = self.read_byte()
        if value == 0x4a:
            timestamp = unpack('!q', self.read_bytes(8))[0]
        elif value == 0x4b:
            timestamp = unpack('!i', self.read_bytes(4))[0]
            timestamp *= 60000
        else:
            raise HessianTypeError('{0} is not date type'.format(value))
        return datetime.fromtimestamp(timestamp / 1e3).strftime("%Y-%m-%dT%H:%M:%S.%f+0800")

    @ranges(0x51)
    def read_ref(self):
        """
        读取一个已知的object/list/map
        :return:
        """
        self.read_byte()  # 干掉0x51
        ref_id = self.read_int()
        return self.objects[ref_id]

    def read_next(self):
        """
        读取下一个变量，自动识别变量类型
        :return:
        """
        data_type = self.get_byte()
        func = functions[data_type]
        return func(self)

    def read_error(self):
        """
        解析Java的错误信息，因为需要知道错误的类型，所以需要单独处理
        :return:
        """
        self.read_byte()
        error_type = self.read_string()
        self.paths.append(error_type)

        field_length = self.read_int()
        field_names = []
        for i in range(field_length):
            field_names.append(self.read_string())
        self.field_names.append(field_names)

        error = self.read_object()
        error['cause'] = error_type
        return error

    def __repr__(self):
        return str(self.__data)


def parse_response_head(response_head):
    """
    对响应头部的字节做解析
    :param response_head:
    :return:
    """
    # Magic number
    if not (response_head[0] == 0xda and response_head[1] == 0xbb):
        raise DubboException('illegal response')

    # 第三位为1表示这是一个心跳包
    if response_head[2] & 0x20 == 0x20:
        if response_head[2] & 0x80 == 0x80:
            # 第一位为1，一个心跳请求的包
            heartbeat = 2
        else:
            # 第一位为0，一个心跳响应的包
            heartbeat = 1
            response_status = response_head[3]
            if response_status != 20:
                raise DubboException(response_status_message[response_status])
    else:
        heartbeat = 0
        response_status = response_head[3]
        if response_status != 20:
            raise DubboResponseException(response_status_message[response_status])
    return heartbeat, unpack('!i', response_head[12:])[0]


if __name__ == '__main__':
    pass
