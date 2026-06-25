<template>
  <div ref="pageRef" class="studio-landing">
    <div class="bgwash" aria-hidden="true">
      <i class="b1"></i>
      <i class="b2"></i>
      <i class="b3"></i>
    </div>

    <div ref="scrollSpaceRef" class="scroll-space" aria-hidden="true"></div>

    <nav class="studio-nav" aria-label="Main navigation">
      <button class="brand hoverable" type="button" @click="goTo('/')">
        <span class="brand-mark" aria-hidden="true">S</span>
        <span>Studybuddy</span>
      </button>
      <div class="navlinks">
        <button class="btn outline hoverable" type="button" @click="goTo('/login')">
          <span class="lbl">Log in</span>
        </button>
        <button class="btn primary hoverable" type="button" @click="goTo('/register')">
          <span class="fill"></span>
          <span class="lbl">Get started</span>
        </button>
        <SbThemeToggle />
      </div>
    </nav>

    <main ref="smoothRef" class="smooth-root">
      <section class="hero">
        <div class="inner">
          <p class="kick reveal in">Peer tutoring &mdash; by students, for students</p>
          <h1 ref="heroTitleRef" class="hero-title">
            <span class="row"><span>Learn it from</span></span>
            <span class="row"><span>someone who</span></span>
            <span class="row"><span><em>just aced it.</em></span></span>
          </h1>
          <div class="hero-sub">
            <p class="reveal">
              Studybuddy matches you with students on your campus who took the class,
              passed the exam, and can actually explain it. Book a session, study
              together, get it.
            </p>
            <div class="hero-actions" aria-label="Primary actions">
              <button class="btn primary hoverable" type="button" @click="goTo('/register')">
                <span class="fill"></span>
                <span class="lbl">Find my tutor</span>
              </button>
              <button class="btn outline hoverable" type="button" @click="goTo('/register')">
                <span class="lbl">Become a tutor</span>
              </button>
            </div>
            <div class="scroll-cue" aria-hidden="true">
              Scroll <span class="bar"></span>
            </div>
          </div>
        </div>
      </section>

      <div class="marquee" aria-label="Studybuddy highlights">
        <div class="marquee-track">
          <span v-for="copy in 2" :key="copy" class="marquee-copy">
            <template v-for="item in marqueeItems" :key="`${copy}-${item.text}`">
              <em v-if="item.em">{{ item.text }}</em>
              <span v-else>{{ item.text }}</span>
              <span class="dot" :class="item.dot" aria-hidden="true"></span>
            </template>
          </span>
        </div>
      </div>

      <section class="panels" aria-label="How Studybuddy works">
        <div class="inner">
          <article
            v-for="(panel, index) in panels"
            :key="panel.title"
            class="panel"
          >
            <div class="idx"><b>{{ String(index + 1).padStart(2, '0') }}</b> / 03</div>
            <div class="panel-copy">
              <h2>
                <span v-for="line in panel.titleLines" :key="line" class="row">
                  <span>{{ line }}</span>
                </span>
              </h2>
              <p>{{ panel.copy }}</p>
            </div>

            <div class="viz hoverable">
              <div class="ill" :data-depth="panel.depth">
                <svg
                  v-if="panel.id === 'need'"
                  viewBox="0 0 440 240"
                  fill="none"
                  role="img"
                  aria-label="Subject picker interface"
                >
                  <text x="24" y="48" class="svg-label svg-ink-fill">What do you need help with?</text>
                  <rect x="24" y="70" width="118" height="40" rx="20" class="svg-primary-fill" />
                  <text x="46" y="95" class="svg-small-label svg-contrast-fill">Calculus 2</text>
                  <rect x="154" y="70" width="100" height="40" rx="20" class="svg-card-fill svg-card-stroke" stroke-width="2" />
                  <text x="174" y="95" class="svg-muted-label svg-muted-fill">Physics</text>
                  <rect x="266" y="70" width="110" height="40" rx="20" class="svg-card-fill svg-card-stroke" stroke-width="2" />
                  <text x="284" y="95" class="svg-muted-label svg-muted-fill">Chemistry</text>
                  <rect x="24" y="126" width="196" height="40" rx="20" class="svg-card-fill svg-card-stroke" stroke-width="2" />
                  <text x="42" y="151" class="svg-muted-label svg-muted-fill">Thu, 7:00 PM onwards</text>
                  <path d="M330 168 q 26 14 52 -6" class="svg-yellow-stroke" stroke-width="3.5" stroke-linecap="round" />
                  <path d="M372 160 l 11 1 l -4 10" class="svg-yellow-stroke" stroke-width="3.5" stroke-linecap="round" />
                </svg>

                <svg
                  v-else-if="panel.id === 'match'"
                  viewBox="0 0 440 240"
                  fill="none"
                  role="img"
                  aria-label="Two matched student avatars"
                >
                  <g class="char" data-amp="2.5">
                    <circle cx="120" cy="106" r="32" class="svg-card-fill svg-ink-stroke" stroke-width="2.8" />
                    <path d="M90 99 q 2 -27 30 -27 q 26 0 30 21 M103 76 q 6 -7 12 -8" class="svg-ink-stroke" stroke-width="2.4" stroke-linecap="round" />
                    <path d="M110 102 q 3 4 8 0 M131 102 q 3 4 8 0 M113 118 q 7 5 14 0" class="svg-ink-stroke" stroke-width="2.4" stroke-linecap="round" />
                    <path d="M103 110 l 7 1 M144 111 l -7 -1" class="svg-pink-stroke" stroke-width="2.2" stroke-linecap="round" opacity=".75" />
                  </g>
                  <g class="char" data-amp="3">
                    <circle cx="320" cy="106" r="32" class="svg-card-fill svg-ink-stroke" stroke-width="2.8" />
                    <path d="M290 99 q 4 -26 30 -26 q 25 0 30 20" class="svg-ink-stroke" stroke-width="2.4" stroke-linecap="round" />
                    <circle cx="348" cy="80" r="6" class="svg-ink-fill" />
                    <path d="M310 102 q 3 4 8 0 M331 102 q 3 4 8 0" class="svg-ink-stroke" stroke-width="2.4" stroke-linecap="round" />
                    <circle cx="313.5" cy="103" r="8" class="svg-ink-stroke" stroke-width="2" />
                    <circle cx="334.5" cy="103" r="8" class="svg-ink-stroke" stroke-width="2" />
                    <path d="M321 103 h 6 M314 121 q 6 4 12 0" class="svg-ink-stroke" stroke-width="2.2" stroke-linecap="round" />
                  </g>
                  <path d="M158 98 q 62 -44 124 0" class="svg-primary-stroke" stroke-width="3" stroke-linecap="round" stroke-dasharray="7 8" />
                  <g class="char" data-amp="6">
                    <circle cx="220" cy="64" r="14" class="svg-yellow-fill" />
                    <path d="M214 64 l 5 5 l 8 -9" class="svg-ink-stroke" stroke-width="2.6" stroke-linecap="round" />
                  </g>
                  <rect x="150" y="176" width="140" height="34" rx="17" class="svg-green-tint-fill svg-green-tint-stroke" stroke-width="2" />
                  <text x="176" y="198" class="svg-small-label svg-primary-fill">98% match</text>
                </svg>

                <svg
                  v-else
                  viewBox="0 0 440 240"
                  fill="none"
                  role="img"
                  aria-label="Two students studying at a table"
                >
                  <path d="M60 196 h 320" class="svg-ink-stroke" stroke-width="2.8" stroke-linecap="round" />
                  <g class="char" data-amp="2.5">
                    <circle cx="170" cy="120" r="28" class="svg-card-fill svg-ink-stroke" stroke-width="2.6" />
                    <path d="M144 114 q 2 -23 26 -23 q 22 0 26 17" class="svg-ink-stroke" stroke-width="2.2" stroke-linecap="round" />
                    <path d="M161 117 q 3 4 6 0 M180 117 q 3 4 6 0 M163 130 q 6 5 13 0" class="svg-ink-stroke" stroke-width="2.2" stroke-linecap="round" />
                    <path d="M170 148 v 46" class="svg-ink-stroke" stroke-width="2.6" stroke-linecap="round" />
                  </g>
                  <g class="char" data-amp="3">
                    <circle cx="276" cy="120" r="28" class="svg-card-fill svg-ink-stroke" stroke-width="2.6" />
                    <path d="M250 114 q 2 -23 26 -23 q 22 0 26 17" class="svg-ink-stroke" stroke-width="2.2" stroke-linecap="round" />
                    <circle cx="298" cy="96" r="5" class="svg-ink-fill" />
                    <path d="M267 117 q 3 4 6 0 M286 117 q 3 4 6 0 M269 131 q 6 5 13 0" class="svg-ink-stroke" stroke-width="2.2" stroke-linecap="round" />
                    <path d="M276 148 v 46" class="svg-ink-stroke" stroke-width="2.6" stroke-linecap="round" />
                  </g>
                  <rect x="200" y="160" width="48" height="30" rx="5" class="svg-note-fill svg-ink-stroke" stroke-width="2" transform="rotate(-3 224 175)" />
                  <g class="char" data-amp="5">
                    <circle cx="170" cy="58" r="13" class="svg-yellow-fill" />
                    <path d="M164 76 h 12" class="svg-ink-stroke" stroke-width="2.4" stroke-linecap="round" />
                    <path d="M150 42 l -7 -5 M190 42 l 7 -5 M170 38 v -9" class="svg-orange-stroke" stroke-width="2.6" stroke-linecap="round" />
                  </g>
                  <g class="char" data-amp="4">
                    <text x="316" y="70" class="svg-small-label svg-primary-fill">Got it!</text>
                  </g>
                </svg>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section ref="toolsSectionRef" class="tools nopin">
        <div ref="toolstageRef" class="toolstage">
          <div ref="toolpinRef" class="toolpin">
            <div class="inner toolhead">
              <div class="head">
                <span class="kick2">Platform tools</span>
                <h2>
                  <span class="row"><span>Everything the</span></span>
                  <span class="row"><span>tutoring loop needs.</span></span>
                </h2>
                <p>
                  Built for peer learning programs that need matching, scheduling, reporting,
                  and fair tutor visibility.
                </p>
              </div>
            </div>
            <div ref="tooltrackRef" class="tooltrack">
              <article
                v-for="(tool, index) in railTools"
                :key="tool.id"
                class="tslab hoverable"
              >
                <span class="num" aria-hidden="true">{{ String(index + 1).padStart(2, '0') }}</span>
                <div class="ttext">
                  <h3>{{ tool.title }}</h3>
                  <p>{{ tool.copy }}</p>
                </div>
                <div class="tviz" aria-hidden="true">
                  <svg
                    v-if="tool.id === 'matching'"
                    viewBox="0 0 200 170"
                    fill="none"
                  >
                    <g class="char" data-amp="3">
                      <circle cx="86" cy="76" r="46" class="svg-green-tint-fill svg-ink-stroke" stroke-width="2.5" />
                      <path d="M120 110 l 34 34" class="svg-ink-stroke" stroke-width="3" stroke-linecap="round" />
                      <path
                        d="M86 56 l 6.2 13.2 14.6 1.9 -10.7 10 2.8 14.4 -12.9 -7.1 -12.9 7.1 2.8 -14.4 -10.7 -10 14.6 -1.9 z"
                        class="svg-yellow-fill svg-ink-stroke"
                        stroke-width="2.2"
                        stroke-linejoin="round"
                      />
                    </g>
                    <g class="char" data-amp="5">
                      <path d="M160 36 q 6 -10 14 -2" class="svg-primary-stroke" stroke-width="2.5" stroke-linecap="round" />
                      <path d="M156 50 q 8 -4 12 2" class="svg-primary-stroke" stroke-width="2.5" stroke-linecap="round" />
                    </g>
                    <g class="char" data-amp="4">
                      <path
                        d="M22 28 l 3 8 8 1.5 -6 5.6 1.6 8.2 -6.6 -4.4 -6.6 4.4 1.6 -8.2 -6 -5.6 8 -1.5 z"
                        class="svg-pink-fill svg-ink-stroke svg-fade-strong"
                        stroke-width="2"
                        stroke-linejoin="round"
                      />
                    </g>
                  </svg>

                  <svg
                    v-else-if="tool.id === 'scheduling'"
                    viewBox="0 0 200 170"
                    fill="none"
                  >
                    <g class="char" data-amp="2.5">
                      <rect x="30" y="34" width="124" height="108" rx="14" class="svg-card-fill svg-ink-stroke" stroke-width="2.5" />
                      <path d="M30 64 h 124" class="svg-ink-stroke" stroke-width="2.5" />
                      <path d="M58 24 v 18 M126 24 v 18" class="svg-ink-stroke" stroke-width="3" stroke-linecap="round" />
                      <circle cx="58" cy="88" r="4" class="svg-calendar-dot-fill" />
                      <circle cx="92" cy="88" r="4" class="svg-calendar-dot-fill" />
                      <circle cx="126" cy="88" r="4" class="svg-calendar-dot-fill" />
                      <circle cx="58" cy="116" r="4" class="svg-calendar-dot-fill" />
                      <circle cx="126" cy="116" r="4" class="svg-calendar-dot-fill" />
                      <circle cx="92" cy="116" r="13" class="svg-soft-primary-fill svg-primary-stroke" stroke-width="2.5" />
                      <path d="M86.5 116 l 4 4.5 7 -9" class="svg-primary-stroke" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
                    </g>
                    <g class="char" data-amp="4.5">
                      <circle cx="166" cy="52" r="20" class="svg-soft-yellow-fill svg-ink-stroke" stroke-width="2.5" />
                      <path d="M166 42 v 10 l 7 5" class="svg-ink-stroke" stroke-width="2.5" stroke-linecap="round" />
                    </g>
                  </svg>

                  <svg
                    v-else-if="tool.id === 'reports'"
                    viewBox="0 0 200 170"
                    fill="none"
                  >
                    <g class="char" data-amp="2.5">
                      <path d="M34 142 q 66 4 132 0" class="svg-ink-stroke" stroke-width="2.5" stroke-linecap="round" />
                      <rect x="48" y="100" width="26" height="40" rx="7" class="svg-soft-pink-fill svg-ink-stroke" stroke-width="2.5" />
                      <rect x="88" y="76" width="26" height="64" rx="7" class="svg-soft-yellow-fill svg-ink-stroke" stroke-width="2.5" />
                      <rect x="128" y="50" width="26" height="90" rx="7" class="svg-green-tint-fill svg-ink-stroke" stroke-width="2.5" />
                    </g>
                    <g class="char" data-amp="4">
                      <path d="M44 64 q 48 -34 96 -22" class="svg-primary-stroke" stroke-width="2.5" stroke-dasharray="2 8" stroke-linecap="round" />
                      <path d="M132 36 l 12 4 -6 11 z" class="svg-primary-fill" />
                    </g>
                    <g class="char" data-amp="5">
                      <circle cx="170" cy="92" r="16" class="svg-yellow-fill svg-ink-stroke" stroke-width="2.5" />
                      <path d="M170 84 v 16 M164 88 h 9 q 4 0 4 4 t -4 4 h -9" class="svg-ink-stroke" stroke-width="2" stroke-linecap="round" />
                    </g>
                  </svg>

                  <svg
                    v-else
                    viewBox="0 0 200 170"
                    fill="none"
                  >
                    <g class="char" data-amp="2.5">
                      <path d="M100 50 v 64" class="svg-ink-stroke" stroke-width="2.5" stroke-linecap="round" />
                      <path d="M76 130 q 24 -8 48 0 l -6 12 q -18 -6 -36 0 z" class="svg-green-tint-fill svg-ink-stroke" stroke-width="2.5" stroke-linejoin="round" />
                      <path d="M40 56 q 60 -12 120 0" class="svg-ink-stroke" stroke-width="2.5" stroke-linecap="round" />
                      <circle cx="100" cy="48" r="6" class="svg-yellow-fill svg-ink-stroke" stroke-width="2.2" />
                    </g>
                    <g class="char" data-amp="4">
                      <path d="M40 56 l -10 26 q 10 8 20 0 z" class="svg-soft-primary-fill svg-ink-stroke" stroke-width="2.2" stroke-linejoin="round" />
                      <circle cx="40" cy="94" r="11" class="svg-primary-fill svg-ink-stroke" stroke-width="2.2" />
                    </g>
                    <g class="char" data-amp="4.5">
                      <path d="M160 56 l -10 26 q 10 8 20 0 z" class="svg-soft-pink-fill svg-ink-stroke" stroke-width="2.2" stroke-linejoin="round" />
                      <circle cx="160" cy="94" r="11" class="svg-pink-fill svg-ink-stroke" stroke-width="2.2" />
                    </g>
                  </svg>
                </div>
              </article>
            </div>
          </div>
        </div>
      </section>

      <section class="countband" aria-label="Studybuddy product facts">
        <div class="inner countstrip">
          <div v-for="count in counts" :key="count.label" class="count reveal">
            <div class="n">
              <span :data-count="count.value">0</span>{{ count.suffix }}
            </div>
            <div class="l">{{ count.label }}</div>
          </div>
        </div>
      </section>

      <section class="faqsec">
        <div class="inner faq">
          <div class="head">
            <span class="kick2">Common questions</span>
            <h2>
              <span class="row"><span>Asked a lot,</span></span>
              <span class="row"><span>answered straight.</span></span>
            </h2>
          </div>
          <article
            v-for="(item, index) in faqs"
            :key="item.question"
            class="faqitem"
            :class="{ open: openFaq === index }"
          >
            <button
              class="faqq hoverable"
              type="button"
              :aria-expanded="openFaq === index"
              :aria-controls="`faq-answer-${index}`"
              @click="toggleFaq(index)"
            >
              <span class="no">{{ String(index + 1).padStart(2, '0') }}</span>
              <span class="q">{{ item.question }}</span>
              <span class="plusw" aria-hidden="true">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M7 1v12M1 7h12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                </svg>
              </span>
            </button>
            <div class="faqa" :id="`faq-answer-${index}`">
              <div>
                <p>{{ item.answer }}</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <div class="ctawrap">
        <section class="ctapanel" aria-labelledby="landing-cta-title">
          <h2 id="landing-cta-title">
            Your study buddy is<br />
            <em>already on campus.</em>
          </h2>
          <p>Free with your student email &mdash; whether you need the help or you are the help.</p>
          <span ref="magnetRef" class="magnet">
            <button class="btn primary hoverable" type="button" @click="goTo('/register')">
              <span class="fill"></span>
              <span class="lbl">Get started</span>
            </button>
          </span>
        </section>
      </div>

      <footer>Studybuddy &mdash; built by students, for students. Bring it to your campus.</footer>
    </main>
  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import SbThemeToggle from '@/components/SbThemeToggle.vue'

