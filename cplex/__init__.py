# --------------------------------------------------------------------------
# File: __init__.py
# ---------------------------------------------------------------------------
# Licensed Materials - Property of IBM
# 5725-A06 5725-A29 5724-Y48 5724-Y49 5724-Y54 5724-Y55
# Copyright IBM Corporation 2008, 2011. All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with
# IBM Corp.
# --------------------------------------------------------------------------

"""The CPLEX Python API.

This package contains classes for accessing CPLEX from the Python
programming language.  The most important class defined by this
package is the Cplex class, which provides methods for creating,
modifying, querying, or solving an optimization problem, and for
querying aspects of a solution.

The exceptions module defines the exception classes that are raised
during abnormal operation by the CPLEX Python API.

The callbacks module within this package defines callback classes that
can be used to alter the behavior of the algorithms used by CPLEX.

The constant infinity, defined in the cplex package, should be used to
set infinite upper and lower bounds.

The classes SparsePair and SparseTriple are used as input and output
classes for sparse vector and sparse matrix output, respectively.  See
the documentation for individual methods for details about the usage
of these classes.

"""


__all__ = ["Cplex", "callbacks", "exceptions", "infinity", "terminate", "SparsePair", "SparseTriple"]


import weakref

import callbacks
import exceptions
import _internal
from _internal._matrices import SparsePair, SparseTriple


infinity = _internal._constants.CPX_INFBOUND


def terminate():
    """Gracefully stops a CPLEX algorithm.

    When this function is called, the currently running CPLEX
    algorithm gracefully stops execution.  This method can be called
    during the execution of a callback or to intercept a user action,
    such as clicking a button on a GUI.

    If it is called while no CPLEX algorithm is running, the next
    CPLEX algorithm to run will terminate immediately.

    """
    _internal._procedural.set_py_terminator()


