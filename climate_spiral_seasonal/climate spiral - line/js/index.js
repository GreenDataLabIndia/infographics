d3.json('js/cumulativeLineData.json', function(data) {
  nv.addGraph(function() {
    var chart = nv.models.lineChart()
                  .x(function(d) { return d[0] })
                  .y(function(d) { return d[1]/1 })
                  .color(d3.scale.category10().range())
                  .useInteractiveGuideline(true)
                  ;

     chart.xAxis
		 .axisLabel('Year')
		 
        .tickValues([1901,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010, 2017]);
       
         

    chart.yAxis
		.axisLabel('Climate Anomalies')
	    .tickFormat(d3.format('0.0002f'));

    d3.select('#chart svg')
        .datum(data)
        .call(chart);

    //TODO: Figure out a good way to do this automatically
    nv.utils.windowResize(chart.update);

    return chart;
  });
});