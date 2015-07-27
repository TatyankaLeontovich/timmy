#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
tools module
"""

import os
import logging
import subprocess
import sys


def get_dir_structure(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    dir = {}
    try:
        rootdir = rootdir.rstrip(os.sep)
        start = rootdir.rfind(os.sep) + 1
        for path, dirs, files in os.walk(rootdir):
            folders = path[start:].split(os.sep)
            subdir = dict.fromkeys(files)
            parent = reduce(dict.get, folders[:-1], dir)
            parent[folders[-1]] = subdir
    except:
        logging.error('failed to create list of the directory: %s' % rootdir)
        sys.exit(1)
    return dir


def mdir(directory):
    if not os.path.exists(directory):
        logging.debug('creating directory %s' % directory)
        try:
            os.makedirs(directory)
        except:
            logging.error("Can't create a directory: %s" % directory)
            sys.exit(3)


def launch_cmd(command, timeout):
    logging.info('launch_cmd: command %s' % command)
    p = subprocess.Popen(command,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    try:
        outs, errs = p.communicate(timeout=timeout+1)
    except subprocess.TimeoutExpired:
        p.kill()
        outs, errs = p.communicate()
        logging.error("command: %s err: %s, returned: %s" %
                      (command, errs, p.returncode))
    logging.debug("ssh return: err:%s\nouts:%s\ncode:%s" %
                  (errs, outs, p.returncode))
    logging.info("ssh return: err:%s\ncode:%s" %
                 (errs, p.returncode))
    return outs, errs, p.returncode


def ssh_node(ip, command, sshopts='', sshvars='', timeout=15, filename=None,
             outputfile=None):
    if (ip in ['localhost', '127.0.0.1']) or ip.startswith('127.'):
        logging.info("skip ssh")
        bstr = "%s timeout '%s' bash -c " % (
               sshvars, timeout)
    else:
        logging.info("exec ssh")
        # base cmd str
        bstr = "timeout '%s' ssh -t -T %s '%s' '%s' " % (
               timeout, sshopts, ip, sshvars)
    if filename is None:
        cmd = bstr + '"' + command + '"'
    else:
        cmd = bstr + " 'bash -s' < '%s'" % (filename)
    # logging.info(cmd)
    if outputfile is not None:
        cmd += ' > "' + outputfile + '"'
    outs, errs, code = launch_cmd(cmd, timeout)
    return outs, errs, code


def get_files_rsync(ip, data, sshopts, dpath, timeout=15):
    if (ip in ['localhost', '127.0.0.1']) or ip.startswith('127.'):
        logging.info("skip ssh rsync")
        cmd = ("timeout '%s' rsync -avzr --files-from=- / '%s'"
               " --progress --partial --delete-before" %
               (timeout, dpath))
    else:
        cmd = ("timeout '%s' rsync -avzr -e 'ssh %s"
               " -oCompression=no' --files-from=- '%s':/ '%s'"
               " --progress --partial --delete-before"
               ) % (timeout, sshopts, ip, dpath)
    logging.debug("command:%s\ndata:\n%s" % (cmd, data))
    if data == '':
        return cmd, '', 127
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    try:
        outs, errs = p.communicate(input=data, timeout=timeout+1)
    except subprocess.TimeoutExpired:
        p.kill()
        outs, errs = p.communicate()
        logging.error("ip: %s, command: %s err: %s, returned: %s" %
                      (ip, cmd, errs, p.returncode))
    logging.debug("ip: %s, ssh return: err:%s\nouts:%s\ncode:%s" %
                  (ip, errs, outs, p.returncode))
    logging.info("ip: %s, ssh return: err:%s\ncode:%s" %
                 (ip, errs, p.returncode))
    return outs, errs, p.returncode


def free_space(destdir, timeout):
    cmd = ("df %s --block-size K 2> /dev/null"
           " | tail -n 1 | awk '{print $2}' | sed 's/K//g'") % (destdir)
    outs, errs, code = launch_cmd(cmd, timeout)
    return outs, errs, code


if __name__ == '__main__':
    exit(0)