const router = useRouter()
const route = useRoute()

const pageRef = ref(null)
const smoothRef = ref(null)
const scrollSpaceRef = ref(null)
const heroTitleRef = ref(null)
const magnetRef = ref(null)
const toolsSectionRef = ref(null)
const toolstageRef = ref(null)
const toolpinRef = ref(null)
const tooltrackRef = ref(null)
const openFaq = ref(null)

const marqueeItems = [
  { text: 'Get matched', dot: 'y' },
  { text: 'Study together', dot: 'p' },
  { text: 'Actually get it', dot: 'o', em: true },
  { text: 'Tutors earn', dot: 'g' },
  { text: 'Your campus, your buddies', dot: 'y' },
]

const panels = [
  {
    id: 'need',
    titleLines: ['Share what', 'you need.'],
    copy: 'Choose a subject, topic, and goal so Studybuddy can surface the right peers.',
    depth: '0.06',
  },
  {
    id: 'match',
    titleLines: ['Match', 'and book.'],
    copy: 'Compare tutor fit, availability, and ratings, then reserve a time that works.',
    depth: '0.09',
  },
  {
    id: 'track',
    titleLines: ['Learn', 'and track.'],
    copy: 'Wrap each session with history, compensation, and progress details in place.',
    depth: '0.07',
  },
]

