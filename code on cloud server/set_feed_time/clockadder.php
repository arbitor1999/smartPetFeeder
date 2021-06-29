<?php
session_start();
$usr = $_COOKIE['username'];
$login = $_POST["change"];
$set = $_POST["set"];
$clear = $_POST["clear"];
$log = fopen('./log.txt','a+');
$local_route= "location:/set_feed_time/clockadder.phtml";
if ($login != '') {
    # navigate to other functions
    switch ($login) {
        case "喂食设置":
            $route = "location:/set_feed_time/clockadder.phtml";
            break;
        case "宠物照片":
            $route = "location:/petpic/petpic.phtml";
            break;
        case "饮食情况":
            $route = "location:/petstatus/drawgraph.phtml";
            break;
        case "报警信息":
            $route = "location:/warn/warn.phtml";
            break;
        default:
            $route = $local_route;
    }
    header($route);
}
if ($set=='设置' || $clear=='清除'){
    # database information
    $password = 'yshbscjt2021!';
    $dbname = "petfeeder";
    $servername = "localhost";
    $username = "root";
    $conn = mysqli_connect($servername,$username,$password,$dbname);
    if (!$conn){
        echo 'fail';
        die('Error:"'.mysqli_connect_error());
    }
    $user_sql = "SELECT `usr_id` FROM `user` WHERE `usr_name` LIKE '$usr'";
    $user_result = mysqli_query($conn, $user_sql);
    $row = mysqli_fetch_array($user_result);
    $uid = $row['usr_id'];
    $target_db = $uid.'_feedtime';

    # input from UI
    $hour=$_POST['hour'];
    $minute=$_POST['minute'];
    $time=$hour.":".$minute.":00";
    $weight=$_POST['weight'];

    if ($set=='设置'){
        $add_set_sql ="INSERT INTO `$target_db` (set_time, set_weight) VALUES ('$time', '$weight')";
        if(mysqli_query($conn, $add_set_sql)){
            echo 'success!';
        } else {
            echo "Error: " . $add_set_sql . "<br>" . mysqli_error($conn);
        }
    }

    if ($clear=='清除'){
        $add_set_sql ="DELETE FROM `$target_db` where `set_time`='$time'";
        if(mysqli_query($conn, $add_set_sql)){
            echo 'success!';
        } else {
            echo "Error: " . $add_set_sql . "<br>" . mysqli_error($conn);
        }
    }

    $all_sql="SELECT * FROM `$target_db`";
    $all_result = mysqli_query($conn, $all_sql);
    chmod("./setting.txt",0777);
    $all_setting = fopen('./setting.txt','w') or die('dafsdf');
    while ($all_row = mysqli_fetch_array($all_result)){
        $times = $all_row['set_time'];
        $weight = $all_row['set_weight'];
        $data = $times." ".$weight."\n";
        echo $data;
        fwrite($all_setting, $data);
    }

    mysqli_close($conn);
    header($local_route);
    fclose($log);
    fclose($all_setting);
}
?>