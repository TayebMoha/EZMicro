document.addEventListener("DOMContentLoaded", () => {

        function renderAgeChart() {
            const traces = ["Male", "Female"].map(gender => ({
                x: ageGroupData.filter(d => d["Sex"] === gender).map(d => d["Age Group"]),
                y: ageGroupData.filter(d => d["Sex"] === gender).map(d => d["Count"]),
                name: gender,
                type: "bar",
            }));

            Plotly.newPlot("age-chart", traces, {
                barmode: "group",
                title: "Répartition par groupe d'âge",
                xaxis: {title: "Groupe d'âge"},
                yaxis: {title: "Nombre de cas"},
            });
        }

        renderAgeChart();

        // Script for Cancer Age Chart
       
        function renderCancerAgeChart() {
            const types = [...new Set(cancerAgeData.map(d => d["Type"]))];
            const ageGroups = [...new Set(cancerAgeData.map(d => d["Age Group"]))];

            const traces = types.map(type => ({
                x: cancerAgeData.filter(d => d["Type"] === type).map(d => d["Age Group"]),
                y: cancerAgeData.filter(d => d["Type"] === type).map(d => d["Count"]),
                name: type,
                type: "bar",
            }));

            Plotly.newPlot("cancer-age-chart", traces, {
                barmode: "stack",
                title: "Répartition des types de cancer par groupe d'âge",
                xaxis: {title: "Groupe d'âge"},
                yaxis: {title: "Nombre de cas"},
            });
        }

        renderCancerAgeChart();

        

        function renderDiagnosisAgeLineChart() {
            const cancerTypes = [...new Set(lineGraphData.map(d => d["CancerType"]))]; // Unique cancer types
            const traces = cancerTypes.map(type => ({
                x: lineGraphData.filter(d => d["CancerType"] === type).map(d => d["Year"]), // Years on x-axis
                y: lineGraphData.filter(d => d["CancerType"] === type).map(d => d["AverageAge"]), // Average ages on y-axis
                name: type, // Cancer type as the legend name
                type: "scatter",
                mode: "lines+markers", // Line with markers
            }));

            const layout = {
                title: "Âge moyen des patients par année de diagnostic et type de cancer",
                xaxis: {title: "Année de diagnostic"},
                yaxis: {title: "Âge moyen des patients (années)"},
                legend: {title: {text: "Type de cancer"}},
            };

            Plotly.newPlot("diagnosis-age-line-chart", traces, layout);
        }

        renderDiagnosisAgeLineChart();


        // Script for Line Chart
       

        function renderLineChart() {
            const types = [...new Set(lineChartData.map(d => d["Type"]))];
            const traces = types.map(type => {
                const maleData = lineChartData.filter(d => d["Type"] === type && d["Sex"] === "Male");
                const femaleData = lineChartData.filter(d => d["Type"] === type && d["Sex"] === "Female");

                return [
                    {
                        x: maleData.map(d => d["Yeardiag"]),
                        y: maleData.map(d => d["Count"]),
                        name: `${type} (Homme)`,
                        type: "scatter",
                        mode: "lines+markers",
                    },
                    {
                        x: femaleData.map(d => d["Yeardiag"]),
                        y: femaleData.map(d => d["Count"]),
                        name: `${type} (Femme)`,
                        type: "scatter",
                        mode: "lines+markers",
                    },
                ];
            }).flat();

            Plotly.newPlot("line-chart", traces, {
                title: "Évolution du nombre de cas par type de cancer (Homme/Femme)",
                xaxis: {title: "Année de diagnostic"},
                yaxis: {title: "Nombre de cas"},
                legend: {title: "Type de cancer et sexe"},
            });
        }

        renderLineChart();


        // Populate the dropdown dynamically with unique ethnicities
        const dropdown = document.getElementById("ethnicity-dropdown");
        const races = [...new Set(ethnicityCancerData.map(d => d["Race"]))];
        races.forEach(race => {
            const option = document.createElement("option");
            option.value = race;
            option.textContent = race;
            dropdown.appendChild(option);
        });

        // Function to render the pie chart for a selected ethnicity
        function renderEthnicityPieChart(selectedEthnicity) {
            const filteredData = ethnicityCancerData.filter(d => d["Race"] === selectedEthnicity);
            const pieData = [
                {
                    values: filteredData.map(d => d["Count"]), // Use percentage for the pie slices
                    labels: filteredData.map(d => d["Type"]), // Cancer types as labels
                    type: "pie",
                    hoverinfo: "label+percent", // Tooltip with labels and percentages
                    textinfo: "label+value", // Show label and value inside the chart
                },
            ];

            const layout = {
                title: `Répartition (%) des types de cancer pour ${selectedEthnicity}`,
            };

            Plotly.newPlot("ethnicity-pie-chart", pieData, layout);
        }

        // Set up event listener for dropdown change
        dropdown.addEventListener("change", event => {
            renderEthnicityPieChart(event.target.value);
        });

        // Render the pie chart for the first ethnicity by default
        if (races.length > 0) {
            dropdown.value = races[0]; // Set the default selection to the first ethnicity
            renderEthnicityPieChart(races[0]);
        }

       

        // Populate the dropdown dynamically with unique cancer types
        const cancerDropdown = document.getElementById("cancer-type-dropdown");
        const cancerTypes = [...new Set(vitalStatusData.map(d => d["Type"]))];
        cancerTypes.forEach(type => {
            const option = document.createElement("option");
            option.value = type;
            option.textContent = type;
            cancerDropdown.appendChild(option);
        });

        // Function to render the pie chart for a selected cancer type
        function renderVitalStatusPieChart(selectedCancerType) {
            const filteredData = vitalStatusData.filter(d => d["Type"] === selectedCancerType);
            const labels = filteredData.map(d => d["COD"] === "Alive" ? "En vie" : d["COD"]);
            const pieData = [
                {
                    values: filteredData.map(d => d["Count"]), // Use counts for the pie slices
                    labels: labels,  // COD (cause of death or "En vie") as labels
                    type: "pie",
                    automargin: true,
                    hoverinfo: "label+percent+value", // Tooltip with labels and percentages
                },
            ];

            const layout = {
                title: `Répartition des statuts vitaux pour le type de cancer : ${selectedCancerType}`,
                height: 700,
                width: 800
            };

            Plotly.newPlot("vital-status-pie-chart", pieData, layout);
        }

        // Set up event listener for dropdown change
        cancerDropdown.addEventListener("change", event => {
            renderVitalStatusPieChart(event.target.value);
        });

        // Render the pie chart for the first cancer type by default
        if (cancerTypes.length > 0) {
            cancerDropdown.value = cancerTypes[0]; // Set the default selection to the first cancer type
            renderVitalStatusPieChart(cancerTypes[0]);
        }

       

        function renderBoxPlot() {
            const causes = [...new Set(boxPlotData.map(d => d["COD"]))];
            const traces = causes.map(cause => ({
                y: boxPlotData.filter(d => d["COD"] === cause).map(d => d["Age"]),
                name: cause,
                type: "box",
                boxpoints: "outliers", // Show individual outliers
                jitter: 0.3, // Spread out points for better visibility
            }));

            const layout = {
                title: "Distribution des âges par cause de décès",
                xaxis: {title: "Cause de décès"},
                yaxis: {title: "Âge (en années)"},
            };

            Plotly.newPlot("age-cod-boxplot", traces, layout);
        }

        renderBoxPlot();

        
        function renderVitalStatusEthnicityChart() {
            const statuses = [...new Set(vitalStatusEthnicityData.map(d => d["COD"]))]; // Unique CODs (vital statuses)
            const traces = statuses.map(status => ({
                x: vitalStatusEthnicityData.filter(d => d["COD"] === status).map(d => d["Race"]), // Ethnicities on x-axis
                y: vitalStatusEthnicityData.filter(d => d["COD"] === status).map(d => d["Percentage"]), // Counts for each status
                name: status === "Alive" ? "En vie" : status, // Replace "Alive" with "En vie"
                type: "bar",
            }));

            const layout = {
                title: "Répartition du statut vital par ethnie",
                barmode: "group",
                xaxis: {title: "Ethnie"},
                yaxis: {title: "Pourcentage"},
                legend: {title: {text: "Statut vital"}},
            };

            Plotly.newPlot("vital-status-ethnicity-chart", traces, layout);
        }

        renderVitalStatusEthnicityChart();
  });
  