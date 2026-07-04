import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { useOrbitStrip } from './useOrbitStrip'

const { useSessionsStore } = await import('@/stores/completedSessions')
const { useActiveSessionStore } = await import('@/stores/activeSession')

const pad = (value) => String(value).padStart(2, '0')
const toDateKey = (date) => `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
const toTimeKey = (date) => `${pad(date.getHours())}:${pad(date.getMinutes())}`
const addMinutes = (date, minutes) => new Date(date.getTime() + minutes * 60 * 1000)

const TestHarness = defineComponent({
  props: {
    session: { type: Object, required: true },
  },
  setup(props) {
    const { presentation } = useOrbitStrip({ session: props.session })
    return { presentation }
  },
  template: '<div>{{ presentation.state }}</div>',
})

describe('useOrbitStrip composable (explicit session)', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    window.localStorage.clear()
  })

  afterEach(() => {
    wrapper?.unmount()
  })

  it('derives the explicit session\'s own phase instead of leaking the global queue\'s state', () => {
    // Regression for the fix in useOrbitStrip.js: passing an explicit `session`
    // with no explicit `state` must not fall back to the global queue's state.
    // Before the fix, `sourceState` returned `queueState.value` unconditionally,
    // so a detail page rendering its own live session would show whatever
    // state the front-of-queue item happened to be in (e.g. a different,
    // already-ended session sitting in Payment Required).
    const now = new Date()

    const sessionsStore = useSessionsStore()
    const activeSession = useActiveSessionStore()

    const queueFrontSession = {
      id: 1,
      status: 'Payment Required',
      date: toDateKey(addMinutes(now, -180)),
      startTime: toTimeKey(addMinutes(now, -180)),
      endTime: toTimeKey(addMinutes(now, -150)),
      subject: 'Older handoff session',
    }
    sessionsStore.sessions = [queueFrontSession]
    activeSession.currentTime = now

    expect(activeSession.queueState).toBe('handoff')

    const explicitLiveSession = {
      id: 2,
      status: 'Ongoing',
      date: toDateKey(now),
      startTime: toTimeKey(addMinutes(now, -15)),
      endTime: toTimeKey(addMinutes(now, 15)),
      subject: 'Current live session',
    }

    wrapper = mount(TestHarness, {
      props: { session: explicitLiveSession },
    })

    expect(wrapper.vm.presentation.state).toBe('live')
    expect(wrapper.vm.presentation.state).not.toBe(activeSession.queueState)
  })
})
