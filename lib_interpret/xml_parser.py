################################################################################
# Project:   2BIT IPP, Project                                                 #
#            Faculty of Information Technolgy                                  #
#            Brno University of Technology                                     #
# File:      xml_parser.py                                                     #
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
import xml.etree.ElementTree as ET

################################# "CONSTANTS" ##################################
# INSTRUCTION FORMAT 1: op_code
O = ["CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK"]
# INSTRUCTION FORMAT 2: op_code <var>
OV = ["DEFVAR", "POPS"]
# INSTRUCTION FORMAT 3: op_code <symb>
OS = ["PUSHS", "WRITE", "EXIT", "DPRINT"]
# INSTRUCTION FORMAT 4: op_code <label>
OL = ["CALL", "LABEL", "JUMP"]
# INSTRUCTION FORMAT 5: op_code <var> <symb>
OVS = ["MOVE", "INT2CHAR", "STRLEN", "TYPE", "NOT"]
# INSTRUCTION FORMAT 6: op_code <var> <type>
OVT = ["READ"]
# INSTRUCTION FORMAT 7: op_code <var> <symb1> <symb2>
OVSS = ["ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT",
        "CONCAT", "GETCHAR", "SETCHAR"]
# INSTRUCTION FORMAT 8: op_code <label> <symb1> <symb2>
OLSS = ["JUMPIFEQ", "JUMPIFNEQ"]

# ALL OPCODES
OP_CODES = O + OV + OS + OL + OVS + OVT + OVSS + OLSS;

# ARGS TYPES
t_var = "var"
t_symb = ["var", "nil", "string", "int", "bool"]
t_type = "type"
t_label = "label"

# ARGS VALUES
v_var = "^(GF|TF|LF)@([a-zA-Z]|(_|-|\$|&|%|\*|!|\?))([a-zA-Z0-9]|(_|-|\$|&|%|\*|!|\?))*$" # variable
v_nil = "^nil$" # nil
v_int = "^[+-]?[0-9]+$" # int
v_string = "^(((?!#)(?!\s)(?!\\\\).)|(\\\\[0-9][0-9][0-9]))*$" # string
v_bool = "^(true|false)$" # bool
v_type = "^(int|string|bool)$" # type
v_label = "^([a-zA-Z]|(_|-|\$|&|%|\*|!|\?))([a-zA-Z0-9]|(_|-|\$|&|%|\*|!|\?))*$" # label

################################### CLASSES ####################################
# Parser of XML representation IPPcode19
class XMLParser:
########################## READING XML FILE INTO TREE ##########################
    def readXML(self, xml_file):
        try:
            xml_tree = ET.parse(xml_file)
            xml_root = xml_tree.getroot()
        except:
            errors.error_exit(errors.XML_WELLFORMED_ERR)
        return xml_root

############################# CHECKING XML ELEMENT #############################
    def checkXML(self, xml_root):
        self.checkXMLProgElement(xml_root)
        self.checkXMLInstrElement(xml_root)
        xml_root = self.reOrderInstructions(xml_root)
        self.checkXMLInstructions(xml_root)

######################### CHECKING INSTRUCTION ELEMENT #########################
    def checkXMLInstrElement(self, program):
        for instruction in program:
            if (instruction.tag != "instruction"):
                errors.error_exit(errors.XML_LEXSYN_ERR)
            if ("order" not in instruction.attrib):
                errors.error_exit(errors.XML_LEXSYN_ERR)
            if ("opcode" not in instruction.attrib) or (len(instruction.attrib) != 2):
                errors.error_exit(errors.XML_LEXSYN_ERR)
            instruction.attrib["opcode"] = instruction.attrib["opcode"].upper();
            if (instruction.attrib["opcode"] not in OP_CODES):
                errors.error_exit(errors.XML_LEXSYN_ERR)
            try:
                instruction.attrib["order"] = int(instruction.attrib["order"])
            except:
                errors.error_exit(errors.XML_LEXSYN_ERR)

########################## CHECKING PROGRAM ELEMENT ############################
    def checkXMLProgElement(self, program):
        if (program.tag != "program"):
            errors.error_exit(errors.XML_LEXSYN_ERR)
        for attr in program.attrib:
            if (attr != "language") and (attr != "name") and (attr != "description"):
                errors.error_exit(errors.XML_LEXSYN_ERR)
        if (program.attrib["language"] != "IPPcode19"):
            errors.error_exit(errors.XML_LEXSYN_ERR)

