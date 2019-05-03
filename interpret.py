################################################################################
# Project:   2BIT IPP, Project                                                 #
#            Faculty of Information Technolgy                                  #
#            Brno University of Technology                                     #
# File:      interpret.py                                                      #
# Date:      11.04.2019 (03.04.2019)                                           #
# Author:    Peter Kruty, xkruty00                                             #
################################################################################

################################### MODULES ####################################
from lib_interpret import errors
from lib_interpret import arg_parser as AP
from lib_interpret import xml_parser as XP
import sys
import os.path
import re

################################### CLASSES ####################################
# Interpret of IPPcode19 XML representation
class Interpret:
    def __init__(self):
        self.GF = {}
        self.LF = None
        self.TF = None
        self.LF_stack = []
        self.call_stack = []
        self.labels = {}
        self.data_stack = []

    # Method gets value from variable
    def get_value_from_var(self, variable):
        var_frame1 = re.search("^(GF|TF|LF)@", variable) # FRAME DETECTION
        var1 = re.sub("^(GF|TF|LF)@", "", variable) # VAR NAME DETECTION

        if (var_frame1.group() == "GF@"):
            if (var1 not in self.GF):
                errors.error_exit(errors.VAR_NEXISTS_ERR)
            else:
                value = [self.GF[var1][0], self.GF[var1][1]]

        elif (var_frame1.group() == "LF@"):
            if (self.LF == None):
                errors.error_exit(errors.FRAME_NEXISTS_ERR)
            if (var1 not in self.LF):
                errors.error_exit(errors.VAR_NEXISTS_ERR)
            else:
                value = [self.LF[var1][0], self.LF[var1][1]]

        elif (var_frame1.group() == "TF@"):
            if (self.TF == None):
                errors.error_exit(errors.FRAME_NEXISTS_ERR)
            if (var1 not in self.TF):
                errors.error_exit(errors.VAR_NEXISTS_ERR)
            else:
                value = [self.TF[var1][0], self.TF[var1][1]]

        if value[0] == None:
            errors.error_exit(errors.MISS_VAL_ERR)

        return value

    # Method sets value to variable
    def set_value_to_var(self, variable, value):
        var_frame0 = re.search("^(GF|TF|LF)@", variable) # FRAME DETECTION
        var0 = re.sub("^(GF|TF|LF)@", "", variable) # VAR NAME DETECTION

        if (var_frame0.group() == "GF@"):
            if (var0 not in self.GF):
                errors.error_exit(errors.VAR_NEXISTS_ERR)
            else:
                self.GF[var0] = value

        elif (var_frame0.group() == "LF@"):
            if (self.LF == None):
                errors.error_exit(errors.FRAME_NEXISTS_ERR)
            if (var0 not in self.LF):
                errors.error_exit(errors.VAR_NEXISTS_ERR)
            else:
                self.LF[var0] = value

        elif (var_frame0.group() == "TF@"):
            if (self.TF == None):
                errors.error_exit(errors.FRAME_NEXISTS_ERR)
            if (var0 not in self.TF):
                errors.error_exit(errors.VAR_NEXISTS_ERR)
            else:
                self.TF[var0] = value

    # Method checks if operand is int type
    def checkIntOp(self, instruction):
        if instruction.attrib["type"] == "var":
            value = self.get_value_from_var(instruction.text)
            if (value[0] != "int"):
                errors.error_exit(errors.OP_TYPES_ERR)
            else:
                int_val = value[1]
        elif (instruction.attrib["type"] == "int"):
            int_val = instruction.text
        else:
            errors.error_exit(errors.OP_TYPES_ERR)

        return int_val

    # Method checks if operand is string type
    def checkStringOp(self, instruction):
        if instruction.attrib["type"] == "var":
            value = self.get_value_from_var(instruction.text)
            if (value[0] != "string"):
                errors.error_exit(errors.OP_TYPES_ERR)
            else:
                string_val = value[1]
        elif (instruction.attrib["type"] == "string"):
            string_val = instruction.text
        else:
            errors.error_exit(errors.OP_TYPES_ERR)

        return string_val

    # Method parse labels in XML IPPcode19
    def parseLabels(self, program):
        for instruction in program:
            # LABEL <label>
            if instruction.attrib["opcode"] == "LABEL":
                if (instruction[0].text in self.labels):
                    errors.error_exit(errors.IPPCODE19_SEM_ERR)
                else:
                    # Label Name                       Label Line
                    self.labels[instruction[0].text] = instruction.attrib["order"]

    # Method interprets XML IPPcode19
    def interprete(self, program):
        global stats_insts
        global stats_vars
        stats_vars = 0
        for instruction in program:
            stats_insts += 1
            stats_vars_new = 0
            if (self.GF):
                for var in self.GF:
                    if (self.GF[var][0] != None):
                        stats_vars_new += 1
            if (self.TF):
                for var in self.TF:
                    if (self.TF[var][0] != None):
                        stats_vars_new += 1
            if (self.LF):
                for var in self.LF:
                    if (self.LF[var][0] != None):
                        stats_vars_new += 1
            if (stats_vars_new > stats_vars):
                stats_vars = stats_vars_new

            for arg in instruction:
                # Convert "string int" to int
                if arg.attrib["type"] == "int":
                    arg.text = int(arg.text)
                # Convert "string bool" to bool
                if arg.attrib["type"] == "bool":
                    if arg.text == "true":
                        arg.text = True
                    else:
                        arg.text = False
                # Convert "string nil" to None
                if arg.attrib["type"] == "nil":
                    arg.text = None
                # Convert escape sequence to char
                if arg.attrib["type"] == "string":
                    esc = re.findall("\\\\\d\d\d", arg.text)
                    for escape_seq in esc:
                        arg.text = arg.text.replace(escape_seq, chr(int(escape_seq.lstrip('\\'))))

            ####################################################################
            # MOVE <var> <symb>
            if instruction.attrib["opcode"] == "MOVE":
                if (instruction[1].attrib["type"] == "var"):
                    value = self.get_value_from_var(instruction[1].text)
                else:
                    value = [instruction[1].attrib["type"], instruction[1].text]

                self.set_value_to_var(instruction[0].text, value)

            # CREATEFRAME
            if instruction.attrib["opcode"] == "CREATEFRAME":
                self.TF = {}

            # PUSHFRAME
            if instruction.attrib["opcode"] == "PUSHFRAME":
                if (self.TF != None):
                    self.LF_stack.append(self.TF)
                    self.LF = self.TF
                    self.TF = None
                else:
                    errors.error_exit(errors.FRAME_NEXISTS_ERR)

            # POPFRAME
            if instruction.attrib["opcode"] == "POPFRAME":
                if (self.LF != None):
                    self.TF = self.LF
                    self.LF_stack.pop()
                    if (self.LF_stack):
                        self.LF = self.LF_stack[len(self.LF_stack)-1]
                    else:
                        self.LF = None
                else:
                    errors.error_exit(errors.FRAME_NEXISTS_ERR)

            # DEFVAR <var>
            if instruction.attrib["opcode"] == "DEFVAR":
                var_frame = re.search("^(GF|TF|LF)@", instruction[0].text)
                var = re.sub("^(GF|TF|LF)@", "", instruction[0].text)

                if (var_frame.group() == "GF@"):
                    self.GF[var] = [None, None]
                elif (var_frame.group() == "LF@"):
                    if (self.LF != None):
                        self.LF[var] = [None, None]
                    else:
                        errors.error_exit(errors.FRAME_NEXISTS_ERR)
                elif (var_frame.group() == "TF@"):
                    if (self.TF != None):
                        self.TF[var] = [None, None]
                    else:
                        errors.error_exit(errors.FRAME_NEXISTS_ERR)

            # CALL <label>
            if instruction.attrib["opcode"] == "CALL":
                if (instruction[0].text not in self.labels):
                    errors.error_exit(errors.IPPCODE19_SEM_ERR)
                else:
                    self.call_stack.append(instruction.attrib["order"])
                    self.interprete(xml_root[int(self.labels[instruction[0].text]):]) # xml_root from main
                    break

            # RETURN
            if instruction.attrib["opcode"] == "RETURN":
                try:
                    ret_inst = self.call_stack.pop()
                except:
                    errors.error_exit(errors.MISS_VAL_ERR)

                self.interprete(xml_root[ret_inst:]) # xml_root from main
                break


            ####################################################################
            # PUSHS <symb>
            if instruction.attrib["opcode"] == "PUSHS":
                if (instruction[0].attrib["type"] == "var"):
                    value = self.get_value_from_var(instruction[0].text)
                else:
                    value = [instruction[0].attrib["type"], instruction[0].text]

                self.data_stack.append(value)

            # POPS <var>
            if instruction.attrib["opcode"] == "POPS":
                try:
                    value = self.data_stack[len(self.data_stack)-1]
                    self.data_stack.pop()
                except:
                    errors.error_exit(errors.MISS_VAL_ERR)

                self.set_value_to_var(instruction[0].text, value)

            ####################################################################
            # ADD <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "ADD":
                int1 = self.checkIntOp(instruction[1])
                int2 = self.checkIntOp(instruction[2])

                result = int1 + int2
                value = ["int", result]

                self.set_value_to_var(instruction[0].text, value)


            # SUB <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "SUB":
                int1 = self.checkIntOp(instruction[1])
                int2 = self.checkIntOp(instruction[2])

                result = int1 - int2
                value = ["int", result]

                self.set_value_to_var(instruction[0].text, value)


            # MUL <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "MUL":
                int1 = self.checkIntOp(instruction[1])
                int2 = self.checkIntOp(instruction[2])

                result = int1 * int2
                value = ["int", result]

                self.set_value_to_var(instruction[0].text, value)


            # IDIV <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "IDIV":
                int1 = self.checkIntOp(instruction[1])
                int2 = self.checkIntOp(instruction[2])

                if int2 == 0:
                    errors.error_exit(errors.WRONG_VAL_ERR)

                result = int1 // int2
                value = ["int", result]

                self.set_value_to_var(instruction[0].text, value)


            # LT <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "LT":
                if (instruction[1].attrib["type"] == "var"):
                    value1 = self.get_value_from_var(instruction[1].text)
                else:
                    value1 = [instruction[1].attrib["type"], instruction[1].text]

                if (instruction[2].attrib["type"] == "var"):
                    value2 = self.get_value_from_var(instruction[2].text)
                else:
                    value2 = [instruction[2].attrib["type"], instruction[2].text]

                # Different operand types
                if ((value1[0] != value2[0]) or (value1[0] == "nil")):
                    errors.error_exit(errors.OP_TYPES_ERR)

                # Compare
                result = value1[1] < value2[1]

                value = ["bool", result]

                self.set_value_to_var(instruction[0].text, value)

            # GT <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "GT":
                if (instruction[1].attrib["type"] == "var"):
                    value1 = self.get_value_from_var(instruction[1].text)
                else:
                    value1 = [instruction[1].attrib["type"], instruction[1].text]

                if (instruction[2].attrib["type"] == "var"):
                    value2 = self.get_value_from_var(instruction[2].text)
                else:
                    value2 = [instruction[2].attrib["type"], instruction[2].text]

                # Different operand types
                if ((value1[0] != value2[0]) or (value1[0] == "nil")):
                    errors.error_exit(errors.OP_TYPES_ERR)

                # Compare
                result = value1[1] > value2[1]

                value = ["bool", result]

                self.set_value_to_var(instruction[0].text, value)

            # EQ <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "EQ":
                if (instruction[1].attrib["type"] == "var"):
                    value1 = self.get_value_from_var(instruction[1].text)
                else:
                    value1 = [instruction[1].attrib["type"], instruction[1].text]

                if (instruction[2].attrib["type"] == "var"):
                    value2 = self.get_value_from_var(instruction[2].text)
                else:
                    value2 = [instruction[2].attrib["type"], instruction[2].text]

                if ((value1[0] != value2[0]) and (value1[0] != "nil" and value2[0] != "nil")):
                    errors.error_exit(errors.OP_TYPES_ERR)

                # Compare
                result = value1[1] == value2[1]

                value = ["bool", result]

                self.set_value_to_var(instruction[0].text, value)

            # AND <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "AND":
                if (instruction[1].attrib["type"] == "var"):
                    value1 = self.get_value_from_var(instruction[1].text)
                else:
                    value1 = [instruction[1].attrib["type"], instruction[1].text]

                if (instruction[2].attrib["type"] == "var"):
                    value2 = self.get_value_from_var(instruction[2].text)
                else:
                    value2 = [instruction[2].attrib["type"], instruction[2].text]

                if value1[0] != "bool":
                    errors.error_exit(errors.OP_TYPES_ERR)

                if value2[0] != "bool":
                    errors.error_exit(errors.OP_TYPES_ERR)

                # Compare
                result = value1[1] and value2[1]

                value = ["bool", result]

                self.set_value_to_var(instruction[0].text, value)

            # OR <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "OR":
                if (instruction[1].attrib["type"] == "var"):
                    value1 = self.get_value_from_var(instruction[1].text)
                else:
                    value1 = [instruction[1].attrib["type"], instruction[1].text]

                if (instruction[2].attrib["type"] == "var"):
                    value2 = self.get_value_from_var(instruction[2].text)
                else:
                    value2 = [instruction[2].attrib["type"], instruction[2].text]

                if value1[0] != "bool":
                    errors.error_exit(errors.OP_TYPES_ERR)

                if value2[0] != "bool":
                    errors.error_exit(errors.OP_TYPES_ERR)

                # Compare
                result = value1[1] or value2[1]

                value = ["bool", result]

                self.set_value_to_var(instruction[0].text, value)

            # NOT <var> <symb>
            if instruction.attrib["opcode"] == "NOT":
                if (instruction[1].attrib["type"] == "var"):
                    value1 = self.get_value_from_var(instruction[1].text)
                else:
                    value1 = [instruction[1].attrib["type"], instruction[1].text]

                if value1[0] != "bool":
                    errors.error_exit(errors.OP_TYPES_ERR)

                # Compare
                result = (not value1[1])
                value = ["bool", result]

                self.set_value_to_var(instruction[0].text, value)

            # INT2CHAR <var> <symb>
            if instruction.attrib["opcode"] == "INT2CHAR":
                if (instruction[1].attrib["type"] == "var"):
                    value1 = self.get_value_from_var(instruction[1].text)
                else:
                    value1 = [instruction[1].attrib["type"], instruction[1].text]

                if value1[0] != "int":
                    errors.error_exit(errors.OP_TYPES_ERR)

                try:
                    result = chr(value1[1])
                except:
                    errors.error_exit(errors.STRING_ERR)

                value = ["string", result]

                self.set_value_to_var(instruction[0].text, value)

            # STRI2INT <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "STRI2INT":
                if (instruction[1].attrib["type"] == "var"):
                    value1 = self.get_value_from_var(instruction[1].text)
                else:
                    value1 = [instruction[1].attrib["type"], instruction[1].text]

                if (instruction[2].attrib["type"] == "var"):
                    value2 = self.get_value_from_var(instruction[2].text)
                else:
                    value2 = [instruction[2].attrib["type"], instruction[2].text]

                if value1[0] != "string":
                    errors.error_exit(errors.OP_TYPES_ERR)

                if value2[0] != "int":
                    errors.error_exit(errors.OP_TYPES_ERR)

                try:
                    result = ord(value1[1][value2[1]])
                except:
                    errors.error_exit(errors.STRING_ERR)

                value = ["int", result]

                self.set_value_to_var(instruction[0].text, value)

            ####################################################################
            # READ <var> <type>
            if instruction.attrib["opcode"] == "READ":
                value2 = [instruction[1].attrib["type"], instruction[1].text]

                interpret_input = ""

                try:
                    interpret_input = input()
                except:
                    if (value2[1] == "int"):
                        value = ["int", 0]
                    elif (value2[1] == "string"):
                        value = ["string", ""]
                    elif (value2[1] == "bool"):
                        value = ["bool", False]

                if (value2[1] == "int"):
                    try:
                        value = ["int", int(interpret_input)]
                    except:
                        value = ["int", 0]
                elif (value2[1] == "string"):
                    try:
                        value = ["string", interpret_input]
                    except:
                        value = ["string", ""]
                elif (value2[1] == "bool"):
                    if (interpret_input.upper() == "TRUE"):
                        value = ["bool", True]
                    else:
                        value = ["bool", False]

                self.set_value_to_var(instruction[0].text, value)

            # WRITE <symb>
            if instruction.attrib["opcode"] == "WRITE":
                if (instruction[0].attrib["type"] == "var"):
                    value = self.get_value_from_var(instruction[0].text)
                else:
                    value = [instruction[0].attrib["type"], instruction[0].text]

                if value[0] == None:
                    errors.error_exit(errors.MISS_VAL_ERR)

                if value[0] == "nil":
                    value[1] = ""

                if value[0] == "bool":
                    if value[1] == True:
                        value[1] = "true"
                    elif value[1] == False:
                        value[1] = "false"

                print(value[1], end='')

            ####################################################################
            # CONCAT <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "CONCAT":
                string1 = self.checkStringOp(instruction[1])
                string2 = self.checkStringOp(instruction[2])

                value = ["string" ,string1 + string2]

                self.set_value_to_var(instruction[0].text, value)

            # STRLEN <var> <symb>
            if instruction.attrib["opcode"] == "STRLEN":
                string1 = self.checkStringOp(instruction[1])

                value = ["int", len(string1)]

                self.set_value_to_var(instruction[0].text, value)


            # GETCHAR <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "GETCHAR":
                string1 = self.checkStringOp(instruction[1])
                int2 = self.checkIntOp(instruction[2])

                try:
                    value = ["string", string1[int2]]
                except:
                    errors.error_exit(errors.STRING_ERR)

                self.set_value_to_var(instruction[0].text, value)

            # SETCHAR <var> <symb1> <symb2>
            if instruction.attrib["opcode"] == "SETCHAR":
                string0 = self.checkStringOp(instruction[0])
                int1 = self.checkIntOp(instruction[1])
                string2 = self.checkStringOp(instruction[2])

                try:
                    string0 = list(string0)
                    string0[int1] = string2[0]
                    string0 = ''.join(string0)
                except:
                    errors.error_exit(errors.STRING_ERR)

                value = ["string", string0]

                self.set_value_to_var(instruction[0].text, value)


            ####################################################################
            # TYPE <var> <symb>
            if instruction.attrib["opcode"] == "TYPE":
                if (instruction[1].attrib["type"] == "var"):
                    var_frame1 = re.search("^(GF|TF|LF)@", instruction[1].text) # FRAME DETECTION
                    var1 = re.sub("^(GF|TF|LF)@", "", instruction[1].text) # VAR NAME DETECTION

                    if (var_frame1.group() == "GF@"):
                        if (var1 not in self.GF):
                            errors.error_exit(errors.VAR_NEXISTS_ERR)
                        else:
                            value1 = [self.GF[var1][0], self.GF[var1][1]]

                    elif (var_frame1.group() == "LF@"):
                        if (self.LF == None):
                            errors.error_exit(errors.FRAME_NEXISTS_ERR)
                        if (var1 not in self.LF):
                            errors.error_exit(errors.VAR_NEXISTS_ERR)
                        else:
                            value1 = [self.LF[var1][0], self.LF[var1][1]]

                    elif (var_frame1.group() == "TF@"):
                        if (self.TF == None):
                            errors.error_exit(errors.FRAME_NEXISTS_ERR)
                        if (var1 not in self.TF):
                            errors.error_exit(errors.VAR_NEXISTS_ERR)
                        else:
                            value1 = [self.TF[var1][0], self.TF[var1][1]]
                else:
                    value1 = [instruction[1].attrib["type"], instruction[1].text]

                if (value1[0] == "int"):
                    value = ["string", "int"]
                elif (value1[0] == "string"):
                    value = ["string", "string"]
                elif (value1[0] == "bool"):
                    value = ["string", "bool"]
                elif (value1[0] == "nil"):
                    value = ["string", "nil"]
                else:
                    value = ["string", ""]

                self.set_value_to_var(instruction[0].text, value)

            ####################################################################
            # JUMP <label>
            if instruction.attrib["opcode"] == "JUMP":
                if (instruction[0].text not in self.labels):
                    errors.error_exit(errors.IPPCODE19_SEM_ERR)
                else:
                    self.interprete(xml_root[int(self.labels[instruction[0].text]):]) # xml_root from main
                    break


            # JUMPIFEQ <label> <symb1> <symb2>
            if instruction.attrib["opcode"] == "JUMPIFEQ":
                if (instruction[0].text not in self.labels):
                    errors.error_exit(errors.IPPCODE19_SEM_ERR)

                if (instruction[1].attrib["type"] == "var"):
                    value1 = self.get_value_from_var(instruction[1].text)
                else:
                    value1 = [instruction[1].attrib["type"], instruction[1].text]

                if (instruction[2].attrib["type"] == "var"):
                    value2 = self.get_value_from_var(instruction[2].text)
                else:
                    value2 = [instruction[2].attrib["type"], instruction[2].text]

                if (value1[0] != value2[0]):
                    errors.error_exit(errors.OP_TYPES_ERR)

                if (value1[1] == value2[1]):
                    self.interprete(xml_root[int(self.labels[instruction[0].text]):]) # xml_root from main
                    break

            # JUMPIFNEQ <label> <symb1> <symb2>
            if instruction.attrib["opcode"] == "JUMPIFNEQ":
                if (instruction[0].text not in self.labels):
                    errors.error_exit(errors.IPPCODE19_SEM_ERR)

                if (instruction[1].attrib["type"] == "var"):
                    value1 = self.get_value_from_var(instruction[1].text)
                else:
                    value1 = [instruction[1].attrib["type"], instruction[1].text]

                if (instruction[2].attrib["type"] == "var"):
                    value2 = self.get_value_from_var(instruction[2].text)
                else:
                    value2 = [instruction[2].attrib["type"], instruction[2].text]

                if (value1[0] != value2[0]):
                    errors.error_exit(errors.OP_TYPES_ERR)

                if (value1[1] != value2[1]):
                    self.interprete(xml_root[int(self.labels[instruction[0].text]):]) # xml_root from main
                    break

            # EXIT <symb>
            if instruction.attrib["opcode"] == "EXIT":
                int0 = self.checkIntOp(instruction[0])
                if ((int0 >= 0) and (int0 <= 49)):
                    return int0
                else:
                    errors.error_exit(errors.WRONG_VAL_ERR)


            ####################################################################
            # DPRINT <symb>
            if instruction.attrib["opcode"] == "DPRINT":
                if (instruction[0].attrib["type"] == "var"):
                    value = self.get_value_from_var(instruction[0].text)
                else:
                    value = [instruction[0].attrib["type"], instruction[0].text]

                print(value[1], file=sys.stderr, end='')

            # BREAK
            if instruction.attrib["opcode"] == "BREAK":
                print("Position in code:\t", instruction.attrib["order"], file=sys.stderr)
                print("Global frame:\t\t", self.GF, file=sys.stderr)
                print("Local frame:\t\t",self.LF, file=sys.stderr)
                print("Temporary frame:\t",self.TF, file=sys.stderr)
                print("Local frames stack:\t",self.LF_stack, file=sys.stderr)
                print("Labels:\t\t\t",self.labels, file=sys.stderr)
                print("Calls stack:\t\t",self.call_stack, file=sys.stderr)
                print("Data stack:\t\t",self.data_stack, file=sys.stderr)

        # Interpret ends
        return errors.SCRIPT_SUCC

