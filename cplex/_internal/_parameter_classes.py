# --------------------------------------------------------------------------
# File: _parameter_classes.py 
# ---------------------------------------------------------------------------
# Licensed Materials - Property of IBM
# 5725-A06 5725-A29 5724-Y48 5724-Y49 5724-Y54 5724-Y55
# Copyright IBM Corporation 2008, 2011. All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with
# IBM Corp.
# ------------------------------------------------------------------------
"""Parameters for the CPLEX Python API.

This module defines classes for parameters, groups of parameters, and
the hierarchy of parameter groups used in the CPLEX Python API.
For more detail, see also the corresponding commands of the
Interactive Optimizer documented in the
CPLEX Parameters Reference Manual.


"""

import weakref
import _procedural as CPX_PROC
from _parameters_auto import *
import _constants
from cplex import exceptions

class Parameter(object):

    """Base class for Cplex parameters.

       
    """

    def __init__(self, env, about, parent, name, constants = None):
        """non-public"""
        self._env    = weakref.proxy(env)
        self._id     = about[0]
        self._help   = lambda : about[1]
        self._parent = parent
        self._name   = name
        if constants is not None:
            self.values = constants()

    def __repr__(self):
        """Returns the name of the parameter within the hierarchy."""
        return "".join([self._parent.__repr__(), '.', self._name])

    def set(self, value):
        """Sets the parameter to value."""
        if self._id == _constants.CPX_PARAM_APIENCODING:
            if not self._isvalid(value):
                raise exceptions.CplexError("Invalid argument to "+self.__repr__()+".set")
            self._apiencoding_value = value
            value = "UTF-8"
        if self._id == _constants.CPX_PARAM_FILEENCODING:
            value = CPX_PROC.cpx_decode(value, self._env.parameters.read.apiencoding.get())
        if self._isvalid(value):
            self._env.parameters._set(self._id, value)
        else:
            raise exceptions.CplexError("Invalid argument to "+self.__repr__()+".set")

    def get(self):
        """Returns the current value of the parameter."""
        if self._id == _constants.CPX_PARAM_APIENCODING:
            if hasattr(self, "_apiencoding_value"):
                return self._apiencoding_value
        if self._id == _constants.CPX_PARAM_FILEENCODING:
            return CPX_PROC.cpx_encode(self._env.parameters._get(self._id),
                                       self._env.parameters.read.apiencoding.get())
        return self._env.parameters._get(self._id)

    def reset(self):
        """Sets the parameter to its default value."""
        self.set(self._defval)

    def default(self):
        """Returns the default value of the parameter."""
        if self._id == _constants.CPX_PARAM_DATACHECK:
            return 1
        else:
            return self._defval

    def type(self):
        """Returns the type of the parameter. Allowed types are 
        float, int, and string.
        """
        return type(self._defval)

    def help(self):
        """Returns the documentation for the parameter."""
        return self._help()
    
        
class NumParameter(Parameter):

    """Class for integer and float parameters.

       
    """

    def __init__(self, env, about, parent, name, constants = None):
        """non-public"""
        Parameter.__init__(self, env, about, parent, name, constants)
        (self._defval, self._minval, self._maxval) = self._env.parameters._get_info(self._id)
        if self._id == _constants.CPX_PARAM_CLONELOG:
            self._minval = 0
            
    def _isvalid(self, value):
        """Returns whether value is a valid value for the parameter."""
        if isinstance(1L, self.type()):
            if isinstance(value, type(1)) and value >= self._minval and value <= self._maxval:
                return True
        if isinstance(value, self.type()) and value >= self._minval and value <= self._maxval:
            return True
        if isinstance(value, type(0)) and isinstance(0.0, self.type()) and value >= self._minval and value <= self._maxval:
            return True
        if self.type() is type(0.0) and self._minval == 0.0 and self._maxval == 0.0 and (isinstance(value, type(0)) or isinstance(value, type(0.0))):
            return True
        else:
            return False

    def min(self):
        """Returns the minimum value for the parameter."""
        return self._minval

    def max(self):
        """Returns the maximum value for the parameter."""
        return self._maxval


class StrParameter(Parameter):

    """Class for string parameters.

       
    """

    def __init__(self, env, about, parent, name, constants = None):
        """non-public"""
        Parameter.__init__(self, env, about, parent, name, constants)
        self._defval = self._env.parameters._get_info(self._id)

    def _isvalid(self, value):
        """Returns whether value is a valid value for the parameter."""
        if isinstance(value, self.type()):
            if self._id == _constants.CPX_PARAM_APIENCODING:
                if (value.lower().startswith("utf") and value.find("7") != -1):
                    return False
            return True
        else:
            return False


class ParameterGroup(object):

    """Class containing a group of Cplex parameters.

       
    """

    def __init__(self, env, members, parent):
        """non-public"""
        self._env = weakref.proxy(env)
        self._parent = parent
        self.__dict__.update(members(env, self))

    def __repr__(self):
        """Returns the name of the parameter group within the hierarchy."""
        return "".join([self._parent.__repr__(), '.', self._name])

    def reset(self):
        """Sets the parameters in the group to their default values."""
        for member in self.__dict__.values():
            if (isinstance(member, ParameterGroup) or isinstance(member, Parameter)) and member != self._parent:
                member.reset()

    def get_changed(self):
        """Returns a list of the changed parameters in the group.

        Returns a list of (parameter, value) pairs.  Each parameter is
        an instance of the Parameter class, and thus the parameter
        value can be changed via its set method, or this object can be
        passed to the tuning functions.

        """
        retval = []
        for member in self.__dict__.values():
            if isinstance(member, ParameterGroup) and member != self._parent:
                retval.extend(member.get_changed())
            if isinstance(member, Parameter):
                if member.get() != member.default():
                    retval.append((member, member.get()))
        return retval
                    

