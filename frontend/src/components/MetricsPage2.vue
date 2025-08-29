<template>
    <div class="page-container">
        <!-- Header matching HomePage and ActivityPage -->
        <!-- Header Component -->
        <AppHeader @runSaved="onRunSaved" />

        <!-- Navigation -->
        <BottomNavigation />

        <!-- Main content -->
        <main class="main-content">
            <h2 class="page-title"> </h2>
            <!-- Time Period Selectors -->
            <div class="time-selectors">
            
                <div class="period-type-selector">
                <button 
                    v-for="period in periodTypes" 
                    :key="period.value"
                    class="period-btn"
                    :class="{ active: selectedPeriodType === period.value }"
                    @click="selectPeriodType(period.value)"
                >
                    {{ period.label }}
                </button>
                </div>

                <div class="specific-selectors">
                <div v-if="selectedPeriodType === 'month'" class="selector-group">
                    <label>Month:</label>
                    <select v-model="selectedMonth" @change="updateData">
                    <option v-for="month in months" :key="month.value" :value="month.value">
                        {{ month.label }}
                    </option>
                    </select>
                </div>

                <div v-if="selectedPeriodType !== 'all'" class="selector-group">
                    <label>Year:</label>
                    <select v-model="selectedYear" @change="updateData">
                    <option v-for="year in years" :key="year" :value="year">
                        {{ year }}
                    </option>
                    </select>
                </div>
                </div>
            </div>

            <!-- KPI Cards -->
            <div class="kpi-section">
                <div class="section-title">Key Metrics</div>
                <div class="kpi-grid">
                <div v-for="kpi in kpiData" :key="kpi.key" class="kpi-card">
                    <div class="kpi-value">{{ kpi.value }}</div>
                    <div class="kpi-label">{{ kpi.label }} <span class="kpi-unit">{{ kpi.unit }}</span></div>
                </div>
                </div>
            </div>

            <!-- Charts Section -->
            <div class="charts-section">
                <!-- Distance Bar Chart -->
                <div class="chart-container">
                <div class="chart-title">{{ distanceChartTitle }}</div>
                <div class="chart-wrapper">
                    <canvas ref="distanceChartRef"></canvas>
                </div>
                </div>

                <!-- Pace Line Chart -->
                <div class="chart-container">
                <div class="chart-title">{{ paceChartTitle }}</div>
                <div class="chart-wrapper">
                    <canvas ref="paceChartRef"></canvas>
                </div>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick, watch } from 'vue'
import BottomNavigation from './BottomNavigation.vue'
import AppHeader from './AppHeader.vue'
import { runApi, type RunResponse } from '@/services/api'
import { 
  Chart, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  LineElement, 
  PointElement, 
  Title, 
  Tooltip, 
  Legend, 
  Filler,
  BarController,
  LineController
} from 'chart.js'

// Register Chart.js components including controllers
Chart.register(
  CategoryScale, 
  LinearScale, 
  BarElement, 
  LineElement, 
  PointElement, 
  Title, 
  Tooltip, 
  Legend, 
  Filler,
  BarController,
  LineController
)

// Reactive data
const selectedPeriodType = ref<'month' | 'year' | 'all'>('year')
const selectedMonth = ref<number>(8) // August
const selectedYear = ref<number>(2025)
const isLoading = ref(true)
const allRuns = ref<RunResponse[]>([])

// Charts references
const distanceChartRef = ref<HTMLCanvasElement>()
const paceChartRef = ref<HTMLCanvasElement>()
let distanceChart: any = null
let paceChart: any = null

// Configuration data
const periodTypes = [
  { value: 'month', label: 'Month' },
  { value: 'year', label: 'Year' },
  { value: 'all', label: 'All Time' }
]

const months = [
  { value: 1, label: 'January' },
  { value: 2, label: 'February' },
  { value: 3, label: 'March' },
  { value: 4, label: 'April' },
  { value: 5, label: 'May' },
  { value: 6, label: 'June' },
  { value: 7, label: 'July' },
  { value: 8, label: 'August' },
  { value: 9, label: 'September' },
  { value: 10, label: 'October' },
  { value: 11, label: 'November' },
  { value: 12, label: 'December' }
]

const years = [2023, 2024, 2025]

