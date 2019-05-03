<?php
/******************************************************************************
 * Project:   2BIT IPP, Project                                               *
 *            Faculty of Information Technolgy                                *
 *            Brno University of Technology                                   *
 * File:      test.php                                                        *
 * Date:      13.03.2019                                                      *
 * Author:    Peter Kruty, xkruty00                                           *
 ******************************************************************************/

/********************************** Modules ***********************************/
include "lib_parse/errors.php";

/* Tests stats */
$tests_counter = 0;
$succ_counter = 0;
$fail_counter = 0;
$succ_rate = 0;

/* HTML output */
$html_begin = "<!DOCTYPE html> <html> ";
$html_head_begin = "<head> <title>IPPcode19 tests</title> <meta charset=\"UTF-8\"> ";
$html_table_style = "<style> table, th, td { border: 1px solid black; } </style> ";
$html_head_end = "</head> ";
$html_body_begin = "<body> ";
$html_body = "<h1 align=\"center\"> Testy skriptu \"parse.php\", \"interpret.py\" </h1> ".
             "<h2 align=\"center\"> Pocet testu: $tests_counter</h2> ".
             "<h2 align=\"center\"> Pocet uspesnych testu: $succ_counter</h2> ".
             "<h2 align=\"center\"> Pocet chybnych testu: $fail_counter</h2> ".
             "<h2 align=\"center\"> Uspesnost testu: $succ_rate%</h2> ";
$html_table_begin = "<table style=\"width:75%\" align=\"center\"> <tr> <th>USPESNOST</th> <th>NAZEV TESTU</th> <th>ADRESAR TESTU</th> <th>TESTOVACI SKRIPT</th> </tr> ";
$html_table = "";
$html_table_end = "</table> ";
$html_body_end = "</body> ";
$html_end = "</html>";

/* Help message */
const HELP_MSG = "NAPOVEDA SKRIPTU \"test.php\"\n\n" .
"POPIS\n" .
"\tSkript slouzi pro automaticke testovani postupne aplikace \"parse.php\" a \"interpret.py\". ".
"Skript projde zadany adresar s testy a vyuzije je pro automaticke otestovani spravne ".
"funknosti obou predchozich programu vcetne vygenerovani prehledneho souhrnu v HTML ".
"5 do standardniho vystupu.\n\n".
"NAPOVEDA\n".
"\t--help\t                Vypise na stardni vystup napovedu skriptu\n\n".
"\t--directory=path\tTesty bude hledat v zadanem adresari (chybi-li tento parametr, ".
"tak skript prochazi aktualni adresar)\n\n".
"\t--recursive\t        Testy bude hledat nejen v zadanem adresari, ale i rekurzivne ve vsech jeho podadresarich\n\n".
"\t--parse-script=file\tSoubor se skriptem v PHP 7.3 pro analyzu zdrojoveho kodu v IPPcode19 ".
"(chybi-li tento parametr, tak implicitni hodnotu je \"parse.php\" v aktualnim adresari)\n\n".
"\t--int-script=file\tSoubor se skriptem v Python 3.6 pro interpret XML reprezentace kodu v IPPcode19 ".
"(chybi-li tento parametr, tak implicitni hodnotou je \"interpret.py\" ulozeny v aktualnim adresari)\n\n".
"\t--parse-only\t        Bude testovan pouze skript pro analyzu zdrojoveho kodu v IPPcode19 ".
"(tento parametr se nesmi kombinovat s parametrem \"--int-script\")\n\n".
"\t--int-only\t        Bude testovan pouze skript pro interpret XML reprezentace kodu v IPPcode19 ".
"(tento parametr se nesmi kombinovat s parametrem \"--parse-script\")\n\n";

/* Paths */
$directory = getcwd();
$parse_script = getcwd() . "/parse.php";
$int_script = getcwd() . "/interpret.py";

/***************************** ARGUMENTS HANDLING *****************************/
$int_only_flag = false;
$parse_only_flag = false;
$recursive_flag = false;
$real_argc = 1;

/* Long options */
$long_arg_opts = array(
  "help",
  "directory:",
  "recursive",
  "parse-script:",
  "int-script:",
  "parse-only",
  "int-only",
);

/* Short options */
$short_arg_opts = "";

/* Parsing script parameters */
$arg_opts = getopt($short_arg_opts, $long_arg_opts);