class Stats(object):
    """
    A class whose data members reflect statistics about a CPLEX problem.

    An instance of this class is returned by the Cplex.get_stats() method.

    The __str__ method of this class displays the problem statistics
    in human readable form.

    An instance of this class always has the following integer members:

    num_variables
    num_nonnegative
    num_fixed
    num_boxed
    num_free
    num_other
    num_binary
    num_integer
    num_semicontinuous
    num_semiinteger
    num_quadratic_variables
    num_linear_objective_nz
    num_quadratic_objective_nz
    num_linear_constraints
    num_linear_less
    num_linear_equal
    num_linear_greater
    num_linear_range
    num_linear_nz
    num_linear_rhs_nz
    num_indicator_constraints
    num_indicator_less
    num_indicator_equal
    num_indicator_greater
    num_indicator_complemented
    num_indicator_nz
    num_indicator_rhs_nz
    num_quadratic_constraints
    num_quadratic_less
    num_quadratic_greater
    num_quadratic_linear_nz
    num_quadratic_nz
    num_quadratic_rhs_nz
    num_SOS_constraints
    num_SOS1
    num_SOS1_members
    type_SOS1
    num_SOS2
    num_SOS2_members
    type_SOS2
    num_lazy_constraints
    num_lazy_nnz
    num_lazy_lt
    num_lazy_eq
    num_lazy_gt
    num_lazy_rhs_nnz
    num_user_cuts
    num_user_cuts_nnz
    num_user_cuts_lt
    num_user_cuts_eq
    num_user_cuts_gt
    num_user_cuts_rhs_nnz

    An instance of this class always has the following float members:

    min_lower_bound
    max_upper_bound
    min_linear_objective
    max_linear_objective
    min_linear_constraints
    max_linear_constraints
    min_linear_constraints_rhs
    max_linear_constraints_rhs

    An instance of this class returned by an instance of the Cplex
    class with a quadratic objective also has the following float
    members:

    min_quadratic_objective
    max_quadratic_objective

    An instance of this class returned by an instance of the Cplex
    class with ranged constraints also has the following float
    members:

    min_linear_range
    max_linear_range

    An instance of this class returned by an instance of the Cplex
    class with quadratic constraints also has the following float
    members:

    min_quadratic_linear
    max_quadratic_linear
    min_quadratic
    max_quadratic
    min_quadratic_rhs
    max_quadratic_rhs

    An instance of this class returned by an instance of the Cplex
    class with indicator constraints also has the following float
    members:

    min_indicator
    max_indicator
    min_indicator_rhs
    max_indicator_rhs

    An instance of this class returned by an instance of the Cplex
    class with lazy constraints also has the following float members:

    min_lazy_constraint
    max_lazy_constraint
    min_lazy_constraint_rhs
    max_lazy_constraint_rhs

    An instance of this class returned by an instance of the Cplex
    class with user cuts also has the following float members:

    min_user_cut
    max_user_cut
    min_user_cut_rhs
    max_user_cut_rhs


    """

    def __init__(self, c):
        self.name                 = c.get_problem_name()

        raw_stats = _internal._procedural.getprobstats(c._env._e, c._lp)
        if raw_stats is None:
            raise exceptions.CplexError("Error generating problem statistics")

        ## counts of problem objects
        # variable data
        self.num_variables              = raw_stats[1]
        self.num_nonnegative            = raw_stats[9]
        self.num_fixed                  = raw_stats[11]
        self.num_boxed                  = raw_stats[12]
        self.num_free                   = raw_stats[10]
        self.num_other                  = raw_stats[13]
        self.num_binary                 = raw_stats[14]
        self.num_integer                = raw_stats[15]
        self.num_semicontinuous         = raw_stats[16]
        self.num_semiinteger            = raw_stats[17]
        self.num_quadratic_variables    = raw_stats[18]
        self.num_linear_objective_nz    = raw_stats[2]
        self.num_quadratic_objective_nz = raw_stats[19]
        
        # linear constraint data
        self.num_linear_constraints = raw_stats[0]
        self.num_linear_less        = raw_stats[7]
        self.num_linear_equal       = raw_stats[5]
        self.num_linear_greater     = raw_stats[6]
        self.num_linear_range       = raw_stats[8]
        self.num_linear_nz          = raw_stats[4]
        self.num_linear_rhs_nz      = raw_stats[3]

        # indicator data
        self.num_indicator_constraints  = raw_stats[26]
        self.num_indicator_less         = raw_stats[30]
        self.num_indicator_equal        = raw_stats[31]
        self.num_indicator_greater      = raw_stats[32]
        self.num_indicator_complemented = raw_stats[29]
        self.num_indicator_nz           = raw_stats[28]
        self.num_indicator_rhs_nz       = raw_stats[27]
        
        #quadratic constraints
        self.num_quadratic_constraints = raw_stats[20]
        self.num_quadratic_less        = raw_stats[22]
        self.num_quadratic_greater     = raw_stats[23]
        self.num_quadratic_linear_nz   = raw_stats[25]
        self.num_quadratic_nz          = raw_stats[24]
        self.num_quadratic_rhs_nz      = raw_stats[21]

        # SOS data
        self.num_SOS_constraints              = raw_stats[63]
        if self.num_SOS_constraints > 0:
            sos_string_list = ["",
                               ", all continuous",
                               ", all binary",
                               ", all integer",
                               ", continuous, binary, and integer",
                               ", continuous and binary",
                               ", continuous and integer",
                               ", binary and integer",]
            self.num_SOS1 = raw_stats[64]
            if self.num_SOS1 > 0:
                self.num_SOS1_members = raw_stats[65]
                self.type_SOS1        = sos_string_list[raw_stats[66]]
            self.num_SOS2 = raw_stats[67]
            if self.num_SOS2 > 0:
                self.num_SOS2_members = raw_stats[68]
                self.type_SOS2        = sos_string_list[raw_stats[69]]
        else:
            self.num_SOS1          = 0
            self.num_SOS1_members = 0
            self.type_SOS1         = ""
            self.num_SOS2          = 0
            self.num_SOS2_members = 0
            self.type_SOS2         = ""
            
        # lazy constraint data
        self.num_lazy_constraints = raw_stats[74]
        self.num_lazy_nnz         = raw_stats[75]
        self.num_lazy_lt          = raw_stats[72]
        self.num_lazy_eq          = raw_stats[73]
        self.num_lazy_gt          = raw_stats[71]
        self.num_lazy_rhs_nnz     = raw_stats[70]

        # user cut data
        self.num_user_cuts         = raw_stats[80]
        self.num_user_cuts_nnz     = raw_stats[81]
        self.num_user_cuts_lt      = raw_stats[78]
        self.num_user_cuts_eq      = raw_stats[79]
        self.num_user_cuts_gt      = raw_stats[77]
        self.num_user_cuts_rhs_nnz = raw_stats[76]


        ## min and max data
        # variables 
        self.min_lower_bound      = raw_stats[41]
        self.max_upper_bound      = raw_stats[42]
        self.min_linear_objective = raw_stats[39]
        self.max_linear_objective = raw_stats[40]
        if self.num_quadratic_objective_nz > 0:
            self.min_quadratic_objective = raw_stats[43]
            self.max_quadratic_objective = raw_stats[44]

        # linear constraints
        self.min_linear_constraints     = raw_stats[34]
        self.max_linear_constraints     = raw_stats[33]
        self.min_linear_constraints_rhs = raw_stats[35]
        self.max_linear_constraints_rhs = raw_stats[36]
        if self.num_linear_range > 0:
            self.min_linear_range = raw_stats[37]
            self.max_linear_range = raw_stats[38]
            
        # quadratic constraints
        if self.num_quadratic_constraints> 0:
            self.min_quadratic_linear = raw_stats[47]
            self.max_quadratic_linear = raw_stats[48]
            self.min_quadratic        = raw_stats[45]
            self.max_quadratic        = raw_stats[46]
            self.min_quadratic_rhs    = raw_stats[49]
            self.max_quadratic_rhs    = raw_stats[50]

        # indicator constraints
        if self.num_indicator_constraints > 0:
            self.min_indicator        = raw_stats[51]
            self.max_indicator        = raw_stats[52]
            self.min_indicator_rhs    = raw_stats[53]
            self.max_indicator_rhs    = raw_stats[54]

        # lazy constraints
        if self.num_lazy_constraints > 0:
            self.min_lazy_constraint     = raw_stats[55]
            self.max_lazy_constraint     = raw_stats[56]
            self.min_lazy_constraint_rhs = raw_stats[57]
            self.max_lazy_constraint_rhs = raw_stats[58]

        # user cuts
        if self.num_user_cuts > 0:
            self.min_user_cut            = raw_stats[59]
            self.max_user_cut            = raw_stats[60]
            self.min_user_cut_rhs        = raw_stats[61]
            self.max_user_cut_rhs        = raw_stats[62]

    def __str__(self):
        allinf  = "all infinite"
        allzero = "all zero"
        sep     = ",  "
        ret     = ""
        ret = ret + "Problem name: " + self.name + "\n"
        ret = ret + "Variables            : %7d" % self.num_variables
        if self.num_nonnegative != self.num_variables or self.num_quadratic_variables > 0:
            ret     = ret + "  ["
            sep_ind = 0
            if self.num_nonnegative > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Nneg: %d" % self.num_nonnegative
                sep_ind = 1
            if self.num_fixed > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Fix: %d" % self.num_fixed
                sep_ind = 1
            if self.num_boxed > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Box: %d" % self.num_boxed
                sep_ind = 1
            if self.num_free > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Free: %d" % self.num_free
                sep_ind = 1
            if self.num_binary > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Binary: %d" % self.num_binary
                sep_ind = 1
            if self.num_integer > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "General Integer: %d" % self.num_integer
                sep_ind = 1
            if self.num_semicontinuous > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Semi-continuous: %d" % self.num_semicontinuous
                sep_ind = 1
            if self.num_semiinteger > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Semi-integer: %d" % self.num_semiinteger
                sep_ind = 1
            if self.num_other > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Other: %d" % self.num_other
                sep_ind = 1
            if self.num_quadratic_variables > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Qobj: %d" % self.num_quadratic_variables
                sep_ind = 1
            ret = ret + "]"
        ret = ret + "\n"
        ret = ret + "Objective nonzeros   : %7d" % self.num_linear_objective_nz + "\n"
        if self.num_quadratic_objective_nz > 0:
            ret = ret + "Objective Q nonzeros : %7d" % self.num_quadratic_objective_nz + "\n"
        ret = ret + "Linear constraints   : %7d" % self.num_linear_constraints
        if self.num_linear_constraints > 0:
            ret = ret + "  ["
            sep_ind = 0
            if self.num_linear_less > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Less: %d" % self.num_linear_less
                sep_ind = 1
            if self.num_linear_greater > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Greater: %d" % self.num_linear_greater
                sep_ind = 1
            if self.num_linear_equal > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Equal: %d" % self.num_linear_equal
                sep_ind = 1
            if self.num_linear_range > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Range: %d" % self.num_linear_range
                sep_ind = 1            
            ret = ret + "]"
        ret = ret + "\n"
        ret = ret + "  Nonzeros           : %7d\n" % self.num_linear_nz
        ret = ret + "  RHS nonzeros       : %7d\n" % self.num_linear_rhs_nz
        if self.num_indicator_constraints > 0:
            ret = ret + "Indicator constraints: %7d  [" % self.num_indicator_constraints
            sep_ind = 0
            if self.num_indicator_less > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Less: %d" % self.num_indicator_less
                sep_ind = 1
            if self.num_indicator_equal > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Equal: %d" % self.num_indicator_equal
                sep_ind = 1
            if self.num_indicator_greater > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Greater: %d" % self.num_indicator_greater
                sep_ind = 1
            ret = ret + "]\n"
            if self.num_indicator_complemented:
                ret = ret + "  Complemented       : %7d\n" % self.num_indicator_complemented
                ret = ret + "  Nonzeros           : %7d\n" % self.num_indicator_nz
                ret = ret + "  RHS nonzeros       : %7d\n" % self.num_indicator_rhs_nz
        if self.num_quadratic_constraints> 0:
            ret = ret + "Quadratic constraints: %7d  [" % self.num_quadratic_constraints
            sep_ind = 0
            if self.num_quadratic_less > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Less: %d" % self.num_quadratic_less
                sep_ind = 1
            if self.num_quadratic_greater > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "Greater: %d" % self.num_quadratic_greater
                sep_ind = 1
            ret = ret + "]\n"
            ret = ret + "  Linear terms       : %7d\n" % self.num_quadratic_linear_nz
            ret = ret + "  Quadratic terms    : %7d\n" % self.num_quadratic_nz
            ret = ret + "  RHS nonzeros       : %7d\n" % self.num_quadratic_rhs_nz
        if self.num_SOS_constraints > 0:
            ret = ret + "SOS                  : %7d  [" % self.num_SOS_constraints
            sep_ind = 0
            if self.num_SOS1 > 0:
                if sep_ind:
                    ret = ret + sep
                ret = ret + "SOS1: %d, %d members%s" % (self.num_SOS1, self.num_SOS1_members, self.type_SOS1)
                sep_ind = 1
            if self.num_SOS2 > 0:
                if sep_ind:
                    ret = ret + ";  "
                ret = ret + "SOS2: %d, %d members%s" % (self.num_SOS2, self.num_SOS2_members, self.type_SOS2)
                sep_ind = 1
            ret = ret + "]\n"
        ret = ret + "\n"
        if self.min_lower_bound > -infinity:
            valstr1 = str("%#-15.7g" % self.min_lower_bound)
        else:
            valstr1 = allinf
        if self.max_upper_bound <  infinity:
            valstr2 = str("%#-15.7g" % self.max_upper_bound)
        else:
            valstr2 = allinf
        ret = ret + "Variables            : Min LB: %-15s  Max UB: %-15s\n" % (valstr1, valstr2)
        if self.min_linear_objective > -infinity:
            valstr1 = str("%#-15.7g" % self.min_linear_objective)
        else:
            valstr1 = allzero
        if self.max_linear_objective <  infinity:
            valstr2 = str("%#-15.7g" % self.max_linear_objective)
        else:
            valstr2 = allzero
        ret = ret + "Objective nonzeros   : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
        if self.num_quadratic_objective_nz > 0:
            if self.min_quadratic_objective > -infinity:
                valstr1 = str("%#-15.7g" % self.min_quadratic_objective)
            else:
                valstr1 = allzero
            if self.max_quadratic_objective <  infinity:
                valstr2 = str("%#-15.7g" % self.max_quadratic_objective)
            else:
                valstr2 = allzero
            ret = ret + "Objective Q nonzeros : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
        ret = ret + "Linear constraints   :\n"
        if self.min_linear_constraints > -infinity:
            valstr1 = str("%#-15.7g" % self.min_linear_constraints)
        else:
            valstr1 = allzero
        if self.max_linear_constraints <  infinity:
            valstr2 = str("%#-15.7g" % self.max_linear_constraints)
        else:
            valstr2 = allzero
        ret = ret + "  Nonzeros           : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
        if self.min_linear_constraints_rhs > -infinity:
            valstr1 = str("%#-15.7g" % self.min_linear_constraints_rhs)
        else:
            valstr1 = allzero
        if self.max_linear_constraints_rhs <  infinity:
            valstr2 = str("%#-15.7g" % self.max_linear_constraints_rhs)
        else:
            valstr2 = allzero
        ret = ret + "  RHS nonzeros       : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
        if self.num_linear_range > 0:
            ret = ret + "  Range values       : Min   : %#-15.7g  Max   : %#-15.7g\n" % (self.min_linear_range, self.max_linear_range)
        if self.num_quadratic_constraints> 0:
            ret = ret + "Quadratic constraints:\n"
            if self.min_quadratic_linear > -infinity:
                valstr1 = str("%#-15.7g" % self.min_quadratic_linear)
            else:
                valstr1 = allzero
            if self.max_quadratic_linear <  infinity:
                valstr2 = str("%#-15.7g" % self.max_quadratic_linear)
            else:
                valstr2 = allzero
            ret = ret + "  Linear terms       : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
            if self.min_quadratic > -infinity:
                valstr1 = str("%#-15.7g" % self.min_quadratic)
            else:
                valstr1 = allzero
            if self.max_quadratic <  infinity:
                valstr2 = str("%#-15.7g" % self.max_quadratic)
            else:
                valstr2 = allzero
            ret = ret + "  Quadratic terms    : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
            if self.min_quadratic_rhs > -infinity:
                valstr1 = str("%#-15.7g" % self.min_quadratic_rhs)
            else:
                valstr1 = allzero
            if self.max_quadratic_rhs <  infinity:
                valstr2 = str("%#-15.7g" % self.max_quadratic_rhs)
            else:
                valstr2 = allzero
            ret = ret + "  RHS nonzeros       : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
        if self.num_indicator_constraints > 0:
            ret = ret + "Indicator constraints:\n"
            if self.min_indicator > -infinity:
                valstr1 = str("%#-15.7g" % self.min_indicator)
            else:
                valstr1 = allzero
            if self.max_indicator <  infinity:
                valstr2 = str("%#-15.7g" % self.max_indicator)
            else:
                valstr2 = allzero
            ret = ret + "  Nonzeros           : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
            if self.min_indicator_rhs > -infinity:
                valstr1 = str("%#-15.7g" % self.min_indicator_rhs)
            else:
                valstr1 = allzero
            if self.max_indicator_rhs <  infinity:
                valstr2 = str("%#-15.7g" % self.max_indicator_rhs)
            else:
                valstr2 = allzero
            ret = ret + "  RHS nonzeros       : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
        if self.num_lazy_constraints > 0:
            ret = ret + "Lazy constraints     :\n"
            if self.min_lazy_constraint > -infinity:
                valstr1 = str("%#-15.7g" % self.min_lazy_constraint)
            else:
                valstr1 = allzero
            if self.max_lazy_constraint <  infinity:
                valstr2 = str("%#-15.7g" % self.max_lazy_constraint)
            else:
                valstr2 = allzero
            ret = ret + "  Nonzeros           : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
            if self.min_lazy_constraint_rhs > -infinity:
                valstr1 = str("%#-15.7g" % self.min_lazy_constraint_rhs)
            else:
                valstr1 = allzero
            if self.max_lazy_constraint_rhs <  infinity:
                valstr2 = str("%#-15.7g" % self.max_lazy_constraint_rhs)
            else:
                valstr2 = allzero
            ret = ret + "  RHS nonzeros       : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
        if self.num_user_cuts > 0:
            ret = ret + "User cuts            :\n"
            if self.min_user_cut > -infinity:
                valstr1 = str("%#-15.7g" % self.min_user_cut)
            else:
                valstr1 = allzero
            if self.max_user_cut <  infinity:
                valstr2 = str("%#-15.7g" % self.max_user_cut)
            else:
                valstr2 = allzero
            ret = ret + "  Nonzeros           : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
            if self.min_user_cut_rhs > -infinity:
                valstr1 = str("%#-15.7g" % self.min_user_cut_rhs)
            else:
                valstr1 = allzero
            if self.max_user_cut_rhs <  infinity:
                valstr2 = str("%#-15.7g" % self.max_user_cut_rhs)
            else:
                valstr2 = allzero
            ret = ret + "  RHS nonzeros       : Min   : %-15s  Max   : %-15s\n" % (valstr1, valstr2)
        return ret


