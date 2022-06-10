 const chartConfig = ({ dataItems, labels }) => {
  return {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data: dataItems,
          backgroundColor: ["#51E5FF", "#440381", "#EC368D", "#FFE66D"],
          borderWidth: 1
        }
      ]
    },
    options: {
      title: {
        display: false
      },
      tooltips: {
        callbacks: {
          label: (tooltipItem, data) => {
            const label = data.labels[tooltipItem.index];
            const val =
              data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
            return label + ": $" + val;
          }
        }
      },
      legend: {
        position: "bottom",
        display: false
      },
      legendCallback: (chart) => {
        const renderLabels = (chart) => {
          const { data } = chart;
          return data.datasets[0].data
            .map(
              (_, i) =>
                `<li>
                    <div id="legend-${i}-item" class="legend-item">
                      <span style="background-color:
                        ${data.datasets[0].backgroundColor[i]}">
                        &nbsp;&nbsp;&nbsp;&nbsp;
                      </span>
                      ${
                        data.labels[i] &&
                        `<span class="label">${data.labels[i]}: $${data.datasets[0].data[i]}</span>`
                      }
                    </div>
                </li>
              `
            )
            .join("");
        };
        return `
          <ul class="chartjs-legend">
            ${renderLabels(chart)}
          </ul>`;
      },
      responsive: true
    }
  };
};

 const bindChartEvents = (myChart, containerElement) => {
  const legendItemSelector = ".legend-item";
  const labelSeletor = ".label";

  const legendItems = [
    ...containerElement.querySelectorAll(legendItemSelector)
  ];
  legendItems.forEach((item, i) => {
    item.addEventListener("click", (e) =>
      updateDataset(e.target.parentNode, i)
    );
  });

  const updateDataset = (currentEl, index) => {
    const meta = myChart.getDatasetMeta(0);
    const labelEl = currentEl.querySelector(labelSeletor);
    const result = meta.data[index].hidden === true ? false : true;
    if (result === true) {
      meta.data[index].hidden = true;
      labelEl.style.textDecoration = "line-through";
    } else {
      labelEl.style.textDecoration = "none";
      meta.data[index].hidden = false;
    }
    myChart.update();
  };
};



const chartSelector = "[data-results-chart]";
const chartTitleSelector = "[data-results-chart-title]";
const chartLegendSelector = "[data-results-chart-legends]";

let chartEl;
let chartTitleEl;
let chartLegendEL;
let myChart;

chartEl = document.querySelector(chartSelector);
chartTitleEl = document.querySelector(chartTitleSelector);
chartLegendEL = document.querySelector(chartLegendSelector);

const renderTitle = () => "Total value: $500.00";

const renderChart = () => {
  chartTitleEl.textContent = renderTitle();

  const dataItems = ["280.00", "80.00", "50.33", "89.67"];
  const labels = ["Principal & Interest", "Taxes ", "Insurance", "PMI"];

  const ctx = chartEl.getContext("2d");
  myChart = new Chart(ctx, chartConfig({ dataItems, labels }));
  chartLegendEL.innerHTML = myChart.generateLegend();
  bindChartEvents(myChart, document);
};

renderChart();
