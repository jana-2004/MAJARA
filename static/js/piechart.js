document.addEventListener('DOMContentLoaded', function() {
    fetch('/get-datapiechart')
        .then(response => response.json())
        .then(data => {
            console.log("Pie Chart Data:", data);
            renderPieChart(data);
        })
        .catch(error => console.error('Error fetching data:', error));
});

function renderPieChart(data_df) {
    am5.ready(function() {
        var root = am5.Root.new("piechartdiv");
        root.setThemes([am5themes_Animated.new(root)]);

        var chart = root.container.children.push(
            am5percent.PieChart.new(root, {
                layout: root.verticalLayout
            })
        );

        var series = chart.series.push(
            am5percent.PieSeries.new(root, {
                valueField: "values",
                categoryField: "categories"
            })
        );

        series.data.setAll(data_df);

        chart.children.push(
            am5.Legend.new(root, {
                centerY: am5.percent(50),
                y: am5.percent(50),
                layout: root.verticalLayout
            })
        );
    });
}