class Cplex(object):
    """
    A class encapsulating a CPLEX Problem.

    An instance of the Cplex class provides methods for creating,
    modifying, and querying an optimization problem, solving it, and
    querying aspects of the solution.

    Most of the methods are provided within categories of methods: for
    example, methods for adding, modifying, and querying data
    associated with variables are within the Cplex.variables category,
    and methods for querying the solution are within the
    Cplex.solution category.    
    
       
    """

    problem_type = _internal.ProblemType()
    """See `_internal.ProblemType()` """
    variables             = _internal._subinterfaces.VariablesInterface()
    """See `_internal._subinterfaces.VariablesInterface()` """
    linear_constraints    = _internal._subinterfaces.LinearConstraintInterface()
    """See `_internal._subinterfaces.LinearConstraintInterface()` """
    quadratic_constraints = _internal._subinterfaces.QuadraticConstraintInterface()
    """See `_internal._subinterfaces.QuadraticConstraintInterface()` """
    indicator_constraints = _internal._subinterfaces.IndicatorConstraintInterface()
    """See `_internal._subinterfaces.IndicatorConstraintInterface()` """
    SOS                   = _internal._subinterfaces.SOSInterface()
    """See `_internal._subinterfaces.SOSInterface()` """
    objective             = _internal._subinterfaces.ObjectiveInterface()
    """See `_internal._subinterfaces.ObjectiveInterface()` """
    MIP_starts            = _internal._subinterfaces.MIPStartsInterface()
    """See `_internal._subinterfaces.MIPStartsInterface()` """
    solution              = _internal._subinterfaces.SolutionInterface()
    """See `_internal._subinterfaces.SolutionInterface()` """
    presolve              = _internal._subinterfaces.PresolveInterface()
    """See `_internal._subinterfaces.PresolveInterface()` """
    order                 = _internal._subinterfaces.OrderInterface()
    """See `_internal._subinterfaces.OrderInterface()` """
    conflict              = _internal._subinterfaces.ConflictInterface()
    """See `_internal._subinterfaces.ConflictInterface()` """
    advanced              = _internal._subinterfaces.AdvancedCplexInterface()
    """See `_internal._subinterfaces.AdvancedCplexInterface()` """
    start                 = _internal._subinterfaces.InitialInterface()
    """See `_internal._subinterfaces.InitialInterface()` """
    feasopt               = _internal._subinterfaces.FeasoptInterface()
    """See `_internal._subinterfaces.FeasoptInterface()` """
    parameters            = _internal._parameter_classes.RootParameterGroup(None, None)
    """See `_internal._parameter_classes.RootParameterGroup` """

    def __init__(self, *args):
        """Constructor of the Cplex class.

        The Cplex constructor accepts four types of argument lists.

        cpx = cplex.Cplex()
        cpx is a new problem with no data

        cpx = cplex.Cplex("filename")
        cpx is a new problem containing the data in filename.  If
        filename does not exist, an exception is raised.

        cpx = cplex.Cplex("filename", "filetype")
        same as form 2, but cplex reads the file filename as a file of
        type filetype, rather than inferring the file type from its
        extension.

        cpx = cplex.Cplex(old_cpx)
        cpx contains the same problem data as old_cpx, but is a
        different object and contains no solution data.  Future
        changes to one do not affect the other.
        
        """
        if len(args) > 3:
            raise exceptions.CplexError("Too many arguments to Cplex()")
        if len(args) > 0 and isinstance(args[-1], _internal.Environment):
            env = args[-1]
            raise exceptions.CplexError("shared Environment not supported")
        else:
            env = _internal.Environment()
        if len(args) > 0 and isinstance(args[0], Cplex):
            self.__copy_init(args[0], env)
        else:
            if len(args) > 0 and isinstance(args[0], type("")):
                filename = args[0]
                filetype = ""
                if len(args) > 1 and isinstance(args[1], type("")):
                    filetype = args[1]
                self._lp = _internal._procedural.createprob(env._e, filename, env.parameters.read.apiencoding.get())
                _internal._procedural.readcopyprob(env._e, self._lp, filename, filetype)
            else:
                self._lp = _internal._procedural.createprob(env._e, "", env.parameters.read.apiencoding.get())
        self._env              = env
        self._env_lp_ptr       = _internal._procedural.pack_env_lp_ptr(self._env._e, self._lp)
        self.parameters        = env.parameters
        self.parameters._cplex = weakref.proxy(self)
        self.variables             = _internal._subinterfaces.VariablesInterface()
        self.linear_constraints    = _internal._subinterfaces.LinearConstraintInterface()
        self.quadratic_constraints = _internal._subinterfaces.QuadraticConstraintInterface()
        self.indicator_constraints = _internal._subinterfaces.IndicatorConstraintInterface()
        self.SOS                   = _internal._subinterfaces.SOSInterface()
        self.objective             = _internal._subinterfaces.ObjectiveInterface()
        self.MIP_starts            = _internal._subinterfaces.MIPStartsInterface()
        self.solution              = _internal._subinterfaces.SolutionInterface()
        self.presolve              = _internal._subinterfaces.PresolveInterface()
        self.order                 = _internal._subinterfaces.OrderInterface()
        self.conflict              = _internal._subinterfaces.ConflictInterface()
        self.advanced              = _internal._subinterfaces.AdvancedCplexInterface()
        self.start                 = _internal._subinterfaces.InitialInterface()
        self.feasopt               = _internal._subinterfaces.FeasoptInterface()
        self.variables._setup(self)
        self.linear_constraints._setup(self)
        self.quadratic_constraints._setup(self)
        self.indicator_constraints._setup(self)
        self.SOS._setup(self)
        self.objective._setup(self)
        self.MIP_starts._setup(self)
        self.solution._setup(self)
        self.presolve._setup(self)
        self.order._setup(self)
        self.conflict._setup(self)
        self.advanced._setup(self)
        self.start._setup(self)
        self.feasopt._setup(self)

    def __del__(self):
        """non-public"""
        if hasattr(self, "_env"):
            _internal._procedural.freeprob(self._env._e, self._lp)

    def __copy_init(self, old_cplex, env):
        """non-public"""
        self._lp  = _internal._procedural.cloneprob(env._e, old_cplex._lp)

    def read(self, filename, filetype = ""):
        """Reads a problem from file.

        The first argument is a string specifying the filename from
        which the problem will be read.

        If the method is called with two arguments, 
        the second argument is a string
        specifying the file type.  If this argument is omitted,
        filetype is taken to be the extension of the filename.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> out = c.set_results_stream(None)
        >>> out = c.set_log_stream(None)
        >>> c.read("lpex.mps")

        """
        _internal._procedural.readcopyprob(self._env._e, self._lp, filename, filetype)

    def write(self, filename, filetype = ""):
        """Writes a problem to file.

        The first argument is a string specifying the filename to
        which the problem will be written.

        If the method is called with two arguments, 
        the second argument is a string
        specifying the file type.  If this argument is omitted,
        filetype is taken to be the extension of the filename.

        If filetype is any of "sav", "mps", "lp", the problem is
        written in the corresponding format.  If filetype is either
        "rew" or "rlp" the problem is written with generic names in
        mps or lp format, respectively.  If filetype is "alp" the
        problem is written with generic names in lp format, where the
        variable names are annotated to indicate the type and bounds
        of each variable.

        If filetype is "dua", the dual problem is written to file.  If
        filetype is "emb", an embedded network problem is written to
        file.  If filetype is "ppe", the perturbed problem is written
        to file.  If filetype is "dpe", the perturbed dual problem is
        written to file.

        If filetype is none of the above strings, the problem will be
        written to file in mps format.

        For documentation of the file types, see the CPLEX File Format
        Reference Manual.

        """
        if filetype == "":
            (basename, filetype) = _internal.os.path.splitext(filename)
            filetype = filetype[1:]
        if filetype in ["sav", "mps", "lp", "rew", "rlp", "alp"]:
            _internal._procedural.writeprob(self._env._e, self._lp, filename, filetype)
        elif filetype == "dua":
            _internal._procedural.dualwrite(self._env._e, self._lp, filename)
        elif filetype == "emb":
            _internal._procedural.embwrite(self._env._e, self._lp, filename)
        elif filetype == "dpe":
            epsilon = self.parameters._get(_internal._constants.CPX_PARAM_EPPER)
            _internal._procedural.dperwrite(self._env._e, self._lp, filename, epsilon)
        elif filetype == "ppe":
            epsilon = self.parameters._get(_internal._constants.CPX_PARAM_EPPER)
            _internal._procedural.pperwrite(self._env._e, self._lp, filename, epsilon)
        else:
            _internal._procedural.writeprob(self._env._e, self._lp, filename, "mps")

    def get_problem_type(self):
        """Returns the problem type.

        The return value is an attribute of self.problem_type.

        >>> import cplex
        >>> c = cplex.Cplex()
        >>> out = c.set_results_stream(None)
        >>> out = c.set_log_stream(None)
        >>> c.read("lpex.mps")
        >>> c.get_problem_type()
        0
        >>> c.problem_type[c.get_problem_type()]
        'LP'

        """
        return _internal._procedural.getprobtype(self._env._e, self._lp)

    def set_problem_type(self, type, soln = None):
        """Changes the problem type.

        If only one argument is given, that argument specifies the new
        problem type.  It must be one of the following:

        Cplex.problem_type.LP
        Cplex.problem_type.MILP
        Cplex.problem_type.fixed_MILP
        Cplex.problem_type.QP
        Cplex.problem_type.MIQP
        Cplex.problem_type.fixed_MIQP
        Cplex.problem_type.QCP
        Cplex.problem_type.MIQCP
        
        If an optional second argument is given, it is taken to be an
        identifier of a member of the solution pool.  In this case,
        the first argument must be one of the following:

        Cplex.problem_type.fixed_MILP
        Cplex.problem_type.fixed_MIQP

        """
        if soln is None:
            _internal._procedural.chgprobtype(self._env._e, self._lp, type)
        else:
            _internal._procedural.chgprobtypesolnpool(self._env._e, self._lp, type, soln)

    def _is_MIP(self):
        """non-public"""
        if self.variables.get_num_integer() > 0 or self.variables.get_num_binary() > 0:
            return True
        if self.variables.get_num_semicontinuous() > 0 or self.variables.get_num_semiinteger() > 0:
            return True
        if self.SOS.get_num() > 0:
            return True
        if _internal._procedural._getnumusercuts(self._env._e, self._lp) > 0:
            return True
        if _internal._procedural._getnumlazyconstraints(self._env._e, self._lp) > 0:
            return True
        if _internal._procedural._hasgeneralconstraints(self._env._e, self._lp):
            return True
        else:
            return False

    def solve(self):
        """Solves the problem.

        Note
          The solve method returning normally does not necessarily mean
          that an optimal or feasible solution has been found.  Use
          Cplex.solution.get_status() to query the status of the current
          solution.

        """
        for cb in self._env._callbacks:
            cb._env_lp_ptr = self._env_lp_ptr
            if hasattr(cb, "_setup"):
                cb._setup(self._env._e, self._lp)
        if self._is_MIP():
            _internal._procedural.mipopt(self._env._e, self._lp)
        elif self.quadratic_constraints.get_num() > 0:
            lpmethod = self.parameters.lpmethod.get()
            if lpmethod == _internal._constants.CPX_ALG_BARRIER or lpmethod == _internal._constants.CPX_ALG_AUTOMATIC:
                _internal._procedural.hybbaropt(self._env._e, self._lp, _internal._constants.CPX_ALG_NONE)
            else:
                _internal._procedural.qpopt(self._env._e, self._lp)
        elif not self.objective.get_num_quadratic_nonzeros() > 0:
            try:
                _internal._procedural.lpopt(self._env._e, self._lp)
            except exceptions.CplexSolverError, exc:
                if exc.args[2] == _internal._pycplex.CPXERR_NOT_FOR_MIP:
                    _internal._procedural.mipopt(self._env._e, self._lp)
                else:
                    raise exc
        else:
            _internal._procedural.qpopt(self._env._e, self._lp)
        
    def populate_solution_pool(self):
        """Generates a variety of solutions to a discrete problem 
        (MIP, MIQP, MIQCP).

        The algorithm that populates the solution pool works in two
        phases.

        In the first phase, it solves the problem to optimality (or
        some stopping criterion set by the user) while it sets up a
        branch and cut tree for the second phase.

        In the second phase, it generates multiple solutions by using
        the information computed and stored in the first phase and by
        continuing to explore the tree.

        For more information, see the function CPXpopulate in the
        Callable Library Reference Manual and the topic solution pool
        in the CPLEX User's Manual.

        """
        _internal._procedural.populate(self._env._e, self._lp)

    def get_problem_name(self):
        """Returns the problem name."""
        return _internal._procedural.getprobname(self._env._e, self._lp, self.parameters.read.apiencoding.get())

    def set_problem_name(self, name):
        """Sets the problem name."""
        _internal._procedural.chgprobname(self._env._e, self._lp, name, self.parameters.read.apiencoding.get())

    def cleanup(self, epsilon):
        """Deletes values from the problem data 
           with absolute value smaller than epsilon.
        """
        _internal._procedural.cleanup(self._env._e, self._lp, epsilon)

    def register_callback(self, callback_class):
        """Registers a callback class for use during optimization.

        callback_class must be a proper subclass of one of the
        callback classes defined in the module callbacks.  It must
        override the __call__ method with a method that has signature
        __call__(self) -> None.  If callback_class is a subclass of
        more than one callback class, it will only be called when its
        first superclass is called.  register_callback returns the
        instance of callback_class registered for use.  Any previously
        registered callback of the same class will no longer be
        registered.

        """
        return self._env.register_callback(callback_class)
        
    def unregister_callback(self, callback_class):
        """Stops a callback class from being used.

        callback_class must be one of the callback classes defined in
        the module callback or a subclass of one of them.  This method 
        unregisters any previously registered callback of the same
        class.  If callback_class is a subclass of more than one
        callback class, this method will unregister only the callback of the
        same type as its first superclass.  unregister_callback
        returns the instance of callback_class just unregistered.

        """
        return self._env.unregister_callback(callback_class)
        
    def set_results_stream(self, results_file, fn=None):
        """Specifies where results will be printed.

        The first argument must be either a file-like object (i.e., an
        object with a write method and a flush method) or the name of
        a file to be written to.  Use None as the first argument to
        suppress output.

        The second optional argument is a function that takes a string
        as input and returns a string.  If specified, strings sent to
        this stream will be processed by this function before being
        written.

        Returns the stream to which results will be written.  To write
        to this stream, use this object's write() method.

        """
        return self._env.set_results_stream(results_file, fn)

    def set_warning_stream(self, warning_file, fn=None):
        """Specifies where warnings will be printed.

        The first argument must be either a file-like object (i.e., an
        object with a write method and a flush method) or the name of
        a file to be written to.  Use None as the first argument to
        suppress output.

        The second optional argument is a function that takes a string
        as input and returns a string.  If specified, strings sent to
        this stream will be processed by this function before being
        written.

        Returns the stream to which warnings will be written.  To write
        to this stream, use this object's write() method.

        """
        return self._env.set_warning_stream(warning_file, fn)

    def set_error_stream(self, error_file, fn=None):
        """Specifies where errors will be printed.
        
        The first argument must be either a file-like object (i.e., an
        object with a write method and a flush method) or the name of
        a file to be written to.  Use None as the first argument to
        suppress output.

        The second optional argument is a function that takes a string
        as input and returns a string.  If specified, strings sent to
        this stream will be processed by this function before being
        written.

        Returns the stream to which errors will be written.  To write
        to this stream, use this object's write() method.

        """
        return self._env.set_error_stream(error_file, fn)

    def set_log_stream(self, log_file, fn=None):
        """Specifies where the log will be printed.

        The first argument must be either a file-like object (i.e., an
        object with a write method and a flush method) or the name of
        a file to be written to.  Use None as the first argument to
        suppress output.

        The second optional argument is a function that takes a string
        as input and returns a string.  If specified, strings sent to
        this stream will be processed by this function before being
        written.

        Returns the stream to which the log will be written.  To write
        to this stream, use this object's write() method.

        """
        return self._env.set_log_stream(log_file, fn)

    def get_version(self):
        """Returns a string specifying the version of CPLEX."""
        return self._env.get_version()

    def get_stats(self):
        """Returns an object containing problem statistics.

        
        """
        return Stats(self)
