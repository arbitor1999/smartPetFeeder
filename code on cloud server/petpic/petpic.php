<?php
session_start();
$login = $_POST["change"];
$usr = $_COOKIE['username'];
$local = "location:/petpic/petpic.phtml";
$search = $_POST['search'];
if ($login != '') {
    switch ($login){
        case "喂食设置":
            $route = "location:/set_feed_time/clockadder.phtml";
            break;
        case "宠物照片":
            $route ="location:/petpic/petpic.phtml";
            break;
        case "饮食情况":
            $route ="location:/petstatus/drawgraph.phtml";
            break;
        case "报警信息":
            $route ="location:/warn/warn.phtml";
            break;
        default:
            $route = $local;
    }
    header($route);
}
if($search=='查询'){
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
    $target_db = $uid.'_petpic';

    # input from UI
    $year =$_POST['year'];
    $month=$_POST['month'];
    $day  =$_POST['day'];
    $date =$year.'-'.$month.'-'.$day;
    $type = $_POST['type'];
    echo $type.'<br>';
    echo 'date '.$date.'<br>';
    $match=array('猫'=>'b','狗'=>'a');
    $pic_sql = "SELECT * FROM `$target_db` WHERE  `pic_time`= '$date' AND `pic_label`='$type' ";
    if($pic_result = mysqli_query($conn, $pic_sql)){
        echo $pic_sql.'success!';
    } else {
        echo "Error: " . $pic_sql . "<br>" . mysqli_error($conn);
    }

    $picture_route =fopen('./pic_route.txt','w+') or die("Unable to open file!");
    while ($all_row = mysqli_fetch_array($pic_result)){
        $temp_route = $all_row['pic_route'];
        $temp_date = $all_row['pic_time'];
        $temp_pet_id = $all_row['pet_id'];
        $temp_label = $all_row['pic_label'];
        $temp = $temp_pet_id.' '.$temp_route.' '.$temp_date.' '.$temp_label."\n";
        fwrite($picture_route, $temp);
    }
    mysqli_close($conn);
    fclose($picture_route);
    header($local);
}
?>
