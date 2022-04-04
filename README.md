# Example Shell
## Current Documentation Version:
- Latest Update Version 2.0.0, updated by matthew branche on 01/16/2022

## Introduction
This Shell is an example shell or headless app, to showcase the basic functionality, that can be used to build and run any scalable automation or tools. This includes using Makefile, Python, pip, Docker, Docker-compose functionality tools

## Production Location
- The production location is currently loaded in git for example use in development. No vm location given as this is each person's personal development use case
- The PRIMARY SHELL RUN is highly suggested running from an UBUNTU (20.04 at this current version date) LINUX VM, that uses the following tools:
  - Make, Docker, and Docker-compose.
  - Please see 'Additional Information' and 'Appendix' for installation instructions and reference documentation

## Running Shell
- Validate local linux box has the following loaded: docker, docker-compose, make
    - with the current versions of each: 
        - Docker: Docker version 20.10.8, build 3967b7d
        - Docker Compose: docker-compose version 1.29.2, build 5becea4c
        - Make: make/focal,now 4.2.1-1.2 amd64 [installed]
- Download a copy of the shell from Git to a local linux box
- cd into the shell directory
- COPY IN THE FOLLOWING FILES:'main_config.ini', and '.env' filled out with your specific variable and information
- run the following command:
```
$ make
```
- or alternatively
```
$ docker-compose up -d

```

## Docker Environment Variables
file: .env
- Variables:
    - EXAMPLE_SHELL_TAG: used to notate the image version, allowing for docker container versioning (Critical Variable)
```
EXAMPLE_SHELL_TAG=2.0.0

```

## Main Config Environment Variables
- primary variables
    - run_primary_shell: Used as a lever to allow for docker to run, but the shell to run without setting any variables (Critical Variable)
    - DRY_RUN: Used as a lever to allow docker and the shell to run, but no changes to be made with the shell (Critical Variable)
    - primary_json_whitelist_location: The production location of your ESM system ID white lists, to allow for efficient ESM asset library functionality (Critical Variable)
```
[primary-variables]
# Run just Docker Automation - no running code = default = False
run_primary_shell: True

# Dry Run - run through full automation code, but make no changes
DRY_RUN: False

shell_root_location: /usr/local/app/
```
- Syslog variables
    - syslog_hosts_list: This is your syslog server target list. can be optionally set to 'na' if you do not wish to have syslog
    - syslog_port_list: This is the port list, matched to the above target list
    - system_log_name: This is the log name used to notate which shell you are logging.
```
[syslog-variables]
# MAKE SURE YOU HAVE A MATCHING NUMBER OF PORTS TO SYSLOG HOSTS, AS THIS WILL ERROR THE SHELL
# additionally, you can set syslog_hosts_list to 'na' if you don't wish to utilize syslog
# example1: syslog_hosts_list=falcon.brs.lab.emc.com, example2: syslog_hosts_list=na
syslog_hosts_list: falcon.brs.lab.emc.com
syslog_port_list: 514

# log name for primary logging functionality
system_log_name: esm_dev_sync

```
- SysAdmin Email
    - email: The email or DL email to be used. By default, set to an empty list
    - sysadmin_email: The Sysadmin email to be used for logging and error handling. By default, set to matthew.branche@dell.com
```
[sysadmin-email]
# uncomment the email below if you wish to have an email of the report sent to you
# email=example_email@example123.com or an email list: email=example_email@example123.com,example_email199@example123.com
# if no email, set to na
email: na
sysadmin_email: na
```
- Timer Variables
  - run_timer: To run the scheduler or not
  - crontab_string: a cron string used to find the next iteration of time to execute the shell. This could be in a minute cycle such as every 15 minutes, every hour... or even once a week at a specific time.
```
[timer-variables]
# set timer to True or false
run_timer: False
# timer set to crontab settings. All cron tab settings available, provided developer understands cron settings
# this timer function simply uses the "croniter" package to read the cron string below, and provide the next execution
# time to the timer, which computes everything into hours, minutes, and seconds, until execution.
# make sure to complete "spaces" with "_" to insure proper timer functionality
crontab_string: 0_20_*_*_5
```

## Supportability
- for supportability or questions if you are internal dell, please create an ESM ticket at [https://emcesm.service-now.com/navpage.do](https://emcesm.service-now.com/navpage.do). If you are external Dell, please feel free to post an issue against the shell.
- 
## Additional information
- installing docker: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04
- installing docker-compose: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04
    - please use version: 1.29.2 when running the below command
    - using 1.29.2 will allow for the correct docker-compose file version of **'3.8'** to work.
```
$ sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
- installing make: run following command:
```
$ apt-get install -y make

```
- make sure once this is complete, to add the following file: (and restart the server to update the service json)
/etc/docker/daemon.json (add your own dns servers to the below list)
  - currently ["10.199.39.7", "10.199.39.10", "10.226.241.10", "10.226.216.10"] are the dns servers IEO west lab ops uses. This is for Internal Dell purposes.
  - If you are external Dell, use the alternative deamon.json file example.
```
{
  "debug": true,
  "live-restore": true,
  "dns": [
    "10.199.39.7",
    "10.199.39.10",
    "10.226.241.10",
    "10.226.216.10"
  ],
  "log-opts": {
    "max-size": "8m",
    "max-file": "8"
  },
  "registry-mirrors": [
    "https://ap-sc.drm.ops.lab.dell.com:8446"
  ],
  "insecure-registries": [
    "ap-sc.drm.ops.lab.dell.com:8446"
  ]
}
```
  - alternative daemon.json example:
```
{
  "debug": true,
  "live-restore": true,
  "dns": [
    "8.8.8.8",
    "8.8.4.4"
  ],
  "log-opts": {
    "max-size": "8m",
    "max-file": "8"
  }
}
```

## Appendix
- https://docs.docker.com/ - for docker and docker-compose referencing
- https://pypi.org/ - for python referencing
- https://docs.docker.com/engine/reference/commandline/dockerd/#daemon-configuration-file - for docker daemon.json external examples
- https://gist.github.com/melozo/6de91558242fb8ca4212e4a73fbddde6 - for docker daemon.json external examples

## License
[MIT](https://choosealicense.com/licenses/mit/)
