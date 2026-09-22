d3.json('js/cumulativeLineData.json', function(data) {
  nv.addGraph(function() {
    var chart = nv.models.lineChart()
                  .x(function(d) { return d[0] })
                  .y(function(d) { return d[1]/1 })
                  .color(d3.scale.category10().range())
                  .useInteractiveGuideline(true)
                  ;

     chart.xAxis
		 .axisLabel('Climate Anomalies Year')
		 
        .tickValues([1901,1902,1903,1904]);
       
         

    chart.yAxis
		.axisLabel('Climate Anomalies')
	    .tickFormat(d3.format('0.0001f'));

    d3.select('#chart svg')
        .datum(data)
        .call(chart);

    //TODO: Figure out a good way to do this automatically
    nv.utils.windowResize(chart.update);

    return chart;
  });
});