##################################### MAIN #####################################
stats_insts = 0
stats_vars = 0
# CREATING OBJECT ARGUMENTS PARSER
args_parser = AP.ArgsParser()
# PARSING ARGUMENTS
src_file, input_file, stats_file, insts_flag, vars_flag, insts_first_flag = args_parser.parseArguments()

# CHANGING STDIN
if (input_file != sys.stdin):
    old_stdin = sys.stdin
    sys.stdin = open(input_file)

# CREATING OBJECT XML PARSER
xml_parser = XP.XMLParser()
# READING XML FILE INTO TREE
xml_root = xml_parser.readXML(src_file)
# CHECKING XML ELEMENTS
xml_parser.checkXML(xml_root)

# CREATING OBJECT INTERPRET
interpret = Interpret()

# LABELS VERIFICATION
interpret.parseLabels(xml_root)

# Interpretation
interpret_rc = interpret.interprete(xml_root)

# Stats print
if (stats_file):
    stats_file = open(stats_file, "w")
    if insts_first_flag == True:
        if insts_flag:
            print(stats_insts, file=stats_file)
        if vars_flag:
            print(stats_vars, file=stats_file)
    else:
        if vars_flag:
            print(stats_vars, file=stats_file)
        if insts_flag:
            print(stats_insts, file=stats_file)
    stats_file.close()

exit(interpret_rc)
