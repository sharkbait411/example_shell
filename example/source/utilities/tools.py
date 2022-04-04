import os
import subprocess
import base64

import logging
import logging.handlers
from logging.handlers import SysLogHandler

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from paramiko import client, SSHClient
from scp import SCPClient

from time import strftime
import time
from datetime import timedelta, date, datetime
from croniter import croniter

import string

import ssl
import json
import urllib3

import datetime

from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from email_validator import validate_email, EmailNotValidError

import requests

from configparser import ConfigParser


# <editor-fold desc="# Logging">
# Logging Class - pulls Dictionary above in from the configs variable below - set up to point to a log file for
# error handling, and to 2 CID syslog servers for documentation, and error handling
#
# setup = initialize log file, and log function... then call 'setup_logger' with correct log_file and syslog
# booleans. Default is to point to the syslog servers, and not use error_handling log file
class Logs(object):
    def __init__(self, configs):
        self.configs = configs
        self.bool_return = BoolReturn()
        self.BAD_VALUE = self.configs.log_library.BAD_VALUE
        self.LOG_DICT = self.configs.log_library.LOG_DICT
        self.LOG_TIME = strftime('%Y-%m-%d_%H-%M')
        self.LOGFORMAT = '{}.%(module)s[%(process)d] [%(levelname)s] - %(message)s'.format(self.configs.log_name)
        self.LOG_NAME = self.configs.log_name
        self.LOG_FILE_NAME = 'log-{}.txt'.format(self.LOG_TIME)
        self.LOG_FILE_PATH = self.LOG_FILE_NAME
        self.LOG_DEFAULT_LEVEL = self.configs.log_library.LOG_DEFAULT_LEVEL
        self.SYSLOG_PORT = self.configs.log_library.SYSLOG_PORT

        # initialize log file
        self.log_file_initialization()

    def add_console_logger(self, logger):
        console_formatter = logging.Formatter("%s %s" % ("%(asctime)-15s", self.LOGFORMAT))
        console = logging.StreamHandler()
        console.setFormatter(console_formatter)
        logger.addHandler(console)

    @staticmethod
    def get_file_handler(log_file, formatter):
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        return file_handler

    @staticmethod
    def get_syslog_handler(formatter, syslog_host, syslog_port):
        syslog_handler = logging.handlers.SysLogHandler(address=(syslog_host,
                                                                 syslog_port))
        syslog_handler.setFormatter(formatter)

        return syslog_handler

    def log_file_clean_up(self):
        try:
            os.remove(self.LOG_FILE_PATH)
        except:
            pass
        try:
            os.remove(self.LOG_FILE_NAME)
        except:
            pass

    def log_file_initialization(self):
        # try to create log file
        try:
            os.remove(self.LOG_FILE_PATH)
        except:
            pass
        try:
            with open(self.LOG_FILE_PATH, 'a'):
                os.utime(self.LOG_FILE_PATH, None)
        except:
            pass

    def setup_logger(self, file_log=False, file_syslog=True):
        """Function setup as many loggers as you want"""
        # formatter used for file logging - this will become the error log handler - which emails the team upon error,
        # and sends the logs along with the email
        formatter = logging.Formatter(self.LOGFORMAT)
        syslog_formatter = logging.Formatter(self.LOGFORMAT)
        logger = logging.getLogger(self.LOG_NAME)
        logger.setLevel(logging.INFO)
        if file_log is True:
            try:
                handler = self.get_file_handler(
                    log_file=self.LOG_FILE_PATH,
                    formatter=formatter)
                logger.addHandler(handler)
            except Exception as err:
                message = '# CRITICAL ERROR - FAILED TO SETUP FILE LOG HANDLER - {}'.format(err)
                raise Exception(message)
        if file_syslog is True and self.configs.log_library.USE_SYSLOG_HOSTS is True:
            e = 0
            try:
                for host in self.configs.log_library.syslog_hosts:
                    syslog_handler = self.get_syslog_handler(formatter=syslog_formatter,
                                                             syslog_host=host,
                                                             syslog_port=self.configs.log_library.syslog_port_list[e])
                    logger.addHandler(syslog_handler)
                    e += 1
            except Exception as err:
                message = '# CRITICAL ERROR - FAILED TO SETUP SYSLOG LOG HANDLER - {}'.format(err)
                raise Exception(message)
        return logger