class TuningConstants:

    """Status codes returned by tuning methods.

       For an exaplanation of tuning, see that topic in
       the CPLEX User's Manual.

    """

    abort      = _constants.CPX_TUNE_ABORT
    time_limit = _constants.CPX_TUNE_TILIM
    dettime_limit = _constants.CPX_TUNE_DETTILIM
    
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.tuning_status.abort
        1
        >>> c.parameters.tuning_status[1]
        'abort'

        """
        if item == 0:
            return 'completed'
        if item == _constants.CPX_TUNE_ABORT:
            return 'abort'
        if item == _constants.CPX_TUNE_TILIM:
            return 'time_limit'
        if item == _constants.CPX_TUNE_DETTILIM:
            return 'dettime_limit'
        

class RootParameterGroup(ParameterGroup):

    """Class containing all the Cplex parameters.

       
    """

    tuning_status = TuningConstants()

    def __init__(self, env, members):
        if env is None and members is None:
            return
        env.parameters = self
        ParameterGroup.__init__(self, env, members, None)
        self.read.apiencoding.set("UTF8")
        self.read.datacheck.set(1)

    def __repr__(self):
        """Return 'parameters'."""
        return self._name

    def _set(self, which_parameter, value):
        """non-public"""
        if which_parameter in intParameterSet:
            # prevent access to presolved problem in MIP callbacks
            if which_parameter == 2055 and value != 0:
                return
            param_type = CPX_PROC.getparamtype(self._env._e, which_parameter)
            if param_type == _constants.CPX_PARAMTYPE_INT:
                CPX_PROC.setintparam(self._env._e, which_parameter, value)
            else:
                CPX_PROC.setlongparam(self._env._e, which_parameter, value)
        elif which_parameter in dblParameterSet:
            if isinstance(value, type(0)):
                value = float(value)
            CPX_PROC.setdblparam(self._env._e, which_parameter, value)
        elif which_parameter in strParameterSet:
            CPX_PROC.setstrparam(self._env._e, which_parameter, value)
        else:
            raise exceptions.CplexError("Bad parameter identifier")

    def _get(self, which_parameter):
        """non-public"""
        if which_parameter in intParameterSet:
            param_type = CPX_PROC.getparamtype(self._env._e, which_parameter)
            if param_type == _constants.CPX_PARAMTYPE_INT:
                return CPX_PROC.getintparam(self._env._e, which_parameter)
            else:
                return CPX_PROC.getlongparam(self._env._e, which_parameter)
        elif which_parameter in dblParameterSet:
            return CPX_PROC.getdblparam(self._env._e, which_parameter)
        elif which_parameter in strParameterSet:
            return CPX_PROC.getstrparam(self._env._e, which_parameter)
        else:
            raise exceptions.CplexError("Bad parameter identifier")

    def _get_info(self, which_parameter):
        """non-public"""
        if which_parameter in intParameterSet:
            param_type = CPX_PROC.getparamtype(self._env._e, which_parameter)
            if param_type == _constants.CPX_PARAMTYPE_INT:
                return CPX_PROC.infointparam(self._env._e, which_parameter)
            else:
                return CPX_PROC.infolongparam(self._env._e, which_parameter)
        elif which_parameter in dblParameterSet:
            return CPX_PROC.infodblparam(self._env._e, which_parameter)
        elif which_parameter in strParameterSet:
            return CPX_PROC.infostrparam(self._env._e, which_parameter)
        else:
            raise exceptions.CplexError("Bad parameter identifier")

    def _get_name(self, which):
        """non-public"""
        return CPX_PROC.getparamname(self._env._e, which, self._env.parameters.read.apiencoding.get())

    def tune_problem_set(self, filenames, filetypes = [], fixed_parameters_and_values = []):
        """Tunes parameters for a set of problems.

        filenames must be a sequence of strings specifying a set of
        problems to tune.
        
        If filetypes is given, it must be a sequence of the same
        length as filenames also consisting of strings that specify
        the types of the corresponding files.
        
        fixed_parameters_and_values is a sequence of sequences of
        length 2 containing instances of the Parameter class that are
        to be fixed during the tuning process and the values at which
        they are to be fixed.

        tune_problem_set returns the status of the tuning procedure,
        which is an attribute of parameters.tuning.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> out = c.set_results_stream(None)
        >>> out = c.set_log_stream(None)
        >>> status = c.parameters.tune_problem_set(["lpex.mps", "example.mps"],\
                                                   fixed_parameters_and_values = [(c.parameters.lpmethod, 0)])
        >>> c.parameters.tuning_status[status]
        'completed'

        """
        int_params_and_values = []
        dbl_params_and_values = []
        str_params_and_values = []
        for pv_pair in fixed_parameters_and_values:
            if pv_pair[0]._id in  intParameterSet:
                int_params_and_values.append((pv_pair[0]._id, pv_pair[1]))
            elif pv_pair[0]._id in dblParameterSet:
                dbl_params_and_values.append((pv_pair[0]._id, pv_pair[1]))
            elif pv_pair[0]._id in strParameterSet:
                str_params_and_values.append((pv_pair[0]._id, pv_pair[1]))
            else:
                raise exceptions.CplexError("Bad input to parameters.tune_problem_set")
        status = CPX_PROC.tuneparamprobset(self._env._e, filenames, filetypes, int_params_and_values,
                                           dbl_params_and_values, str_params_and_values)
        return status

    def tune_problem(self, fixed_parameters_and_values = []):
        """Tunes parameters for a Cplex problem.

        fixed_parameters_and_values is a sequence of sequences of
        length 2 containing instances of the Parameter class that are
        to be fixed during the tuning process and the values at which
        they are to be fixed.

        tune_problem returns the status of the tuning procedure, which
        is an attribute of parameters.tuning.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> out = c.set_results_stream(None)
        >>> status = c.parameters.tune_problem([(c.parameters.lpmethod, 0)])
        >>> c.parameters.tuning_status[status]
        'completed'
        >>> status = c.parameters.tune_problem()
        >>> c.parameters.tuning_status[status]
        'completed'
        
        """
        int_params_and_values = []
        dbl_params_and_values = []
        str_params_and_values = []
        for pv_pair in fixed_parameters_and_values:
            if pv_pair[0]._id in  intParameterSet:
                int_params_and_values.append((pv_pair[0]._id, pv_pair[1]))
            elif pv_pair[0]._id in dblParameterSet:
                dbl_params_and_values.append((pv_pair[0]._id, pv_pair[1]))
            elif pv_pair[0]._id in strParameterSet:
                str_params_and_values.append((pv_pair[0]._id, pv_pair[1]))
            else:
                raise exceptions.CplexError("Bad input to parameters.tune_problem")
        status = CPX_PROC.tuneparam(self._env._e, self._cplex._lp, int_params_and_values,
                                    dbl_params_and_values, str_params_and_values)
        return status
    
    def read_file(self, filename):
        """Reads a set of parameters from the file filename."""
        CPX_PROC.readcopyparam(self._env._e, filename)

    def write_file(self, filename):
        """Writes a set of parameters to the file filename."""
        CPX_PROC.writeparam(self._env._e, filename)


class off_on_constants:
    off = _constants.CPX_OFF
    on  = _constants.CPX_ON
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.output.mpslong.values.on
        1
        >>> c.parameters.output.mpslong.values[1]
        'on'

        """
        if item == _constants.CPX_OFF:
            return 'off'
        if item == _constants.CPX_ON:
            return 'on'

class writelevel_constants:
    auto                       = _constants.CPX_WRITELEVEL_AUTO
    all_variables              = _constants.CPX_WRITELEVEL_ALLVARS
    discrete_variables         = _constants.CPX_WRITELEVEL_DISCRETEVARS
    nonzero_variables          = _constants.CPX_WRITELEVEL_NONZEROVARS
    nonzero_discrete_variables = _constants.CPX_WRITELEVEL_NONZERODISCRETEVARS
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.output.writelevel.values.auto
        0
        >>> c.parameters.output.writelevel.values[0]
        'auto'

        """
        if item == _constants.CPX_WRITELEVEL_AUTO:
            return 'auto'
        if item == _constants.CPX_WRITELEVEL_ALLVARS:
            return 'all_variables'
        if item == _constants.CPX_WRITELEVEL_DISCRETEVARS:
            return 'discrete_variables'
        if item == _constants.CPX_WRITELEVEL_NONZEROVARS:
            return 'nonzero_variables'
        if item == _constants.CPX_WRITELEVEL_NONZERODISCRETEVARS:
            return 'nonzero_discrete_variables'

def output_members(env, parent):
    return dict(_name      = "output",
                help       = lambda : "Output parameters.",
                clonelog   = NumParameter(env, OutputCloneLog, parent, 'clonelog', off_on_constants),
                intsolfileprefix = StrParameter(env, OutputIntSolFilePrefix, parent, 'intsolfileprefix'),
                mpslong    = NumParameter(env, OutputMPSLong, parent, 'mpslong', off_on_constants),
                writelevel = NumParameter(env, OutputWriteLevel, parent, 'writelevel', writelevel_constants),
                )

class scale_constants:
    none = -1
    equilibration = 0
    aggressive = 1
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.read.scale.values.none
        -1
        >>> c.parameters.read.scale.values[-1]
        'none'
        
        """
        if item == -1:
            return 'none'
        if item == 0:
            return 'equilibration'
        if item == 1:
            return 'aggressive'

