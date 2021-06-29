<?php
$servername = "localhost";
$username = "root";
define('STDOUT',fopen('php://stdout', 'a'));
function stdout($c){
    fwrite(STDOUT, $c);
}
$password = 'yshbscjt2021!';
$dbname = "petfeeder";
$conn = mysqli_connect($servername,$username,$password,$dbname);
if (!$conn)
{
    echo 'fail';
    die('Error:"'.mysqli_connect_error());
}
else echo 'success!';
session_start();
if ($_SERVER["REQUEST_METHOD"] == "POST") {

    $login = $_POST["login"];
    $register = $_POST['register'];
    $pwd = $_POST["password"];
    $usr = $_POST["username"];
    stdout($login);
    echo $login.'<br>';
    echo $pwd, $usr;
    if($login=='登录'){
        if ($usr != NULL && $pwd != NULL) {
        $sql = "SELECT * FROM `user` WHERE `usr_name` LIKE '$usr'";
        $result = mysqli_query($conn, $sql);
        $row = mysqli_fetch_array($result);
        if ($row['usr_name']==$usr && $row['usr_pswd']==$pwd) {
            echo $row;
            $_SESSION["username"] = $usr;
            setcookie("username", $usr);
            echo 'right!';
            header("location:/set_feed_time/clockadder.phtml");
        } else {
            echo 'wrong';
            header("location:index.html");
        }
    }
        else { //no stuff
            echo 'information missed!';
            header("location:index.html");
        }
    }
    if($register=='注册'){
        if ($usr != NULL && $pwd != NULL){
            $sql = "SELECT * FROM `user` WHERE `usr_name` LIKE '$usr'";
            $result = mysqli_query($conn, $sql);
            $row = mysqli_fetch_array($result);

            # 用户名不存在，可以注册
            if ($row['usr_id']==''){
                $register_sql = "INSERT INTO `user` (usr_name, usr_pswd) VALUES ('$usr', '$pwd')";
                if(mysqli_query($conn, $register_sql)){
                    echo 'register scuccess!';
                }
                else echo 'register failure!';
            }
            # 用户名存在
            else{

            }

        }
        //no stuff
        else {
            echo 'information missed!';
            header("location:index.html");
        }
    }
}

?>