# </editor-fold>


# <editor-fold desc="# Error Handling">
# Error Handling Class - pulls in Dictionary above via 'configs' and initializes the function that can be called later
# for exceptions and email the user and logs to syslog servers
# This class includes its own email function instead of using the Email Class.
class ErrorHandling(object):
    def __init__(self, configs, log, log_file_name):
        """
        :param configs: dictionary library. This must be filled out before hand. this includes basic environment info,
        device info
        :param error_true: Error flag if error is found
        :param basic_error_level: Error default level - INFO
        """
        self.configs = configs
        self.error_true = self.configs.error_library.ERROR_TRUE
        self.basic_error_level = self.configs.error_library.ERROR_DEFAULT_LEVEL
        self.log = log
        self.log_file_name = log_file_name
        self.boolean_return = BoolReturn()
        self.email_function = Email(configs=self.configs,
                                    log=log)

    def error_handling(self, error_level, local_function, message_body, text_filtered_arg):
        """
        :param log: log object that includes all the handler information
        :param log_file_name: log file name that the File log handler is pointing to
        :param error_level: <int> error level
        :param local_function: <str> location that error happened
        :param message_body: <str> error message
        :param text_filtered_arg: <str> variables necessary to help in troubleshooting
        :return:
        """
        if error_level >= 40:
            error_part = self.error_level(error_level=error_level)
            # <error level>, <environment>, <command>, <owner>, <reservation_id>
            subject = '# ERROR: {} - {} - {}'.format(
                error_part,
                self.configs.log_name,
                local_function
            )
            body = 'ERROR LEVEL: {}\n' \
                   'ERROR NAME: {}\n' \
                   'function: {}\n' \
                   'message: {}\n' \
                   'variables: {}'.format(
                error_level,
                error_part,
                local_function,
                message_body,
                text_filtered_arg)
            self.log.critical(subject)
            self.log.critical(body)
            self.email_function.send_email(
                sent_from=self.configs.email_library.TICKETING_EMAIL,
                subject=subject,
                body=body,
                recipients=self.configs.email_library.SYSADMIN_EMAIL_LIST,
                file_list=[self.log_file_name],
                file_boolean=True)

            # self.send_error_email(subject=subject,
            #                      body=body,
            #                      file_name=self.log_file_name)

        elif error_level >= 30:
            self.highest_error_level = error_level
            error_part = self.error_level(error_level=self.highest_error_level)
            # <error level>, <environment>, <command>, <owner>, <reservation_id>
            subject = '# WARNING: {} - {} - {}'.format(
                error_part,
                self.configs.basic_service_library.command,
                local_function
            )
            text = 'ERROR LEVEL: {}\n' \
                   'ERROR NAME: {}\n' \
                   'function: {}\n' \
                   'message: {}\n' \
                   'variables: {}'.format(error_level,
                                          error_part,
                                          local_function,
                                          message_body,
                                          text_filtered_arg)
            message = '{}\n' \
                      '\n' \
                      '{}'.format(self.configs.error_library.ERROR_MESSAGE_DICT['message'],
                                  text)
            body = message
            self.configs.error_library.ERROR_MESSAGE_DICT['message'] = message
            self.configs.error_library.ERROR_MESSAGE_DICT['subject'] = subject
            self.log.warning(subject)
            self.log.warning(message)
            self.email_function.send_email(
                sent_from=self.configs.email_library.TICKETING_EMAIL,
                subject=subject,
                body=body,
                recipients=self.configs.email_library.SYSADMIN_EMAIL_LIST,
                file_list=[self.log_file_name],
                file_boolean=True)

        else:
            pass

    def error_level(self, error_level):
        if error_level == 10:
            err_name = self.configs.error_library.ERROR_DICT['10']
        elif error_level == 20:
            err_name = self.configs.error_library.ERROR_DICT['20']
        elif error_level == 30:
            err_name = self.configs.error_library.ERROR_DICT['30']
        elif error_level == 40:
            err_name = self.configs.error_library.ERROR_DICT['40']
        elif error_level == 50:
            err_name = self.configs.error_library.ERROR_DICT['50']
        else:
            err_name = 'CRITICAL'
        return err_name
# </editor-fold>


