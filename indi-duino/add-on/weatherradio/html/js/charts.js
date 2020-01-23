function weatherChart(lastValue, category, series) {
    var chart = {
	height: 300,
	width: "95%",
	type: "area",
	animations: {
	    initialAnimation: {
		enabled: false
	    }
	}
    };
    var title = {
	text: lastValue,
	offsetX: 30,
	style: {fontSize: '24px', color: '#ccc'}
    };
    var subtitle = {
	text: category,
	offsetX: 30,
	style: {fontSize: '16px', color: '#ccc'}
    };

    xaxis = {type: "datetime"};

    return {chart: chart,
	    title: title,
	    subtitle: subtitle,
	    xaxis: xaxis,
	    series: series};
}

var hchart = new ApexCharts(document.querySelector("#humidity"),
			    weatherChart('52%', 'Humidity', seriesHumidity));
hchart.render();
var cchart = new ApexCharts(document.querySelector("#clouds"),
			    weatherChart('17%', 'Cloud Coverage', seriesCloudCoverage));
cchart.render();
var tchart = new ApexCharts(document.querySelector("#temperature"),
			    weatherChart('5.2°C', 'Temperature', seriesHumidity));
tchart.render();
var pchart = new ApexCharts(document.querySelector("#pressure"),
			    weatherChart('1024.2 hPa', 'Pressure', seriesCloudCoverage));
pchart.render();