const railTools = [
  {
    id: 'matching',
    title: 'Smart tutor matching',
    copy: 'Rank peer tutors by subject fit, ratings, availability, and workload balance.',
  },
  {
    id: 'scheduling',
    title: 'Flexible scheduling',
    copy: 'Book around real tutor availability and keep upcoming sessions easy to scan.',
  },
  {
    id: 'reports',
    title: 'Reports and earnings',
    copy: 'Track completed sessions, tutor compensation, and program-level performance.',
  },
  {
    id: 'balance',
    title: 'Balanced workloads',
    copy: 'Protect session quality by keeping tutor demand visible before calendars fill up.',
  },
]

const counts = [
  { value: 20, suffix: 's', label: "to tell us what's hurting" },
  { value: 98, suffix: '%', label: 'match scores, out in the open' },
  { value: 1, suffix: ' min', label: 'to join with your student email' },
]

const faqs = [
  {
    question: 'Who can become a tutor?',
    answer: "Any student who's strong in a subject. Set your subjects, rate, and availability - you earn per completed session while keeping your own schedule.",
  },
  {
    question: 'How much does it cost?',
    answer: "Joining is free. You only pay per booked session at the tutor's listed rate, and payments are handled online inside the platform.",
  },
  {
    question: 'Can I use it on my campus?',
    answer: "Studybuddy is open to any campus. Sign up with your student email and you'll be matched with peers from your own school.",
  },
  {
    question: 'What happens if a session falls through?',
    answer: 'You can reschedule or cancel ahead of time, and session history keeps everything on record. If something goes wrong, support is one tap away.',
  },
]

