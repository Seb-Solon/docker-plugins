#!/usr/bin/python

from docker import Client
import os
import sys
import re
import socket
import time


def graphite_output(data_dict, hostname=socket.gethostname(), metric_name="docker_direct_lvm_usage"):
    """Output in graphite like mode.

    :param data_dict: dict containing usage data
    :param hostname: server hostname
    :param metric_name: metric name
    :return: None
    """
    timestamp = int(time.time())
    for key, val in data_dict.iteritems():
        for subkey, subval in val.iteritems():
            print("%s.%s.%s.%s %.4f %s"
                  % (hostname, metric_name, key, subkey, subval, timestamp))


def to_float(size_str):
    """Convert string size to value in GB

    :param size_str: string size to convert
    :type size_str: str
    :return: size in GB
    :rtype: float
    """
    # See : https://github.com/docker/go-units/blob/master/size.go
    # Humansize function is called. We divide by 1000 not 1024
    value, unit = size_str.split(" ")
    value = float(value)
    if unit == "MB":
        value *= 0.001

    return value


def main():
    if not os.access("/var/run/docker.sock", 4):
        print("This plugin must be run with good privileges"
              "to connect docker sock (root or docker group)")
        sys.exit(4)

    cli = Client()
    info = cli.info()
    data_dict = {"metadata": {}, "data": {}}

    # Store into a dict
    for key, val in info['DriverStatus']:
        matches = re.search("([meta]*data) space (.*)$", key.lower())
        if matches:
            data_dict[matches.groups()[0]][matches.groups()[1]] = to_float(val)

    # Compute percent
    for key in data_dict:
        data_dict[key]["used_percentage"] = 100 * data_dict[key]["used"] / data_dict[key]["total"]

    graphite_output(data_dict)

if __name__ == '__main__':
    main()


