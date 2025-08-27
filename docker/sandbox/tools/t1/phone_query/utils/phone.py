import phonenumbers
from phonenumbers import carrier, geocoder, PhoneNumberMatcher, PhoneNumberType, number_type

from config.constant import DEFAULT_LANG, DEFAULT_REGION

class PhoneNumberUtils:
    """电话号码处理工具类（支持国际/国内号码）"""

    @staticmethod
    def parse(phone_str: str, default_region=DEFAULT_REGION) -> phonenumbers.PhoneNumber:
        """
        解析电话号码（自动处理带/不带国际区号的情况）
        :param phone_str: 原始电话号码字符串
        :param default_region: 默认国家/地区代码（如CN表示中国）
        :return: PhoneNumber对象
        """
        try:
            return phonenumbers.parse(phone_str, default_region)
        except phonenumbers.NumberParseException as e:
            raise ValueError(f"Error: {str(e)}") from e

    @staticmethod
    def validate(phone_str: str, default_region=DEFAULT_REGION) -> bool:
        """
        验证电话号码有效性
        :return: True/False
        """
        try:
            num = PhoneNumberUtils.parse(phone_str, default_region)
            return phonenumbers.is_valid_number(num)
        except ValueError:
            return False

    @staticmethod
    def extract_phone_numbers(text: str, default_region=DEFAULT_REGION) -> list:
        """从文本中提取电话号码（支持国际/国内格式）如果没有地区编号，默认为DEFAULT_REGION"""
        try:
            matches = PhoneNumberMatcher(text, default_region)
            results = []
            for match in matches:
                number = phonenumbers.format_number(
                    match.number,
                    phonenumbers.PhoneNumberFormat.E164
                )
                results.append(number)
            return results
        except ValueError:
            return []

    @staticmethod
    def batch_validate(phone_list: list, default_region=DEFAULT_REGION) -> dict:
        """
        批量验证电话号码
        :return: {号码: 有效性} 的字典
        """
        results = {}
        for num in phone_list:
            results[num] = PhoneNumberUtils.validate(num, default_region)
        return results

    @staticmethod
    def get_location_info(phone_str: str, lang=DEFAULT_LANG) -> dict:
        """
        获取归属地、运营商、类型信息
        :param phone_str: 电话号码
        :param lang: 语言代码（zh/en等）
        :return: 包含归属地、运营商、时区的字典
        """
        try:
            num = PhoneNumberUtils.parse(phone_str)
            return {
                "country": geocoder.country_name_for_number(num, lang),
                "location": geocoder.description_for_number(num, lang),
                "operator": carrier.name_for_number(num, lang) or 'UNKNOWN',
                # "zone": timezone.time_zones_for_number(num),
                "type": PhoneNumberType.to_string(number_type(num))
            }
        except ValueError:
            return {"Error": "Invalid number"}