const tiltCfg = [
  { max: 7, dir: 1, twist: 0 },
  { max: 12, dir: -1, twist: 1.4 },
  { max: 9, dir: 1, twist: -1.8 },
]

let reducedQuery = null
let pointerQuery = null
let resizeObserver = null
let revealObserver = null
let smoothRafId = null
let heroTimeoutId = null
let motionRunning = false
let isMounted = false
let targetScroll = 0
let currentScroll = 0
let railTravel = 0
const cleanupFns = []
const motionCleanupFns = []
const countRafs = new Set()

const goTo = (path) => {
  stopContinuousMotion({ reset: true })
  router.push(path)
}

const toggleFaq = (index) => {
  openFaq.value = openFaq.value === index ? null : index
}

const addCleanup = (target, event, handler, options, bucket = cleanupFns) => {
  target.addEventListener(event, handler, options)
  bucket.push(() => target.removeEventListener(event, handler, options))
}

const canRunContinuousMotion = () => (
  isMounted
  && route.name === 'home'
  && typeof document !== 'undefined'
  && document.visibilityState === 'visible'
  && reducedQuery
  && pointerQuery
  && !reducedQuery.matches
  && pointerQuery.matches
  && window.innerWidth >= 900
)

const setSpace = () => {
  if (!smoothRef.value || !scrollSpaceRef.value) return
  scrollSpaceRef.value.style.height = `${smoothRef.value.scrollHeight}px`
}

const parallax = () => {
  if (!pageRef.value) return
  const viewportCenter = window.innerHeight / 2
  pageRef.value.querySelectorAll('[data-depth]').forEach((el) => {
    const rect = el.getBoundingClientRect()
    const centerOffset = rect.top + rect.height / 2 - viewportCenter
    const depth = Number.parseFloat(el.dataset.depth || '0')
    el.style.transform = `translateY(${-centerOffset * depth}px)`
  })
}

const charWiggle = (scrollValue) => {
  if (!pageRef.value) return
  pageRef.value.querySelectorAll('.char').forEach((el, index) => {
    const amp = Number.parseFloat(el.dataset.amp || '3')
    const phase = index * 1.7
    const rotate = Math.sin(scrollValue / 55 + phase) * amp
    const y = Math.cos(scrollValue / 48 + phase) * amp * 0.7
    el.style.transform = `rotate(${rotate.toFixed(3)}deg) translateY(${y.toFixed(3)}px)`
  })
}

const measureRail = () => {
  if (!tooltrackRef.value) return
  railTravel = Math.max(0, tooltrackRef.value.scrollWidth - (window.innerWidth - 80))
}

const resetToolRail = () => {
  railTravel = 0
  toolsSectionRef.value?.classList.add('nopin')
  if (toolpinRef.value) {
    toolpinRef.value.style.transform = ''
  }
  if (tooltrackRef.value) {
    tooltrackRef.value.style.transform = ''
  }
}

const toolPin = () => {
  if (!toolstageRef.value || !toolpinRef.value || !tooltrackRef.value || !toolsSectionRef.value) return

  const rect = toolstageRef.value.getBoundingClientRect()
  const span = rect.height - window.innerHeight
  if (span <= 0) return

  const y = Math.max(0, Math.min(span, -rect.top))
  toolpinRef.value.style.transform = `translate3d(0, ${y.toFixed(1)}px, 0)`

  const progress = y / span
  if (progress > 0.01) {
    toolsSectionRef.value.classList.add('in')
  }

  const railProgress = Math.max(0, Math.min(1, (progress - 0.05) / 0.85))
  tooltrackRef.value.style.transform = `translate3d(${(-railProgress * railTravel).toFixed(1)}px, 0, 0)`
}

const runSmoothLoop = () => {
  if (!motionRunning || !smoothRef.value) return

  currentScroll += (targetScroll - currentScroll) * 0.085
  if (Math.abs(targetScroll - currentScroll) < 0.05) {
    currentScroll = targetScroll
  }

  smoothRef.value.style.transform = `translate3d(0, ${-currentScroll}px, 0)`
  parallax()
  charWiggle(currentScroll)
  toolPin()
  smoothRafId = window.requestAnimationFrame(runSmoothLoop)
}

const setupTilt = () => {
  if (!pageRef.value) return
  pageRef.value.querySelectorAll('.panel .viz').forEach((card, index) => {
    const cfg = tiltCfg[index % tiltCfg.length]
    const handleMove = (event) => {
      const rect = card.getBoundingClientRect()
      const px = (event.clientX - rect.left) / rect.width - 0.5
      const py = (event.clientY - rect.top) / rect.height - 0.5
      card.style.transition = 'clip-path .9s var(--sb-spring), box-shadow .4s ease, transform .1s linear'
      card.style.transform =
        `perspective(900px) rotateX(${(-py * cfg.max * cfg.dir).toFixed(2)}deg)` +
        ` rotateY(${(px * cfg.max * cfg.dir).toFixed(2)}deg) rotate(${cfg.twist}deg) scale(1.025)`
    }
    const handleLeave = () => {
      card.style.transition = 'clip-path .9s var(--sb-spring), box-shadow .4s ease, transform .6s var(--sb-spring)'
      card.style.transform = ''
    }
    addCleanup(card, 'mousemove', handleMove, undefined, motionCleanupFns)
    addCleanup(card, 'mouseleave', handleLeave, undefined, motionCleanupFns)
  })
}

const setupMagnet = () => {
  if (!magnetRef.value) return
  const strength = 0.35
  const handleMove = (event) => {
    const rect = magnetRef.value.getBoundingClientRect()
    const dx = event.clientX - (rect.left + rect.width / 2)
    const dy = event.clientY - (rect.top + rect.height / 2)
    magnetRef.value.style.transition = ''
    magnetRef.value.style.transform = `translate(${dx * strength}px, ${dy * strength}px)`
  }
  const handleLeave = () => {
    magnetRef.value.style.transition = 'transform .5s var(--sb-spring)'
    magnetRef.value.style.transform = 'translate(0, 0)'
  }
  addCleanup(magnetRef.value, 'mousemove', handleMove, undefined, motionCleanupFns)
  addCleanup(magnetRef.value, 'mouseleave', handleLeave, undefined, motionCleanupFns)
}

