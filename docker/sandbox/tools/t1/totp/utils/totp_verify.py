import pyotp
import time

def verify_totp(secret_key, totp_code, offset=5, strict=False):
    """
    Verify one-time password based on TOTP.

    :param secret_key: Secret key or provisioned URL used to generate TOTP
    :param totp_code: Dynamic token submitted by user
    :param offset: Seconds allowed for early or delayed verification
    :param strict: Whether to use strict validation (only return success when exact match)
    :return: Dictionary containing:
            - 'status': 'success' or 'fail'
            - 'detail': Internal message (not for end users)
    """
    try:
        # 检测是否为 provisioned URL
        if secret_key.startswith('otpauth://'):
            totp = pyotp.parse_uri(secret_key)
        else:
            totp = pyotp.TOTP(secret_key)
            
        current_time = time.time()

        if totp.verify(totp_code):  # Exact time verification
            return {'status': 'success', 'detail': 'Token is valid'}

        # Offset verification
        early_valid = totp.verify(totp_code, for_time=current_time + offset)
        late_valid = totp.verify(totp_code, for_time=current_time - offset)
        off_time_valid = early_valid or late_valid

        detail_message = (
            f"Token is valid but not on time. "
            f"{'Early' if early_valid else 'Late'} within {offset} seconds"
            if off_time_valid else
            "Token is invalid"
        )

        if strict:
            return {'status': 'fail', 'dev_detail': detail_message}
        else:
            return (
                {'status': 'success', 'detail': detail_message}
                if off_time_valid
                else {'status': 'fail', 'detail': detail_message}
            )
    except Exception as e:
        return {'status': 'fail', 'detail': f'Verification error: {str(e)}'}