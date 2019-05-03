<?php
/******************************************************************************
 * Project:   2BIT IPP, Project                                               *
 *            Faculty of Information Technolgy                                *
 *            Brno University of Technology                                   *
 * File:      parse.php                                                       *
 * Date:      13.03.2019 (06.03.2019)                                         *
 * Author:    Peter Kruty, xkruty00                                           *
 ******************************************************************************/

/********************************** MODULES ***********************************/
include "lib_parse/errors.php";
include "lib_parse/parser.php";

/************************** CONSTATNS AND VARIABLES ***************************/
/* Stats Counters */
$instruction_counter = 0;
$comment_counter = 0;
$label_counter = 0;
$jump_counter = 0;
$labels = array();

/* Help message */
const HELP_MSG = "NAPOVEDA SKRIPTU \"parse.php\"\n\n".
"POPIS\n".
"\tSkript typu filtr nacte ze standardniho vstupu zdrojovy kod v IPPcode19,".
" zkontroluje lexikalni a syntaktickou spravnost kodu a vypise na standardni".
" vystup XML reprezentaci programu.\n\n".
"MOZNOSTI\n".
"\t--help\t        Vypise na standardni vystup napovedu skriptu\n\n".
"\t--stats=file\tSkript sesbira statistiky a zapise je do vystupniho souboru ".
"\"file\" na zaklade poradi nasledujucich parametru:\n\n".
"\t\t--loc\t        Vypise do statistik pocet radku s instrukcemi\n\n".
"\t\t--comments\tVypise do statistik pocet radku, na kterych se vyskytoval komentar\n\n".
"\t\t--labels\tVypise do statistik pocet definovanych navesti\n\n".
"\t\t--jumps\t        Vypise do statistik pocet instrukci pro podminene a nepodminene skoky dohromady\n\n";

/***************************** ARGUMENTS PARSING *****************************/
/* Long options */
$long_arg_opts = array(
  "help",
  "stats:",
  "loc",
  "comments",
  "labels",
  "jumps",
);
/* Short options */
$short_arg_opts = "";

/* Parsing script parameters */
$arg_opts = getopt($short_arg_opts, $long_arg_opts);

$real_argc = 1;
$stats_flag = false;

if ((array_key_exists("help", $arg_opts)) && ($argc == 2)) {
  echo HELP_MSG;
  return SCRIPT_SUCC;
}
else if (array_key_exists("stats", $arg_opts) && $arg_opts["stats"]) {
  $real_argc++;
  $stats_flag = true;
  if (array_key_exists("loc", $arg_opts)) {
    $real_argc++;
  }
  if (array_key_exists("comments", $arg_opts)) {
    $real_argc++;
  }
  if (array_key_exists("labels", $arg_opts)) {
    $real_argc++;
  }
  if (array_key_exists("jumps", $arg_opts)) {
    $real_argc++;
  }
  if ($real_argc != $argc) {
    error_exit(ARGS_ERR); // Function from errors.php
  }
}
/* Wrong structure of script arguments */
else if ($argc != 1) {
  error_exit(ARGS_ERR); // Function from errors.php
}

/******************************* INPUT PARSING ********************************/
$XML_output = parser(); // Function from parser.php

/**************************** XML OUTPUT PRINTING *****************************/
echo $XML_output;

/******************************** STATS OUTPUT ********************************/
if ($stats_flag) {
  /* File opening */
  $stats_fw = fopen($arg_opts["stats"], "w");
  if (!$stats_fw) {
    error_exit(OUTPUT_FILE_ERR);
  }

  /* Writting stats to file */
  foreach ($arg_opts as $k => $v) {
    if ($k == "loc") {
      fwrite($stats_fw, "$instruction_counter\n");
    }
    else if ($k == "comments") {
      fwrite($stats_fw, "$comment_counter\n");
    }
    else if ($k == "jumps") {
      fwrite($stats_fw, "$jump_counter\n");
    }
    else if ($k == "labels") {
      fwrite($stats_fw, "$label_counter\n");
    }
  }

  /* File closing */
  if (!fclose($stats_fw)) {
    error_exit(OUTPUT_FILE_ERR);
  }
}

return SCRIPT_SUCC;
?>