if (array_key_exists("help", $arg_opts) && ($argc == 2)) {
  echo HELP_MSG;
  return SCRIPT_SUCC;
}
if (array_key_exists("directory", $arg_opts)) {
  if (array_key_exists("testlist", $arg_opts)) {
    error_exit(ARGS_ERR); // Function from errors.php
  }
  $real_argc++;
  /* Conversion to realpath */
  $directory = realpath($arg_opts["directory"]);
}
if (array_key_exists("int-script", $arg_opts)) {
  if (array_key_exists("parse-only", $arg_opts)) {
    error_exit(ARGS_ERR); // Function from errors.php
  }
  $real_argc++;
  /* Conversion to realpath */
  $int_script = realpath($arg_opts["int-script"]);
}
if (array_key_exists("parse-script", $arg_opts)) {
  if (array_key_exists("int-only", $arg_opts)) {
    error_exit(ARGS_ERR); // Function from errors.php
  }
  $real_argc++;
  /* Conversion to realpath */
  $parse_script = realpath($arg_opts["parse-script"]);
}
if (array_key_exists("int-only", $arg_opts)) {
  if (array_key_exists("parse-only", $arg_opts)) {
    error_exit(ARGS_ERR); // Function from errors.php
  }
  $real_argc++;
  $int_only_flag = true;
}
if (array_key_exists("parse-only", $arg_opts)) {
  $real_argc++;
  $parse_only_flag = true;
}
if (array_key_exists("recursive", $arg_opts)) {
  $real_argc++;
  $recursive_flag = true;
}

if ($argc != $real_argc) {
  error_exit(ARGS_ERR); // Function from errors.php
}

/******************** Kontrola ci su vsetky skripty dostupne ******************/
/* Testing only parser */
if ($parse_only_flag ) {
  if (!file_exists($parse_script)) {
    error_exit(INPUT_FILE_ERR);
  }
}
/* Testing only interpret */
else if ($int_only_flag ) {
  if (!file_exists($int_script)) {
    error_exit(INPUT_FILE_ERR);
  }
}
/* Testing both */
else {
  if (!file_exists($parse_script)) {
    error_exit(INPUT_FILE_ERR);
  }
  if (!file_exists($int_script)) {
    error_exit(INPUT_FILE_ERR);
  }
}
/* Kontrola priecinku s testami */
if (!is_dir($directory)) {
  error_exit(INPUT_FILE_ERR);
}

/*----------------------------------------------------------------------*/
/* Get all file paths */
$files = array();
if ($recursive_flag) {
  /* Directory iterator*/
  $file_iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($directory));

  foreach ($file_iterator as $file) {
    if (!is_dir($file)) {
      array_push($files, $file->getPathname());
    }
  }
}
else {
  $files = glob($directory.'/*.{src,in,out,rc}', GLOB_BRACE);
}

/* All .src files */
$src_files = preg_grep('/.*.src/', $files);

/* .src files not found */
if (!$src_files) {
  echo $html_begin;
  echo $html_head_begin;
  echo $html_table_style;
  echo $html_head_end;
  echo $html_body_begin;
  echo $html_body;
  echo $html_table_begin;
  echo $html_table_end;
  echo $html_body_end;
  echo $html_end;

  return SCRIPT_SUCC;
}

