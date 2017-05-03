<?php

header("Content-type: text/html");

$execOut = "";
$execErr = "";

$cablingTxt = "";

if (isset($_POST["getCabling"]))
{
  $cablingTxt = $_POST["getCabling"];
  $detid = $_POST["detid"];
  
  $detid = str_replace("\r", " ", $detid);
	$detid = str_replace("\n", "", $detid); 
  $detidSpl = explode(" ", $detid);
  
  $execTime = time();
  
  $inputFileName = "/tmp/pixelCablingIds_".$execTime.".dat";
  $outputXMLFileName = "/tmp/pixelTrackerMap_".$execTime.".xml";
  
  exec("echo > $inputFileName"); // create empty file
  for ($i = 0; $i < count($detidSpl); $i++)
  {
    if ($detidSpl[$i] != "" && $detidSpl[$i] != " ")
    {
      // right now only static (one) color is allowed
      exec("echo '$detidSpl[$i] 255 0 0' >> $inputFileName"); // append (>>) to the file 
    }
  } 
  $output = shell_exec("python PixelTrackerMap.py $inputFileName > $outputXMLFileName 2>&1");
  // echo "<pre>$output</pre>";
}
?>

<link rel="stylesheet" href="https://unpkg.com/purecss@0.6.2/build/pure-min.css" integrity="sha384-UQiGfs9ICog+LwheBSRCt1o5cbyKIHbwjWscjemyBMT9YCUMZffs6UqUTd0hObXD" crossorigin="anonymous">
<link rel="stylesheet" href="DATA/main.css">
<meta name="viewport" content="width=device-width, initial-scale=1">

<div class="pure-g">
  <div class= "pure-u-1-5">
    <div class="l-box">
      <img style="height: 6em;" src="http://radecs2017.vitalis-events.com/wp-content/uploads/2016/09/CERN_logo2.svg_.png"/>
    </div>
  </div>
  <div class= "pure-u-3-5">
    <div class="l-box">
      <h1> Pixel Cabling Viewer </h1>
    </div>
  </div>
    <div class= "pure-u-1-5">
    <div class="l-box">
      <img style="position: absolute; right: 1em; height: 6em" src="https://cms-docdb.cern.ch/cgi-bin/PublicDocDB/RetrieveFile?docid=3045&filename=CMSlogo_black_label_1024_May2014.png&version=3"/>
    </div>
  </div>
</div>

<div class="pure-g">
    <div class="pure-u-1-6">
      <div class="l-box">
        <form class="pure-form pure-form-stacked" enctype = "multipart/form-data" action = "pixelcablingweb.php" method = "POST">
            <legend>Insert pixel detIds to be marked:</legend>
        
            <textarea name="detid"  placeholder="353309700"><?php echo $detid ?></textarea>
        
            <button class="pure-button pure-button-primary" name="getCabling" type="submit" value="GetCabling">Get Cabling</button>
        </form>
      </div>
    </div>
    
    <div class="pure-u-5-6">
      <div class="l-box">
        <?php 
          if (isset($_POST["getCabling"]))
          {
            echo "<iframe src='xml_cabling_web_from_tmp.php?file=$outputXMLFileName'></iframe>";
          }
        ?>
      <div>
    </div>
</div>