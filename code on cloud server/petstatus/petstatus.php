<?php
session_start();
$login = $_POST["change"];

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $login = $_POST["change"];
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
    }
    header($route);
}
?>
