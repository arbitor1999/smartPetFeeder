let dataTYPE = 1;
let day=14;
let month=6;
let year=2021;

async function getdata(targeturl, data){
    $.getJSON(targeturl, function(data1) {
        for (let time_key in data1) {
            let times = time_key.split(':');
            let d = new Date(year, month - 1, day,
                parseInt(times[0]), parseInt(times[1]), parseInt(times[2]), 0);
            console.log(d);
            data.push({
                x: d.getTime(),
                y: parseInt(data1[time_key])
            });
            console.log('insert',data);
        }
        return data;
    })
}

$(document).ready(function(){
    $("#arrow1").click(function(){
        $("#alert1").toggle();
    });

    $("#data-btn1").click(function(){
        dataTYPE = 1;
        $('#data-show').html('环境温度');
    });

    $("#data-btn2").click(function(){
        dataTYPE = 2;
        $('#data-show').html('进食状况');
    });

    // 读取查询日期
    $("#search_button").click(function(){
        console.log('search');
        console.log('dd');
        let form=document.getElementById("search_box");
        let form_elements = form.getElementsByTagName('input');
        year = form_elements[0].value;
        month = form_elements[1].value;
        day = form_elements[2].value;
        console.log('date',day,month,year);
    });
});

var latest_raw = '';
var my_series;
$(function () {
    $(document).ready(function() {
        /*highcharts */
        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });

        $('#mychart').highcharts({
            chart: {
                type: 'scatter',
                backgroundColor: 'rgba(0,0,0,0)',
                animation: Highcharts.svg, // don't animate in old IE
                marginRight: 10,
                events: {
                    load: function() {

                        // set up the updating of the chart each second
                        this.series[0].remove();
                        let labelname='环境温度';
                        if(dataTYPE==2) labelname='数据';
                        this.addSeries({name:labelname,data:(function() {
                                // generate an array of random data
                                var data = [],
                                    time = (new Date()).getTime(),
                                    i;

                                for (i = -10; i <= 0; i++) {
                                    data.push({
                                        x: 0,
                                        y: 0
                                    });
                                }
                                return data;
                            })()});
                        my_series = this.series[0];

                        /*for debug
                            setInterval(function() {
                            var x = (new Date()).getTime(), // current time
                                y = Math.random();
                            my_series.addPoint([x, y], true, true);
                            }, 1000);


                        for debug end*/
                        let theID=1;
                        setInterval(function() {
                            let targeturl = 'getdata.php?myid='+theID+
                                '&data='+dataTYPE+'&day='+day+'&month='+month+'&year='+year;
                            console.log(targeturl);
                            let labelname='环境温度';
                            if(dataTYPE==2) labelname='饮食情况';
                            my_series.name=labelname;
                            $.getJSON( targeturl,
                                function(data){
                                    // console.log(targeturl);
                                    let count=0;
                                    for(let key in data){
                                        count++;
                                    }
                                    console.log('data',count,data);
                                    if(count===0){
                                        for(let k=0;k<10;k++) {
                                                data.push({
                                                    x: (new Date()).getTime(),
                                                    y: 0
                                            });
                                        }
                                    }
                                    if (count>30){
                                        let interval = Math.round(count/10);
                                        let i=0;
                                        for(let time_key in data){
                                            i++;
                                            console.log('i',i%interval);
                                            if(i%interval===0) {
                                                console.log('insert!');
                                                let times = time_key.split(':');
                                                let d = new Date(year, month - 1, day,
                                                    parseInt(times[0]), parseInt(times[1]), parseInt(times[2]), 0);
                                                //console.log(d);
                                                my_series.addPoint([d.getTime(), parseFloat(data[time_key])], true, true);
                                            }
                                        }
                                    }
                                    else{
                                        for(let time_key in data){
                                            let times = time_key.split(':');
                                            let d = new Date(year, month - 1, day,
                                                parseInt(times[0]), parseInt(times[1]), parseInt(times[2]), 0);
                                                //console.log(d);
                                            my_series.addPoint([d.getTime(), parseFloat(data[time_key])], true, true);
                                        }
                                    }

                                    /*
                                    if (data.time !== latest_raw) {
                                        var tempDATA = 0;
                                        if(dataTYPE ===1){tempDATA = data.dataA;}
                                        if(dataTYPE ===2){tempDATA = data.dataB;}
                                        if(dataTYPE ===3){tempDATA = data.dataC;}
                                        //console.log(data.time+'....'+latest_raw);
                                        my_series.addPoint([(new Date()).getTime(), parseInt(tempDATA)], true, true);
                                        latest_raw = data.time;
                                    }
                                    else{
                                        my_series.addPoint([(new Date()).getTime(), 0], true, true);
                                    }*/

                                    //my_series.addPoint([(new Date()).getTime(),2], true, true);
                                });
                            //var x = (new Date()).getTime(), // current time
                            //	y = Math.random();
                            //series.addPoint([x, y], true, true);
                        }, 1000);
                    }
                }
            },
            xAxis: {
                type: 'datetime',
                tickPixelInterval: 100
            },
            yAxis: {
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                formatter: function() {
                    return '<b>'+ this.series.name +'</b><br/>'+
                        Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) +'<br/>'+
                        Highcharts.numberFormat(this.y, 2);
                }
            },
            legend: {
                enabled: false
            },
            exporting: {
                enabled: false
            },
            /*series: [{
                name: '数据展示',
                data: (function() {
                    // generate an array of random data

                    let data = [];

                    console.log('data',data);
                    return data;
                })()
            }]*/
            series: [{
                name: '数据展示',
                data: (function() {
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        i;

                    for (i = -10; i <= 0; i++) {
                        data.push({
                            x: 0,
                            y: 0
                        });
                    }
                    return data;
                })()
            }]
        });
    });

});