# <editor-fold desc="# Email">
# Email Class - used for sending Emails in functionality
# Requires gmail email user and password for simple functionality
# if gmail is not available, please update Dictionary with appropriate settings
# This class includes the ability to send csv or txt files as part of the 'send_email' function
# simply set 'file_boolean' to True
class Email(object):
    def __init__(self, configs, log):
        self.configs = configs
        self.log = log

    @staticmethod
    def add_attachment(msg, file_list=None):
        if file_list is None:
            file_list = []
        for file_name in file_list:
            filename = file_name
            attachment = open(filename, 'rb')

            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename= %s' % filename)

            msg.attach(part)

        return msg

    def check_email_for_validation(self, email):
        primary_email_check_dictionary = {'primary_check': False,
                                          'error_dictionary': {}}
        v = None
        # grab email info
        try:
            v = validate_email(email,
                               allow_smtputf8=False,
                               allow_empty_local=False,
                               check_deliverability=True)
            message = '{}'.format(v)
            self.log.info(message)
            primary_email_check_dictionary['primary_check'] = True
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            message = str(e)
            self.log.info(message)
            primary_email_check_dictionary['primary_check'] = False
            primary_email_check_dictionary['error_dictionary'] = \
                self.configs.email_dictionary.email_error_dictionary['10']
        return primary_email_check_dictionary

    def send_email(self, sent_from, subject, body, recipients=None, file_list=None, file_boolean=False):
        # if len(recipients) == 0:
        #    message = '# recipients currently is 0, please enter at least one recipient'
        #    self.log.error(message)
        #    raise Exception(message)
        # gmail_user = self.configs.email_dictionary.SMTP_USER
        # gmail_pwd = self.configs.email_dictionary.SMTP_PASSWORD
        if file_list is None:
            file_list = []
        if recipients is None:
            recipients = []
        FROM = sent_from
        TO = ','.join(recipients)
        SUBJECT = subject
        BODY = body
        # Prepare actual message
        message = 'From: {}\nTo: {}\nSubject: {}\n\n{}'.format(FROM, TO, SUBJECT, BODY)

        msg = MIMEMultipart()

        msg['From'] = FROM
        msg['To'] = TO
        msg['Subject'] = SUBJECT

        msg.attach(MIMEText(message, 'plain'))
        if file_boolean is True:
            new_msg = self.add_attachment(msg=msg,
                                          file_list=file_list)
        else:
            new_msg = msg

        server = smtplib.SMTP(self.configs.email_library.SMTP_SERVER,
                              self.configs.email_library.SMTP_PORT)
        # server.starttls()
        # server.login(gmail_user, gmail_pwd)
        text = new_msg.as_string()
        server.sendmail(FROM, TO, text)
        server.quit()

        pass
# </editor-fold>


# <editor-fold desc="# Base64 Encode and Decode">
# Base64 encoder and decoder
class Base64(object):
    def __init__(self, string='', encoded_string=True):
        if encoded_string is True:
            # encoded string to be decoded
            decrypted_bytes = base64.b64decode(string)
            self.return_string = decrypted_bytes.decode("UTF-8")
        else:
            # string ready to be encrypted
            encrypted_bytes = string.encode("UTF-8")
            self.return_string = base64.b64encode(encrypted_bytes)


# </editor-fold>


# <editor-fold desc="# SSH Session and Ping Check">
# This SshSession Class provides SSH access to devices via Paramiko package. Initialization provides initial login
# access with options to:
#   - send commands and return output
#   - reboot linux machines with 'shutdown -r 0'
#   - pull a file to the execution server with scp
#   - push a file to the SSH location from the execution server and automation directory
class SshSession(object):
    client = None

    def __init__(self, log, log_file_name, address, username, password):
        self.log = log
        self.log_file_name = log_file_name
        self.log.info('# Connecting to Server: {}'.format(address))
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.connect(hostname=address,
                            username=username,
                            password=password,
                            look_for_keys=False)

    def reboot(self):
        stdin, stdout, stderr = self.client.exec_command(command='shutdown -r 0')

    def scp_get(self, file_path):
        with SCPClient(self.client.get_transport()) as scp:
            scp.get(file_path)

    def scp_put(self, file_source, file_destination):
        with SCPClient(self.client.get_transport()) as scp:
            scp.put(file_source, file_destination)

    def send_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command=command)
        output = stdout.readlines()
        return output

    def session_close(self):
        self.client.close()

    def sftp_get(self, remote_file_path, local_file_path):
        ftp_client = self.client.open_sftp()
        ftp_client.get(remote_file_path, local_file_path)

    def sftp_put(self, remote_file_path, local_file_path):
        ftp_client = self.client.open_sftp()
        ftp_client.put(local_file_path, remote_file_path)


