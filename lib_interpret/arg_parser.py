################################################################################
# Project:   2BIT IPP, Project                                                 #
#            Faculty of Information Technolgy                                  #
#            Brno University of Technology                                     #
# File:      arg_parser.py                                                     #
# Date:      11.04.2019 (03.04.2019)                                           #
# Author:    Peter Kruty, xkruty00                                             #
################################################################################

################################### MODULES ####################################
from lib_interpret import errors
import sys
import getopt
import os.path
import re
from os.path import abspath

################################# "CONSTANTS" ##################################
HELP_MSG = ("NAPOVEDA PROGRAMU \"interpret.py\"\n\n"
            "POPIS\n"
            "\tProgram nacte XML reprezentaci programu ze zadaneho souboru a tento program "
            "s vyuzitim standardniho vstupu a vystupu interpretuje.\n\n"
            "NAPOVEDA\n"
            "\tAlespon jeden z parametru (--source nebo --input) musi byt vzdy zadan. Pokud jeden "
            "z nich chybi, tak jsou odpovidajici data nacitana ze standardniho vstupu.\n\n"
            "\t--help\t\tVypise na standardni vystup napovedu programu\n\n"
            "\t--source=file\tVstupni soubor s XML reprezentaci zdrojoveho kodu\n\n"
            "\t--input=file\tSoubor se vstupy pro samotnou interpretaci zadaneho zdrojoveho kodu\n\n"
            "\t--stats=file\tSoubor pro vypis agregovanych statistik:\n\n"
            "\t\t--insts\tPocet vykonanych instrukci\n\n"
            "\t\t--vars\tMaximalny pocet inicializovanych promennych\n")

################################### CLASSES ####################################
# Parser of script arguments
class ArgsParser:
    # Constructor
    def __init__(self):
        # Short options
        self.short_arg_opts = ""
        # Long options
        self.long_arg_opts = ["help", "source=", "input=", "stats=", "insts", "vars"]

    # Parse script arguments
    def parseArguments(self):
        # Parsing
        try:
            opts, args = getopt.getopt(sys.argv[1:], self.short_arg_opts, self.long_arg_opts)
        except getopt.GetoptError:
            errors.error_exit(errors.ARGS_ERR)

        #############################
        argc = len(sys.argv[1:])
        opts_count = len(opts)
        if (argc != opts_count):
            errors.error_exit(errors.ARGS_ERR)

        ##############################
        input_file = sys.stdin
        source_file = sys.stdin
        stats_file = None
        source_flag = 0
        input_flag = 0
        insts_flag = False
        vars_flag = False
        insts_first_flag = False

        for o, a in opts:
            if (o == "--help") and (argc == 1):
                print(HELP_MSG)
                exit(errors.SCRIPT_SUCC)
            elif (o == "--source"):
                source_flag = 1
                source_file = abspath(a)
                # Is it file?
                if not(os.path.isfile(source_file)):
                    errors.error_exit(errors.INPUT_FILE_ERR)
            elif (o == "--input"):
                input_flag = 1
                input_file = abspath(a)
                # Is it file?
                if not(os.path.isfile(input_file)):
                    errors.error_exit(errors.INPUT_FILE_ERR)
            elif (o == "--stats"):
                stats_file = abspath(a)
                # Is it file?
            elif (o == "--insts"):
                if vars_flag == True:
                    insts_first_flag = False
                insts_flag = True
                stats_flag = False
                for o, a in opts:
                    if (o == "--stats"):
                        stats_flag = True
                if (stats_flag == False):
                    errors.error_exit(errors.ARGS_ERR)
            elif (o == "--vars"):
                if insts_flag == True:
                    insts_first_flag = True
                vars_flag = True
                stats_flag = False
                for o, a in opts:
                    if (o == "--stats"):
                        stats_flag = True
                if (stats_flag == False):
                    errors.error_exit(errors.ARGS_ERR)
            else:
                errors.error_exit(errors.ARGS_ERR)

        if (source_flag == 0) and (input_flag == 0):
            errors.error_exit(errors.ARGS_ERR)

        return (source_file, input_file, stats_file, insts_flag, vars_flag, insts_first_flag)