// Helper functions for data processing
const parseDate = (dateStr: string) => new Date(dateStr.split('T')[0])
const formatDate = (date: Date) => date.toISOString().split('T')[0]

const parsePace = (paceStr: string): number => {
  // Parse "5:30" format to minutes as decimal (5.5)
  const [minutes, seconds] = paceStr.split(':').map(Number)
  return minutes + (seconds / 60)
}

const formatTime = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const parseDuration = (durationStr: string): number => {
  // Parse "HH:MM:SS" to total seconds
  const parts = durationStr.split(':').map(Number)
  if (parts.length === 3) {
    return parts[0] * 3600 + parts[1] * 60 + parts[2]
  }
  return 0
}

// Filter runs based on selected period
const filteredRuns = computed(() => {
  if (selectedPeriodType.value === 'all') {
    return allRuns.value
  }
  
  return allRuns.value.filter(run => {
    const runDate = parseDate(run.date)
    const runYear = runDate.getFullYear()
    const runMonth = runDate.getMonth() + 1 // JavaScript months are 0-based
    
    if (selectedPeriodType.value === 'year') {
      return runYear === selectedYear.value
    } else if (selectedPeriodType.value === 'month') {
      return runYear === selectedYear.value && runMonth === selectedMonth.value
    }
    
    return true
  })
})

// Generate chart data based on filtered runs and period type
const chartData = computed(() => {
  const runs = filteredRuns.value
  
  if (selectedPeriodType.value === 'month') {
    // Group by weeks in the selected month
    const weekData: { [key: string]: { distance: number, runs: number, totalSeconds: number, paces: number[] } } = {}
    
    runs.forEach(run => {
      const runDate = parseDate(run.date)
      const weekNumber = Math.ceil(runDate.getDate() / 7)
      const weekKey = `Week ${weekNumber}`
      
      if (!weekData[weekKey]) {
        weekData[weekKey] = { distance: 0, runs: 0, totalSeconds: 0, paces: [] }
      }
      
      weekData[weekKey].distance += run.distance_km
      weekData[weekKey].runs += 1
      weekData[weekKey].totalSeconds += parseDuration(run.duration)
      weekData[weekKey].paces.push(parsePace(run.pace))
    })
    
    return Object.entries(weekData)
      .map(([week, data]) => ({
        period: week,
        distance_km: data.distance,
        runs: data.runs,
        avg_pace: data.paces.length > 0 ? (data.paces.reduce((a, b) => a + b, 0) / data.paces.length) : 0,
        total_seconds: data.totalSeconds
      }))
      .sort((a, b) => parseInt(a.period.split(' ')[1]) - parseInt(b.period.split(' ')[1]))
      
  } else if (selectedPeriodType.value === 'all') {
    // Group by years for "All Time" view
    const yearData: { [key: string]: { distance: number, runs: number, totalSeconds: number, paces: number[] } } = {}
    
    runs.forEach(run => {
      const runDate = parseDate(run.date)
      const yearKey = runDate.getFullYear().toString()
      
      if (!yearData[yearKey]) {
        yearData[yearKey] = { distance: 0, runs: 0, totalSeconds: 0, paces: [] }
      }
      
      yearData[yearKey].distance += run.distance_km
      yearData[yearKey].runs += 1
      yearData[yearKey].totalSeconds += parseDuration(run.duration)
      yearData[yearKey].paces.push(parsePace(run.pace))
    })
    
    return Object.entries(yearData)
      .map(([year, data]) => ({
        period: year,
        distance_km: data.distance,
        runs: data.runs,
        avg_pace: data.paces.length > 0 ? (data.paces.reduce((a, b) => a + b, 0) / data.paces.length) : 0,
        total_seconds: data.totalSeconds
      }))
      .sort((a, b) => parseInt(a.period) - parseInt(b.period))
      
  } else {
    // Group by months for "Year" view
    const monthData: { [key: string]: { distance: number, runs: number, totalSeconds: number, paces: number[] } } = {}
    
    runs.forEach(run => {
      const runDate = parseDate(run.date)
      const monthKey = runDate.toLocaleString('default', { month: 'short' })
      
      if (!monthData[monthKey]) {
        monthData[monthKey] = { distance: 0, runs: 0, totalSeconds: 0, paces: [] }
      }
      
      monthData[monthKey].distance += run.distance_km
      monthData[monthKey].runs += 1
      monthData[monthKey].totalSeconds += parseDuration(run.duration)
      monthData[monthKey].paces.push(parsePace(run.pace))
    })
    
    const monthOrder = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    return monthOrder
      .filter(month => monthData[month])
      .map(month => ({
        period: month,
        distance_km: monthData[month].distance,
        runs: monthData[month].runs,
        avg_pace: monthData[month].paces.length > 0 ? (monthData[month].paces.reduce((a, b) => a + b, 0) / monthData[month].paces.length) : 0,
        total_seconds: monthData[month].totalSeconds
      }))
  }
})

