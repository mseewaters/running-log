<template>
  <div class="calendar-container">
    <!-- Calendar Header with Navigation -->
    <div class="calendar-header">
      <button
        @click="goToPreviousMonth"
        class="nav-button"
        data-testid="prev-month-btn"
        aria-label="Previous month"
      >
        ‹
      </button>

      <h3 class="month-year" data-testid="calendar-header">
        {{ currentMonthDisplay }} {{ currentYear }}
      </h3>

      <button
        @click="goToNextMonth"
        class="nav-button"
        data-testid="next-month-btn"
        aria-label="Next month"
      >
        ›
      </button>
    </div>

    <!-- Days of Week Header -->
    <div class="weekdays-header">
      <div class="weekday" v-for="day in weekdays" :key="day">{{ day }}</div>
    </div>

    <!-- Calendar Grid -->
    <div class="calendar-grid">
      <!-- Leading empty cells for days before month starts -->
      <div
        v-for="n in leadingEmptyDays"
        :key="`empty-${n}`"
        class="calendar-day empty"
      ></div>

      <!-- Actual days of the month -->
      <div
        v-for="day in daysInCurrentMonth"
        :key="day"
        :data-testid="`calendar-day-${day}`"
        class="calendar-day"
        :class="{
          'today': isToday(day),
          'has-run': hasRunOnDay(day)
        }"
      >
        <span class="day-number">{{ day }}</span>

        <!-- Run indicator (yellow dot) -->
        <div
          v-if="hasRunOnDay(day)"
          class="run-indicator"
          data-testid="run-indicator"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { RunResponse } from '@/services/api'

// Props
interface Props {
  runs: RunResponse[]
}

const props = defineProps<Props>()

// Get current date (this will respect fake timers in tests)
const getCurrentDate = () => new Date()

// State for current month/year being viewed - initialize with current date
const currentMonth = ref(getCurrentDate().getMonth()) // 0-11
const currentYear = ref(getCurrentDate().getFullYear())

// Weekday labels
const weekdays = ['S', 'M', 'T', 'W', 'T', 'F', 'S']

// Month names
const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

// Computed: Current month display name
const currentMonthDisplay = computed(() => {
  return monthNames[currentMonth.value]
})

// Computed: Number of days in current month
const daysInCurrentMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value + 1, 0).getDate()
})

// Computed: Number of empty cells before month starts (for proper grid alignment)
const leadingEmptyDays = computed(() => {
  const firstDayOfMonth = new Date(currentYear.value, currentMonth.value, 1)
  return firstDayOfMonth.getDay() // 0 = Sunday, 1 = Monday, etc.
})

// Computed: Current period key for filtering runs (YYYY-MM format)
const currentPeriodKey = computed(() => {
  const month = (currentMonth.value + 1).toString().padStart(2, '0')
  return `${currentYear.value}-${month}`
})

// Computed: Runs filtered to current month
const runsInCurrentMonth = computed(() => {
  return props.runs.filter(run => {
    // Extract YYYY-MM from run date (YYYY-MM-DD format)
    const runMonth = run.date.substring(0, 7)
    return runMonth === currentPeriodKey.value
  })
})

// Computed: Set of days that have runs (for quick lookup)
const daysWithRuns = computed(() => {
  const days = new Set<number>()
  runsInCurrentMonth.value.forEach(run => {
    // Extract day from YYYY-MM-DD format
    const day = parseInt(run.date.substring(8, 10), 10)
    days.add(day)
  })
  return days
})

// Helper: Check if a day is today
const isToday = (day: number): boolean => {
  const today = getCurrentDate() // Use our helper function that respects fake timers
  return (
    day === today.getDate() &&
    currentMonth.value === today.getMonth() &&
    currentYear.value === today.getFullYear()
  )
}

// Helper: Check if a day has runs
const hasRunOnDay = (day: number): boolean => {
  return daysWithRuns.value.has(day)
}

// Navigation: Go to previous month
const goToPreviousMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

// Navigation: Go to next month
const goToNextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}
</script>

<style scoped>
.calendar-container {
  background-color: var(--charcoal-medium);
  border-radius: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--gray-cool);
}

/* Header */
.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.nav-button {
  background-color: var(--charcoal-dark);
  color: var(--white-off);
  border: 1px solid var(--gray-cool);
  border-radius: 0.25rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.25rem;
  font-weight: bold;
  transition: background-color 0.2s ease;
}

.nav-button:hover {
  background-color: var(--yellow-safety);
  color: var(--charcoal-dark);
}

.month-year {
  color: var(--white-off);
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}

/* Weekdays Header */
.weekdays-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.weekday {
  text-align: center;
  color: var(--gray-cool);
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.5rem 0;
}

/* Calendar Grid */
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
}

.calendar-day {
  position: relative;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  transition: background-color 0.2s ease;
  min-height: 2.5rem;
}

.calendar-day.empty {
  /* Empty cells before month starts */
}

.calendar-day:not(.empty) {
  background-color: var(--charcoal-dark);
  border: 1px solid transparent;
}

.calendar-day.today {
  background-color: var(--blue-cyan);
  color: var(--charcoal-dark);
  font-weight: bold;
}

.calendar-day.has-run {
  border-color: var(--yellow-safety);
  border-width: 2px; /* Make it more prominent */
}

.calendar-day.today.has-run {
  background-color: var(--blue-cyan);
  border-color: var(--yellow-safety);
  border-width: 2px;
  /* Keep the blue background but add prominent yellow border */
}

.day-number {
  color: var(--white-off);
  font-size: 0.875rem;
  font-weight: 500;
  z-index: 1;
}

.calendar-day.today .day-number {
  color: var(--charcoal-dark);
}

/* Run Indicator (Yellow Dot) */
.run-indicator {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  width: 0.5rem;
  height: 0.5rem;
  background-color: var(--yellow-safety);
  border-radius: 50%;
  z-index: 2;
}

.calendar-day.today .run-indicator {
  background-color: var(--yellow-safety);
}

/* Responsive adjustments */
@media (max-width: 400px) {
  .calendar-container {
    padding: 0.75rem;
  }

  .day-number {
    font-size: 0.75rem;
  }

  .run-indicator {
    width: 0.375rem;
    height: 0.375rem;
  }

  .calendar-day {
    min-height: 2rem;
  }
}
</style>
