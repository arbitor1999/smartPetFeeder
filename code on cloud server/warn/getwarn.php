<?php
//     $type = $_GET["mod"];
session_start();
//  $theID = $_SESSION['id'];
// if($checkID == $theID)
{
    $servername = "localhost";
    $username = "root";
    $password = "yshbscjt2021!";
    $dbname = "petfeeder";
    $conn = mysqli_connect($servername, $username, $password,$dbname);
    $warn_query = "SELECT * FROM `1_warning` ORDER BY `warn_date` DESC,`warn_time` DESC ";
    $result = mysqli_query($conn,$warn_query);

    if(!mysqli_query($conn, $warn_query)){
        echo "Error: " . $warn_query . "<br>" . mysqli_error($conn);
    }

    $warn_date=array();
    $warn_time=array();
    $warn_label=array();

    while ($all_row = mysqli_fetch_array($result)){
        $tempX = $all_row['warn_date'];
        $tempY = $all_row['warn_time'];
        $tempZ = $all_row['warn_label'];
        array_push($warn_date,$tempX);
        array_push($warn_time,$tempY);
        array_push($warn_label,$tempZ);
    }

    echo json_encode(array('warn_date' => $warn_date, 'warn_time' => $warn_time, 'warn_label' => $warn_label));
}
?>