// Generate pace trend data (last 30 runs)
const paceChartData = computed(() => {
  const recentRuns = [...filteredRuns.value]
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .slice(-30) // Last 30 runs
  
  return recentRuns.map(run => ({
    date: parseDate(run.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    pace: parsePace(run.pace)
  }))
})

// Computed properties for dynamic titles and data
const distanceChartTitle = computed(() => {
  if (selectedPeriodType.value === 'month') {
    const monthName = months.find(m => m.value === selectedMonth.value)?.label
    return `Distance by Week (${monthName} ${selectedYear.value})`
  } else if (selectedPeriodType.value === 'all') {
    return 'Distance by Month (All Time)'
  } else {
    return `Distance by Month (${selectedYear.value})`
  }
})

const paceChartTitle = computed(() => {
  if (selectedPeriodType.value === 'month') {
    const monthName = months.find(m => m.value === selectedMonth.value)?.label
    return `Pace Trend (${monthName} ${selectedYear.value})`
  } else if (selectedPeriodType.value === 'all') {
    return 'Pace Trend - 7 Day Rolling Average (All Time)'
  } else {
    return `Pace Trend - 7 Day Rolling Average (${selectedYear.value})`
  }
})

// Computed KPI data based on current selection
const kpiData = computed(() => {
  const runs = filteredRuns.value
  
  if (runs.length === 0) {
    return [
      { key: 'totalDistance', value: '0.0', label: 'Total Distance', unit: '(km)' },
      { key: 'totalRuns', value: '0', label: 'Number of Runs', unit: '' },
      { key: 'avgPace', value: '0:00', label: 'Average Pace', unit: '(min/km)' },
      { key: 'totalTime', value: '0:00:00', label: 'Total Time', unit: '(HH:MM:SS)' },
      { key: 'longestRun', value: '0.0', label: 'Longest Run', unit: '(km)' },
      { key: 'fastestPace', value: '0:00', label: 'Fastest Pace', unit: '(min/km)' }
    ]
  }
  
  const totalDistance = runs.reduce((sum, run) => sum + run.distance_km, 0)
  const totalRuns = runs.length
  const totalSeconds = runs.reduce((sum, run) => sum + parseDuration(run.duration), 0)
  const longestRun = Math.max(...runs.map(run => run.distance_km))
  const paces = runs.map(run => parsePace(run.pace))
  const avgPace = paces.reduce((sum, pace) => sum + pace, 0) / paces.length
  const fastestPace = Math.min(...paces)
  
  const formatPace = (paceDecimal: number) => {
    const minutes = Math.floor(paceDecimal)
    const seconds = Math.round((paceDecimal - minutes) * 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }
  
  return [
    { key: 'totalDistance', value: totalDistance.toFixed(1), label: 'Total Distance', unit: '(km)' },
    { key: 'totalRuns', value: totalRuns.toString(), label: 'Number of Runs', unit: '' },
    { key: 'avgPace', value: formatPace(avgPace), label: 'Average Pace', unit: '(min/km)' },
    { key: 'totalTime', value: formatTime(totalSeconds), label: 'Total Time', unit: '(HH:MM:SS)' },
    { key: 'longestRun', value: longestRun.toFixed(1), label: 'Longest Run', unit: '(km)' },
    { key: 'fastestPace', value: formatPace(fastestPace), label: 'Fastest Pace', unit: '(min/km)' }
  ]
})

// Methods
const selectPeriodType = (type: 'month' | 'year' | 'all') => {
  selectedPeriodType.value = type
  updateCharts()
}

const updateData = () => {
  // Data updates automatically via computed properties
  updateCharts()
}

const loadRunData = async () => {
  isLoading.value = true
  try {
    allRuns.value = await runApi.getRuns()
  } catch (error) {
    console.error('Failed to load runs:', error)
    allRuns.value = []
  } finally {
    isLoading.value = false
  }
}

// Handle run saved from AppHeader
const onRunSaved = async () => {
  // Reload data to include the new run
  await loadRunData()
}

const initCharts = () => {
  if (!distanceChartRef.value || !paceChartRef.value) {
    console.warn('Canvas refs not ready')
    return
  }

  // Distance Bar Chart
  const distanceCtx = distanceChartRef.value.getContext('2d')
  distanceChart = new Chart(distanceCtx, {
    type: 'bar',
    data: {
      labels: chartData.value.map(item => item.period),
      datasets: [{
        label: 'Distance (km)',
        data: chartData.value.map(item => item.distance_km),
        backgroundColor: 'rgba(255, 193, 7, 0.8)', // --yellow-safety with transparency
        borderColor: '#ffc107', // --yellow-safety
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: '#f8f9fa' // --white-off
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Distance (km)',
            color: '#f8f9fa' // --white-off
          },
          ticks: {
            color: '#bdc3c7' // --gray-light
          },
          grid: {
            color: 'rgba(189, 195, 199, 0.2)' // --gray-light with transparency
          }
        },
        x: {
          title: {
            display: true,
            text: selectedPeriodType.value === 'month' ? 'Week' : 'Month',
            color: '#f8f9fa' // --white-off
          },
          ticks: {
            color: '#bdc3c7' // --gray-light
          },
          grid: {
            color: 'rgba(189, 195, 199, 0.2)' // --gray-light with transparency
          }
        }
      }
    }
  })

  // Pace Line Chart
  const paceCtx = paceChartRef.value.getContext('2d')
  paceChart = new Chart(paceCtx, {
    type: 'line',
    data: {
      labels: paceChartData.value.map(item => item.date),
      datasets: [{
        label: 'Pace (min/km)',
        data: paceChartData.value.map(item => item.pace),
        borderColor: '#17a2b8', // --blue-cyan
        backgroundColor: 'rgba(23, 162, 184, 0.1)', // --blue-cyan with transparency
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#17a2b8',
        pointBorderColor: '#f8f9fa',
        pointBorderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: '#f8f9fa' // --white-off
          }
        }
      },
      scales: {
        y: {
          reverse: true, // Lower pace is better
          title: {
            display: true,
            text: 'Pace (min/km)',
            color: '#f8f9fa' // --white-off
          },
          ticks: {
            color: '#bdc3c7' // --gray-light
          },
          grid: {
            color: 'rgba(189, 195, 199, 0.2)' // --gray-light with transparency
          }
        },
        x: {
          title: {
            display: true,
            text: 'Date',
            color: '#f8f9fa' // --white-off
          },
          ticks: {
            color: '#bdc3c7' // --gray-light
          },
          grid: {
            color: 'rgba(189, 195, 199, 0.2)' // --gray-light with transparency
          }
        }
      }
    }
  })
}