def read_members(env, parent):
    return dict(_name       = "read",
                help     = lambda : "Read parameters.",
                apiencoding = StrParameter(env, ReadAPIEncoding, parent, 'apiencoding'),
                constraints = NumParameter(env, ReadConstraints, parent, 'constraints'),
                datacheck   = NumParameter(env, ReadDataCheck, parent, 'datacheck', off_on_constants),
                fileencoding = StrParameter(env, ReadFileEncoding, parent, 'fileencoding'),
                nonzeros    = NumParameter(env, ReadNonzeros, parent, 'nonzeros'),
                qpnonzeros  = NumParameter(env, ReadQPNonzeros, parent, 'qpnonzeros'),
                scale       = NumParameter(env, ReadScale, parent, 'scale', scale_constants),
                variables   = NumParameter(env, ReadVariables, parent, 'variables'),
                )

class mip_emph_constants:
    balanced    = _constants.CPX_MIPEMPHASIS_BALANCED
    optimality  = _constants.CPX_MIPEMPHASIS_OPTIMALITY
    feasibility = _constants.CPX_MIPEMPHASIS_FEASIBILITY
    best_bound   = _constants.CPX_MIPEMPHASIS_BESTBOUND
    hidden_feasibility  = _constants.CPX_MIPEMPHASIS_HIDDENFEAS 
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.emphasis.mip.values.balanced
        0
        >>> c.parameters.emphasis.mip.values[0]
        'balanced'
        
        """
        if item == _constants.CPX_MIPEMPHASIS_BALANCED:
            return 'balanced'
        if item == _constants.CPX_MIPEMPHASIS_OPTIMALITY:
            return 'optimality'
        if item == _constants.CPX_MIPEMPHASIS_FEASIBILITY:
            return 'feasibility'
        if item == _constants.CPX_MIPEMPHASIS_BESTBOUND:
            return 'best_bound'
        if item == _constants.CPX_MIPEMPHASIS_HIDDENFEAS :
            return 'hidden_feasibility'

def emphasis_members(env, parent):
    return dict(_name       = "emphasis",
                help      = lambda : "Emphasis parameters.",
                memory    = NumParameter(env, EmphasisMemory, parent, 'memory', off_on_constants),
                mip       = NumParameter(env, EmphasisMIP, parent, 'mip', mip_emph_constants),
                numerical = NumParameter(env, EmphasisNumerical, parent, 'numerical', off_on_constants),
                )


def mip_limit_members(env, parent):
    return dict(_name       = "limits",
                help           = lambda : "MIP limit parameters.",
                aggforcut      = NumParameter(env, MIPLimitAggForCut, parent, 'aggforcut'),
                cutpasses      = NumParameter(env, MIPLimitCutPasses, parent, 'cutpasses'),
                cutsfactor     = NumParameter(env, MIPLimitCutsFactor, parent, 'cutsfactor'),
                eachcutlimit   = NumParameter(env, MIPLimitEachCutLimit, parent, 'eachcutlimit'),
                gomorycand     = NumParameter(env, MIPLimitGomoryCand, parent, 'gomorycand'),
                gomorypass     = NumParameter(env, MIPLimitGomoryPass, parent, 'gomorypass'),
                nodes          = NumParameter(env, MIPLimitNodes, parent, 'nodes'),
                polishtime     = NumParameter(env, MIPLimitPolishTime, parent, 'polishtime'),
                populate       = NumParameter(env, MIPLimitPopulate, parent, 'populate'),
                probetime      = NumParameter(env, MIPLimitProbeTime, parent, 'probetime'),
                repairtries    = NumParameter(env, MIPLimitRepairTries, parent, 'repairtries'),
                auxrootthreads = NumParameter(env, MIPLimitAuxRootThreads, parent, 'auxrootthreads'),
                solutions      = NumParameter(env, MIPLimitSolutions, parent, 'solutions'),
                strongcand     = NumParameter(env, MIPLimitStrongCand, parent, 'strongcand'),
                strongit       = NumParameter(env, MIPLimitStrongIt, parent, 'strongit'),
                submipnodelim  = NumParameter(env, MIPLimitSubMIPNodeLim, parent, 'submipnodelim'),
                treememory     = NumParameter(env, MIPLimitTreeMemory, parent, 'treememory'),
                )

class brdir_constants:
    down = _constants.CPX_BRDIR_DOWN
    auto = _constants.CPX_BRDIR_AUTO
    up   = _constants.CPX_BRDIR_UP
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.branch.values.down
        -1
        >>> c.parameters.mip.strategy.branch.values[-1]
        'down'
        
        """
        if item == _constants.CPX_BRDIR_DOWN:
            return 'down'
        if item == _constants.CPX_BRDIR_AUTO:
            return 'auto'
        if item == _constants.CPX_BRDIR_UP:
            return 'up'

class search_constants:
    auto        = _constants.CPX_MIPSEARCH_AUTO
    traditional = _constants.CPX_MIPSEARCH_TRADITIONAL
    dynamic     = _constants.CPX_MIPSEARCH_DYNAMIC      
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.search.values.auto
        0
        >>> c.parameters.mip.strategy.search.values[0]
        'auto'
        
        """
        if item == _constants.CPX_MIPSEARCH_AUTO:
            return 'auto'
        if item == _constants.CPX_MIPSEARCH_TRADITIONAL:
            return 'traditional'
        if item == _constants.CPX_MIPSEARCH_DYNAMIC      :
            return 'dynamic'

class subalg_constants:
    auto       = _constants.CPX_ALG_AUTOMATIC
    primal     = _constants.CPX_ALG_PRIMAL
    dual       = _constants.CPX_ALG_DUAL
    barrier    = _constants.CPX_ALG_BARRIER
    sifting    = _constants.CPX_ALG_SIFTING
    network    = _constants.CPX_ALG_NET
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.subalgorithm.values.auto
        0
        >>> c.parameters.mip.strategy.subalgorithm.values[0]
        'auto'
        
        """
        if item == _constants.CPX_ALG_AUTOMATIC:
            return 'auto'
        if item == _constants.CPX_ALG_PRIMAL:
            return 'primal'
        if item == _constants.CPX_ALG_DUAL:
            return 'dual'
        if item == _constants.CPX_ALG_BARRIER:
            return 'barrier'
        if item == _constants.CPX_ALG_SIFTING:
            return 'sifting'
        if item == _constants.CPX_ALG_NET:
            return 'network'