# This PingCheck class is built allow a linux/MAC OS user to ping a device with either a DNS entry or IP4 Address
class PingCheck(object):
    def __init__(self, configs, log, log_file_name):
        self.configs = configs
        self.log = log
        self.log_file_name = log_file_name
        self.error_handling = ErrorHandling(configs=configs,
                                            log=log,
                                            log_file_name=log_file_name)

    def ipv4_ip_address_test(self, ip_address):
        validate_ip_address = False
        ip_list = ip_address.split('.')
        if len(ip_list) != 3:
            # ip address has too many '.' and octets to be an ip address
            validate_ip_address = True
        else:
            for octet in ip_list:
                try:
                    octet_int_test = int(octet)
                    if octet_int_test not in range(1, 255):
                        validate_ip_address = True
                        message = '# ERROR # IP address failed octet test - integer outside of range: {} - {}'.format(
                            ip_address,
                            octet_int_test)
                        self.log.error(message)
                except Exception as err:
                    validate_ip_address = True
                    message = '# ERROR # IP address failed octet test: {} - {}'.format(ip_address, err)
                    self.log.error(message)
        return validate_ip_address

    def dns_check(self, dns_entry):
        self.log.debug('# searching: {}'.format(dns_entry))
        ip_address = None
        try:
            nslookup_dns_entry = ['nslookup', dns_entry]
            process = subprocess.Popen(nslookup_dns_entry, stdout=subprocess.PIPE)
            output = str(process.communicate()[0])

            ip_list = []
            output_list = output.split('\\n')
            name_returned = False
            for data in output_list:
                if 'Name' in data:
                    name_returned = True
                if 'Address' in data and name_returned:
                    ip_address = data.split('Address: ')[1]
                    ip_list.append(ip_address)
            # ip_list.pop(0)
            if len(ip_list) == 0:
                ip_address = None
            else:
                ip_address = ip_list[0]
            self.log.info('# successfully pulled ip for: {} - {}'.format(dns_entry, ip_address))
            return ip_address
        except Exception as err:
            message = '# ERROR # Failed to return an IP address with nslookup of: {} - {}'.format(dns_entry, err)
            self.log.error(message)
            return ip_address
            # raise Exception(message)

    def ping_check(self, ip):
        ip_string = ['ping', ip, '-c', '1', '-W', '1']
        p = subprocess.Popen(ip_string, stdout=subprocess.PIPE)
        output = str(p.communicate()[0])
        p.wait()
        self.log.debug('# output: {}'.format(output))
        if output in self.configs.ping_failed_check_list:
            results = {'host': ip, 'host_ip_response': None}
        else:
            output_string = output.split('\n')[0]
            string_split = output_string.split(')')[0]
            response_ip_address = string_split.split('(')[1]
            results = {'host': ip, 'host_ip_response': response_ip_address}
        if p.poll():
            results['ping_result'] = False
        else:
            results['ping_result'] = True
        self.log.debug('# results: {}'.format(results))
        return results
# </editor-fold>