const updateCharts = () => {
  if (!distanceChart || !paceChart) return

  // Update distance chart
  distanceChart.data.labels = chartData.value.map(item => item.period)
  distanceChart.data.datasets[0].data = chartData.value.map(item => item.distance_km)
  distanceChart.options.scales.x.title.text = selectedPeriodType.value === 'month' ? 'Week' : 'Month'
  distanceChart.update()

  // Update pace chart
  paceChart.data.labels = paceChartData.value.map(item => item.date)
  paceChart.data.datasets[0].data = paceChartData.value.map(item => item.pace)
  paceChart.update()
}

// Lifecycle
onMounted(async () => {
  // Load real run data first
  await loadRunData()
  
  // Wait for next tick to ensure DOM is ready
  await nextTick()
  initCharts()
})

// Watch for period type changes and data updates
watch([selectedPeriodType, selectedMonth, selectedYear, filteredRuns], () => {
  nextTick(() => {
    updateCharts()
  })
}, { deep: true })
</script>

<style scoped>
:root {
  --charcoal-dark: #2c3e50;
  --charcoal-medium: #34495e;
  --white-off: #f8f9fa;
  --gray-light: #bdc3c7;
  --gray-medium: #6c757d;
  --gray-cool: #8e9aaf;
  --yellow-safety: #ffc107;
  --yellow-bright: #ffcd3c;
  --blue-cyan: #17a2b8;
  --red-alert: #dc3545;
}

