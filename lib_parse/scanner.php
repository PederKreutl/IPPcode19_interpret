<?php
/******************************************************************************
 * Project:   2BIT IPP, Project                                               *
 *            Faculty of Information Technolgy                                *
 *            Brno University of Technology                                   *
 * File:      scanner.php                                                     *
 * Date:      13.03.2019 (06.03.2019)                                         *
 * Author:    Peter Kruty, xkruty00                                           *
 ******************************************************************************/

const EOF = -1;

/********************** INSTRUCTIONS - OPERATIONAL CODES **********************/
$op_codes = array(
  /* Frames instructions, Function calls */
  "MOVE" => 0, "CREATEFRAME" => 1, "PUSHFRAME" => 2, "POPFRAME" => 3,
  "DEFVAR" => 4, "CALL" => 5, "RETURN" => 6,
  /* Stack instructions */
  "PUSHS" => 7, "POPS" => 8,
  /* Arithmetic, bool, ... instructions */
  "ADD" => 9, "SUB" => 10, "MUL" => 11, "IDIV" => 12, "LT" => 13, "GT" => 14,
  "EQ" => 15, "AND" => 16, "OR" => 17, "NOT" => 18, "INT2CHAR" => 19, "STRI2INT" => 20,
  /* Input-Output instructions */
  "READ" => 21, "WRITE" => 22, "CONCAT" => 23, "STRLEN" => 24, "GETCHAR" => 25,
  "SETCHAR" => 26,
  /* Types */
  "TYPE" => 27,
  /* Jumps */
  "LABEL" => 28, "JUMP" => 29, "JUMPIFEQ" => 30,
  "JUMPIFNEQ" => 31, "EXIT" => 32,
  /* Debug instructions */
  "DPRINT" => 33, "BREAK" => 34,
);

/*************************** INSTRUCTIONS - Operands **************************/
$operands = array(
  '/^nil@nil$/' => 0, /* nil */
  '/^int@[+-]?[0-9]+$/' => 1, /* int */
  '/^string@(((?!\\\\).)|(\\\\[0-9][0-9][0-9]))*$/u' => 2, /* string */
  '/^bool@(true|false)$/' => 3, /* bool */
  '/^(GF|LF|TF)@([[:alpha:]]|(_|-|\$|&|%|\*|!|\?))([[:alnum:]]|(_|-|\$|&|%|\*|!|\?))*$/' => 4, /* variable */
  '/^(int|string|bool)$/' => 5, /* type */
  '/^([[:alpha:]]|(_|-|\$|&|%|\*|!|\?))([[:alnum:]]|(_|-|\$|&|%|\*|!|\?))*$/' => 6, /* label */
);

/*************************** Other program elements ***************************/
const COMMENT1 = '/^#/';
const COMMENT2 = '/.*#.*/';

/* Helpful regular expressions for lexical analysis */
const EMPTY_STRING = "";
const REPLACE_AMP = "/&/";
const REPLACE_COMMENT = '/#.*/';
const REPLACE_NIL = '/^nil@/';
const REPLACE_INT = '/^int@/';
const REPLACE_STRING = '/^string@/';
const REPLACE_BOOL = '/^bool@/';
const WHITESPACE = '/\s+/'; /* "\s" means any whitespace character */

/************************* Lexical analysis of 1 line *************************/
function scanner() {
  /* Stats counters */
  global $instruction_counter;
  global $comment_counter;
  global $label_counter;
  global $jump_counter;
  global $labels;

  global $op_codes;
  global $operands;

  /* Return array */
  $instruction_ret_array = array();

  /* Cycle for reading a line with instruction (skip empty lines and comments) */
  while (true) {

    /* End of file detection */
    if (feof(STDIN)) {
      return EOF;
    }

    /* Line reading */
    $input_line = fgets(STDIN);
    $input_line = trim($input_line); /* Trim whitespaces */

    /* Empty line => read new line */
    if ($input_line == EMPTY_STRING) {
      continue;
    }
    /* Comment => read new line */
    else if (preg_match(COMMENT1, $input_line)) {
      $comment_counter++;
      continue;
    }
    /* Instruction and comment => erase comment */
    else if (preg_match(COMMENT2, $input_line)) {
      $comment_counter++;
      $input_line = preg_replace(REPLACE_COMMENT, '', $input_line); /* Erase comment */
      $input_line = trim($input_line);
      break;
    }
    else {
      break;
    }
  }

  /*------------------------------ Instructions ------------------------------*/
  $instruction_counter++;
  $input_word = preg_split(WHITESPACE, $input_line); /* Split string to array of words */
  $input_word[0] = strtoupper($input_word[0]); /* Op code is case insensitive (strtoupper for instruction comparison) */
  $input_word_count = count($input_word);

  /*--------------------------- Op Code parsing ------------------------------*/
  if (!array_key_exists($input_word[0], $op_codes)) {
    error_exit(OP_CODE_ERR);
  }
  else {
    if ($input_word[0] == "CALL" || $input_word[0] == "RETURN" || $input_word[0] == "JUMP" || $input_word[0] == "JUMPIFEQ" || $input_word[0] == "JUMPIFNEQ") {
      $jump_counter++;
    }
    if ($input_word[0] == "LABEL") {
      if (count($input_word) == 2) {
        if (!in_array($input_word[1], $labels)) {
          array_push($labels, $input_word[1]);
          $label_counter++;
        }
      }
    }

    $input_word_count--; /* Will be used as index to array $input_word */

    /*-------------------------- Operands parsing ----------------------------*/
    while ($input_word_count) { /* While there is some operand */
      $wrong_operand = true; /* Flag for wrong operand */
      foreach ($operands as $k => $v) {
        if (preg_match($k, $input_word[$input_word_count])) {
          if ($v == 0) {  /* Trim nil  */
            $input_word[$input_word_count] = preg_replace(REPLACE_NIL, '', $input_word[$input_word_count]);
          }
          if ($v == 1) { /* Trim int */
            $input_word[$input_word_count] = preg_replace(REPLACE_INT, '', $input_word[$input_word_count]);
          }
          if ($v == 2) { /* Trim string */
            $input_word[$input_word_count] = preg_replace(REPLACE_STRING, '', $input_word[$input_word_count]);
            $input_word[$input_word_count] = preg_replace(REPLACE_AMP, '&amp;', $input_word[$input_word_count]); /* & in XML */
          }
          if ($v == 3) { /* trim bool */
            $input_word[$input_word_count] = preg_replace(REPLACE_BOOL, '', $input_word[$input_word_count]);
          }
          if (($v == 4) || ($v == 6)) { /* trim variable and label */
            $input_word[$input_word_count] = preg_replace(REPLACE_AMP, '&amp;', $input_word[$input_word_count]); /* & in XML */
          }
          array_push($instruction_ret_array, $input_word[$input_word_count]); /* Push operand to return array */
          array_push($instruction_ret_array, $v); /* Push operand number to return array */
          $wrong_operand = false; /* Operand is correct */
          break;
        }
      }
      if ($wrong_operand) {
        print("ahoj");

        error_exit(OTHER_LEX_SYN_ERR);
      }
      $input_word_count--; /* Next argument */
    }
    array_push($instruction_ret_array, $op_codes[$input_word[0]]); /* Push op code number to return array */
    $instruction_ret_array = array_reverse($instruction_ret_array); /* Reverse array for correct order */
  }

  return $instruction_ret_array;
}
?>