####################### CHECKING XML ELEMENTS INSTRUCTION ######################
    def checkXMLInstructions(self, program):
        instr_order = 0

        for instruction in program:
            instr_order += 1
            if (instruction.attrib["order"] != instr_order):
                errors.error_exit(errors.XML_LEXSYN_ERR)

            # Checking element argument
            self.checkXMLArg(instruction)

            # INSTRUCTION FORMAT 1: op_code
            if (instruction.attrib["opcode"] in O):
                # Checking instruction length
                self.checkInstrLen(instruction, 0)

            # INSTRUCTION FORMAT 2: op_code <var>
            if (instruction.attrib["opcode"] in OV):
                # Checking instruction length
                self.checkInstrLen(instruction, 1)
                # Checking argument type
                self.checkArgType(instruction[0], t_var)
                # Checking argument value
                self.checkArgVal(instruction[0])

            # INSTRUCTION FORMAT 3: op_code <symb>
            if (instruction.attrib["opcode"] in OS):
                # Checking instruction length
                self.checkInstrLen(instruction, 1)
                # Checking argument type
                self.checkArgType(instruction[0], t_symb)
                # Checking argument value
                self.checkArgVal(instruction[0])

            # INSTRUCTION FORMAT 4: op_code <label>
            if (instruction.attrib["opcode"] in OL):
                # Checking instruction length
                self.checkInstrLen(instruction, 1)
                # Checking argument type
                self.checkArgType(instruction[0], t_label)
                # Checking argument value
                self.checkArgVal(instruction[0])

            # INSTRUCTION FORMAT 5: op_code <var> <symb>
            if (instruction.attrib["opcode"] in OVS):
                # Checking instruction length
                self.checkInstrLen(instruction, 2)
                # Checking arguments type
                self.checkArgType(instruction[0], t_var)
                self.checkArgType(instruction[1], t_symb)
                # Checking argument value
                self.checkArgVal(instruction[0])
                self.checkArgVal(instruction[1])

            # INSTRUCTION FORMAT 6: op_code <var> <type>
            if (instruction.attrib["opcode"] in OVT):
                # Checking instruction length
                self.checkInstrLen(instruction, 2)
                # Checking arguments type
                self.checkArgType(instruction[0], t_var)
                self.checkArgType(instruction[1], t_type)
                # Checking argument value
                self.checkArgVal(instruction[0])
                self.checkArgVal(instruction[1])

            # INSTRUCTION FORMAT 7: op_code <var> <symb1> <symb2>
            if (instruction.attrib["opcode"] in OVSS):
                # Checking instruction length
                self.checkInstrLen(instruction, 3)
                # Checking arguments type
                self.checkArgType(instruction[0], t_var)
                self.checkArgType(instruction[1], t_symb)
                self.checkArgType(instruction[2], t_symb)
                # Checking argument value
                self.checkArgVal(instruction[0])
                self.checkArgVal(instruction[1])
                self.checkArgVal(instruction[2])

            # INSTRUCTION FORMAT 8: op_code <label> <symb1> <symb2>
            if (instruction.attrib["opcode"] in OLSS):
                # Checking instruction length
                self.checkInstrLen(instruction, 3)
                # Checking arguments type
                self.checkArgType(instruction[0], t_label)
                self.checkArgType(instruction[1], t_symb)
                self.checkArgType(instruction[2], t_symb)
                # Checking argument value
                self.checkArgVal(instruction[0])
                self.checkArgVal(instruction[1])
                self.checkArgVal(instruction[2])

########################## CHECKING INSTRUCTION LENGTH #########################
    def checkInstrLen(self, instruction, length):
        if (len(instruction) != length):
            errors.error_exit(errors.XML_LEXSYN_ERR)

########################### CHECKING XML ELEMENT ARG ###########################
    def checkXMLArg(self, instr):
        arg_order = 0

        for arg in instr:
            arg_order += 1
            arg_ref_tag = "arg" + str(arg_order)
            if (arg.tag != arg_ref_tag):
                errors.error_exit(errors.XML_LEXSYN_ERR)

            if ((arg.tag != arg_ref_tag) or ("type" not in arg.attrib) or (len(arg.attrib) != 1)):
                errors.error_exit(errors.XML_LEXSYN_ERR)

############################## CHECKING ARG TYPE ###############################
    def checkArgType(self, arg, type):
        if (arg.attrib["type"] not in type):
            errors.error_exit(errors.XML_LEXSYN_ERR)

############################# CHECKING ARG VALUE ###############################
    def checkArgVal(self, arg):
        if ((not arg.text) and (arg.attrib["type"] != "string")):
            errors.error_exit(errors.XML_LEXSYN_ERR)

        if (arg.attrib["type"] == "nil"):
            OK_flag = re.search(v_nil, arg.text)
        if (arg.attrib["type"] == "int"):
            OK_flag = re.search(v_int, arg.text)
        if (arg.attrib["type"] == "string"):
            if (arg.text == None):
                arg.text = ""
            OK_flag = re.search(v_string, arg.text)
        if (arg.attrib["type"] == "bool"):
            OK_flag = re.search(v_bool, arg.text)
        if (arg.attrib["type"] == "var"):
            OK_flag = re.search(v_var, arg.text)
        if (arg.attrib["type"] == "type"):
            OK_flag = re.search(v_type, arg.text)
        if (arg.attrib["type"] == "label"):
            OK_flag = re.search(v_label, arg.text)

        if (not OK_flag):
            errors.error_exit(errors.XML_LEXSYN_ERR)

######################### METHOD FOR reOrderInstructions #######################
    def takeInstrOrder(self, instruction):
        return instruction.attrib["order"]

########################### RE-ORDERING INSTRUCTIONS ###########################
    def reOrderInstructions(self, program):
        sorted_program = sorted(program, key=self.takeInstrOrder)
        i = 0
        for instruction in program:
            program[i] = sorted_program[i]
            program[i] = self.reOrderArgs(program[i])
            i += 1

        return program

############################ METHOD FOR reOrderArgs ############################
    def takeArgOrder(self, arg):
        return arg.tag

############################### RE-ORDERING ARGS ###############################
    def reOrderArgs(self, instruction):
        # Works only for instrunctions with < 10 arguments
        sorted_instruction = sorted(instruction, key=self.takeArgOrder)
        i = 0
        for arg in instruction:
            instruction[i] = sorted_instruction[i]
            i += 1

        return instruction