class nodesel_constants:
    depth_first       = _constants.CPX_NODESEL_DFS
    best_bound        = _constants.CPX_NODESEL_BESTBOUND
    best_estimate     = _constants.CPX_NODESEL_BESTEST
    best_estimate_alt = _constants.CPX_NODESEL_BESTEST_ALT     
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.nodeselect.values.depth_first
        0
        >>> c.parameters.mip.strategy.nodeselect.values[0]
        'depth_first'
        
        """
        if item == _constants.CPX_NODESEL_DFS:
            return 'depth_first'
        if item == _constants.CPX_NODESEL_BESTBOUND:
            return 'best_bound'
        if item == _constants.CPX_NODESEL_BESTEST:
            return 'best_estimate'
        if item == _constants.CPX_NODESEL_BESTEST_ALT     :
            return 'best_estimate_alt'

class alg_constants:
    auto       = _constants.CPX_ALG_AUTOMATIC
    primal     = _constants.CPX_ALG_PRIMAL
    dual       = _constants.CPX_ALG_DUAL
    barrier    = _constants.CPX_ALG_BARRIER
    sifting    = _constants.CPX_ALG_SIFTING
    network    = _constants.CPX_ALG_NET
    concurrent = _constants.CPX_ALG_CONCURRENT
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.startalgorithm.values.auto
        0
        >>> c.parameters.mip.strategy.startalgorithm.values[0]
        'auto'
        
        """
        if item == _constants.CPX_ALG_AUTOMATIC:
            return 'auto'
        if item == _constants.CPX_ALG_PRIMAL:
            return 'primal'
        if item == _constants.CPX_ALG_DUAL:
            return 'dual'
        if item == _constants.CPX_ALG_BARRIER:
            return 'barrier'
        if item == _constants.CPX_ALG_SIFTING:
            return 'sifting'
        if item == _constants.CPX_ALG_NET:
            return 'network'
        if item == _constants.CPX_ALG_CONCURRENT:
            return 'concurrent'

class varsel_constants:
    min_infeasibility    = _constants.CPX_VARSEL_MININFEAS
    default              = _constants.CPX_VARSEL_DEFAULT
    max_infeasibility    = _constants.CPX_VARSEL_MAXINFEAS
    pseudo_costs         = _constants.CPX_VARSEL_PSEUDO
    strong_branching     = _constants.CPX_VARSEL_STRONG
    pseudo_reduced_costs = _constants.CPX_VARSEL_PSEUDOREDUCED 
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.variableselect.values.default
        0
        >>> c.parameters.mip.strategy.variableselect.values[0]
        'default'
        
        """
        if item == _constants.CPX_VARSEL_MININFEAS:
            return 'min_infeasibility'
        if item == _constants.CPX_VARSEL_DEFAULT:
            return 'default'
        if item == _constants.CPX_VARSEL_MAXINFEAS:
            return 'max_infeasibility'
        if item == _constants.CPX_VARSEL_PSEUDO:
            return 'pseudo_costs'
        if item == _constants.CPX_VARSEL_STRONG:
            return 'strong_branching'
        if item == _constants.CPX_VARSEL_PSEUDOREDUCED :
            return 'pseudo_reduced_costs'

class dive_constants:
    auto = 0
    traditional = 1
    probing = 2
    guided = 3
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.dive.values.auto
        0
        >>> c.parameters.mip.strategy.dive.values[0]
        'auto'
        
        """
        if item == 0:
            return 'auto'
        if item == 1:
            return 'traditional'
        if item == 2:
            return 'probing'
        if item == 3:
            return 'guided'

class file_constants:
    auto = 0
    memory = 1
    disk = 2
    disk_compressed = 3
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.file.values.auto
        0
        >>> c.parameters.mip.strategy.file.values[0]
        'auto'
        
        """
        if item == 0:
            return 'auto'
        if item == 1:
            return 'memory'
        if item == 2:
            return 'disk'
        if item == 3:
            return 'disk_compressed'

class fpheur_constants:
    none = -1
    auto = 0
    feas = 1
    obj_and_feas = 2
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.fpheur.values.auto
        0
        >>> c.parameters.mip.strategy.fpheur.values[0]
        'auto'
        
        """
        if item == -1:
            return 'none'
        if item == 0:
            return 'auto'
        if item == 1:
            return 'feas'
        if item == 2:
            return 'obj_and_feas'

class miqcp_constants:
    auto = 0
    QCP_at_node = 1
    LP_at_node = 2
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.miqcpstrat.values.auto
        0
        >>> c.parameters.mip.strategy.miqcpstrat.values[0]
        'auto'
        
        """
        if item == 0:
            return 'auto'
        if item == 1:
            return 'QCP_at_node'
        if item == 2:
            return 'LP_at_node'

class presolve_constants:
    none = -1
    auto = 0
    force = 1
    probe = 2
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.presolvenode.values.auto
        0
        >>> c.parameters.mip.strategy.presolvenode.values[0]
        'auto'
        
        """
        if item == -1:
            return 'none'
        if item == 0:
            return 'auto'
        if item == 1:
            return 'force'
        if item == 2:
            return 'probe'

class v_agg_constants:
    none            = -1
    auto            = 0
    moderate        = 1
    aggressive      = 2
    very_aggressive = 3
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.probe.values.auto
        0
        >>> c.parameters.mip.strategy.probe.values[0]
        'auto'
        
        """
        if item == -1:
            return 'none'
        if item == 0:
            return 'auto'
        if item == 1:
            return 'moderate'
        if item == 2:
            return 'aggressive'
        if item == 3:
            return 'very_aggressive'

class kappastats_constants:
    none   = -1
    auto   = 0
    sample = 1
    full   = 2
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.strategy.kappastats.values.full
        2
        >>> c.parameters.mip.strategy.kappastats.values[2]
        'full'

        """
        if item == -1:
            return 'none'
        if item == 0:
            return 'auto'
        if item == 1:
            return 'sample'
        if item == 2:
            return 'full'

def mip_strategy_members(env, parent):
    return dict(_name       = "strategy",
                help           = lambda : "MIP strategy parameters.",
                backtrack      = NumParameter(env, MIPStrategyBacktrack, parent, 'backtrack'),
                bbinterval     = NumParameter(env, MIPStrategyBBInterval, parent, 'bbinterval'),
                branch         = NumParameter(env, MIPStrategyBranch, parent, 'branch', brdir_constants),
                dive           = NumParameter(env, MIPStrategyDive, parent, 'dive', dive_constants),
                file           = NumParameter(env, MIPStrategyFile, parent, 'file', file_constants),
                fpheur         = NumParameter(env, MIPStrategyFPHeur, parent, 'fpheur', fpheur_constants),
                heuristicfreq  = NumParameter(env, MIPStrategyHeuristicFreq, parent, 'heuristicfreq'),
                lbheur         = NumParameter(env, MIPStrategyLBHeur, parent, 'lbheur', off_on_constants),
                miqcpstrat     = NumParameter(env, MIPStrategyMIQCPStrat, parent, 'miqcpstrat', miqcp_constants),
                nodeselect     = NumParameter(env, MIPStrategyNodeSelect, parent, 'nodeselect', nodesel_constants),
                order          = NumParameter(env, MIPStrategyOrder, parent, 'order', off_on_constants),
                presolvenode   = NumParameter(env, MIPStrategyPresolveNode, parent, 'presolvenode', presolve_constants),
                probe          = NumParameter(env, MIPStrategyProbe, parent, 'probe', v_agg_constants),
                rinsheur       = NumParameter(env, MIPStrategyRINSHeur, parent, 'rinsheur'),
                search         = NumParameter(env, MIPStrategySearch, parent, 'search', search_constants),
                startalgorithm = NumParameter(env, MIPStrategyStartAlgorithm, parent, 'startalgorithm', alg_constants),
                subalgorithm   = NumParameter(env, MIPStrategySubAlgorithm, parent, 'subalgorithm', subalg_constants),
                variableselect = NumParameter(env, MIPStrategyVariableSelect, parent, 'variableselect', varsel_constants),
                kappastats     = NumParameter(env, MIPStrategyKappaStats, parent, 'kappastats', kappastats_constants),
                )

