#!/usr/bin/python

from source.libraries.primary_libraries import * # pull in all libraries from libraries package (Dictionaries)
from source.utilities.tools import *  # pull in all objects from tools package (logger, error handling, etc)
from source.example_app.example import Example  # pull in shell project where the shell work actually happens

# standard python packages used
import time  # used for pausing shell at different points for viewing necessary log information


if __name__ == '__main__':
    # instantiate primary timer
    timer = TimeUuidStamps()

    # instantiate primary variable storage library
    # This also initializes and loads the main_config.ini in the Dictionaries() class
    # See /example_shell/example/source/libraries/primary_libraries.py file for specific process flows
    configs = Dictionaries()

    # initialize the logging functionality
    logger = Logs(
        configs=configs
    )
    # initialize logger
    log = logger.setup_logger(
        file_log=True,
        file_syslog=True
    )
    logger.add_console_logger(logger=log)  # configure logger to push to console, in order to see logging
    #                                      # live for docker logs and printing to screen for development
    logfilename = logger.LOG_FILE_NAME  # set log file name = whats in this folder
    log_name = logger.LOG_NAME  # set log name for log text file functionality
    log_file_path = logger.LOG_FILE_PATH  # setting log file location
    configs.log_file_path = log_file_path  # pushing log location to global configs

    # initialize email functionality
    email = Email(configs=configs,
                  log = log)

    # initialize error handling functionality
    error_handling = ErrorHandling(
        configs=configs,
        log=log,
        log_file_name=logger.LOG_FILE_NAME)

    # set log time - this allows for individual file creation later as well as the script start time,
    # and shell directory location
    configs.log_time = logger.LOG_TIME
    configs.now = timer.now_sec

    log.info('# Start time: {} UTC'.format(timer.start_time))
    log.info('# Initialized Basic Functions')
    time.sleep(1)

    # scheduling timed release if scheduler turned on
    if configs.run_timer:
        log.info('# Starting Scheduler')
        timer.scheduler(
            configs=configs,
            log=log)
        log.info('# Scheduler Complete')
    else:
        log.warning('# WARNING # Skipping scheduler')

    # Running Primary Shell #
    log.info('### SHELL Start ###')
    # run primary shell if above boolean is set to "True" (default = False)
    if configs.run_primary_shell is True:
        main_function = Example(configs=configs,
                                log=log,
                                log_file_name=logfilename,
                                error_handling=error_handling)
        time.sleep(2)
        message = '# Shell Function Complete'
        log.info(message)

    # final time tallying - printing elapsed time, and final time stamp, as well as log cleanup
    time_list = timer.grab_end_time(time_stamp=configs.now)
    log.info(time_list[0])
    message = '#{}                                                      ### FULL SHELL COMPLETE ###'.format(
        time_list[1])
    log.info(message)

    logger.log_file_clean_up()