const startContinuousMotion = () => {
  if (motionRunning || !canRunContinuousMotion() || !smoothRef.value || !scrollSpaceRef.value) return

  motionRunning = true
  targetScroll = window.scrollY
  currentScroll = window.scrollY
  toolsSectionRef.value?.classList.remove('nopin')
  setSpace()
  measureRail()
  smoothRef.value.style.position = 'fixed'
  smoothRef.value.style.top = '0'
  smoothRef.value.style.left = '0'
  smoothRef.value.style.width = '100%'
  smoothRef.value.style.transform = `translate3d(0, ${-currentScroll}px, 0)`
  scrollSpaceRef.value.style.display = 'block'

  resizeObserver = new ResizeObserver(setSpace)
  resizeObserver.observe(smoothRef.value)

  addCleanup(window, 'scroll', () => {
    targetScroll = window.scrollY
  }, { passive: true }, motionCleanupFns)

  addCleanup(window, 'resize', () => {
    measureRail()
  }, { passive: true }, motionCleanupFns)

  setupTilt()
  setupMagnet()
  runSmoothLoop()
}

const stopContinuousMotion = ({ reset = false } = {}) => {
  motionRunning = false

  if (smoothRafId) window.cancelAnimationFrame(smoothRafId)
  smoothRafId = null

  motionCleanupFns.splice(0).forEach((cleanup) => cleanup())

  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }

  if (!reset) return

  if (smoothRef.value) {
    smoothRef.value.style.position = ''
    smoothRef.value.style.top = ''
    smoothRef.value.style.left = ''
    smoothRef.value.style.width = ''
    smoothRef.value.style.transform = ''
  }
  if (scrollSpaceRef.value) {
    scrollSpaceRef.value.style.height = '0px'
    scrollSpaceRef.value.style.display = 'none'
  }
  resetToolRail()
  pageRef.value?.querySelectorAll('[data-depth], .char, .panel .viz').forEach((el) => {
    el.style.transform = ''
    el.style.transition = ''
  })
  if (magnetRef.value) {
    magnetRef.value.style.transform = ''
    magnetRef.value.style.transition = ''
  }
}

const runCount = (el) => {
  if (el.dataset.done) return
  el.dataset.done = '1'
  const end = Number.parseInt(el.dataset.count || '0', 10)

  if (reducedQuery?.matches) {
    el.textContent = String(end)
    return
  }

  const startedAt = performance.now()
  const tick = (time) => {
    countRafs.delete(rafId)
    if (!isMounted || document.visibilityState !== 'visible') {
      return
    }
    const progress = Math.min(1, (time - startedAt) / 1100)
    el.textContent = String(Math.round(end * (1 - Math.pow(1 - progress, 3))))
    if (progress < 1) {
      rafId = window.requestAnimationFrame(tick)
      countRafs.add(rafId)
    } else {
      countRafs.delete(rafId)
    }
  }

  let rafId = window.requestAnimationFrame(tick)
  countRafs.add(rafId)
}

const revealAllStatic = () => {
  if (!pageRef.value) return
  pageRef.value.querySelectorAll('.reveal, .panel, .tools, .faq, .tslab, .faqitem, .hero-title').forEach((el) => {
    el.classList.add('in')
  })
  pageRef.value.querySelectorAll('[data-count]').forEach((el) => {
    el.textContent = el.dataset.count || '0'
    el.dataset.done = '1'
  })
}

const setupReveals = () => {
  if (!pageRef.value) return

  if (reducedQuery?.matches) {
    revealAllStatic()
    return
  }

  revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return
      entry.target.classList.add('in')
      entry.target.querySelectorAll('[data-count]').forEach(runCount)
    })
  }, { threshold: 0.25 })

  pageRef.value.querySelectorAll('.reveal, .panel, .tools, .faq, .tslab, .faqitem, .count').forEach((el) => {
    revealObserver.observe(el)
  })

  heroTimeoutId = window.setTimeout(() => {
    heroTitleRef.value?.classList.add('in')
  }, 80)
}

const handleVisibilityChange = () => {
  if (document.visibilityState === 'hidden') {
    stopContinuousMotion({ reset: false })
    return
  }

  setSpace()
  startContinuousMotion()
}

const handleMotionPreferenceChange = () => {
  stopContinuousMotion({ reset: true })
  if (reducedQuery?.matches) {
    revealAllStatic()
    return
  }
  startContinuousMotion()
}

const handleEligibilityResize = () => {
  if (!canRunContinuousMotion()) {
    stopContinuousMotion({ reset: true })
    return
  }

  if (motionRunning) {
    setSpace()
    measureRail()
    return
  }

  startContinuousMotion()
}

const cleanupAll = () => {
  isMounted = false
  document.body.classList.remove('sb-landing-route')
  stopContinuousMotion({ reset: true })

  if (revealObserver) {
    revealObserver.disconnect()
    revealObserver = null
  }

  if (heroTimeoutId) {
    window.clearTimeout(heroTimeoutId)
    heroTimeoutId = null
  }

  countRafs.forEach((id) => window.cancelAnimationFrame(id))
  countRafs.clear()
  cleanupFns.splice(0).forEach((cleanup) => cleanup())
}

onMounted(async () => {
  isMounted = true
  document.body.classList.add('sb-landing-route')
  reducedQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  pointerQuery = window.matchMedia('(pointer: fine)')

  addCleanup(document, 'visibilitychange', handleVisibilityChange)
  addCleanup(reducedQuery, 'change', handleMotionPreferenceChange)
  addCleanup(pointerQuery, 'change', handleMotionPreferenceChange)
  addCleanup(window, 'resize', handleEligibilityResize, { passive: true })

  await nextTick()
  setupReveals()
  startContinuousMotion()
})

onBeforeRouteLeave(() => {
  cleanupAll()
})

onUnmounted(() => {
  cleanupAll()
})
</script>

<style scoped>
.studio-landing {
  min-height: 100vh;
  color: var(--sb-text-main);
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  overflow-x: hidden;
  position: relative;
}

.studio-landing,
.studio-landing *,
.studio-landing *::before,
.studio-landing *::after {
  box-sizing: border-box;
}

.bgwash {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
  background: linear-gradient(180deg, var(--sb-aurora-wash-start) 0%, var(--sb-bg) 40%, var(--sb-aurora-wash-end) 100%);
}

.bgwash i {
  position: absolute;
  display: block;
}

.bgwash .b1 {
  left: -25vw;
  top: -14vh;
  width: 150vw;
  height: 58vh;
  background: var(--sb-wash-blob-1);
  animation: sway1 36s ease-in-out infinite alternate;
}

.bgwash .b2 {
  right: -30vw;
  top: 20vh;
  width: 135vw;
  height: 50vh;
  background: var(--sb-wash-blob-2);
  animation: sway2 44s ease-in-out infinite alternate;
}

.bgwash .b3 {
  left: -22vw;
  bottom: -18vh;
  width: 145vw;
  height: 52vh;
  background: var(--sb-wash-blob-3);
  animation: sway3 40s ease-in-out infinite alternate;
}

.scroll-space {
  position: relative;
  width: 1px;
  height: 0;
  pointer-events: none;
  z-index: 0;
}

.smooth-root {
  position: relative;
  z-index: 1;
}

.studio-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 40px;
}

