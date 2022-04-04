from source.utilities.tools import BoolReturn, Base64
from configparser import ConfigParser


# <editor-fold desc="# Primary Dictionary Class">
# Primary Dictionary Class - Used for all functions that follow - This is what is pulled in first on any command
class Dictionaries(object):
    def __init__(self):
        self.bool_return = BoolReturn()
        self.log_name = 'default'  # default, but can be changed at time of primary function configuration
        self.log_default_dir = '/var/log/{}/log'.format(
            self.log_name)  # default, but can be changed at time of primary function configuration
        self.log_file_path = None
        self.log_library = LogDictionary()
        self.email_library = EmailDictionary()
        self.error_library = ErrorDictionary()
        self.log_time = None
        self.shell_root_location = None
        self.now = False
        self.debug = False
        self.send_email = False
        self.subject = ''
        self.body_list = []
        self.run_primary_shell = ''
        self.run_timer = False
        self.crontab_string = None

        self.env_var_setting()

    def env_var_setting(self):
        # load config variables from config.ini file
        try:
            config = ConfigParser()
            config.read('/usr/local/app/main_config.ini')
        except Exception as err:
            message = '# ERROR # Failed to load the main configuration file - {}'.format(err)
            raise BaseException(message)

        # set environment primary shell variable
        try:
            self.run_primary_shell = self.bool_return.bool_return(
                string=config.get('primary-variables', 'run_primary_shell'))
        except Exception as err:
            message = '# CRITICAL ERROR # - Failed to set primary SHELL BOOLEAN: {} - error message: {}'.format(
                self.log_name,
                err)
            raise BaseException(message)

        # set log name
        try:
            self.log_name = config.get('syslog-variables', 'system_log_name')
        except Exception as err:
            message = '# CRITICAL ERROR # - Failed to set Log Name for logging: {} - error message: {}'.format(
                self.log_name,
                err)
            raise BaseException(message)

        # set syslog variables
        self.log_library.syslog_hosts_list = []
        self.log_library.syslog_port_list = []
        self.log_library.USE_SYSLOG_HOSTS = False
        if config.get('syslog-variables', 'syslog_hosts_list') == 'na':
            pass
        else:
            try:
                self.log_library.syslog_hosts = config.get('syslog-variables', 'syslog_hosts_list').split(',')
            except:
                pass
            # set the port list
            try:
                port_list = []
                port_string_list = config.get('syslog-variables', 'syslog_port_list').split(',')
                for port in port_string_list:
                    port_list.append(int(port))
                self.log_library.syslog_port_list = port_list
                self.log_library.USE_SYSLOG_HOSTS = True
            except Exception as err:
                message = '# CRITICAL ERROR # - received syslog hosts: {}, but did not receive the correct port ' \
                          'list: {} - error message: {}'.format(self.log_library.syslog_hosts_list,
                                                                self.log_library.syslog_port_list,
                                                                err)
                raise BaseException(message)

        # set sysadmin email list
        try:
            if config.get('sysadmin-email', 'email') != 'na':
                self.email_library.RECIPIENT_EMAIL_LIST = config.get('sysadmin-email', 'email').split(',')
                self.send_email = True
            if config.get('sysadmin-email', 'sysadmin_email') != 'na':
                self.email_library.SYSADMIN_EMAIL_LIST = config.get('sysadmin-email', 'sysadmin_email').split(',')
            else:
                self.email_library.SYSADMIN_EMAIL_LIST = [self.email_library.BACKUP_SYSADMIN_EMAIL]
        except Exception as err:
            message = '# ERROR # Failed to set SYS ADMIN EMAIL list - {}'.format(err)
            raise BaseException(message)

        # set environment variables
        try:
            self.shell_root_location = config.get('primary-variables', 'shell_root_location')
            self.debug = BoolReturn().bool_return(string=config.get('primary-variables', 'DRY_RUN'))
            self.run_timer = BoolReturn().bool_return(string=config.get('timer-variables', 'run_timer'))
            crontab_list = config.get('timer-variables', 'crontab_string').split("_")
            if len(crontab_list) != 5:
                raise BaseException('# CRITICAL ERROR # Failed to set crontab_string properly!!')
            self.crontab_string = ' '.join(crontab_list)
        except Exception as err:
            message = '# CRITICAL ERROR # Failed to set debug and timer values - {}'.format(err)
            raise BaseException(message)
# </editor-fold>


# <editor-fold desc="# Main Dictionaries">
#################################################
#
# variable classes to create dictionaries
#
#################################################


class LogDictionary(object):
    def __init__(self):
        self.BAD_VALUE = ' 80y  | 53hak~ljbdpiSY* piwh4t[09AP s<cj'
        self.LOG_FILE_NAME = 'log'
        self.LOGGER_NAME = 'MY_LOGGER'
        self.LOG_DEFAULT_LEVEL = 'INFO'
        self.syslog_hosts_list = []
        self.syslog_port_list = []
        self.SYSLOG_PORT = 514
        self.USE_SYSLOG_HOSTS = False
        self.LOG_DICT = {
            'DEBUG': 10,
            'INFO': 20,
            'WARNING': 30,
            'WARN': 30,
            'ERROR': 40,
            'CRITICAL': 50,
            'CRIT': 50
        }
        self.LOG_FILE_PATH = ''
        self.FULL_FILE_PATH = ''


class ErrorDictionary(object):
    def __init__(self):
        self.ERROR_TRUE = False,
        self.ERROR_LEVEL = ''
        self.ERROR_DICT = {
            '10': 'DEBUG',
            '20': 'INFO',
            '30': 'WARNING',
            '40': 'ERROR',
            '50': 'CRITICAL'
        }
        self.ERROR_DEFAULT_LEVEL = 20
        self.ERROR_MESSAGE_DICT = {
            'subject': '',
            'body': ''
        }


class EmailDictionary(object):
    def __init__(self):
        self.SMTP_USER = ''  # please provide correct email at start of automation
        self.SMTP_PASSWORD = ''  # please provide correct password at start of automation if smtp.gmail.com is used
        self.SMTP_SERVER = 'mail.example.com'
        self.TICKETING_EMAIL = 'lab_notification_noreply@mail.example.com'
        self.EMAIL_REGEX = '^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$'
        self.SMTP_PORT = 25
        self.FILE_NAME = 'resource_info.txt'
        self.SSL_REQUIRED = False
        self.SYSADMIN_EMAIL_LIST = []
        self.RECIPIENT_EMAIL_LIST = []
        self.BACKUP_SYSADMIN_EMAIL = 'example.user.123@example.com'
        self.email_error_dictionary = {
            '10': '# email is not valid, exception message is human-readable',
            '20': '# failed ping check',
            '30': '# failed SMTP check',
            '40': '# Failed to Grab Email info - no Dictionary'}
# </editor-fold>