def mip_tolerance_members(env, parent):
    return dict(_name       = "tolerances",
                help             = lambda : "MIP tolerance parameters.",
                absmipgap        = NumParameter(env, MIPToleranceAbsMIPGap, parent, 'absmipgap'),
                integrality      = NumParameter(env, MIPToleranceIntegrality, parent, 'integrality'),
                lowercutoff      = NumParameter(env, MIPToleranceLowerCutoff, parent, 'lowercutoff'),
                mipgap           = NumParameter(env, MIPToleranceMIPGap, parent, 'mipgap'),
                objdifference    = NumParameter(env, MIPToleranceObjDifference, parent, 'objdifference'),
                relobjdifference = NumParameter(env, MIPToleranceRelObjDifference, parent, 'relobjdifference'),
                uppercutoff      = NumParameter(env, MIPToleranceUpperCutoff, parent, 'uppercutoff'),
                )

class agg_constants:
    none            = -1
    auto            = 0
    moderate        = 1
    aggressive      = 2
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.cuts.gomory.values.auto
        0
        >>> c.parameters.mip.cuts.gomory.values[0]
        'auto'
        
        """
        if item == -1:
            return 'none'
        if item == 0:
            return 'auto'
        if item == 1:
            return 'moderate'
        if item == 2:
            return 'aggressive'

def mip_cut_members(env, parent):
    return dict(_name       = "cuts",
                help        = lambda : "MIP cut parameters.",
                cliques     = NumParameter(env, MIPCutCliques, parent, 'cliques', v_agg_constants),
                covers      = NumParameter(env, MIPCutCovers, parent, 'covers', v_agg_constants),
                disjunctive = NumParameter(env, MIPCutDisjunctive, parent, 'disjunctive', v_agg_constants),
                flowcovers  = NumParameter(env, MIPCutFlowCovers, parent, 'flowcovers', agg_constants),
                gomory      = NumParameter(env, MIPCutGomory, parent, 'gomory', agg_constants),
                gubcovers   = NumParameter(env, MIPCutGUBCovers, parent, 'gubcovers', agg_constants),
                implied     = NumParameter(env, MIPCutImplied, parent, 'implied', agg_constants),
                mcfcut      = NumParameter(env, MIPCutMCFCut, parent, 'mcfcut', agg_constants),
                mircut      = NumParameter(env, MIPCutMIRCut, parent, 'mircut', agg_constants),
                pathcut     = NumParameter(env, MIPCutPathCut, parent, 'pathcut', agg_constants),
                zerohalfcut = NumParameter(env, MIPCutZeroHalfCut, parent, 'zerohalfcut', agg_constants),
                )

class replace_constants:
    firstin_firstout = _constants.CPX_SOLNPOOL_FIFO
    worst_objective  = _constants.CPX_SOLNPOOL_OBJ
    diversity        = _constants.CPX_SOLNPOOL_DIV
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.pool.replace.values.diversity
        2
        >>> c.parameters.mip.pool.replace.values[2]
        'diversity'
        
        """
        if item == _constants.CPX_SOLNPOOL_FIFO:
            return 'firstin_firstout'
        if item == _constants.CPX_SOLNPOOL_OBJ:
            return 'worst_objective'
        if item == _constants.CPX_SOLNPOOL_DIV:
            return 'diversity'

def mip_solution_members(env, parent):
    return dict(_name       = "pool",
                help      = lambda : "MIP solution parameters.",
                absgap    = NumParameter(env, MIPSolutionAbsGap, parent, 'absgap'),
                capacity  = NumParameter(env, MIPSolutionCapacity, parent, 'capacity'),
                intensity = NumParameter(env, MIPSolutionIntensity, parent, 'intensity', v_agg_constants),
                relgap    = NumParameter(env, MIPSolutionRelGap, parent, 'relgap'),
                replace   = NumParameter(env, MIPSolutionReplace, parent, 'replace', replace_constants),
                )


def mip_polish_members(env, parent):
    return dict(_name       = "polishafter",
                help      = lambda : "MIP solution-polishing parameters.",
                absmipgap = NumParameter(env, PolishingAbsMIPGap, parent, 'absmipgap'),
                mipgap    = NumParameter(env, PolishingMIPGap, parent, 'mipgap'),
                nodes     = NumParameter(env, PolishingNodes, parent, 'nodes'),
                solutions = NumParameter(env, PolishingSolutions, parent, 'solutions'),
                time      = NumParameter(env, PolishingTime, parent, 'time'),
                )

class ordertype_constants:
    default     = 0
    cost        = _constants.CPX_MIPORDER_COST
    bounds      = _constants.CPX_MIPORDER_BOUNDS
    scaled_cost = _constants.CPX_MIPORDER_SCALEDCOST
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.ordertype.values.cost
        1
        >>> c.parameters.mip.ordertype.values[1]
        'cost'
        
        """
        if item == 0:
            return 'default'
        if item == _constants.CPX_MIPORDER_COST:
            return 'cost'
        if item == _constants.CPX_MIPORDER_BOUNDS:
            return 'bounds'
        if item == _constants.CPX_MIPORDER_SCALEDCOST:
            return 'scaled_cost'
        
class mip_display_constants:
    none = 0
    integer_feasible = 1
    mip_interval_nodes = 2
    node_cuts = 3
    LP_root = 4
    LP_all = 5
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.mip.display.values.none
        0
        >>> c.parameters.mip.display.values[0]
        'none'
        
        """
        if item == 0:
            return 'none'
        if item == 1:
            return 'integer_feasible'
        if item == 2:
            return 'mip_interval_nodes'
        if item == 3:
            return 'node_cuts'
        if item == 4:
            return 'LP_root'
        if item == 5:
            return 'LP_all'
    
def mip_members(env, parent):
    return dict(_name       = "mip",
                help       = lambda : "MIP parameters.",
                cuts       = ParameterGroup(env, mip_cut_members, parent),
                display    = NumParameter(env, MIPDisplay, parent, 'display', mip_display_constants),
                interval   = NumParameter(env, MIPInterval, parent, 'interval'),
                limits     = ParameterGroup(env, mip_limit_members, parent),
                ordertype  = NumParameter(env, MIPOrderType, parent, 'ordertype', ordertype_constants),
                polishing  = ParameterGroup(env, mip_polish_members, parent),
                strategy   = ParameterGroup(env, mip_strategy_members, parent),
                tolerances = ParameterGroup(env, mip_tolerance_members, parent),
                pool       = ParameterGroup(env, mip_solution_members, parent),
                )


def simplex_limit_members(env, parent):
    return dict(_name       = "limits",
                help         = lambda : "Simplex limit parameters.",
                iterations   = NumParameter(env, SimplexLimitIterations, parent, 'iterations'),
                lowerobj     = NumParameter(env, SimplexLimitLowerObj, parent, 'lowerobj'),
                perturbation = NumParameter(env, SimplexLimitPerturbation, parent, 'perturbation', off_on_constants),
                singularity  = NumParameter(env, SimplexLimitSingularity, parent, 'singularity'),
                upperobj     = NumParameter(env, SimplexLimitUpperObj, parent, 'upperobj'),
                )


