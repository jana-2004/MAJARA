document.addEventListener('DOMContentLoaded', function () {
    var chartInstance;

    // Fetch and render chart on dropdown change
    document.getElementById('favoriteProductCount').addEventListener('change', function () {
        getChartData();
    });

    // Function to fetch and update chart data
    function getChartData() {
        var topN = document.getElementById('favoriteProductCount').value;

        // Log the selected value
        console.log("Fetching chart data for top " + topN + " favorite products...");

        // Fetch data from the server
        fetch(`/get-barchart?topCount=${topN}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server responded with status ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Chart data received:", data);

                if (data.error) {
                    console.error("Error in response:", data.error);
                    alert(data.error);
                    return;
                }

                if (data.length === 0) {
                    console.warn("No data available to render the chart.");
                    alert("No favorite products found.");
                    return;
                }

                // Update or create the chart
                if (chartInstance) {
                    updateChartData(chartInstance, data);
                } else {
                    chartInstance = createFavoriteChart(data);
                }
            })
            .catch(error => {
                console.error('Error fetching chart data:', error);
                alert('Failed to load data for the chart. Please try again.');
            });
    }

    // Function to create a new chart
    function createFavoriteChart(data) {
        var root = am5.Root.new("favoriteProductsChartDiv");
        root.setThemes([am5themes_Animated.new(root)]);

        var chart = root.container.children.push(am5xy.XYChart.new(root, {
            panX: true,
            panY: true,
            wheelX: "panX",
            wheelY: "zoomX",
            pinchZoomX: true
        }));

        var cursor = chart.set("cursor", am5xy.XYCursor.new(root, {}));
        cursor.lineY.set("visible", false);

        var xAxis = chart.xAxes.push(am5xy.CategoryAxis.new(root, {
            categoryField: "categories",
            renderer: am5xy.AxisRendererX.new(root, {
                minGridDistance: 30,
                minorGridEnabled: true
            })
        }));
        xAxis.get("renderer").labels.template.setAll({
            rotation: 15,
            centerX: am5.p50,  // Center the label horizontally
            centerY: am5.p50,  // Center the label vertically
            disableRotation: false // Ensure rotation is applied
        });

        var yAxis = chart.yAxes.push(am5xy.ValueAxis.new(root, {
            renderer: am5xy.AxisRendererY.new(root, { strokeOpacity: 0.1 })
        }));

        var series = chart.series.push(am5xy.ColumnSeries.new(root, {
            name: "Favorites",
            xAxis: xAxis,
            yAxis: yAxis,
            valueYField: "values",
            categoryXField: "categories",
            tooltip: am5.Tooltip.new(root, {
                labelText: "[bold]{categoryX}[/]: {valueY} users"
            })
        }));

        series.columns.template.setAll({ cornerRadiusTL: 5, cornerRadiusTR: 5, strokeOpacity: 0 });

        // Set data to chart
        xAxis.data.setAll(data);
        series.data.setAll(data);

        chart.appear(1000, 100);
        return chart;
    }

    // Function to update the existing chart with new data
    function updateChartData(chart, data) {
        console.log("Updating chart with new data:", data);
        chart.xAxes.getIndex(0).data.setAll(data);
        chart.series.getIndex(0).data.setAll(data);
        chart.appear(1000, 100);
    }

    // Fetch the initial chart data on page load
    getChartData();
});

