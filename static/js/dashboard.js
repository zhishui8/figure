document.addEventListener('DOMContentLoaded', () => {
  const partnerCanvas = document.getElementById('partnerChart');
  if (partnerCanvas && partnerChartData.labels.length) {
    new Chart(partnerCanvas, {
      type: 'bar',
      data: {
        labels: partnerChartData.labels,
        datasets: [
          {
            label: '收入',
            data: partnerChartData.income,
            backgroundColor: 'rgba(60, 171, 99, 0.75)'
          },
          {
            label: '支出',
            data: partnerChartData.expense.map(v => -Math.abs(v)),
            backgroundColor: 'rgba(240, 77, 77, 0.75)'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            ticks: {
              callback: (value) => `¥ ${value}`
            }
          }
        }
      }
    });
  }

  const monthlyCanvas = document.getElementById('monthlyChart');
  if (monthlyCanvas && monthlyChartData.labels.length) {
    new Chart(monthlyCanvas, {
      type: 'line',
      data: {
        labels: monthlyChartData.labels,
        datasets: [
          {
            label: '收入',
            data: monthlyChartData.income,
            borderColor: '#3ac47d',
            backgroundColor: 'rgba(60, 171, 99, 0.2)',
            tension: 0.3
          },
          {
            label: '支出',
            data: monthlyChartData.expense,
            borderColor: '#f04d4d',
            backgroundColor: 'rgba(240, 77, 77, 0.15)',
            tension: 0.3
          },
          {
            label: '结余',
            data: monthlyChartData.net,
            borderColor: '#4d79f0',
            backgroundColor: 'rgba(77, 121, 240, 0.1)',
            borderDash: [5, 5],
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        stacked: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        },
        scales: {
          y: {
            ticks: {
              callback: (value) => `¥ ${value}`
            }
          }
        }
      }
    });
  }

  const categoryCanvas = document.getElementById('categoryChart');
  if (categoryCanvas && categoryChartData.labels.length) {
    new Chart(categoryCanvas, {
      type: 'doughnut',
      data: {
        labels: categoryChartData.labels,
        datasets: [
          {
            label: '支出',
            data: categoryChartData.values,
            backgroundColor: generatePalette(categoryChartData.labels.length)
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    });
  }
});

function generatePalette(length) {
  const baseColors = ['#4d79f0', '#56d8a7', '#f04d4d', '#ffa94d', '#9b59b6', '#16a085', '#fd7e14'];
  const colors = [];
  for (let i = 0; i < length; i += 1) {
    colors.push(baseColors[i % baseColors.length]);
  }
  return colors;
}