.brand,
.navlinks {
  min-width: 0;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  border: 0;
  background: transparent;
  color: var(--sb-text-main);
  font: inherit;
  font-size: 19px;
  font-weight: 900;
  cursor: pointer;
  white-space: nowrap;
}

.brand-mark {
  width: 34px;
  height: 34px;
  flex: 0 0 auto;
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 18px;
}

.navlinks {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.btn {
  font: 600 14.5px 'Inter', system-ui, sans-serif;
  text-decoration: none;
  padding: 10px 26px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border: 0;
  cursor: pointer;
  white-space: nowrap;
  line-height: 1.2;
}

.btn.primary {
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
}

.btn.outline {
  border: 1.5px solid color-mix(in srgb, var(--sb-text-main) 20%, transparent);
  color: var(--sb-text-main);
  background: color-mix(in srgb, var(--sb-card-bg) 84%, transparent);
}

.btn .fill {
  position: absolute;
  inset: 0;
  background: var(--sb-dark);
  border-radius: inherit;
  transform: translateY(101%);
  transition: transform .35s var(--sb-spring);
  z-index: 0;
}

.btn .lbl {
  position: relative;
  z-index: 1;
}

.btn:hover .fill,
.btn:focus-visible .fill {
  transform: translateY(0);
}

.btn:focus-visible,
.brand:focus-visible,
.faqq:focus-visible {
  outline: 3px solid color-mix(in srgb, var(--sb-primary) 34%, transparent);
  outline-offset: 4px;
}

section {
  position: relative;
  padding: 0 40px;
}

.inner {
  max-width: 1240px;
  margin: 0 auto;
}

.hero {
  min-height: 100vh;
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-top: 86px;
}

.kick,
.kick2 {
  display: block;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--sb-primary);
}

.kick {
  margin: 0 0 26px;
}

.hero-title {
  margin: 0;
  font-size: clamp(54px, 8.6vw, 132px);
  font-weight: 900;
  letter-spacing: -0.045em;
  line-height: 0.96;
  text-wrap: balance;
}

.row {
  display: block;
  overflow: hidden;
  padding-bottom: .08em;
  margin-bottom: -.08em;
}

.row > span {
  display: inline-block;
  transform: translateY(112%);
  transition: transform 1s var(--sb-spring);
}

.in .row > span,
.hero-title.in .row > span {
  transform: none;
}

.in .row,
.hero-title.in .row {
  overflow: visible;
}

.hero-title .row:nth-child(2) > span,
.tools h2 .row:nth-child(2) > span,
.faq h2 .row:nth-child(2) > span {
  transition-delay: .08s;
}

.hero-title .row:nth-child(3) > span {
  transition-delay: .16s;
}

.hero-title em,
.marquee em {
  font-style: normal;
  color: var(--sb-primary);
}

.hero-sub {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: 40px;
  gap: 32px;
  flex-wrap: wrap;
}

.hero-sub p {
  max-width: 430px;
  min-width: min(100%, 280px);
  margin: 0;
  font-size: 17px;
  line-height: 1.65;
  color: var(--sb-text-muted);
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.scroll-cue {
  font-size: 12px;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--sb-text-muted);
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}

.scroll-cue .bar {
  width: 1.5px;
  height: 44px;
  background: color-mix(in srgb, var(--sb-text-main) 25%, transparent);
  position: relative;
  overflow: hidden;
}

.scroll-cue .bar::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  height: 50%;
  background: var(--sb-primary);
  animation: cue 1.6s ease-in-out infinite;
}

.marquee {
  border-top: 1px solid var(--sb-card-border);
  border-bottom: 1px solid var(--sb-card-border);
  padding: 22px 0;
  overflow: hidden;
  background: var(--sb-card-bg);
  position: relative;
  z-index: 1;
}

.marquee-track {
  display: flex;
  width: fit-content;
  animation: mq 26s linear infinite;
}

.marquee-copy {
  font-size: clamp(20px, 2.4vw, 30px);
  font-weight: 800;
  letter-spacing: -0.5px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: space-around;
  gap: 56px;
  flex: 0 0 auto;
  min-width: 100vw;
  width: max-content;
  padding-right: 56px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  flex: 0 0 auto;
}

.dot.y { background: var(--sb-pop-yellow); }
.dot.p { background: var(--sb-pop-pink); }
.dot.o { background: var(--sb-pop-orange); }
.dot.g { background: var(--sb-primary); }

.panels {
  padding-top: 110px;
  padding-bottom: 40px;
}

.panel {
  display: grid;
  grid-template-columns: 90px minmax(0, 1fr) minmax(280px, 1fr);
  gap: 40px;
  align-items: center;
  border-top: 1px solid var(--sb-card-border);
  padding: 64px 0;
}

.idx {
  font-size: 15px;
  font-weight: 800;
  color: var(--sb-text-muted);
}

.idx b {
  color: var(--sb-primary);
}

.panel-copy {
  min-width: 0;
}

.panel h2,
.tools h2,
.faq h2 {
  margin: 0;
  font-weight: 900;
  text-wrap: balance;
}

.panel h2 {
  font-size: clamp(30px, 3.8vw, 52px);
  letter-spacing: -0.03em;
  line-height: 1.02;
  margin-bottom: 16px;
}

.panel h2 .row > span {
  transition-duration: .85s;
}

.panel p,
.tools .head p,
.faq .head p {
  color: var(--sb-text-muted);
  line-height: 1.65;
}

.panel p {
  margin: 0;
  font-size: 15.5px;
  max-width: 430px;
}

.viz {
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 26px;
  overflow: hidden;
  box-shadow: 0 24px 60px color-mix(in srgb, var(--sb-dark) 7%, transparent);
  clip-path: inset(12% 6% 12% 6% round 26px);
  transition: clip-path .9s var(--sb-spring), box-shadow .4s ease, border-color .4s ease;
  min-width: 0;
}

.panel.in .viz {
  clip-path: inset(0 0 0 0 round 26px);
}

.panel:nth-of-type(1) .viz:hover {
  border-color: color-mix(in srgb, var(--sb-primary) 55%, var(--sb-card-border));
  box-shadow: 0 8px 20px color-mix(in srgb, var(--sb-dark) 22%, transparent), 0 28px 56px color-mix(in srgb, var(--sb-dark) 26%, transparent), 0 48px 110px color-mix(in srgb, var(--sb-primary) 55%, transparent);
}

.panel:nth-of-type(2) .viz:hover {
  border-color: color-mix(in srgb, var(--sb-pop-yellow) 55%, var(--sb-card-border));
  box-shadow: 0 8px 20px color-mix(in srgb, var(--sb-dark) 22%, transparent), 0 28px 56px color-mix(in srgb, var(--sb-dark) 26%, transparent), 0 48px 110px color-mix(in srgb, var(--sb-pop-yellow) 60%, transparent);
}

.panel:nth-of-type(3) .viz:hover {
  border-color: color-mix(in srgb, var(--sb-pop-orange) 55%, var(--sb-card-border));
  box-shadow: 0 8px 20px color-mix(in srgb, var(--sb-dark) 22%, transparent), 0 28px 56px color-mix(in srgb, var(--sb-dark) 26%, transparent), 0 48px 110px color-mix(in srgb, var(--sb-pop-orange) 58%, transparent);
}

