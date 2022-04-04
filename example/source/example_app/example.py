import time


class Example(object):
    def __init__(self, configs, log, log_file_name, error_handling):
        self.configs = configs
        self.log = log
        self.log_file_name = log_file_name
        self.error_handling = error_handling
        # Example function with error handling - in this case there is no error possible,
        # so error handling is mute, but concept is the same
        try:
            message = 'THIS IS AN EXAMPLE APP'
            self.log.info(message)
            time.sleep(3)
        except Exception as err:
            # for use in the error email function below
            example_library = {'user': 'example_user', 'password': 'example123', 'command': 'ls - la'}
            message = 'Failed to complete step - {}'.format(err)
            self.log.error(message)
            self.error_handling.error_handling(
                error_level=40, # error level, 50 is critical, and 30 is a warning, and sends no email
                local_function='example.Example-init', # file, class, function
                message_body='This is a error test',
                text_filtered_arg='{}'.format(example_library))
            # you can raise an exception here if necessary, or continue
            # raise Exception(message)
        # example test break for testing a piece of automation
        # (simply insert the below into the spot of code area you are troubleshooting
        # as we log, we can simply raise an Exception with a message at the point we wish
        #                                                                   # to see a variable output, and test break
        # example: dictionary for an SSH command, that might have an issue,
        #                                                   # you can simply create a dictionary with the necessary info
        example_variable = {'user': 'example_user', 'password': 'example123', 'command': 'ls - la'}
        self.log.warning(example_variable)
