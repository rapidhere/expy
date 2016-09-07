#-*- coding: utf-8 -*-
"""
Constants

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"


class Stub(object):
    """
    Compiled stub configs
    """
    STUB_FILENAME = "<expy>"
    RET_VARNAME = "__ret__"


class Function(object):
    """
    Function configs
    """
    POWER_A_VARNAME = "__a__"
    POWER_U_VARNAME = "__u__"
    POWER_N_LOOP_LABEL = "__power_nloop__"
    POWER_C_LOOP_LABEL = "__power_cloop__"
    POWER_END_LABEL = "__power_end__"

    POWERMOD_A_VARNAME = "__ma__"
    POWERMOD_M_VARNAME = "__mm__"
    POWERMOD_U_VARNAME = "__mu__"
    POWERMOD_N_LOOP_LABEL = "__powerm_nloop__"
    POWERMOD_C_LOOP_LABEL = "__powerm_cloop__"
    POWERMOD_END_LABEL = "__powerm_end__"
