from phonenumbers import PhoneNumberType

# default lang：en, not zh ja pt
DEFAULT_LANG = 'en'

# default region code，if not contain region code，set default
DEFAULT_REGION = 'CN'

# zh number type bak
TYPE_MAP = {
    PhoneNumberType.FIXED_LINE: "固定电话",
    PhoneNumberType.MOBILE: "移动电话",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "固话或移动",
    PhoneNumberType.TOLL_FREE: "免费电话",
    PhoneNumberType.PREMIUM_RATE: "付费电话",
    PhoneNumberType.SHARED_COST: "共享资费",
    PhoneNumberType.VOIP: "网络电话",
    PhoneNumberType.PERSONAL_NUMBER: "个人号码",
    PhoneNumberType.PAGER: "寻呼机",
    PhoneNumberType.UAN: "通用接入号",
    PhoneNumberType.VOICEMAIL: "语音信箱",
    PhoneNumberType.UNKNOWN: "未知类型",
}