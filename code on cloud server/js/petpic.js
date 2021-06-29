let current_pic=0;
let all_pic=[];
let screen = document.getElementById("screen");
let ul = document.getElementById('ul');
let ol = document.getElementById('ol');
let div = document.getElementById('arr');
let download = document.getElementById('DL');
let imgWidth = screen.offsetWidth;

function getCookie(cname)
{
    var name = cname + "=";
    var ca = document.cookie.split(';');

    for(var i=0; i<ca.length; i++)
    {
        var c = ca[i].trim();
        if (c.indexOf(name)==0) {return c.substring(name.length,c.length);console.log(c);}
    }
    return "";
}

async function loadPic(){
    const pictures_route =
           await fetch('../petpic/pic_route.txt')
            .then(response => response.text())
            .then(result => result.split("\n"));
    console.log(pictures_route.length);
    if(pictures_route.length<=1){
        alert('该日期没有拍摄图片！');
    }
    else{
    for(let x=0;x<pictures_route.length-1;x++){
        let temp_pic = pictures_route[x].split(" ");
        console.log('reading!');
        console.log(temp_pic);
        pic_info = {'pet_id':temp_pic[0],'pic_route':temp_pic[1],'pic_time':temp_pic[2],'pic_label':temp_pic[3]};
        all_pic.push(pic_info);
        let ulchild = document.createElement("li");
        let imgchild = document.createElement("img");
        imgchild.setAttribute('src', pic_info['pic_route']);
        imgchild.setAttribute('AlternateText', pic_info['pic_route']);
        ulchild.appendChild(imgchild);
        ul.appendChild(ulchild);
    }
    //ul.setAttribute('style','left:-500px');
    console.log(all_pic[0]['pic_route']);
    download.setAttribute('href',all_pic[0]['pic_route']);
    download.setAttribute('download',all_pic[0]['pic_route']);
    }
}
function read_select(){
    let form=document.getElementById("search_box");
    let form_elements = form.getElementsByTagName('input');
    let year = form_elements[0].value;
    let month = form_elements[1].value;
    let day = form_elements[2].value;
    let form_select = form.getElementsByTagName('select');
    let b=0;
    let se = form_select[0].value;
    document.cookie = "selection="+b+'!'+year+'!'+month+'!'+day+'!'+se;
    getCookie('selection');
}

$(document).ready(function(){
    b++;
    let a = document.getElementById('search_button');

    $("#arrow1").click(function(){
            $("#alert1").toggle();
        });
    // getCookie('selection');

});

window.onload = function () {
    let year,month,day,choice;
    if(getCookie('selection').split('!')[1]===undefined){
        year=2021;
        month=6;
        day=15;
        choice='a';
    }else{
        year=getCookie('selection').split('!')[1];
        month=getCookie('selection').split('!')[2];
        day=getCookie('selection').split('!')[3];
        choice=getCookie('selection').split('!')[4];
    }
    let tempyear = document.getElementById('Year');
    tempyear.setAttribute('value',year);
    let tempmonth = document.getElementById('Month');
    tempmonth.setAttribute('value',month);
    let tempday = document.getElementById('Day');
    tempday.setAttribute('value',day);
    let tempvalue = document.getElementById(choice);
    tempvalue.setAttribute('selected','selected');
    console.log('dame');
    setInterval(function(){read_select()},1000);
    loadPic();
    //
    //需求：无缝滚动。
    //思路：赋值第一张图片放到ul的最后，然后当图片切换到第五张的时候
    //     直接切换第六，再次从第一张切换到第二张的时候先瞬间切换到
    //     第一张图片，然后滑动到第二张
    //步骤：
    //1.获取事件源及相关元素。（老三步）
    //2.复制第一张图片所在的li,添加到ul的最后面。
    //3.给ol中添加li，ul中的个数-1个，并点亮第一个按钮。
    //4.鼠标放到ol的li上切换图片
    //5.添加定时器
    //6.左右切换图片（鼠标放上去隐藏，移开显示）
    div.style.display="block";
    var divArr = div.children;

    divArr[0].onclick = function (ev) {
        current_pic--;
        console.log(current_pic);
        if(current_pic < 0) {
            ul.style.left = -(ul.children.length-1) * imgWidth + "px";
            current_pic = all_pic.length-1;
        }
        else{
            ul.style.left = -current_pic * imgWidth + "px";
        }
        download.setAttribute('href',all_pic[current_pic]['pic_route']);
    }
    divArr[1].onclick =function(ev){
        current_pic++;
        console.log(current_pic);
        if(current_pic>all_pic.length-1){
            ul.style.left='0px';
            current_pic=0;
        }
        else{
            ul.style.left = -current_pic * imgWidth + "px";
        }
        download.setAttribute('href',all_pic[current_pic]['pic_route']);
    }
}


