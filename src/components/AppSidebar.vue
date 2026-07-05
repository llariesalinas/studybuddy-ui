<template>
  <aside class="sb-sidebar" :class="{ 'sb-sidebar--collapsed': sidebar.collapsed }">
    <div class="sb-brand">
      <span class="sb-brand-badge"><i class="bi bi-book"></i></span>
      <span class="sb-brand-word">StudyBuddy</span>
      <button
        type="button"
        class="sb-collapse-btn sb-btn"
        data-test="collapse-toggle"
        :aria-label="sidebar.collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        :aria-expanded="!sidebar.collapsed"
        @click="sidebar.toggle()"
      >
        <i class="bi" :class="sidebar.collapsed ? 'bi-chevron-right' : 'bi-chevron-left'"></i>
      </button>
    </div>

    <RouterLink :to="profileRoute" class="sb-profile" :title="fullName">
      <span class="sb-avatar">
        <img v-if="user?.profile_picture_url" :src="user.profile_picture_url" :alt="fullName" />
        <span v-else>{{ initials }}</span>
      </span>
      <span class="sb-profile-copy">
        <span class="sb-profile-name">{{ fullName }}</span>
        <span class="sb-profile-role">{{ roleLabel }}</span>
      </span>
    </RouterLink>

    <p class="sb-section-label">Menu</p>
    <nav class="sb-nav" aria-label="Primary">
      <RouterLink
        v-for="item in menuItems"
        :key="item.to"
        :to="item.to"
        class="sb-item"
        active-class="sb-item--active"
        :title="item.label"
        :aria-label="item.label"
      >
        <span class="sb-chip"><i class="bi" :class="item.icon"></i></span>
        <span class="sb-item-label">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <p class="sb-section-label">Support</p>
    <nav class="sb-nav" aria-label="Support">
      <button
        type="button"
        class="sb-item sb-item-btn"
        data-test="help"
        title="Help"
        aria-label="Help"
        @click="emit('open-support')"
      >
        <span class="sb-chip"><i class="bi bi-question-circle"></i></span>
        <span class="sb-item-label">Help</span>
      </button>
    </nav>

    <div class="sb-spacer"></div>

    <div class="sb-footer">
      <button
        type="button"
        class="sb-item sb-item-btn sb-item--danger"
        data-test="logout"
        title="Log out"
        aria-label="Log out"
        @click="emit('logout')"
      >
        <span class="sb-chip"><i class="bi bi-box-arrow-right"></i></span>
        <span class="sb-item-label">Log out</span>
      </button>
      <SbThemeToggle class="sb-footer-toggle" />
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSidebarStore } from '@/stores/sidebar'
import SbThemeToggle from '@/components/SbThemeToggle.vue'

const emit = defineEmits(['logout', 'open-support'])

const authStore = useAuthStore()
const sidebar = useSidebarStore()

const user = computed(() => authStore.user)
const role = computed(() => user.value?.role?.toLowerCase() || null)

const fullName = computed(() => {
  const first = user.value?.fname || ''
  const last = user.value?.lname || ''
  return `${first} ${last}`.trim() || 'Studybuddy User'
})

const initials = computed(() => {
  const first = user.value?.fname?.[0] || ''
  const last = user.value?.lname?.[0] || ''
  return `${first}${last}`.toUpperCase() || 'SB'
})

const roleLabel = computed(() => {
  if (!role.value) return ''
  return role.value.charAt(0).toUpperCase() + role.value.slice(1)
})

const profileRoute = computed(() => {
  if (role.value === 'tutor') return '/tutor-profile'
  if (role.value === 'admin' || role.value === 'superadmin') return '/admin/dashboard'
  return '/tutee-profile'
})

const menuItems = computed(() => {
  if (role.value === 'admin') {
    return [
      { to: '/admin/dashboard', label: 'Dashboard', icon: 'bi-grid-1x2' },
      { to: '/admin/withdrawals', label: 'Withdrawals', icon: 'bi-wallet2' },
      { to: '/admin/users', label: 'Users', icon: 'bi-people' },
      { to: '/admin/tutor-applications', label: 'Tutor Applications', icon: 'bi-person-check' },
      { to: '/admin/reports', label: 'Reports', icon: 'bi-bar-chart-line' },
      { to: '/admin/support', label: 'Support Desk', icon: 'bi-headset' },
    ]
  }

  if (role.value === 'superadmin') {
    return [
      { to: '/superadmin/dashboard', label: 'Dashboard', icon: 'bi-grid-1x2' },
      { to: '/superadmin/institutions', label: 'Institutions', icon: 'bi-building' },
      { to: '/superadmin/users', label: 'All Users', icon: 'bi-people' },
      { to: '/admin/tutor-applications', label: 'Tutor Applications', icon: 'bi-person-check' },
      { to: '/superadmin/reports', label: 'Reports', icon: 'bi-bar-chart-line' },
      { to: '/superadmin/support', label: 'Support Desk', icon: 'bi-headset' },
      { to: '/superadmin/algorithm-demo', label: 'Algorithm Demo', icon: 'bi-diagram-3' },
    ]
  }

  if (role.value === 'tutor') {
    return [
      { to: '/tch-dashboard', label: 'Dashboard', icon: 'bi-grid-1x2' },
      { to: '/tch-requestedSessions', label: 'Requested Sessions', icon: 'bi-inboxes' },
      { to: '/tutor-profile', label: 'Profile', icon: 'bi-person' },
      { to: '/tch-availability', label: 'Schedule', icon: 'bi-calendar3' },
      { to: '/reports', label: 'Sessions & Reports', icon: 'bi-file-earmark-text' },
      { to: '/tch-wallet', label: 'Wallet', icon: 'bi-wallet2' },
    ]
  }

  return [
    { to: '/dashboard', label: 'Dashboard', icon: 'bi-grid-1x2' },
    { to: '/tutee-profile', label: 'Profile', icon: 'bi-person' },
    { to: '/tuteeSessions', label: 'Sessions', icon: 'bi-search' },
  ]
})
</script>

