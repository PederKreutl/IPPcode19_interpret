<?php
/******************************************************************************
 * Project:   2BIT IPP, Project                                               *
 *            Faculty of Information Technolgy                                *
 *            Brno University of Technology                                   *
 * File:      parser.php                                                      *
 * Date:      13.03.2019 (06.03.2019)                                         *
 * Author:    Peter Kruty, xkruty00                                           *
 ******************************************************************************/

/********************************** Modules ***********************************/
include "scanner.php";

const IPPCODE19_HEAD = ".IPPCODE19";

/* Operands types */
$arg_type = array(
  0 => "nil",
  1 => "int",
  2 => "string",
  3 => "bool",
  4 => "var",
  5 => "type",
  6 => "label",
);

/****************************** Syntax analysis *******************************/
function parser() {
  global $op_codes;
  global $arg_type;

  /* File is empty */
  if (feof(STDIN)) {
    return EOF;
  }

  global $comment_counter;

  /* IPPcode19 head parsing */
  $input_line = fgets(STDIN);

  $comment_test = preg_match('/#.*/', $input_line);
  if ($comment_test) {
    $comment_counter++;
  }

  $input_line = preg_replace('/#.*/', '', $input_line); /* Erase comment */
  $input_line = trim($input_line);
  $input_line = strtoupper($input_line);

  if ($input_line != IPPCODE19_HEAD) {
   error_exit(HEAD_ERR);
  }

  /* Creating XML head and program element */
  $dom = new DOMDocument("1.0", "UTF-8");
  $dom->formatOutput = true;
  $program = $dom->createElement("program");
  $program->setAttribute("language", "IPPcode19");
  $dom->appendChild($program);
  $instr_order = 1;

  while (($instruction_array = scanner()) != EOF) {
    /* Creating XML instruction element */
    $instruction = $dom->createElement("instruction");
    $instruction->setAttribute("order", $instr_order);
    $xml_instr = array_keys($op_codes, $instruction_array[0]); /* Need opcode of instruction */
    $instruction->setAttribute("opcode", $xml_instr[0]);
    $instr_order++;

    switch ($instruction_array[0]) {
      /* INSTRUCTION FORMAT 1: op_code */
      case $op_codes["CREATEFRAME"]:
      case $op_codes["PUSHFRAME"]:
      case $op_codes["POPFRAME"]:
      case $op_codes["RETURN"]:
      case $op_codes["BREAK"]:
        if (count($instruction_array) != 1) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        break;

      /* INSTRUCTION FORMAT 2: op_code <var> */
      case $op_codes["DEFVAR"]:
      case $op_codes["POPS"]:
        if (count($instruction_array) != 3) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if ($instruction_array[1] != 4) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        /* Creating XML argument element */
        $arg1 = $dom->createElement("arg1", $instruction_array[2]);
        $arg1->setAttribute("type", $arg_type[$instruction_array[1]]);
        $instruction->appendChild($arg1);

        break;

      /* INSTRUCTION FORMAT 3: op_code <symb> */
      case $op_codes["PUSHS"]:
      case $op_codes["WRITE"]:
      case $op_codes["EXIT"]:
      case $op_codes["DPRINT"]:
        if (count($instruction_array) != 3) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if (($instruction_array[1] < 0) || ($instruction_array[1] > 4)) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        /* Creating XML argument element */
        $arg1 = $dom->createElement("arg1", $instruction_array[2]);
        $arg1->setAttribute("type", $arg_type[$instruction_array[1]]);
        $instruction->appendChild($arg1);

        break;

      /* INSTRUCTION FORMAT 4: op_code <label> */
      case $op_codes["CALL"]:
      case $op_codes["LABEL"]:
      case $op_codes["JUMP"]:
        if (count($instruction_array) != 3) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if (($instruction_array[1] != 6) && ($instruction_array[1] != 5)) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        /* Creating XML argument element */
        $arg1 = $dom->createElement("arg1", $instruction_array[2]);
        $arg1->setAttribute("type", $arg_type[$instruction_array[1]]);
        $instruction->appendChild($arg1);

        break;

      /* INSTRUCTION FORMAT 5: op_code <var> <symb> */
      case $op_codes["MOVE"]:
      case $op_codes["INT2CHAR"]:
      case $op_codes["STRLEN"]:
      case $op_codes["TYPE"]:
      case $op_codes["NOT"]:
        if (count($instruction_array) != 5) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if ($instruction_array[1] != 4) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if (($instruction_array[3] < 0) || ($instruction_array[3] > 4)) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        /* Creating XML argument element */
        $arg1 = $dom->createElement("arg1", $instruction_array[2]);
        $arg1->setAttribute("type", $arg_type[$instruction_array[1]]);
        $instruction->appendChild($arg1);

        $arg2 = $dom->createElement("arg2", $instruction_array[4]);
        $arg2->setAttribute("type", $arg_type[$instruction_array[3]]);
        $instruction->appendChild($arg2);

        break;

      /* INSTRUCTION FORMAT 6: op_code <var> <type> */
      case $op_codes["READ"]:
        if (count($instruction_array) != 5) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if ($instruction_array[1] != 4) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if ($instruction_array[3] != 5) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        /* Creating XML argument element */
        $arg1 = $dom->createElement("arg1", $instruction_array[2]);
        $arg1->setAttribute("type", $arg_type[$instruction_array[1]]);
        $instruction->appendChild($arg1);

        $arg2 = $dom->createElement("arg2", $instruction_array[4]);
        $arg2->setAttribute("type", $arg_type[$instruction_array[3]]);
        $instruction->appendChild($arg2);

        break;

      /* INSTRUCTION FORMAT 7: op_code <var> <symb1> <symb2> */
      case $op_codes["ADD"]:
      case $op_codes["SUB"]:
      case $op_codes["MUL"]:
      case $op_codes["IDIV"]:
      case $op_codes["LT"]:
      case $op_codes["GT"]:
      case $op_codes["EQ"]:
      case $op_codes["AND"]:
      case $op_codes["OR"]:
      case $op_codes["STRI2INT"]:
      case $op_codes["CONCAT"]:
      case $op_codes["GETCHAR"]:
      case $op_codes["SETCHAR"]:
        if (count($instruction_array) != 7) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if ($instruction_array[1] != 4) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if (($instruction_array[3] < 0) || ($instruction_array[3] > 4)) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if (($instruction_array[5] < 0) || ($instruction_array[5] > 4)) {
          error_exit(OTHER_LEX_SYN_ERR);
        }

        /* Creating XML argument element */
        $arg1 = $dom->createElement("arg1", $instruction_array[2]);
        $arg1->setAttribute("type", $arg_type[$instruction_array[1]]);
        $instruction->appendChild($arg1);

        $arg2 = $dom->createElement("arg2", $instruction_array[4]);
        $arg2->setAttribute("type", $arg_type[$instruction_array[3]]);
        $instruction->appendChild($arg2);

        $arg3 = $dom->createElement("arg3", $instruction_array[6]);
        $arg3->setAttribute("type", $arg_type[$instruction_array[5]]);
        $instruction->appendChild($arg3);

        break;

      /* INSTRUCTION FORMAT 8: op_code <label> <symb1> <symb2> */
      case $op_codes["JUMPIFEQ"]:
      case $op_codes["JUMPIFNEQ"]:
        if (count($instruction_array) != 7) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if (($instruction_array[1] != 6) && ($instruction_array[1] != 5)) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if (($instruction_array[3] < 0) || ($instruction_array[3] > 4)) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        if (($instruction_array[5] < 0) || ($instruction_array[5] > 4)) {
          error_exit(OTHER_LEX_SYN_ERR);
        }
        /* Creating XML argument element */
        $arg1 = $dom->createElement("arg1", $instruction_array[2]);
        $arg1->setAttribute("type", $arg_type[$instruction_array[1]]);
        $instruction->appendChild($arg1);

        $arg2 = $dom->createElement("arg2", $instruction_array[4]);
        $arg2->setAttribute("type", $arg_type[$instruction_array[3]]);
        $instruction->appendChild($arg2);

        $arg3 = $dom->createElement("arg3", $instruction_array[6]);
        $arg3->setAttribute("type", $arg_type[$instruction_array[5]]);
        $instruction->appendChild($arg3);

        break;
    }
    $program->appendChild($instruction);
  }

  return $dom->saveXML();
}
?>
