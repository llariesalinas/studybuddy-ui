<template>
  <div class="schedule-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">My Schedule</h2>
      <p class="text-muted">Manage your availability for tutoring sessions.</p>
    </div>

    <div class="card border-sb border-1 shadow-sm rounded-4">
      <div class="card-body p-4 p-md-5">
        
        <h4 class="fw-bold mb-4 d-flex align-items-center">
          <i class="bi bi-calendar-check text-sb-primary me-3"></i> Weekly Availability
        </h4>

        <div class="d-flex flex-column gap-3">
          
          <div 
            v-for="day in weeklySchedule" 
            :key="day.name" 
            class="card border-sb rounded-4 shadow-none"
          >
            <div class="card-body p-4">
              <h6 class="fw-bold mb-3">{{ day.name }}</h6>
              
              <div class="d-flex flex-wrap gap-3">
                <div 
                  v-for="slot in day.slots" 
                  :key="slot.id"
                  class="time-slot-pill d-flex align-items-center justify-content-between border border-sb rounded-pill px-3 py-2 bg-white"
                >
                  
                  <div class="d-flex align-items-center text-muted" style="font-size: 0.9rem;">
                    <i class="bi bi-clock me-2"></i>
                    <span>{{ slot.time }}</span>
                  </div>

                  <div class="d-flex align-items-center gap-2 ms-4">
                    <div class="form-check form-switch mb-0 custom-switch-wrapper">
                      <input 
                        class="form-check-input custom-switch shadow-none cursor-pointer" 
                        type="checkbox" 
                        role="switch" 
                        v-model="slot.isOpen"
                        @change="handleScheduleChange(day.name, slot)"
                      >
                    </div>
                    <span 
                      class="badge rounded-pill px-3 py-1 fw-normal" 
                      :class="slot.isOpen ? 'bg-sb-primary text-white' : 'bg-light text-muted border border-sb'"
                    >
                      {{ slot.isOpen ? 'Open' : 'Closed' }}
                    </span>
                  </div>

                </div>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Data-driven state: This mimics what your backend API will eventually send
const weeklySchedule = ref([
  {
    name: 'Monday',
    slots: [
      { id: 'm1', time: '9:00 – 12:00', isOpen: true },
      { id: 'm2', time: '14:00 – 17:00', isOpen: false }
    ]
  },
  {
    name: 'Tuesday',
    slots: [
      { id: 't1', time: '10:00 – 13:00', isOpen: true },
      { id: 't2', time: '14:00 – 17:00', isOpen: true }
    ]
  },
  {
    name: 'Wednesday',
    slots: [
      { id: 'w1', time: '9:00 – 12:00', isOpen: false },
      { id: 'w2', time: '14:00 – 17:00', isOpen: true }
    ]
  },
  {
    name: 'Thursday',
    slots: [
      { id: 'th1', time: '9:00 – 12:00', isOpen: true },
      { id: 'th2', time: '14:00 – 17:00', isOpen: false }
    ]
  },
  {
    name: 'Friday',
    slots: [
      { id: 'f1', time: '9:00 – 12:00', isOpen: true },
      { id: 'f2', time: '14:00 – 17:00', isOpen: true }
    ]
  }
])

// Strategic foundation: Prepare for your API logic
const handleScheduleChange = (dayName, slot) => {
  // In the future, this is where you trigger an Axios/Fetch request to update the database
  console.log(`Updated workload capacity: ${dayName} at ${slot.time} is now ${slot.isOpen ? 'Open' : 'Closed'}`);
}
</script>

<style scoped>
/* Force the pill containers to a consistent minimum width matching the design */
.time-slot-pill {
  min-width: 260px;
}

/* Make the toggle pointer act like a clickable button */
.cursor-pointer {
  cursor: pointer;
}

/* Customizing Bootstrap's default blue switch to your brand's green */
.custom-switch-wrapper .form-check-input {
  width: 2.5em;
  height: 1.25em;
}

.custom-switch-wrapper .form-check-input:checked {
  background-color: var(--sb-primary);
  border-color: var(--sb-primary);
}

.custom-switch-wrapper .form-check-input:focus {
  border-color: rgba(0, 137, 90, 0.25);
  box-shadow: 0 0 0 0.25rem rgba(0, 137, 90, 0.25);
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='-4 -4 8 8'%3e%3ccircle r='3' fill='rgba%280, 0, 0, 0.25%29'/%3e%3c/svg%3e");
}

.custom-switch-wrapper .form-check-input:checked:focus {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='-4 -4 8 8'%3e%3ccircle r='3' fill='%23fff'/%3e%3c/svg%3e");
}
</style>