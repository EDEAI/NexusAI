import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import logging
import os
# import sys
# from dotenv import load_dotenv
from config import settings

# Add project root directory to Python path
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(os.path.dirname(current_dir))
# sys.path.insert(0, project_root)

# Load environment variables
# load_dotenv(os.path.join(project_root, '.env'))

def get_smtp_config():
    """
    Get SMTP configuration from environment variables
    :return: SMTP configuration dictionary
    """
    return {
        'smtp_server': settings.SMTP_SERVER,
        'smtp_port': settings.SMTP_PORT,
        'username': settings.SMTP_USERNAME,
        'password': settings.SMTP_PASSWORD,
        'use_tls': settings.SMTP_USE_TLS,
        'timeout': settings.SMTP_TIMEOUT
    }


class SMTPEmailSender:
    """SMTP email sender class"""
    
    def __init__(self, smtp_config=None):
        """
        Initialize SMTP email sender
        :param smtp_config: SMTP configuration dictionary, if None then get from environment variables
        """
        if smtp_config is None:
            smtp_config = get_smtp_config()
        
        self.smtp_server = smtp_config.get('smtp_server')
        self.smtp_port = smtp_config.get('smtp_port', 587)
        self.username = smtp_config.get('username')
        self.password = smtp_config.get('password')
        self.use_tls = smtp_config.get('use_tls', True)
        self.timeout = smtp_config.get('timeout', 30)
        
    def send_text_email(self, to_email, subject, content, cc_emails=None, bcc_emails=None):
        """
        Send plain text email
        :param to_email: Recipient email (string or list)
        :param subject: Email subject
        :param content: Email content
        :param cc_emails: CC email list
        :param bcc_emails: BCC email list
        :return: (success: bool, message: str)
        """
        return self._send_email(to_email, subject, content, 'plain', cc_emails, bcc_emails)
    
    def send_html_email(self, to_email, subject, html_content, cc_emails=None, bcc_emails=None):
        """
        Send HTML email
        :param to_email: Recipient email (string or list)
        :param subject: Email subject
        :param html_content: HTML email content
        :param cc_emails: CC email list
        :param bcc_emails: BCC email list
        :return: (success: bool, message: str)
        """
        return self._send_email(to_email, subject, html_content, 'html', cc_emails, bcc_emails)
    
    def send_verification_code(self, to_email, code, expire_minutes=10):
        """
        Send verification code email
        :param to_email: Recipient email
        :param code: Verification code
        :param expire_minutes: Expiration time (minutes)
        :return: (success: bool, message: str)
        """
        subject = "Email Verification Code"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; text-align: center;">Email Verification</h2>
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p>Hello,</p>
                    <p>Your verification code is:</p>
                    <div style="text-align: center; margin: 20px 0;">
                        <span style="font-size: 24px; font-weight: bold; color: #e74c3c; background-color: #fff; padding: 10px 20px; border: 2px dashed #e74c3c; border-radius: 5px;">{code}</span>
                    </div>
                    <p>The verification code is valid for <strong>{expire_minutes} minutes</strong>, please use it promptly.</p>
                    <p style="color: #7f8c8d; font-size: 14px;">If this is not your operation, please ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return self.send_html_email(to_email, subject, html_content)
    
    def send_password_reset_code(self, to_email, code, expire_minutes=15):
        """
        Send password reset verification code email
        :param to_email: Recipient email
        :param code: Password reset verification code
        :param expire_minutes: Expiration time (minutes)
        :return: (success: bool, message: str)
        """
        subject = "Password Reset Verification Code"
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Microsoft YaHei', Arial, sans-serif; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 300;">🔐 Password Reset</h1>
                    <p style="color: #e8eaf6; margin: 10px 0 0 0; font-size: 16px;">Password Reset Verification</p>
                </div>
                
                <!-- Main Content -->
                <div style="padding: 40px 30px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #ff6b6b, #ee5a24); border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 36px;">
                            🔑
                        </div>
                        <h2 style="color: #2c3e50; margin: 0; font-size: 24px; font-weight: 400;">Password Reset Request</h2>
                    </div>
                    
                    <div style="background-color: #f8f9ff; border-left: 4px solid #667eea; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                        <p style="margin: 0 0 15px 0; color: #34495e; font-size: 16px; line-height: 1.6;">
                            Hello, we have received your password reset request. Please use the following verification code to reset your password:
                        </p>
                    </div>
                    
                    <!-- Verification Code Area -->
                    <div style="text-align: center; margin: 35px 0;">
                        <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 12px; display: inline-block; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
                            <p style="color: #ffffff; margin: 0 0 10px 0; font-size: 14px; opacity: 0.9;">Verification Code</p>
                            <div style="background-color: #ffffff; padding: 15px 25px; border-radius: 8px; margin: 0;">
                                <span style="font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 8px; font-family: 'Courier New', monospace;">{code}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Important Notice -->
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 25px 0;">
                        <div style="display: flex; align-items: flex-start;">
                            <div style="color: #f39c12; font-size: 20px; margin-right: 12px;">⚠️</div>
                            <div>
                                <h3 style="color: #856404; margin: 0 0 10px 0; font-size: 16px;">Important Notice</h3>
                                <ul style="color: #856404; margin: 0; padding-left: 20px; font-size: 14px; line-height: 1.6;">
                                    <li>Verification code is valid for <strong>{expire_minutes} minutes</strong></li>
                                    <li>Do not share the verification code with others</li>
                                    <li>If this is not your operation, please contact customer service immediately</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Operation Steps -->
                    <div style="margin: 30px 0;">
                        <h3 style="color: #2c3e50; font-size: 18px; margin-bottom: 15px;">📋 Operation Steps</h3>
                        <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px;">
                            <ol style="color: #495057; margin: 0; padding-left: 20px; line-height: 1.8;">
                                <li>Return to the password reset page</li>
                                <li>Enter the verification code above</li>
                                <li>Set your new password</li>
                                <li>Complete password reset</li>
                            </ol>
                        </div>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8f9fa; padding: 25px 30px; border-top: 1px solid #e9ecef;">
                    <div style="text-align: center;">
                        <p style="color: #6c757d; margin: 0 0 10px 0; font-size: 14px;">
                            This email is automatically sent by the system, please do not reply
                        </p>
                        <p style="color: #adb5bd; margin: 0; font-size: 12px;">
                            © 2025 NexusAI. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Email Bottom Spacing -->
            <div style="height: 50px;"></div>
        </body>
        </html>
        """
        return self.send_html_email(to_email, subject, html_content)
    
    def send_password_reset_code_simple(self, to_email, code, expire_minutes=15):
        """
        Send simple version password reset verification code email
        :param to_email: Recipient email
        :param code: Password reset verification code
        :param expire_minutes: Expiration time (minutes)
        :return: (success: bool, message: str)
        """
        subject = "Password Reset Verification Code"
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
        </head>
        <body style="margin: 0; padding: 20px; font-family: 'Microsoft YaHei', Arial, sans-serif; background-color: #f5f7fa; color: #333;">
            <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden;">
                
                <!-- Header -->
                <div style="background-color: #4a90e2; color: white; padding: 25px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px; font-weight: normal;">🔐 Password Reset</h1>
                </div>
                
                <!-- Content Area -->
                <div style="padding: 30px;">
                    <p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
                        Hello, we have received your password reset request.
                    </p>
                    
                    <p style="font-size: 16px; line-height: 1.6; margin-bottom: 25px;">
                        Please use the following verification code to complete the password reset:
                    </p>
                    
                    <!-- Verification Code -->
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="background-color: #f8f9fa; border: 2px dashed #4a90e2; border-radius: 8px; padding: 20px; display: inline-block;">
                            <span style="font-size: 28px; font-weight: bold; color: #4a90e2; letter-spacing: 4px; font-family: 'Courier New', monospace;">{code}</span>
                        </div>
                    </div>
                    
                    <!-- Notice Information -->
                    <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 25px 0; border-radius: 4px;">
                        <p style="margin: 0; font-size: 14px; color: #856404;">
                            ⚠️ The verification code is valid for <strong>{expire_minutes} minutes</strong>, please use it promptly. If this is not your operation, please ignore this email.
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return self.send_html_email(to_email, subject, html_content)
    
    def send_user_invitation(self, to_email, invitation_url, team_name=None, inviter_name=None):
        """
        Send user invitation email
        :param to_email: Recipient email
        :param invitation_url: Invitation URL link
        :param team_name: Team name (optional)
        :param inviter_name: Inviter name (optional)
        :return: (success: bool, message: str)
        """
        subject = "You're Invited to Join NexusAI"
        
        # Set default values if not provided
        team_display = f" to {team_name}" if team_name else ""
        inviter_display = f" by {inviter_name}" if inviter_name else ""
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Invitation to Join NexusAI</title>
        </head>
        <body style="margin: 0; padding: 20px; font-family: 'Microsoft YaHei', Arial, sans-serif; background-color: #f5f7fa; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden;">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px; font-weight: 300;">You're Invited!</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Join NexusAI{team_display}</p>
                </div>
                
                <!-- Content Area -->
                <div style="padding: 40px 30px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h2 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 24px; font-weight: 400;">Welcome to NexusAI</h2>
                        <p style="color: #7f8c8d; font-size: 16px; line-height: 1.6; margin: 0;">
                            You have been invited{inviter_display} to join our AI-powered platform.
                        </p>
                    </div>
                    
                    <!-- Invitation Details -->
                    <div style="background-color: #f8f9ff; border-left: 4px solid #667eea; padding: 25px; margin: 30px 0; border-radius: 0 8px 8px 0;">
                        <h3 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 18px;">🚀 What's Next?</h3>
                        <ul style="color: #34495e; margin: 0; padding-left: 20px; font-size: 15px; line-height: 1.8;">
                            <li>Click the invitation link below to get started</li>
                            <li>Create your account or sign in if you already have one</li>
                            <li>Start exploring powerful AI tools and features</li>
                            <li>Collaborate with your team members</li>
                        </ul>
                    </div>
                    
                    <!-- Invitation Button -->
                    <div style="text-align: center; margin: 40px 0;">
                        <a href="{invitation_url}" style="display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); color: #ffffff; text-decoration: none; padding: 16px 40px; border-radius: 50px; font-size: 16px; font-weight: 500; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3); transition: all 0.3s ease;">
                            🎯 Accept Invitation
                        </a>
                    </div>
                    
                    <!-- Alternative Link -->
                    <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 30px 0;">
                        <p style="color: #6c757d; margin: 0 0 10px 0; font-size: 14px; text-align: center;">
                            If the button doesn't work, copy and paste this link into your browser:
                        </p>
                        <div style="background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 4px; padding: 12px; word-break: break-all; font-family: 'Courier New', monospace; font-size: 13px; color: #495057;">
                            {invitation_url}
                        </div>
                    </div>
                    
                    <!-- Important Notice -->
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 25px 0;">
                        <div style="display: flex; align-items: flex-start;">
                            <div style="color: #f39c12; font-size: 18px; margin-right: 12px;">⏰</div>
                            <div>
                                <h4 style="color: #856404; margin: 0 0 8px 0; font-size: 16px;">Important Notice</h4>
                                <p style="color: #856404; margin: 0; font-size: 14px; line-height: 1.6;">
                                    This invitation link is valid and secure. If you didn't expect this invitation, you can safely ignore this email.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Email Bottom Spacing -->
            <div style="height: 50px;"></div>
        </body>
        </html>
        """
        return self.send_html_email(to_email, subject, html_content)
    
    def _send_email(self, to_email, subject, content, content_type='plain', cc_emails=None, bcc_emails=None):
        """
        Internal email sending method
        :param to_email: Recipient email (string or list)
        :param subject: Email subject
        :param content: Email content
        :param content_type: Content type 'plain' or 'html'
        :param cc_emails: CC email list
        :param bcc_emails: BCC email list
        :return: (success: bool, message: str)
        """
        try:
            # Parameter validation
            if not self._validate_config():
                return False, "SMTP configuration incomplete"
            
            # Handle recipient list
            if isinstance(to_email, str):
                to_emails = [to_email]
            else:
                to_emails = to_email
            
            # Create email object
            message = MIMEMultipart()
            message['From'] = self.username
            message['To'] = ', '.join(to_emails)
            message['Subject'] = Header(subject, 'utf-8')
            
            # Add CC
            if cc_emails:
                if isinstance(cc_emails, str):
                    cc_emails = [cc_emails]
                message['Cc'] = ', '.join(cc_emails)
                to_emails.extend(cc_emails)
            
            # Add BCC
            if bcc_emails:
                if isinstance(bcc_emails, str):
                    bcc_emails = [bcc_emails]
                to_emails.extend(bcc_emails)
            
            # Add email content
            message.attach(MIMEText(content, content_type, 'utf-8'))
            
            # Connect to SMTP server and send
            # Check if proxy is configured
            proxy_url = os.environ.get('SOCKS_PROXY')
            if proxy_url:
                # Configure SOCKS proxy globally
                self._setup_socks_proxy(proxy_url)
            
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
            
            if self.use_tls:
                server.starttls()
            
            server.login(self.username, self.password)
            server.sendmail(self.username, to_emails, message.as_string())
            server.quit()
            
            logging.info(f"Email sent successfully: {to_emails}")
            return True, "Email sent successfully"
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "SMTP authentication failed, please check username and password"
            logging.error(error_msg)
            return False, error_msg
        except smtplib.SMTPConnectError:
            error_msg = "Unable to connect to SMTP server"
            logging.error(error_msg)
            return False, error_msg
        except smtplib.SMTPRecipientsRefused:
            error_msg = "Recipient address rejected"
            logging.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Email sending failed: {str(e)}"
            logging.error(error_msg)
            return False, error_msg
    
    def _setup_socks_proxy(self, proxy_url):
        """
        Setup SOCKS proxy globally for smtplib
        :param proxy_url: Proxy URL (e.g., socks5://proxy.example.com:1080 or socks5://user:pass@proxy.example.com:1080)
        """
        try:
            # Import PySocks for SOCKS proxy support
            import socks
        except ImportError:
            raise Exception("PySocks library is required for SOCKS proxy support. Install with: pip install PySocks")
        
        # Parse proxy URL
        username = None
        password = None
        
        if proxy_url.startswith('socks5://'):
            proxy_url = proxy_url[9:]  # Remove socks5://
            proxy_type = socks.PROXY_TYPE_SOCKS5
        elif proxy_url.startswith('socks4://'):
            proxy_url = proxy_url[9:]  # Remove socks4://
            proxy_type = socks.PROXY_TYPE_SOCKS4
        elif proxy_url.startswith('socks://'):
            proxy_url = proxy_url[8:]  # Remove socks://
            proxy_type = socks.PROXY_TYPE_SOCKS5
        else:
            # Default to SOCKS5 if no protocol specified
            proxy_type = socks.PROXY_TYPE_SOCKS5
        
        # Check for username:password in proxy URL
        if '@' in proxy_url:
            auth, proxy_url = proxy_url.split('@', 1)
            if ':' in auth:
                username, password = auth.split(':', 1)
        
        # Split proxy host and port
        if ':' in proxy_url:
            proxy_host, proxy_port = proxy_url.split(':', 1)
            proxy_port = int(proxy_port)
        else:
            proxy_host = proxy_url
            proxy_port = 1080  # Default SOCKS proxy port
        
        # Set global SOCKS proxy with rdns=True for proper DNS resolution through proxy
        socks.setdefaultproxy(proxy_type, proxy_host, proxy_port, True, username, password)
        socks.wrapmodule(smtplib)
    
    def _validate_config(self):
        """Validate if SMTP configuration is complete"""
        required_fields = ['smtp_server', 'username', 'password']
        return all(getattr(self, field) for field in required_fields)





