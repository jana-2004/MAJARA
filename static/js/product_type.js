document.addEventListener('DOMContentLoaded', function () {
    let chartInstance;

    // Function to fetch and update chart data
    function getChartData() {
        const source = document.getElementById('sourceSelect').value;

        console.log(`Fetching chart data for source: ${source}`);

        fetch(`/get-product-type-counts?source=${encodeURIComponent(source)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server responded with status ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                if (data.length === 0) {
                    alert('No products found.');
                    return;
                }

                if (chartInstance) {
                    updateChartData(chartInstance, data);
                } else {
                    chartInstance = createProductTypeChart(data);
                }
            })
            .catch(error => {
                console.error('Error fetching chart data:', error);
                alert('Failed to load data for the chart. Please try again.');
            });
    }

    // Function to create a new bar chart
    function createProductTypeChart(data) {
        var root = am5.Root.new("chartdiv");
        root.setThemes([am5themes_Animated.new(root)]);

        var chart = root.container.children.push(
            am5xy.XYChart.new(root, {
                panX: true,
                panY: true,
                wheelX: "panX",
                wheelY: "zoomX",
                pinchZoomX: true
            })
        );

        var cursor = chart.set("cursor", am5xy.XYCursor.new(root, {}));
        cursor.lineY.set("visible", false);

        var xAxis = chart.xAxes.push(am5xy.CategoryAxis.new(root, {
            categoryField: "category",
            renderer: am5xy.AxisRendererX.new(root, {
                minGridDistance: 30,
                minorGridEnabled: true
            })
        }));
        xAxis.get("renderer").labels.template.setAll({
            rotation: 15,
            centerX: am5.p50,
            centerY: am5.p50
        });

        var yAxis = chart.yAxes.push(am5xy.ValueAxis.new(root, {
            renderer: am5xy.AxisRendererY.new(root, { strokeOpacity: 0.1 })
        }));

        var series = chart.series.push(am5xy.ColumnSeries.new(root, {
            name: "Product Count",
            xAxis: xAxis,
            yAxis: yAxis,
            valueYField: "value",
            categoryXField: "category",
            tooltip: am5.Tooltip.new(root, {
                labelText: "[bold]{categoryX}[/]: {valueY} items\nSource: {source}"
            })
        }));

        series.columns.template.setAll({
            cornerRadiusTL: 5,
            cornerRadiusTR: 5,
            strokeOpacity: 0
        });

        xAxis.data.setAll(data);
        series.data.setAll(data);

        chart.appear(1000, 100);
        return chart;
    }

    function updateChartData(chart, data) {
        chart.xAxes.getIndex(0).data.setAll(data);
        chart.series.getIndex(0).data.setAll(data);
        chart.appear(1000, 100);
    }

    document.getElementById('sourceSelect').addEventListener('change', getChartData);

    getChartData();
});