.ill {
  padding: 30px;
}

.ill svg,
.tviz svg {
  width: 100%;
  height: auto;
  display: block;
}

.tviz svg {
  overflow: visible;
}

.char {
  transform-box: fill-box;
  transform-origin: center;
}

.countband {
  background: color-mix(in srgb, var(--sb-primary) 4.5%, transparent);
  border-top: 1px solid color-mix(in srgb, var(--sb-primary) 12%, var(--sb-card-border));
  border-bottom: 1px solid color-mix(in srgb, var(--sb-primary) 12%, var(--sb-card-border));
}

.countstrip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
  padding: 130px 0;
}

.count {
  border-left: 1px solid color-mix(in srgb, var(--sb-primary) 28%, transparent);
  padding-left: 28px;
  min-width: 0;
  position: relative;
}

.count::before {
  content: "";
  position: absolute;
  top: 4px;
  left: -2px;
  width: 3px;
  height: 58px;
  border-radius: 999px;
  background: var(--sb-primary);
}

.count .n {
  font-size: clamp(54px, 6.7vw, 96px);
  font-weight: 900;
  letter-spacing: -0.03em;
  line-height: 1.04;
}

.count .l {
  color: var(--sb-text-muted);
  font-size: 14px;
  margin-top: 6px;
  line-height: 1.45;
}

.tools {
  padding: 0 40px;
}

.kick2 {
  margin-bottom: 18px;
}

.tools .head,
.faq .head {
  max-width: 780px;
  margin-bottom: 84px;
}

.tools h2,
.faq h2 {
  font-size: clamp(34px, 4.6vw, 64px);
  letter-spacing: -0.035em;
  line-height: 1;
}

.tools h2 .row > span,
.faq h2 .row > span {
  transition-duration: .9s;
}

.tools .head p,
.faq .head p {
  font-size: 16.5px;
  margin: 16px 0 0;
  max-width: 540px;
}

.toolstage {
  height: 300vh;
}

.toolpin {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
  will-change: transform;
}

.toolhead {
  width: 100%;
}

.tooltrack {
  display: flex;
  gap: 28px;
  will-change: transform;
}

.tslab {
  flex: 0 0 60vw;
  min-height: 30vh;
  position: relative;
  overflow: hidden;
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 30px;
  padding: 46px 48px;
  display: flex;
  align-items: center;
  gap: 40px;
  box-shadow: 0 24px 60px color-mix(in srgb, var(--sb-dark) 6%, transparent);
  transition: box-shadow .35s ease;
  min-width: 0;
}

.tslab .num {
  flex: none;
  pointer-events: none;
  user-select: none;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(90px, 8.5vw, 140px);
  font-style: italic;
  font-weight: 700;
  line-height: .8;
  opacity: .2;
  transform: translateY(6px);
}

.tslab:nth-child(1) .num { color: var(--sb-primary); }
.tslab:nth-child(2) .num { color: var(--sb-pop-yellow-deep); }
.tslab:nth-child(3) .num { color: var(--sb-pop-orange-deep); }
.tslab:nth-child(4) .num { color: var(--sb-pop-pink-deep); }

.tslab:nth-child(1):hover {
  box-shadow: 0 30px 70px color-mix(in srgb, var(--sb-primary) 20%, transparent);
}

.tslab:nth-child(2):hover {
  box-shadow: 0 30px 70px color-mix(in srgb, var(--sb-pop-yellow) 26%, transparent);
}

.tslab:nth-child(3):hover {
  box-shadow: 0 30px 70px color-mix(in srgb, var(--sb-pop-orange) 24%, transparent);
}

.tslab:nth-child(4):hover {
  box-shadow: 0 30px 70px color-mix(in srgb, var(--sb-pop-pink) 26%, transparent);
}

.tslab .ttext {
  flex: 1 1 auto;
  min-width: 0;
}

.tslab h3 {
  margin: 0 0 16px;
  font-size: clamp(34px, 3.4vw, 58px);
  font-weight: 900;
  letter-spacing: -0.035em;
  line-height: 1.02;
  text-wrap: balance;
}

.tslab p {
  max-width: 560px;
  margin: 0;
  color: var(--sb-text-muted);
  font-size: clamp(17px, 1.5vw, 21px);
  line-height: 1.6;
}

.tslab .tviz {
  flex: none;
  width: clamp(120px, 11.5vw, 180px);
}

.nopin .toolstage {
  height: auto;
}

.nopin .toolpin {
  height: auto;
  padding: 110px 0 100px;
  transform: none !important;
}

.nopin .tooltrack {
  flex-wrap: wrap;
  transform: none !important;
}

.nopin .tslab {
  flex-basis: 100%;
  min-height: 0;
  padding: 44px 36px 40px;
}

.faqsec {
  padding-top: 170px;
  padding-bottom: 150px;
}

.faq {
  max-width: 880px;
  margin: 0 auto;
}

.faqitem {
  border-top: 1px solid var(--sb-card-border);
  transform: translateY(26px);
  transition: transform .6s var(--sb-spring), border-color .25s ease;
}

.faqitem.in {
  transform: none;
}

.faqitem:nth-of-type(2) { transition-delay: .07s; }
.faqitem:nth-of-type(3) { transition-delay: .14s; }
.faqitem:nth-of-type(4) { transition-delay: .21s; }
.faqitem:last-of-type { border-bottom: 1px solid var(--sb-card-border); }

.faqq {
  width: 100%;
  background: none;
  border: 0;
  font: inherit;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 22px;
  padding: 38px 4px;
  cursor: pointer;
  color: var(--sb-text-main);
}

.faqq .no {
  font-size: 13px;
  font-weight: 800;
  color: var(--sb-primary);
  width: 34px;
  flex: none;
}

.faqq .q {
  font-size: clamp(17px, 2vw, 22px);
  font-weight: 800;
  letter-spacing: -0.3px;
  line-height: 1.25;
  flex: 1 1 auto;
  min-width: 0;
  transition: transform .35s var(--sb-spring), color .25s;
}

.faqq:hover .q {
  transform: translateX(10px);
  color: var(--sb-primary);
}

.faqq .plusw {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1.5px solid var(--sb-card-border);
  display: grid;
  place-items: center;
  flex: none;
  color: var(--sb-text-main);
  transition: transform .45s var(--sb-spring), background .25s, border-color .25s, color .25s;
}

.faqitem.open .plusw {
  transform: rotate(135deg);
  background: var(--sb-primary);
  border-color: var(--sb-primary);
  color: var(--sb-primary-contrast);
}

.faqa {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows .5s var(--sb-spring);
}

.faqitem.open .faqa {
  grid-template-rows: 1fr;
}

.faqa > div {
  overflow: hidden;
}

.faqa p {
  padding: 0 4px 38px 56px;
  margin: 0;
  color: var(--sb-text-muted);
  font-size: 15.5px;
  line-height: 1.65;
  max-width: 660px;
}