foreach ($src_files as $f_src) {
  /* File names */
  $f_out = str_replace("src", 'out', $f_src);
  $f_rc = str_replace("src", 'rc', $f_src);
  $f_in = str_replace("src", 'in', $f_src);
  $f_moj_out = str_replace("src", 'moj_out', $f_src);
  $f_moj_out2 = str_replace("src", 'moj_out2', $f_src);


  /* Checking, if files exists */
  /* test.in */
  if (!in_array($f_in, $files)) {
    if (!($in_file = fopen($f_in, "w"))) {
      error_exit(INTERNAL_ERR);
    }
    if (!fclose($in_file)) {
      error_exit(INTERNAL_ERR);
    }
  }
  /* test.out */
  if (!in_array($f_out, $files)) {
    if (!($out_file = fopen($f_out, "w"))) {
      error_exit(INTERNAL_ERR);
    }
    if (!fclose($out_file)) {
      error_exit(INTERNAL_ERR);
    }
  }
  /* test.rc */
  if (!in_array($f_rc, $files)) {
    if (file_put_contents($f_rc, "0") != true) {
      error_exit(INTERNAL_ERR);
    }
  }

  /* For HTML output */
  $f_directory = preg_replace('~/.*/~', '', $directory);
  $f_name = preg_replace('~/.*/~', '' , $f_src);
  $f_name = str_replace('.src', '' , $f_name);
  $script_name = "";

  /* Test arbitrators */
  $rc_ok = 0;
  $out_ok = 0;

  /************************* Testing only parse.php ***************************/
  if ($parse_only_flag) {
    $script_name = "parse.php";

    exec("php7.3 $parse_script <$f_src >$f_moj_out", $parse_out, $moj_rc);

    /* Return code comaparison */
    $rc = file_get_contents($f_rc);
    $rc_ok = ($rc == $moj_rc);

    /* Output comparison */
    if (!$moj_rc) { /* Compare, if RC == 0 */
      //exec("java -jar jexamxml/jexamxml.jar $f_moj_out $f_out diffs.xml /D jexamxml/options", $parse_diff, $parse_out_ok);
      exec("java -jar /pub/courses/ipp/jexamxml/jexamxml.jar $f_moj_out $f_out diffs.xml /D /pub/courses/ipp/jexamxml/options", $parse_diff, $parse_out_ok);
      $out_ok = !$parse_out_ok;
    }
    else {
      $out_ok = 1;
    }
    exec("rm $f_moj_out");
    //exec("rm $f_moj_out.log");

  }

  /************************ Testing only interpret.py *************************/
  else if ($int_only_flag) {
    $script_name = "interpret.py";

    exec("python3.6 $int_script --source=$f_src <$f_in >$f_moj_out", $int_out, $moj_rc);

    /* Return code comparison */
    $rc = file_get_contents($f_rc);
    $rc_ok = ($rc == $moj_rc);

    /* Output comparison */
    if (!$moj_rc) { /* Compare, if RC == 0 */
      exec("diff $f_out $f_moj_out", $diff_diff, $int_out_ok);
      $out_ok = !$int_out_ok;
    }
    else {
      $out_ok = 1;
    }

    exec("rm $f_moj_out");
  }

  /******************** Testing parse.php and intrepret.py ********************/
  else {
    $script_name = "parse.php + interpret.py";

    exec("php7.3 $parse_script <$f_src >$f_moj_out", $parse_out, $parse_rc);
    /* parse.php OK */
    if ($parse_rc == 0) {
      exec("python3.6 $int_script --source=$f_moj_out <$f_in >$f_moj_out2", $int_out, $int_rc);

      /* Return code comparison */
      $rc = file_get_contents($f_rc);
      $rc_ok = ($int_rc == $rc);

      /* Output comparison */
      if (!$int_rc) { /* Compare, if RC == 0 */
        exec("diff $f_out $f_moj_out2", $diff_diff, $int_out_ok);
        $out_ok = !$int_out_ok;
      }
      else {
        $out_ok = 1;
      }
      exec("rm $f_moj_out");
      exec("rm $f_moj_out2");
    }
    /* parse.php not OK */
    else {
      $rc = file_get_contents($f_rc);
      $rc_ok = ($parse_rc == $rc);
      $out_ok = 1;
    }
  }

  /* HTML Output - test */
  if ($out_ok && $rc_ok) {
    $succ_counter++;
    $html_table .= "<tr bgcolor=\"#33CC33\" align=\"center\"> <td>OK</td> <td>$f_name</td> <td>$f_directory</td> <td>$script_name</td> </tr> ";
  }
  else {
    $fail_counter++;
    if (!$out_ok && !$rc_ok) {
      $html_table .= "<tr bgcolor=\"#FF6666\" align=\"center\"> <td>CHYBA: Vystup + Navratovy kod</td> <td>$f_name</td> <td>$f_directory</td> <td>$script_name</td> </tr> ";
    }
    else if (!$out_ok) {
      $html_table .= "<tr bgcolor=\"#FF6666\" align=\"center\"> <td>CHYBA: Vystup</td> <td>$f_name</td> <td>$f_directory</td> <td>$script_name</td> </tr> ";
    }
    else if (!$rc_ok) {
      $html_table .= "<tr bgcolor=\"#FF6666\" align=\"center\"> <td>CHYBA: Navratovy kod</td> <td>$f_name</td> <td>$f_directory</td> <td>$script_name</td> </tr> ";
    }
  }
}

/* Tests stats */
$tests_counter = $succ_counter + $fail_counter;
if ($tests_counter != 0) {
  $succ_rate = ($succ_counter / $tests_counter)*100;
}
$html_body = "<h1 align=\"center\"> Testy skriptu \"parse.php\", \"interpret.py\" </h1> ".
             "<h2 align=\"center\"> Pocet testu: $tests_counter</h2> ".
             "<h2 align=\"center\"> Pocet uspesnych testu: $succ_counter</h2> ".
             "<h2 align=\"center\"> Pocet chybnych testu: $fail_counter</h2> ".
             "<h2 align=\"center\"> Uspesnost testu: $succ_rate%</h2> ";

/* HTML output */
echo $html_begin;
echo $html_head_begin;
echo $html_table_style;
echo $html_head_end;
echo $html_body_begin;
echo $html_body;
echo $html_table_begin;
echo $html_table;
echo $html_table_end;
echo $html_body_end;
echo $html_end;

?>