.page-container {
  min-height: 100vh;
  background-color: var(--charcoal-dark);
  color: var(--white-off);
  padding-bottom: 80px;
}

/* Header styles matching HomePage and ActivityPage */
.app-header {
  background-color: var(--charcoal-dark);
  padding: 0rem 1rem;
  border-bottom: 6px solid var(--yellow-safety);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 3.5rem;
}

.app-title {
  color: var(--yellow-safety);
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin-top: 0.5rem;
}

.runner-icon-small {
  height: 100%;
  width: auto;
  object-fit: contain;
}

/* Main content */
.main-content {
  padding: 0.5rem 1rem;
}

.page-title {
  color: var(--white-off);
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

/* Time period selectors */
.time-selectors {
  background-color: var(--charcoal-medium);
  border-radius: 0.75rem;
  border: 1px solid var(--gray-medium);
  padding: 0.75rem;
  margin-bottom: 0rem;
}

.section-title {
  color: var(--white-off);
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  border-bottom: 2px solid var(--gray-medium);
  padding-top: 0.5rem;
  padding-bottom: 0rem;
}

.period-type-selector {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin-bottom: 1rem;
}

.period-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.5rem;
  background-color: var(--gray-medium);
  color: var(--white-off);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.2s ease;
  flex: 1;
}

.period-btn.active {
  background-color: var(--yellow-safety);
  color: var(--charcoal-dark);
}

.period-btn:hover:not(.active) {
  background-color: var(--gray-light);
  color: var(--charcoal-dark);
}

.specific-selectors {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
}

.selector-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.selector-group label {
  font-weight: 500;
  color: var(--white-off);
  font-size: 0.8rem;
}

select {
  padding: 0.375rem 0.75rem;
  border: 1px solid var(--gray-medium);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  background-color: var(--charcoal-dark);
  color: var(--white-off);
  cursor: pointer;
}

select:focus {
  outline: none;
  border-color: var(--yellow-safety);
}

/* KPI Cards matching your run metrics style */
.kpi-section {
  margin-bottom: 1rem;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.kpi-card {
  background-color: var(--charcoal-medium);
  border-radius: 0.75rem;
  border: 1px solid var(--gray-medium);
  padding: 1rem 0.75rem;
  text-align: center;
  transition: transform 0.2s ease;
}

.kpi-card:hover {
  transform: translateY(-1px);
}

.kpi-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--yellow-safety);
  margin-bottom: 0.25rem;
}

.kpi-label {
  color: var(--gray-light);
  font-size: 0.8rem;
  font-weight: 500;
  line-height: 1.2;
}

.kpi-unit {
  font-size: 0.75em;
  color: var(--gray-cool);
}

/* Charts section */
.charts-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chart-container {
  background-color: var(--charcoal-medium);
  border-radius: 0.75rem;
  border: 1px solid var(--gray-medium);
  padding: 1rem;
}

.chart-title {
  color: var(--white-off);
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  border-bottom: 2px solid var(--gray-medium);
  padding-bottom: 0.25rem;
}

.chart-wrapper {
  position: relative;
  height: 250px;
  margin-top: 0.5rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .main-content {
    padding: 0.5rem;
  }

  .app-title {
    font-size: 1.5rem;
  }

  .period-type-selector {
    gap: 0.25rem;
  }

  .period-btn {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }

  .specific-selectors {
    gap: 0.75rem;
  }

  .selector-group label {
    font-size: 0.75rem;
  }

  .kpi-grid {
    gap: 0.5rem;
  }

  .kpi-card {
    padding: 0.75rem 0.5rem;
  }

  .kpi-value {
    font-size: 1.25rem;
  }

  .kpi-label {
    font-size: 0.75rem;
  }

  .chart-wrapper {
    height: 200px;
  }

  .chart-title {
    font-size: 0.9rem;
  }
}
</style>