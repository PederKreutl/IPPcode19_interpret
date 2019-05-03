<?php
/******************************************************************************
 * Project:   2BIT IPP, Project                                               *
 *            Faculty of Information Technolgy                                *
 *            Brno University of Technology                                   *
 * File:      errors.php                                                      *
 * Date:      13.03.2019 (06.03.2019)                                         *
 * Author:    Peter Kruty, xkruty00                                           *
 ******************************************************************************/

/******************************** RETURN CODES ********************************/
const SCRIPT_SUCC = 0;
const ARGS_ERR = 10;
const INPUT_FILE_ERR = 11;
const OUTPUT_FILE_ERR = 12;
const INTERNAL_ERR = 99;

const HEAD_ERR = 21;
const OP_CODE_ERR = 22;
const OTHER_LEX_SYN_ERR = 23;

/******************************* ERROR MESSAGES *******************************/
const ARGS_ERR_MSG = "ERROR 10: Arguments error\n";
const INPUT_FILE_ERR_MSG = "ERROR 11: Input file error\n";
const OUTPUT_FILE_ERR_MSG = "ERROR 12: Output file error\n";
const INTERNAL_ERR_MSG = "ERROR 99: Internal error\n";

const HEAD_ERR_MSG = "ERROR 21: IPPcode19 head error\n";
const OP_CODE_ERR_MSG = "ERROR 22: Operational code error\n";
const OTHER_LEX_SYN_ERR_MSG = "ERROR 23: Lexical or syntax error\n";

/********************************* FUNCTIONS **********************************/
function error_exit($error_code) {
  switch ($error_code) {
    case ARGS_ERR:
      fwrite(STDERR, ARGS_ERR_MSG);
      break;
    case INPUT_FILE_ERR:
      fwrite(STDERR, INPUT_FILE_ERR_MSG);
      break;
    case OUTPUT_FILE_ERR:
      fwrite(STDERR, OUTPUT_FILE_ERR_MSG);
      break;
    case INTERNAL_ERR:
      fwrite(STDERR, INTERNAL_ERR_MSG);
      break;
    case HEAD_ERR:
      fwrite(STDERR, HEAD_ERR_MSG);
      break;
    case OP_CODE_ERR:
      fwrite(STDERR, OP_CODE_ERR_MSG);
      break;
    case OTHER_LEX_SYN_ERR:
      fwrite(STDERR, OTHER_LEX_SYN_ERR_MSG);
      break;
  }
  exit($error_code);
}
?>