# <editor-fold desc="# Time, Bool Return, and CSV dictionary Return">
# Cycle time and uuid grab
class TimeUuidStamps(object):
    def __init__(self):
        self.start_now = time.gmtime()  # long format structure_time
        self.date_time = datetime.datetime
        self.start_time = self.date_time.strptime(
            time.strftime(
                '%Y-%m-%d %H:%M:%S',
                self.start_now),
            '%Y-%m-%d %H:%M:%S')
        self.now_sec = time.mktime(self.start_now)  # converts to seconds
        self.utc_time_stamp = '{} UTC'.format(time.strftime(
            '%Y-%m-%d %H:%M:%S', self.start_now))
        self.utc_hour = '{}'.format(time.strftime(
            '%H', self.start_now))
        self.date_month = '{}'.format(time.strftime(
            '%m', self.start_now))
        self.date_day = '{}'.format(time.strftime(
            '%d', self.start_now))
        self.uuid = uuid.uuid4()
        # self.select_date_cycle()
        self.timer_minute_limit = 3600
        self.five_minute_limit = 300
        self.end_time = ''
        self.date_list = []
        self.sprint_date_cycle_count = 1
        self.end_cycle_time = None

    @staticmethod
    def grab_end_time(time_stamp):
        end_now = time.gmtime()
        end_sec = time.mktime(end_now) - time_stamp  # takes converted seconds
        time_elapsed = '# Time Elapsed: {} (HH:MM:SS)'.format(time.strftime('%H:%M:%S',
                                                                            time.gmtime(
                                                                                end_sec)))
        time_complete = '# {} UTC\n'.format(time.strftime('%Y-%m-%d %H:%M:%S',
                                                          end_now))

        time_list = [time_elapsed, time_complete]
        return time_list

    def five_minute_timer(self, log, time_calculation):
        log.debug('# seconds left: {}'.format(time_calculation))
        five_minute_limit = 300
        seconds_count = 1
        cycle_count = 1
        run_timer = True
        while run_timer:
            if seconds_count >= time_calculation:
                run_timer = False
            else:
                if cycle_count >= self.five_minute_limit:
                    message = '# Job Pending - Completed waiting 5 minutes...'
                    log.info(message)
                    cycle_count = 1
                time.sleep(1)
            seconds_count += 1
            cycle_count += 1
            # log.info('# {} - {}'.format(seconds_count, cycle_count))
        message = '# Timer Complete - Executing Job...'
        log.info(message)

    def one_hour_timer(self, log, time_calculation):
        log.debug('# seconds left: {}'.format(time_calculation))
        seconds_count = 1
        cycle_count = 1
        run_timer = True
        while run_timer:
            if seconds_count >= time_calculation:
                run_timer = False
            else:
                if cycle_count >= self.timer_minute_limit:
                    message = '# Job Pending - Completed waiting 1 hour...'
                    log.info(message)
                    cycle_count = 1
                time.sleep(1)
            seconds_count += 1
            cycle_count += 1
        message = '# Timer Complete - Executing Job...'
        log.info(message)

    def time_calculator(self, start_time=None, end_time=None):
        if end_time is None:
            end_now = time.gmtime()
            self.end_time = self.date_time.strptime(
                time.strftime(
                    '%Y-%m-%d %H:%M:%S',
                    end_now),
                '%Y-%m-%d %H:%M:%S')
        else:
            self.end_time = end_time
        if start_time is None:
            diff = self.end_time - self.start_time
        else:
            start_time = self.date_time.strptime(
                time.strftime(
                    '%Y-%m-%d %H:%M:%S',
                    time.gmtime()),
                '%Y-%m-%d %H:%M:%S')
            diff = self.end_time - start_time
        return diff.seconds

    def scheduler(self, configs, log):
        log.info('# Cron string: {}'.format(configs.crontab_string))
        date_string = str(self.start_time).split(' ')[0]
        time_string = str(self.start_time).split(' ')[1]
        base = datetime.datetime(
            int(date_string.split('-')[0]),
            int(date_string.split('-')[1]),
            int(date_string.split('-')[2]),
            int(time_string.split(':')[0]),
            int(time_string.split(':')[1]))
        iter = croniter(configs.crontab_string, base)  # every 5 minutes
        self.end_cycle_time = iter.get_next(datetime.datetime)
        # schedule timer based on time calculator:
        time_calculation = self.time_calculator(start_time=None, end_time=self.end_cycle_time)
        log.info('# Time until execution: {} UTC'.format(self.end_cycle_time))
        log.info('# Minutes left: {}'.format(round((time_calculation / 60), 2)))
        if time_calculation <= self.timer_minute_limit:
            # using 5 minute timer
            self.five_minute_timer(log=log, time_calculation=time_calculation)
        else:
            # using hour timer
            self.one_hour_timer(log=log, time_calculation=time_calculation)
        time_list = self.grab_end_time(time_stamp=self.now_sec)
        message = time_list[0]
        log.info(message)


class BoolReturn(object):
    def __init__(self):
        self.bool = ''

    @staticmethod
    def bool_return(string):
        if string == 'True' or string == 'TRUE':
            return True
        else:
            return False
# </editor-fold>