def simplex_tolerance_members(env, parent):
    return dict(_name       = "tolerances",
                help        = lambda : "Simplex tolerance parameters.",
                feasibility = NumParameter(env, SimplexToleranceFeasibility, parent, 'feasibility'),
                markowitz   = NumParameter(env, SimplexToleranceMarkowitz, parent, 'markowitz'),
                optimality  = NumParameter(env, SimplexToleranceOptimality, parent, 'optimality'),
                )

def simplex_perturbation_members(env, parent):
    return dict(_name     = "perturbation",
                help      = lambda: "Simplex perturbation parameters.",
                constant  = NumParameter(env, SimplexPerturbationConstant, parent, 'constant'),
                indicator = NumParameter(env, SimplexPerturbationIndicator, parent, 'indicator', off_on_constants),
                )

class dual_pricing_constants:
    auto          = _constants.CPX_DPRIIND_AUTO
    full          = _constants.CPX_DPRIIND_FULL
    steep         = _constants.CPX_DPRIIND_STEEP
    full_steep    = _constants.CPX_DPRIIND_FULLSTEEP
    steep_Q_start = _constants.CPX_DPRIIND_STEEPQSTART
    devex         = _constants.CPX_DPRIIND_DEVEX 
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.simplex.dgradient.values.full
        1
        >>> c.parameters.simplex.dgradient.values[1]
        'full'
        
        """
        if item == _constants.CPX_DPRIIND_AUTO:
            return 'auto'
        if item == _constants.CPX_DPRIIND_FULL:
            return 'full'
        if item == _constants.CPX_DPRIIND_STEEP:
            return 'steep'
        if item == _constants.CPX_DPRIIND_FULLSTEEP:
            return 'full_steep'
        if item == _constants.CPX_DPRIIND_STEEPQSTART:
            return 'steep_Q_start'
        if item == _constants.CPX_DPRIIND_DEVEX :
            return 'devex'

class primal_pricing_constants:
    partial       = _constants.CPX_PPRIIND_PARTIAL
    auto          = _constants.CPX_PPRIIND_AUTO
    devex         = _constants.CPX_PPRIIND_DEVEX
    steep         = _constants.CPX_PPRIIND_STEEP
    steep_Q_start = _constants.CPX_PPRIIND_STEEPQSTART
    full          = _constants.CPX_PPRIIND_FULL
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.simplex.pgradient.values.full
        4
        >>> c.parameters.simplex.pgradient.values[4]
        'full'
        
        """
        if item == _constants.CPX_PPRIIND_PARTIAL:
            return 'partial'
        if item == _constants.CPX_PPRIIND_AUTO:
            return 'auto'
        if item == _constants.CPX_PPRIIND_DEVEX:
            return 'devex'
        if item == _constants.CPX_PPRIIND_STEEP:
            return 'steep'
        if item == _constants.CPX_PPRIIND_STEEPQSTART:
            return 'steep_Q_start'
        if item == _constants.CPX_PPRIIND_FULL:
            return 'full'

class display_constants:
    none = 0
    normal = 1
    detailed = 2
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.simplex.display.values.normal
        1
        >>> c.parameters.simplex.display.values[1]
        'normal'
        
        """
        if item == 0:
            return 'none'
        if item == 1:
            return 'normal'
        if item == 2:
            return 'detailed'

def simplex_members(env, parent):
    return dict(_name       = "simplex",
                help         = lambda : "Simplex parameters.",
                crash        = NumParameter(env, SimplexCrash, parent, 'crash'),
                dgradient    = NumParameter(env, SimplexDGradient, parent, 'dgradient', dual_pricing_constants),
                display      = NumParameter(env, SimplexDisplay, parent, 'display', display_constants),
                limits       = ParameterGroup(env, simplex_limit_members, parent),
                perturbation = ParameterGroup(env, simplex_perturbation_members, parent),
                pgradient    = NumParameter(env, SimplexPGradient, parent, 'pgradient', primal_pricing_constants),
                pricing      = NumParameter(env, SimplexPricing, parent, 'pricing'),
                refactor     = NumParameter(env, SimplexRefactor, parent, 'refactor'),
                tolerances   = ParameterGroup(env, simplex_tolerance_members, parent)
                )

class prered_constants:
    none            = _constants.CPX_PREREDUCE_NOPRIMALORDUAL
    primal          = _constants.CPX_PREREDUCE_PRIMALONLY
    dual            = _constants.CPX_PREREDUCE_DUALONLY
    primal_and_dual = _constants.CPX_PREREDUCE_PRIMALANDDUAL
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.preprocessing.reduce.values.dual
        2
        >>> c.parameters.preprocessing.reduce.values[2]
        'dual'
        
        """
        if item == _constants.CPX_PREREDUCE_NOPRIMALORDUAL:
            return 'none'
        if item == _constants.CPX_PREREDUCE_PRIMALONLY:
            return 'primal'
        if item == _constants.CPX_PREREDUCE_DUALONLY:
            return 'dual'
        if item == _constants.CPX_PREREDUCE_PRIMALANDDUAL:
            return 'primal_and_dual'

class boundstrength_constants:
    auto = -1
    off = 0
    on = 1
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.preprocessing.boundstrength.values.auto
        -1
        >>> c.parameters.preprocessing.boundstrength.values[-1]
        'auto'
        
        """
        if item == -1:
            return 'auto'
        if item == 0:
            return 'off'
        if item == 1:
            return 'on'

class coeffreduce_constants:
    none = 0
    integral = 1
    any = 2
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.preprocessing.coeffreduce.values.any
        2
        >>> c.parameters.preprocessing.coeffreduce.values[2]
        'any'
        
        """
        if item == 0:
            return 'none'
        if item == 1:
            return 'integral'
        if item == 2:
            return 'any'

class dependency_constants:
    auto = -1
    off = 0
    begin = 1
    end = 2
    begin_and_end = 3
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.preprocessing.dependency.values.end
        2
        >>> c.parameters.preprocessing.dependency.values[2]
        'end'
        
        """
        if item == -1:
            return 'auto'
        if item == 0:
            return 'off'
        if item == 1:
            return 'begin'
        if item == 2:
            return 'end'
        if item == 3:
            return 'begin_and_end'

class dual_constants:
    no = -1
    auto = 0
    yes = 1
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.preprocessing.dual.values.no
        -1
        >>> c.parameters.preprocessing.dual.values[-1]
        'no'
        
        """
        if item == -1:
            return 'no'
        if item == 0:
            return 'auto'
        if item == 1:
            return 'yes'

class linear_constants:
    only_linear = 0
    full = 1
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.preprocessing.linear.values.full
        1
        >>> c.parameters.preprocessing.linear.values[1]
        'full'
        
        """
        if item == 0:
            return 'only_linear'
        if item == 1:
            return 'full'

class relax_constants:
    auto = -1
    off = 0
    on = 1    
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.preprocessing.relax.values.on
        1
        >>> c.parameters.preprocessing.relax.values[1]
        'on'
        
        """
        if item == -1:
            return 'auto'
        if item == 0:
            return 'off'
        if item == 1    :
            return 'on'

