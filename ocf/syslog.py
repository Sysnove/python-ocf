# This file is part of python-ocf.
# Copyright (C) 2014  Chris Boot <bootc@bootc.net>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# This file is based on code imported from:
# https://raw.githubusercontent.com/bootc/nrpe-ng/master/nrpe_ng/syslog.py

from __future__ import absolute_import

import logging
import syslog


PRIORITY_NAMES = {
    'emerg':    syslog.LOG_EMERG,
    'alert':    syslog.LOG_ALERT,
    'crit':     syslog.LOG_CRIT,
    'err':      syslog.LOG_ERR,
    'warning':  syslog.LOG_WARNING,
    'notice':   syslog.LOG_NOTICE,
    'info':     syslog.LOG_INFO,
    'debug':    syslog.LOG_DEBUG,
}

FACILITY_NAMES = {
    'kern':     syslog.LOG_KERN,
    'user':     syslog.LOG_USER,
    'mail':     syslog.LOG_MAIL,
    'daemon':   syslog.LOG_DAEMON,
    'auth':     syslog.LOG_AUTH,
    'syslog':   syslog.LOG_SYSLOG,
    'lpr':      syslog.LOG_LPR,
    'news':     syslog.LOG_NEWS,
    'uucp':     syslog.LOG_UUCP,
    'cron':     syslog.LOG_CRON,
    # 'authpriv': syslog.LOG_AUTHPRIV,  # not in syslog module
    # 'ftp':      syslog.LOG_FTP,  # not in syslog module
    'local0':   syslog.LOG_LOCAL0,
    'local1':   syslog.LOG_LOCAL1,
    'local2':   syslog.LOG_LOCAL2,
    'local3':   syslog.LOG_LOCAL3,
    'local4':   syslog.LOG_LOCAL4,
    'local5':   syslog.LOG_LOCAL5,
    'local6':   syslog.LOG_LOCAL6,
    'local7':   syslog.LOG_LOCAL7,
}

# Must be in ascending priority order
PRIORITY_MAP = [
    (logging.DEBUG,     syslog.LOG_DEBUG),
    (logging.INFO,      syslog.LOG_INFO),
    (logging.WARNING,   syslog.LOG_WARNING),
    (logging.ERROR,     syslog.LOG_ERR),
    (logging.CRITICAL,  syslog.LOG_CRIT),
]


def priority(priority):
    if isinstance(priority, int):
        return priority
    elif str(priority) == priority:
        if priority not in PRIORITY_NAMES:
            raise ValueError("Unknown priority: %r" % priority)
        return PRIORITY_NAMES[priority]
    else:
        raise TypeError("Priority not an integer or a valid string: {}".format(
            priority))


def facility(facility):
    if isinstance(facility, int):
        return facility
    elif str(facility) == facility:
        if facility not in FACILITY_NAMES:
            raise ValueError("Unknown facility: %r" % facility)
        return FACILITY_NAMES[facility]
    else:
        raise TypeError("Facility not an integer or a valid string: {}".format(
            facility))

# Keep a 2nd reference to this function so that SyslogHandler.__init__ can have
# a parameter named 'facility' without masking this function.
_facility = facility


def encodePriority(fac, pri):
    """
    Encode the facility and priority. You can pass in strings or
    integers - if strings are passed, the FACILITY_NAMES and
    PRIORITY_NAMES mapping dictionaries are used to convert them to
    integers.
    """
    fac = facility(fac)
    pri = priority(pri)
    return fac | pri


def mapPriority(level):
    for lvl, prio in PRIORITY_MAP:
        if level <= lvl:
            return prio
    return syslog.LOG_CRIT


class SyslogHandler(logging.Handler):
    """
    Reimplementation of logging.handlers.SysLogHandler that uses the python
    native syslog module.
    """
    def __init__(self, ident=None, facility=syslog.LOG_USER, options=0):
        super(SyslogHandler, self).__init__()

        # Translate facility names to numbers
        facility = _facility(facility)

        self.facility = facility

        if ident is not None:
            syslog.openlog(ident, logoption=options, facility=facility)
        else:
            syslog.openlog(logoption=options, facility=facility)

    def emit(self, record):
        """
        Emit a record.
        """
        msg = self.format(record)

        # Encode the facility and priority to an integer
        prio = encodePriority(self.facility, mapPriority(record.levelno))

        syslog.syslog(prio, msg)

# vi:tw=0:wm=0:nowrap:ai:et:ts=8:softtabstop=4:shiftwidth=4
