# --------------------------------------------------------------------------
# File: _internal/_pycplex_platform.py
# ---------------------------------------------------------------------------
# Licensed Materials - Property of IBM
# 5725-A06 5725-A29 5724-Y48 5724-Y49 5724-Y54 5724-Y55
# Copyright IBM Corporation 2008, 2011. All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with
# IBM Corp.
# ------------------------------------------------------------------------

import platform

from sys import api_version, version_info

error_string = "CPLEX 12.4.0.0 is not compatible with this version of Python."

if platform.system() == 'Darwin':
    if version_info < (2, 5, 0):
        raise Exception(error_string)
    else:
        from cplex._internal.py1013_cplex124 import *
elif platform.system() in ('Windows', 'Microsoft'):
    if   version_info < (2, 6, 0):
        raise Exception(error_string)
    elif version_info < (2, 7, 0):
        from cplex._internal.py26_cplex124 import *
    elif version_info < (2, 8, 0):
        from cplex._internal.py27_cplex124 import *
    else:
        raise Exception(error_string)
elif platform.system() in ('Linux', 'AIX'):
    if version_info < (2, 4, 0):
        raise Exception(error_string)
    elif api_version == 1012:
        from py1012_cplex124 import *
    elif api_version == 1013:
        from cplex._internal.py1013_cplex124 import *
    else:
        raise Exception(error_string)
else:
    raise Exception("The CPLEX Python API is not supported on this platform.")
