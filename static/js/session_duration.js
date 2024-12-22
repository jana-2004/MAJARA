document.addEventListener('DOMContentLoaded', function() {
    fetch('/get-session-duration-histogram')
        .then(response => response.json())
        .then(data => {
            console.log("Histogram Data:", data);
            renderHistogram(data);
        })
        .catch(error => console.error('Error fetching histogram data:', error));
});

function renderHistogram(data_df) {
    am5.ready(function() {
        var root = am5.Root.new("histogramdiv");
        root.setThemes([am5themes_Animated.new(root)]);

        var chart = root.container.children.push(
            am5xy.XYChart.new(root, {
                panX: false,
                panY: false,
                wheelX: "none",
                wheelY: "none"
            })
        );

        // X-Axis (Ranges)
        var xAxis = chart.xAxes.push(
            am5xy.CategoryAxis.new(root, {
                categoryField: "range",
                renderer: am5xy.AxisRendererX.new(root, {
                    minGridDistance: 30
                })
            })
        );
        xAxis.data.setAll(data_df);

        // Y-Axis (Count)
        var yAxis = chart.yAxes.push(
            am5xy.ValueAxis.new(root, {
                renderer: am5xy.AxisRendererY.new(root, {})
            })
        );

        // Create Histogram Bars
        var series = chart.series.push(
            am5xy.ColumnSeries.new(root, {
                name: "Session Duration",
                xAxis: xAxis,
                yAxis: yAxis,
                valueYField: "count",
                categoryXField: "range",
                tooltip: am5.Tooltip.new(root, {
                    labelText: "{range}: {valueY} users\nSession Time (Average): {session_time} min"
                })
            })
        );

        // Add session_time to each item
        data_df.forEach(function(item) {
            var range = item.range.split(" ")[0]; // Get the lower bound of the range
            var time = parseInt(range);
            item.session_time = time; // Use lower bound time in minutes for the tooltip
        });

        // Set the data for the series
        series.data.setAll(data_df);

        // Add legend
        chart.children.push(am5.Legend.new(root, {}));
    });
}