.ctawrap {
  padding: 40px 40px 120px;
}

.ctapanel {
  background: var(--sb-dark);
  color: white;
  border-radius: 32px;
  padding: 110px 48px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.ctapanel::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(520px 360px at 78% 8%, color-mix(in srgb, var(--sb-primary) 40%, transparent), transparent 70%);
}

.ctapanel h2 {
  position: relative;
  margin: 0;
  font-size: clamp(38px, 5.6vw, 84px);
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 0.98;
  text-wrap: balance;
}

.ctapanel h2 em {
  font-style: normal;
  color: var(--sb-pop-yellow);
}

.ctapanel p {
  position: relative;
  color: color-mix(in srgb, white 62%, transparent);
  margin: 22px auto 38px;
  font-size: 16px;
  line-height: 1.65;
  max-width: 560px;
}

.magnet {
  position: relative;
  display: inline-block;
}

.magnet .btn {
  font-size: 16px;
  padding: 16px 44px;
}

footer {
  padding: 26px 40px 90px;
  text-align: center;
  color: var(--sb-text-muted);
  font-size: 13.5px;
  line-height: 1.65;
}

.reveal {
  opacity: 0;
  transform: translateY(34px);
  transition: opacity .8s ease, transform .8s var(--sb-spring);
}

.reveal.in {
  opacity: 1;
  transform: none;
}

.svg-label { font: 800 17px 'Inter', system-ui, sans-serif; }
.svg-small-label { font: 800 14px 'Inter', system-ui, sans-serif; }
.svg-muted-label { font: 400 14px 'Inter', system-ui, sans-serif; }
.svg-ink-fill { fill: var(--sb-text-main); }
.svg-ink-stroke { stroke: var(--sb-text-main); }
.svg-primary-fill { fill: var(--sb-primary); }
.svg-primary-stroke { stroke: var(--sb-primary); }
.svg-contrast-fill { fill: var(--sb-primary-contrast); }
.svg-card-fill { fill: var(--sb-card-bg); }
.svg-card-stroke { stroke: var(--sb-card-border); }
.svg-muted-fill { fill: var(--sb-text-muted); }
.svg-yellow-fill { fill: var(--sb-pop-yellow); }
.svg-yellow-stroke { stroke: var(--sb-pop-yellow); }
.svg-pink-fill { fill: var(--sb-pop-pink); }
.svg-pink-stroke { stroke: var(--sb-pop-pink); }
.svg-orange-stroke { stroke: var(--sb-pop-orange); }
.svg-green-tint-fill { fill: var(--sb-primary-light); }
.svg-green-tint-stroke { stroke: var(--sb-primary-lighter); }
.svg-note-fill { fill: color-mix(in srgb, var(--sb-pop-yellow) 18%, var(--sb-card-bg)); }
.svg-calendar-dot-fill { fill: color-mix(in srgb, var(--sb-text-muted) 34%, transparent); }
.svg-soft-primary-fill { fill: color-mix(in srgb, var(--sb-primary) 12%, var(--sb-card-bg)); }
.svg-soft-yellow-fill { fill: color-mix(in srgb, var(--sb-pop-yellow) 22%, var(--sb-card-bg)); }
.svg-soft-pink-fill { fill: color-mix(in srgb, var(--sb-pop-pink) 20%, var(--sb-card-bg)); }
.svg-fade-strong { opacity: .85; }

@keyframes sway1 {
  from { transform: rotate(-14deg); }
  to { transform: rotate(-9deg) translate(6vw, 5vh) scaleY(1.18); }
}

@keyframes sway2 {
  from { transform: rotate(10deg); }
  to { transform: rotate(14deg) translate(-7vw, -4vh) scaleY(1.14); }
}

@keyframes sway3 {
  from { transform: rotate(-6deg); }
  to { transform: rotate(-2deg) translate(5vw, -3vh) scaleY(1.2); }
}

@keyframes cue {
  0% { top: -50%; }
  100% { top: 100%; }
}

@keyframes mq {
  to { transform: translateX(-50%); }
}

@media (max-width: 900px) {
  .studio-nav {
    padding: 14px 20px;
  }

  section {
    padding-left: 24px;
    padding-right: 24px;
  }

  .hero-title {
    font-size: clamp(46px, 13vw, 80px);
  }

  .hero-sub {
    align-items: flex-start;
  }

  .scroll-cue {
    margin-left: 0;
  }

  .panel {
    grid-template-columns: minmax(0, 1fr);
    gap: 22px;
  }

  .toolstage {
    height: auto;
  }

  .toolpin {
    height: auto;
    padding: 110px 0 100px;
    transform: none !important;
  }

  .tooltrack {
    flex-wrap: wrap;
    transform: none !important;
  }

  .tslab {
    flex-basis: 100%;
    min-height: 0;
    padding: 36px 30px;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .tslab .num {
    font-size: 90px;
    transform: none;
  }

  .countstrip {
    grid-template-columns: minmax(0, 1fr);
    gap: 30px;
  }

  .faqsec {
    padding-top: 110px;
    padding-bottom: 100px;
  }
}

@media (max-width: 600px) {
  .brand {
    font-size: 0;
  }

  .navlinks {
    gap: 8px;
  }

  .btn {
    padding: 9px 16px;
    font-size: 13px;
  }

  .hero {
    padding-top: 112px;
  }

  .hero-title {
    font-size: clamp(40px, 14vw, 58px);
    line-height: 1;
  }

  .hero-actions {
    width: 100%;
  }

  .hero-actions .btn {
    flex: 1 1 150px;
  }

  .marquee-copy {
    gap: 34px;
    padding-right: 34px;
  }

  .tools {
    padding-left: 24px;
    padding-right: 24px;
  }

  .countstrip {
    padding: 90px 0;
  }

  .faqq {
    gap: 12px;
    padding: 24px 0;
  }

  .faqa p {
    padding-left: 4px;
  }

  .ctawrap {
    padding: 32px 20px 90px;
  }

  .ctapanel {
    padding: 74px 24px;
    border-radius: 26px;
  }

  footer {
    padding-left: 24px;
    padding-right: 24px;
  }
}

@media (pointer: coarse) {
  .toolstage {
    height: auto;
  }

  .toolpin {
    height: auto;
    padding: 110px 0 100px;
    transform: none !important;
  }

  .tooltrack {
    flex-wrap: wrap;
    transform: none !important;
  }

  .tslab {
    flex-basis: 100%;
    min-height: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .row > span {
    transform: none;
    transition: none;
  }

  .viz {
    clip-path: none;
  }

  .reveal,
  .tslab {
    opacity: 1;
    transform: none;
    transition: none;
  }

  .toolstage {
    height: auto;
  }

  .toolpin {
    height: auto;
    padding: 110px 0 100px;
    transform: none !important;
  }

  .tooltrack {
    flex-wrap: wrap;
    transform: none !important;
  }

  .tslab {
    flex-basis: 100%;
    min-height: 0;
  }

  .faqa {
    transition: none;
  }

  .marquee-track,
  .bgwash i,
  .scroll-cue .bar::after {
    animation: none;
  }
}
</style>