class repeatpre_constants:
    auto = -1
    off = 0
    without_cuts = 1
    with_cuts = 2
    new_root_cuts = 3
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.preprocessing.relax.values.off
        0
        >>> c.parameters.preprocessing.relax.values[0]
        'off'
        
        """
        if item == -1:
            return 'auto'
        if item == 0:
            return 'off'
        if item == 1:
            return 'without_cuts'
        if item == 2:
            return 'with_cuts'
        if item == 3:
            return 'new_root_cuts'

class sym_constants:
    auto = -1
    off   = 0
    mild = 1
    moderate = 2
    aggressive = 3
    more_aggressive = 4
    very_aggressive = 5
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.preprocessing.symmetry.values.off
        0
        >>> c.parameters.preprocessing.symmetry.values[0]
        'off'
        
        """
        if item == -1:
            return 'auto'
        if item == 0:
            return 'off'
        if item == 1:
            return 'mild'
        if item == 2:
            return 'moderate'
        if item == 3:
            return 'aggressive'
        if item == 4:
            return 'more_aggressive'
        if item == 5:
            return 'very_aggressive'
    
def preprocessing_members(env, parent):
    return dict(_name       = "preprocessing",
                help           = lambda : "Preprocessing parameters.",
                aggregator     = NumParameter(env, PresolveAggregator, parent, 'aggregator'),
                boundstrength  = NumParameter(env, PresolveBoundStrength, parent, 'boundstrength', boundstrength_constants),
                coeffreduce    = NumParameter(env, PresolveCoeffReduce, parent, 'coeffreduce', coeffreduce_constants),
                dependency     = NumParameter(env, PresolveDependency, parent, 'dependency', dependency_constants),
                dual           = NumParameter(env, PresolveDual, parent, 'dual', dual_constants),
                fill           = NumParameter(env, PresolveFill, parent, 'fill'),
                linear         = NumParameter(env, PresolveLinear, parent, 'linear', linear_constants),
                numpass        = NumParameter(env, PresolveNumPass, parent, 'numpass'),
                presolve       = NumParameter(env, PresolvePresolve, parent, 'presolve', off_on_constants),
                qpmakepsd      = NumParameter(env, PresolveQPMakePSD, parent, 'qpmakepsd', off_on_constants),
                reduce         = NumParameter(env, PresolveReduce, parent, 'reduce', prered_constants),
                relax          = NumParameter(env, PresolveRelax, parent, 'relax', relax_constants),
                repeatpresolve = NumParameter(env, PresolveRepeatPresolve, parent, 'repeatpresolve', repeatpre_constants),
                symmetry       = NumParameter(env, PresolveSymmetry, parent, 'symmetry', sym_constants),
                )

class sift_alg_constants:
    auto       = _constants.CPX_ALG_AUTOMATIC
    primal     = _constants.CPX_ALG_PRIMAL
    dual       = _constants.CPX_ALG_DUAL
    barrier    = _constants.CPX_ALG_BARRIER
    network    = _constants.CPX_ALG_NET
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.sifting.algorithm.values.dual
        2
        >>> c.parameters.sifting.algorithm.values[2]
        'dual'
        
        """
        if item == _constants.CPX_ALG_AUTOMATIC:
            return 'auto'
        if item == _constants.CPX_ALG_PRIMAL:
            return 'primal'
        if item == _constants.CPX_ALG_DUAL:
            return 'dual'
        if item == _constants.CPX_ALG_BARRIER:
            return 'barrier'
        if item == _constants.CPX_ALG_NET:
            return 'network'

def sift_members(env, parent):
    return dict(_name       = "sifting",
                help       = lambda : "Sifting parameters.",
                algorithm  = NumParameter(env, SiftingAlgorithm, parent, 'algorithm', sift_alg_constants),
                display    = NumParameter(env, SiftingDisplay, parent, 'display', display_constants),
                iterations = NumParameter(env, SiftingIterations, parent, 'iterations'),
                )
    

def conflict_members(env, parent):
    return dict(_name       = "conflict",
                help    = lambda : "Conflict parameters.",
                display = NumParameter(env, ConflictDisplay, parent, 'display', display_constants),
                )
    
class feasopt_mode_constants:
    min_sum  = _constants.CPX_FEASOPT_MIN_SUM
    opt_sum  = _constants.CPX_FEASOPT_OPT_SUM
    min_inf  = _constants.CPX_FEASOPT_MIN_INF
    opt_inf  = _constants.CPX_FEASOPT_OPT_INF
    min_quad = _constants.CPX_FEASOPT_MIN_QUAD
    opt_quad = _constants.CPX_FEASOPT_OPT_QUAD         
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.feasopt.mode.values.min_sum
        0
        >>> c.parameters.feasopt.mode.values[0]
        'min_sum'
        
        """
        if item == _constants.CPX_FEASOPT_MIN_SUM:
            return 'min_sum'
        if item == _constants.CPX_FEASOPT_OPT_SUM:
            return 'opt_sum'
        if item == _constants.CPX_FEASOPT_MIN_INF:
            return 'min_inf'
        if item == _constants.CPX_FEASOPT_OPT_INF:
            return 'opt_inf'
        if item == _constants.CPX_FEASOPT_MIN_QUAD:
            return 'min_quad'
        if item == _constants.CPX_FEASOPT_OPT_QUAD         :
            return 'opt_quad'

def feasopt_members(env, parent):
    return dict(_name       = "feasopt",
                help      = lambda : "Feasopt parameters.",
                mode      = NumParameter(env, FeasoptMode, parent, 'mode', feasopt_mode_constants),
                tolerance = NumParameter(env, FeasoptTolerance, parent, 'tolerance'),
                )
    
class measure_constants:
    average  = _constants.CPX_TUNE_AVERAGE
    minmax   = _constants.CPX_TUNE_MINMAX
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.tuning.measure.values.minmax
        2
        >>> c.parameters.tuning.measure.values[2]
        'minmax'
        
        """
        if item == _constants.CPX_TUNE_AVERAGE:
            return 'average'
        if item == _constants.CPX_TUNE_MINMAX:
            return 'minmax'

class tune_display_constants:
    none = 0
    minimal = 1
    settings = 2
    settings_and_logs = 3
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.tuning.display.values.minimal
        1
        >>> c.parameters.tuning.display.values[1]
        'minimal'
        
        """
        if item == 0:
            return 'none'
        if item == 1:
            return 'minimal'
        if item == 2:
            return 'settings'
        if item == 3:
            return 'settings_and_logs'

def tuning_members(env, parent):
    return dict(_name       = "tuning",
                help      = lambda : "Tuning parameters.",
                display   = NumParameter(env, TuneDisplay, parent, 'display', tune_display_constants),
                measure   = NumParameter(env, TuneMeasure, parent, 'measure', measure_constants),
                repeat    = NumParameter(env, TuneRepeat, parent, 'repeat'),
                timelimit = NumParameter(env, TuneTimeLimit, parent, 'timelimit'),
                )
    

def barrier_limit_members(env, parent):
    return dict(_name       = "limit",
                help        = lambda : "Barrier limit parameters.",
                corrections = NumParameter(env, BarrierLimitCorrections, parent, 'corrections'),
                growth      = NumParameter(env, BarrierLimitGrowth, parent, 'growth'),
                iteration   = NumParameter(env, BarrierLimitIteration, parent, 'iteration'),
                objrange    = NumParameter(env, BarrierLimitObjRange, parent, 'objrange'),
                )


