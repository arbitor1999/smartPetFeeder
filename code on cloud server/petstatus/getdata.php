<?php
//     $type = $_GET["mod"];
$theID = $_GET["myid"];
$datatype = $_GET["data"];
$day = $_GET["day"];
$month = $_GET['month'];
$year = $_GET['year'];
$date = mktime(0,0,0,(int)$month,(int)$day,(int)$year);

session_start();
//  $theID = $_SESSION['id'];
// if($checkID == $theID)
# 温度数据
if((int)$datatype==1) {
    $file = "/home/info/temperature/".date("Y-m-d", $date).".txt";
}elseif ((int)$datatype==2) {
    $file = "/home/info/eat/".date("Y-m-d", $date).".txt";
}

    chmod($file,0774);
    $myfile = fopen($file,'r+');
    $info = fread($myfile,filesize($file));
    # echo $info;
    $array_info = explode("\n",$info);
    $temp_date = array();
    for ($i=0;$i<count($array_info)-1;$i++){
        $time = explode("@",$array_info[$i])[0];
        $data = explode("@",$array_info[$i])[1];
        $temp_date[$time]=$data;
    }
    fclose($myfile);
    echo json_encode($temp_date);

?>
