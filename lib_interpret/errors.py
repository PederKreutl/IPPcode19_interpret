################################################################################
# Project:   2BIT IPP, Project                                                 #
#            Faculty of Information Technolgy                                  #
#            Brno University of Technology                                     #
# File:      errors.py                                                         #
# Date:      11.04.2019 (03.04.2019)                                           #
# Author:    Peter Kruty, xkruty00                                             #
################################################################################

import sys

################################# RETURN CODES #################################
SCRIPT_SUCC = 0;
ARGS_ERR = 10;
INPUT_FILE_ERR = 11;
OUTPUT_FILE_ERR = 12;
INTERNAL_ERR = 99;

XML_WELLFORMED_ERR = 31;
XML_LEXSYN_ERR = 32;

IPPCODE19_SEM_ERR = 52;
OP_TYPES_ERR = 53;
VAR_NEXISTS_ERR = 54;
FRAME_NEXISTS_ERR = 55;
MISS_VAL_ERR = 56;
WRONG_VAL_ERR = 57;
STRING_ERR = 58;


##############################  ERROR MESSAGES #################################
ARGS_ERR_MSG = "ERROR 10: Arguments error";
INPUT_FILE_ERR_MSG = "ERROR 11: Input file error";
OUTPUT_FILE_ERR_MSG = "ERROR 12: Output file error";
INTERNAL_ERR_MSG = "ERROR 99: Internal error";

XML_WELLFORMED_ERR_MSG = "ERROR 31: Wrong XML format, not well-formed";
XML_LEXSYN_ERR_MSG = "ERROR 32: Wrong structure of XML, lexical or syntax problem";

IPPCODE19_SEM_ERR_MSG = "ERROR 52: Semantic error in IPPcode19";
OP_TYPES_ERR_MSG = "ERROR 53: Wrong types of operands";
VAR_NEXISTS_ERR_MSG = "ERROR 54: Access to non-existing variable";
FRAME_NEXISTS_ERR_MSG = "ERROR 55: Frame not exists";
MISS_VAL_ERR_MSG = "ERROR 56: Missing value";
WRONG_VAL_ERR_MSG = "ERROR 57: Wrong operand value";
STRING_ERR_MSG = "ERROR 58: Wrong usage of string";

################################# FUNCTIONS ####################################
def error_exit(error_code):
    if error_code == ARGS_ERR:
        print(ARGS_ERR_MSG, file=sys.stderr);
    if error_code == INPUT_FILE_ERR:
        print(INPUT_FILE_ERR_MSG, file=sys.stderr);
    if error_code == OUTPUT_FILE_ERR:
        print(OUTPUT_FILE_ERR_MSG, file=sys.stderr);
    if error_code == INTERNAL_ERR:
        print(INTERNAL_ERR_MSG, file=sys.stderr);
    if error_code == XML_WELLFORMED_ERR:
        print(XML_WELLFORMED_ERR_MSG, file=sys.stderr);
    if error_code == XML_LEXSYN_ERR:
        print(XML_LEXSYN_ERR_MSG, file=sys.stderr);
    if error_code == IPPCODE19_SEM_ERR:
        print(IPPCODE19_SEM_ERR_MSG, file=sys.stderr);
    if error_code == OP_TYPES_ERR:
        print(OP_TYPES_ERR_MSG, file=sys.stderr);
    if error_code == VAR_NEXISTS_ERR:
        print(VAR_NEXISTS_ERR_MSG, file=sys.stderr);
    if error_code == FRAME_NEXISTS_ERR:
        print(FRAME_NEXISTS_ERR_MSG, file=sys.stderr);
    if error_code == MISS_VAL_ERR:
        print(MISS_VAL_ERR_MSG, file=sys.stderr);
    if error_code == WRONG_VAL_ERR:
        print(WRONG_VAL_ERR_MSG, file=sys.stderr);
    if error_code == STRING_ERR:
        print(STRING_ERR_MSG, file=sys.stderr);
    exit(error_code);