class bar_order_constants:
    approx_min_degree = _constants.CPX_BARORDER_AMD
    approx_min_fill   = _constants.CPX_BARORDER_AMF
    nested_dissection = _constants.CPX_BARORDER_ND
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.barrier.ordering.values.nested_dissection
        3
        >>> c.parameters.barrier.ordering.values[3]
        'nested_dissection'
        
        """
        if item == _constants.CPX_BARORDER_AMD:
            return 'approx_min_degree'
        if item == _constants.CPX_BARORDER_AMF:
            return 'approx_min_fill'
        if item == _constants.CPX_BARORDER_ND:
            return 'nested_dissection'
    
class crossover_constants:
    none   = _constants.CPX_ALG_NONE
    auto   = _constants.CPX_ALG_AUTOMATIC
    primal = _constants.CPX_ALG_PRIMAL
    dual   = _constants.CPX_ALG_DUAL
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.barrier.crossover.values.dual
        2
        >>> c.parameters.barrier.crossover.values[2]
        'dual'
        
        """
        if item == _constants.CPX_ALG_NONE:
            return 'none'
        if item == _constants.CPX_ALG_AUTOMATIC:
            return 'auto'
        if item == _constants.CPX_ALG_PRIMAL:
            return 'primal'
        if item == _constants.CPX_ALG_DUAL:
            return 'dual'

class bar_alg_constants:
    default = 0
    infeas_estimate = 1
    infeas_constant = 2
    standard = 3
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.barrier.algorithm.values.standard
        3
        >>> c.parameters.barrier.algorithm.values[3]
        'standard'
        
        """
        if item == 0:
            return 'default'
        if item == 1:
            return 'infeas_estimate'
        if item == 2:
            return 'infeas_constant'
        if item == 3:
            return 'standard'

class bar_start_alg_constants:
    zero_dual = 1
    estimated_dual = 2
    average_primal_zero_dual = 3
    average_primal_estimated_dual = 4
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.barrier.startalg.values.zero_dual
        1
        >>> c.parameters.barrier.startalg.values[1]
        'zero_dual'
        
        """
        if item == 1:
            return 'zero_dual'
        if item == 2:
            return 'estimated_dual'
        if item == 3:
            return 'average_primal_zero_dual'
        if item == 4:
            return 'average_primal_estimated_dual'

def barrier_members(env, parent):
    return dict(_name       = "barrier",
                help           = lambda : "Barrier parameters.",
                algorithm      = NumParameter(env, BarrierAlgorithm, parent, 'algorithm', bar_alg_constants),
                colnonzeros    = NumParameter(env, BarrierColNonzeros, parent, 'colnonzeros'),
                convergetol    = NumParameter(env, BarrierConvergeTol, parent, 'convergetol'),
                crossover      = NumParameter(env, BarrierCrossover, parent, 'crossover', crossover_constants),
                display        = NumParameter(env, BarrierDisplay, parent, 'display', display_constants),
                limits         = ParameterGroup(env, barrier_limit_members, parent),
                ordering       = NumParameter(env, BarrierOrdering, parent, 'ordering', bar_order_constants),
                qcpconvergetol = NumParameter(env, BarrierQCPConvergeTol, parent, 'qcpconvergetol'),
                startalg       = NumParameter(env, BarrierStartAlg, parent, 'startalg', bar_start_alg_constants),
                )

class par_constants:
    opportunistic  = _constants.CPX_PARALLEL_OPPORTUNISTIC
    auto   = _constants.CPX_PARALLEL_AUTO
    deterministic  = _constants.CPX_PARALLEL_DETERMINISTIC      
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.parallel.values.auto
        0
        >>> c.parameters.parallel.values[0]
        'auto'
        
        """
        if item == _constants.CPX_PARALLEL_OPPORTUNISTIC:
            return 'opportunistic'
        if item == _constants.CPX_PARALLEL_AUTO:
            return 'auto'
        if item == _constants.CPX_PARALLEL_DETERMINISTIC:
            return 'deterministic'

class qp_alg_constants:
    auto       = _constants.CPX_ALG_AUTOMATIC
    primal     = _constants.CPX_ALG_PRIMAL
    dual       = _constants.CPX_ALG_DUAL
    network    = _constants.CPX_ALG_NET
    barrier    = _constants.CPX_ALG_BARRIER
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.qpmethod.values.auto
        0
        >>> c.parameters.qpmethod.values[0]
        'auto'
        
        """
        if item == _constants.CPX_ALG_AUTOMATIC:
            return 'auto'
        if item == _constants.CPX_ALG_PRIMAL:
            return 'primal'
        if item == _constants.CPX_ALG_DUAL:
            return 'dual'
        if item == _constants.CPX_ALG_NET:
            return 'network'
        if item == _constants.CPX_ALG_BARRIER:
            return 'barrier'

class advance_constants:
    none = 0
    standard = 1
    alternate = 2
    def __getitem__(self, item):
        """Converts a constant to a string.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> c.parameters.advance.values.none
        0
        >>> c.parameters.advance.values[0]
        'none'
        
        """
        if item == 0:
            return 'none'
        if item == 1:
            return 'standard'
        if item == 2:
            return 'alternate'

class clocktype_constants:
    auto = 0
    CPU  = 1
    wall = 2
    def __getitem__(self, item):
        if item == 0:
            return 'auto'
        if item == 1:
            return 'CPU'
        if item == 2:
            return 'wall'

class solutiontarget_constants:
    auto           = 0
    optimal_convex = 1
    first_order    = 2
    def __getitem__(self, item):
        if item == 0:
            return 'auto'
        if item == 1:
            return 'optimal_convex'
        if item == 2:
            return 'first_order'

def root_members(env, parent):
    return dict(_name       = "parameters",
                help    = lambda : "All CPLEX parameters.",
                advance        = NumParameter(env, setAdvance, parent, 'advance', advance_constants),
                barrier        = ParameterGroup(env, barrier_members, parent),
                clocktype      = NumParameter(env, setClockType, parent, 'clocktype', clocktype_constants),
                conflict       = ParameterGroup(env, conflict_members, parent),
                dettimelimit   = NumParameter(env, setDetTimeLimit, parent, 'dettimelimit'),
                emphasis       = ParameterGroup(env, emphasis_members, parent),
                feasopt        = ParameterGroup(env, feasopt_members, parent),
                lpmethod       = NumParameter(env, setLPMethod, parent, 'lpmethod', alg_constants),
                mip            = ParameterGroup(env, mip_members, parent),
                output         = ParameterGroup(env, output_members, parent),
                parallel       = NumParameter(env, setParallel, parent, 'parallel', par_constants),
                preprocessing  = ParameterGroup(env, preprocessing_members, parent),
                qpmethod       = NumParameter(env, setQPMethod, parent, 'qpmethod', qp_alg_constants),
                read           = ParameterGroup(env, read_members, parent),
                sifting        = ParameterGroup(env, sift_members, parent),
                simplex        = ParameterGroup(env, simplex_members, parent),
                solutiontarget = NumParameter(env, setSolutionTarget, parent, 'solutiontarget', solutiontarget_constants),
                threads        = NumParameter(env, setThreads, parent, 'threads'),
                timelimit      = NumParameter(env, setTimeLimit, parent, 'timelimit'),
                tuning         = ParameterGroup(env, tuning_members, parent),
                workdir        = StrParameter(env, setWorkDir, parent, 'workdir'),
                workmem        = NumParameter(env, setWorkMem, parent, 'workmem'),
                )