<style scoped>
.sb-sidebar {
  --sb-sidebar-width: 250px;
  --sb-green-tint: #edf7f3;
  --sb-green-border: #b8dece;
  display: flex;
  flex-direction: column;
  width: var(--sb-sidebar-width);
  flex: 0 0 var(--sb-sidebar-width);
  height: 100vh;
  padding: 1rem 0.75rem;
  background: var(--sb-card-bg);
  border-right: 1px solid var(--sb-card-border);
  transition: width var(--sb-t-normal) var(--sb-spring),
              flex-basis var(--sb-t-normal) var(--sb-spring);
  overflow: hidden;
}

.sb-sidebar--collapsed {
  --sb-sidebar-width: 76px;
}

.sb-brand {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.4rem 0.5rem 0.85rem;
}

.sb-brand-badge {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  flex: 0 0 auto;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--sb-primary), var(--sb-primary-mid));
  color: #fff;
  font-size: 1.05rem;
}

.sb-brand-word {
  font-size: 1.05rem;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: var(--sb-text-main);
  white-space: nowrap;
}

.sb-collapse-btn {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  margin-left: auto;
  border: 0;
  border-radius: 8px;
  background: var(--sb-bg);
  color: var(--sb-text-muted);
}

.sb-profile {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin: 0 0.25rem 0.5rem;
  padding: 0.6rem;
  border-radius: 14px;
  background: var(--sb-green-tint);
  text-decoration: none;
}

.sb-avatar {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  flex: 0 0 auto;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, var(--sb-primary), var(--sb-primary-mid));
  color: #fff;
  font-size: 0.85rem;
  font-weight: 800;
}

.sb-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sb-profile-copy {
  display: grid;
  gap: 0.1rem;
  min-width: 0;
}

.sb-profile-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--sb-text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sb-profile-role {
  font-size: 0.72rem;
  color: var(--sb-text-muted);
}

.sb-section-label {
  margin: 0.85rem 0 0.35rem;
  padding: 0 0.85rem;
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--sb-text-muted);
}

.sb-nav {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.sb-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.7rem;
  width: 100%;
  padding: 0.5rem 0.6rem;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: var(--sb-text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  transition: background-color var(--sb-t-normal) var(--sb-spring),
              color var(--sb-t-normal) var(--sb-spring);
}

.sb-item:hover {
  background: color-mix(in srgb, var(--sb-card-bg) 88%, var(--sb-primary));
  color: var(--sb-text-main);
}

.sb-item--active {
  background: var(--sb-green-tint);
  color: var(--sb-primary);
  font-weight: 700;
}

.sb-item--active::before {
  content: '';
  position: absolute;
  left: -0.6rem;
  top: 0.45rem;
  bottom: 0.45rem;
  width: 4px;
  border-radius: 0 4px 4px 0;
  background: var(--sb-primary);
}

.sb-chip {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  flex: 0 0 auto;
  border-radius: 10px;
  background: var(--sb-bg);
  color: var(--sb-text-muted);
  font-size: 0.95rem;
  transition: background-color var(--sb-t-normal) var(--sb-spring),
              color var(--sb-t-normal) var(--sb-spring);
}

.sb-item--active .sb-chip {
  background: var(--sb-primary);
  color: #fff;
}

.sb-item-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sb-item--danger { color: var(--sb-danger); }
.sb-item--danger .sb-chip { background: color-mix(in srgb, var(--sb-danger) 12%, transparent); color: var(--sb-danger); }

.sb-spacer { flex: 1 1 auto; }

.sb-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--sb-card-border);
}

.sb-footer .sb-item { width: auto; flex: 1; }

/* Collapsed state */
.sb-sidebar--collapsed .sb-brand { justify-content: center; }
.sb-sidebar--collapsed .sb-brand-badge { display: none; }
.sb-sidebar--collapsed .sb-collapse-btn { margin-left: 0; }
.sb-sidebar--collapsed .sb-brand-word,
.sb-sidebar--collapsed .sb-profile-copy,
.sb-sidebar--collapsed .sb-section-label,
.sb-sidebar--collapsed .sb-item-label,
.sb-sidebar--collapsed .sb-footer-toggle {
  display: none;
}

.sb-sidebar--collapsed .sb-profile { justify-content: center; padding: 0.4rem; }
.sb-sidebar--collapsed .sb-item { justify-content: center; padding: 0.5rem; }
.sb-sidebar--collapsed .sb-footer { flex-direction: column; }
.sb-sidebar--collapsed .sb-footer .sb-item { width: 100%; justify-content: center; }

/* Dark theme accents */
:global([data-sb-theme='dark']) .sb-sidebar {
  --sb-green-tint: rgba(0, 137, 90, 0.16);
  --sb-green-border: #1f4d3c;
}

:global([data-sb-theme='dark']) .sb-item--active {
  color: #7fe3b8;
}

:global([data-sb-theme='dark']) .sb-item--active .sb-chip {
  background: rgba(0, 137, 90, 0.28);
  color: #7fe3b8;
}
</style>