# Usage example
if __name__ == "__main__":
    # 1. Create email sender using environment variable configuration
    email_sender = SMTPEmailSender()
    
    # # 2. Send plain text email
    # success, message = email_sender.send_text_email(
    #     to_email='1833706710@qq.com',
    #     subject='Test Email',
    #     content='This is a test email content'
    # )
    # print(f"Text email: {message}")
    
    # 3. Send password reset email (deluxe version)
    # success, message = email_sender.send_password_reset_code(
    #     to_email='1833706710@qq.com',
    #     code='AB123C',
    #     expire_minutes=15
    # )
    # print(f"Password reset email (deluxe version): {message}")
    
    # 4. Send password reset email (simple version)
    # success, message = email_sender.send_password_reset_code_simple(
    #     to_email='1833706710@qq.com',
    #     code='XY789Z',
    #     expire_minutes=15
    # )
    # print(f"Password reset email (simple version): {message}")
    
    # 5. Send HTML email example
    # success, message = email_sender.send_password_reset_code_simple(
    #     to_email='1833706710@qq.com',
    #     code='AB123C',
    #     expire_minutes=15
    # )
    # print(success)
    # print(f"Password reset email (simple version): {message}")
    
    # 9. Send user invitation email
    success, message = email_sender.send_user_invitation(
        to_email='1833706710@qq.com',
        invitation_url='https://nexusai.com/invite?token=abc123&team=myteam',
        team_name='Development Team',
        inviter_name='John Doe'
    )
    print(f"User invitation email: {message}")
    
    # # 6. Send verification code email
    # success, message = email_sender.send_verification_code(
    #     to_email='1833706710@qq.com',
    #     code='123456',
    #     expire_minutes=10
    # )
    # print(f"Verification code email: {message}")
    
    # 7. Send email with CC and BCC
    # success, message = email_sender.send_text_email(
    #     to_email='1833706710@qq.com',
    #     subject='Important Notice',
    #     content='This is an important notice email',
    #     cc_emails=['517227291@qq.com'],
    #     bcc_emails='517227291@qq.com'
    # )
    # print(f"CC email: {message}")
    
    # # 8. Send bulk email
    # recipients = ['user1@example.com', 'user2@example.com', 'user3@example.com']
    # success, message = email_sender.send_text_email(
    #     to_email=recipients,
    #     subject='Bulk Notification',
    #     content='This is a bulk email'
    # )
    # print(f"Bulk email: {message}")