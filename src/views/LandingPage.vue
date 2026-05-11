<template>
  <div class="sb-landing relative-container">
    <div class="sb-ambient-bg" aria-hidden="true">
      <div class="blob-interactive" :style="{ transform: blob1Transform }">
        <div class="sb-blob sb-blob-1"></div>
      </div>
      <div class="blob-interactive" :style="{ transform: blob2Transform }">
        <div class="sb-blob sb-blob-2"></div>
      </div>
      <div class="blob-interactive" :style="{ transform: blob3Transform }">
        <div class="sb-blob sb-blob-3"></div>
      </div>
    </div>

    <nav class="sb-nav" aria-label="Main navigation">
      <div class="sb-nav-inner">
        <button class="sb-brand group" type="button" @click="router.push('/')">
          <span class="sb-brand-mark" aria-hidden="true">S</span>
          <span class="sb-brand-text">StudyBuddy</span>
        </button>
        <div class="sb-nav-actions">
          <button class="sb-nav-link" type="button" @click="router.push('/login')">Log in</button>
          <button class="sb-btn-pill sb-btn-small hover-lift" type="button" @click="router.push('/register')">
            Get started
          </button>
        </div>
      </div>
    </nav>

    <section class="sb-tile sb-hero">
      <div class="sb-shell sb-split fade-in-up">
        <div class="sb-hero-content text-left">
          <p class="sb-eyebrow">University peer tutoring network</p>
          <h1 class="sb-gradient-text">Learn better, together.</h1>
          <p class="sb-hero-copy" style="margin-left: 0;">
            Learn from trusted peer tutors, book around your schedule, and keep every session
            organized in one StudyBuddy workspace.
          </p>
          <div class="sb-hero-actions" aria-label="Primary actions" style="justify-content: flex-start;">
            <button class="sb-btn-pill hover-lift" type="button" @click="router.push('/register')">
              Get started
            </button>
            <button class="sb-btn-link hover-lift" type="button" @click="router.push('/login')">Log in</button>
          </div>
          <div class="sb-badge-row" aria-label="StudyBuddy highlights" style="justify-content: flex-start;">
            <span class="sb-badge hover-float">Smart matching</span>
            <span class="sb-badge hover-float" style="animation-delay: 0.1s">Flexible booking</span>
            <span class="sb-badge hover-float" style="animation-delay: 0.2s">Tutor earnings</span>
            <span class="sb-badge hover-float" style="animation-delay: 0.3s">Progress reports</span>
          </div>
        </div>

        <div class="sb-image-wrapper sb-clipart-container hover-float">
          <svg class="sb-clipart-svg" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="80" fill="#ffffff" fill-opacity="0.2"/>
            <path d="M60 110L100 80L140 110" stroke="#00895a" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="100" cy="80" r="16" fill="#00895a"/>
            <circle cx="60" cy="110" r="12" fill="#00895a"/>
            <circle cx="140" cy="110" r="12" fill="#00895a"/>
            <path d="M100 80V130" stroke="#00895a" stroke-width="8" stroke-linecap="round"/>
            <circle cx="100" cy="130" r="12" fill="#00895a"/>
          </svg>
        </div>
      </div>
    </section>

    <section class="sb-tile sb-tile-dark sb-stats glass-panel-dark" aria-label="StudyBuddy stats">
      <div class="sb-shell sb-stats-grid">
        <div v-for="stat in stats" :key="stat.label" class="sb-stat hover-scale">
          <strong>{{ stat.value }}</strong>
          <span>{{ stat.label }}</span>
        </div>
      </div>
    </section>

    <section class="sb-tile sb-tile-glass">
      <div class="sb-shell">
        <div class="sb-section-heading text-center">
          <p class="sb-eyebrow">How it works</p>
          <h2>From stuck to scheduled in minutes.</h2>
          <p class="mx-auto" style="max-width: 600px; margin: 16px auto 0;">
            StudyBuddy keeps the flow simple for students and tutors, from the first search to the
            post-session recap.
          </p>
        </div>

        <div class="sb-process-grid">
          <article class="sb-step-card interactive-card text-center">
            <div class="sb-icon-glass">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </div>
            <span class="sb-step-number-sm">Step 01</span>
            <h3>Share what you need</h3>
            <p>Choose a subject, topic, and goal so StudyBuddy can surface the right peers.</p>
          </article>

          <article class="sb-step-card interactive-card text-center">
            <div class="sb-icon-glass" style="animation-delay: 0.1s">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
            </div>
            <span class="sb-step-number-sm">Step 02</span>
            <h3>Match and book</h3>
            <p>Compare tutor fit, availability, and ratings, then reserve a time that works.</p>
          </article>

          <article class="sb-step-card interactive-card text-center">
            <div class="sb-icon-glass" style="animation-delay: 0.2s">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
            </div>
            <span class="sb-step-number-sm">Step 03</span>
            <h3>Learn and track</h3>
            <p>Wrap each session with history, compensation, and progress details in place.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="sb-tile sb-tile-glass">
      <div class="sb-shell">
        <div class="sb-section-heading text-center">
          <p class="sb-eyebrow">Platform tools</p>
          <h2>Everything the tutoring loop needs.</h2>
          <p class="mx-auto" style="max-width: 600px; margin: 16px auto 0;">
            Built for peer learning programs that need matching, scheduling, reporting, and fair
            tutor visibility.
          </p>
        </div>

        <div class="sb-feature-grid">
          <article class="sb-card interactive-card">
            <div class="sb-icon-glass-sm" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
            </div>
            <h3>Smart tutor matching</h3>
            <p>Rank peer tutors by subject fit, ratings, availability, and workload balance.</p>
          </article>

          <article class="sb-card interactive-card">
            <div class="sb-icon-glass-sm" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
            </div>
            <h3>Flexible scheduling</h3>
            <p>Book around real tutor availability and keep upcoming sessions easy to scan.</p>
          </article>

          <article class="sb-card interactive-card">
            <div class="sb-icon-glass-sm" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
              </svg>
            </div>
            <h3>Reports and earnings</h3>
            <p>Track completed sessions, tutor compensation, and program-level performance.</p>
          </article>

          <article class="sb-card interactive-card">
            <div class="sb-icon-glass-sm" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="4" y1="21" x2="4" y2="14"></line>
                <line x1="4" y1="10" x2="4" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12" y2="3"></line>
                <line x1="20" y1="21" x2="20" y2="16"></line>
                <line x1="20" y1="12" x2="20" y2="3"></line>
                <line x1="1" y1="14" x2="7" y2="14"></line>
                <line x1="9" y1="8" x2="15" y2="8"></line>
                <line x1="17" y1="16" x2="23" y2="16"></line>
              </svg>
            </div>
            <h3>Balanced workloads</h3>
            <p>Protect session quality by keeping tutor demand visible before calendars fill up.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="sb-tile sb-tile-dark glass-panel-dark">
      <div class="sb-shell">
        <div class="sb-section-heading sb-heading-dark text-center">
          <p class="sb-eyebrow" style="color: #fff">Student voices</p>
          <h2>Peer support that feels close by.</h2>
          <p class="mx-auto" style="max-width: 600px; margin: 16px auto 0;">Students and tutors get a focused place to meet, prepare, and keep learning moving.</p>
        </div>
        <div class="sb-testimonial-grid">
          <article
            v-for="testimonial in testimonials"
            :key="testimonial.name"
            class="sb-testimonial-card interactive-card-dark"
          >
            <p class="sb-quote">"{{ testimonial.quote }}"</p>
            <div class="sb-person">
              <div class="sb-avatar" aria-hidden="true">{{ testimonial.initials }}</div>
              <div class="sb-person-info">
                <strong>{{ testimonial.name }}</strong>
                <span>{{ testimonial.role }}</span>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="sb-tile sb-tile-glass">
      <div class="sb-shell sb-faq-shell">
        <div class="sb-section-heading text-center">
          <p class="sb-eyebrow">FAQ</p>
          <h2>Questions before your first session.</h2>
        </div>
        <div class="sb-accordion">
          <article v-for="(item, i) in faqs" :key="item.question" class="sb-accordion-item">
            <button
              class="sb-accordion-trigger"
              type="button"
              :aria-expanded="openFaq === i"
              :aria-controls="`faq-answer-${i}`"
              @click="toggleFaq(i)"
            >
              <span>{{ item.question }}</span>
              <span class="sb-accordion-icon" :class="{'rotate-icon': openFaq === i}" aria-hidden="true">
                +
              </span>
            </button>
            <transition name="sb-accordion-panel">
              <div v-show="openFaq === i" :id="`faq-answer-${i}`" class="sb-accordion-answer">
                <p>{{ item.answer }}</p>
              </div>
            </transition>
          </article>
        </div>
      </div>
    </section>

    <section class="sb-tile sb-tile-dark glass-panel-dark sb-cta">
      <div class="sb-shell sb-split">
        <div class="text-left">
          <p class="sb-eyebrow" style="color: #fff">Ready when you are</p>
          <h2 style="text-align: left;">Build your next study session around the right peer tutor.</h2>
          <p style="margin-left: 0; text-align: left;">Join StudyBuddy and make academic support easier to find, book, and track.</p>
          <div class="sb-cta-actions" style="justify-content: flex-start;">
            <button class="sb-btn-pill hover-lift" type="button" @click="router.push('/register')">
              Sign up free
            </button>
            <button class="sb-btn-outline-dark hover-lift" type="button" @click="router.push('/login')">
              Log in
            </button>
          </div>
        </div>

        <div class="sb-image-wrapper sb-clipart-container hover-float" style="border-color: rgba(255,255,255,0.1); background: rgba(255,255,255,0.05)">
          <svg class="sb-clipart-svg" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M100 40L115 80L160 85L125 115L135 160L100 135L65 160L75 115L40 85L85 80L100 40Z" fill="#00895a"/>
            <circle cx="100" cy="100" r="30" fill="#071310"/>
            <path d="M85 100L95 110L115 90" stroke="#00895a" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
    </section>

    <footer class="sb-tile sb-tile-glass sb-footer">
      <div class="sb-shell">
        <div class="sb-footer-grid">
          <div>
            <h3>StudyBuddy</h3>
            <p>Peer tutoring made easier for students, tutors, and learning programs.</p>
          </div>
          <div v-for="group in footerLinks" :key="group.title">
            <h4>{{ group.title }}</h4>
            <a v-for="link in group.links" :key="link" class="footer-link-hover" href="#top">{{ link }}</a>
          </div>
        </div>
        <div class="sb-legal">
          <span>© 2026 StudyBuddy. All rights reserved.</span>
          <span>Built for focused peer learning.</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const mouseX = ref(0)
const mouseY = ref(0)

const handleMouseMove = (e) => {
  if (typeof window !== 'undefined') {
    mouseX.value = (e.clientX / window.innerWidth) * 2 - 1
    mouseY.value = (e.clientY / window.innerHeight) * 2 - 1
  }
}

const blob1Transform = computed(() => `translate(${mouseX.value * 150}px, ${mouseY.value * 150}px)`)
const blob2Transform = computed(() => `translate(${mouseX.value * -150}px, ${mouseY.value * -150}px)`)
const blob3Transform = computed(() => `translate(${mouseX.value * 250}px, ${mouseY.value * 250}px)`)

onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
})
// ------------------------------------

const openFaq = ref(null)
const toggleFaq = (i) => {
  openFaq.value = openFaq.value === i ? null : i
}

const stats = [
  { value: '500+', label: 'Active tutors' },
  { value: '2,000+', label: 'Sessions completed' },
  { value: '4.8', label: 'Average rating' },
  { value: '50+', label: 'Subjects covered' },
]

const testimonials = [
  {
    initials: 'AM',
    name: 'Alyssa M.',
    role: 'Computer science student',
    quote: 'I found someone who had taken the same professor and understood exactly where I was stuck.',
  },
  {
    initials: 'JR',
    name: 'Jon R.',
    role: 'Peer tutor',
    quote: 'My sessions, earnings, and schedule are all in one place, so tutoring feels organized.',
  },
  {
    initials: 'KC',
    name: 'Kara C.',
    role: 'Program coordinator',
    quote: 'The workload view helps us keep support fair without losing sight of student demand.',
  },
]

const faqs = [
  {
    question: 'Who can become a tutor?',
    answer: 'Approved students with strong subject knowledge can offer help in the courses they know best.',
  },
  {
    question: 'How are tutors recommended?',
    answer: 'StudyBuddy weighs subject fit, availability, tutor ratings, and workload signals.',
  },
  {
    question: 'Can tutors manage their schedules?',
    answer: 'Yes. Tutors can keep availability visible so students book sessions at realistic times.',
  },
  {
    question: 'Does StudyBuddy track completed sessions?',
    answer: 'Session history, earnings, and reporting data stay organized for review after tutoring ends.',
  },
]

const footerLinks = [
  { title: 'Product', links: ['Matching', 'Scheduling', 'Reports'] },
  { title: 'Community', links: ['Students', 'Tutors', 'Coordinators'] },
  { title: 'Support', links: ['Help center', 'Privacy', 'Terms'] },
]
</script>

<style scoped>
.sb-landing {
  --sb-primary: #00895a;
  --sb-primary-hover: #00704a;
  --sb-dark: #071310;
  --sb-canvas: #f0fdf4;
  --sb-ink: #0f172a;
  --sb-muted: #475569;
  --sb-muted-dark: #94a3b8;
  --sb-divider: rgba(0, 0, 0, 0.08);

  min-height: 100vh;
  background: var(--sb-canvas);
  color: var(--sb-ink);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  text-rendering: optimizeLegibility;
  position: relative;
  overflow: hidden;
}

.sb-landing *,
.sb-landing *::before,
.sb-landing *::after {
  box-sizing: border-box;
}

/* --- the aesthetic blobs --- */
.sb-ambient-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
  background-color: #f8fafc;
}

.blob-interactive {
  position: absolute;
  width: 100%;
  height: 100%;
  transition: transform 0.2s ease-out;
  will-change: transform;
}

.sb-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(140px);
  mix-blend-mode: multiply;
  animation: swoopIn 2.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.sb-blob-1 {
  width: 70vw;
  height: 70vw;
  background: rgba(16, 185, 129, 0.5);
  top: -20%;
  left: -10%;
}

.sb-blob-2 {
  width: 60vw;
  height: 60vw;
  background: rgba(14, 165, 233, 0.45);
  bottom: -10%;
  right: -10%;
  animation-delay: 0.3s;
}

.sb-blob-3 {
  width: 50vw;
  height: 50vw;
  background: rgba(139, 92, 246, 0.4);
  top: 30%;
  left: 30%;
  animation-delay: 0.6s;
}

@keyframes swoopIn {
  0% { opacity: 0; transform: translate(-10vw, -10vh) scale(0.8); }
  100% { opacity: 1; transform: translate(0, 0) scale(1); }
}

/* --- FOREGROUND COMPONENTS --- */
.sb-nav, .sb-tile {
  position: relative;
  z-index: 1;
}

.sb-nav {
  position: sticky;
  top: 0;
  z-index: 20;
  min-height: 60px;
  background: rgba(255, 255, 255, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(24px) saturate(200%);
  transition: all 0.3s ease;
}

.sb-nav-inner, .sb-shell {
  width: min(100% - 40px, 1120px);
  margin: 0 auto;
}

.sb-nav-inner {
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.sb-brand, .sb-nav-link, .sb-btn-link, .sb-btn-pill, .sb-btn-outline-dark, .sb-accordion-trigger {
  font-family: inherit;
  border: 0;
  background: transparent;
  cursor: pointer;
}

.sb-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--sb-ink);
  font-size: 16px;
  font-weight: 800;
  padding: 0;
  transition: transform 0.2s ease;
}

.sb-brand:hover { transform: scale(1.02); }

.sb-brand-mark {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--sb-primary);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  box-shadow: 0 4px 10px rgba(0, 137, 90, 0.3);
}

.sb-nav-actions { display: flex; align-items: center; gap: 20px; }

.sb-nav-link {
  color: var(--sb-ink);
  font-size: 13px;
  font-weight: 600;
  padding: 8px 0;
  transition: color 0.2s ease;
}

.sb-nav-link:hover, .sb-btn-link:hover { color: var(--sb-primary); }

.sb-tile { margin: 0; }

.sb-tile-glass {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255,255,255,0.8);
}

.glass-panel-dark {
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(24px);
  border-top: 1px solid rgba(255,255,255,0.1);
  border-bottom: 1px solid rgba(0,0,0,0.5);
  color: #fff;
}

.sb-tile:not(.sb-stats):not(.sb-hero):not(.sb-footer) { padding: 100px 0; }
.sb-hero { padding: 120px 0 80px; }

.sb-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
}

.text-left { text-align: left !important; }
.text-center { text-align: center !important; }

.sb-image-wrapper {
  position: relative;
  border-radius: 32px;
  overflow: hidden;
  box-shadow: 0 24px 48px rgba(0,0,0,0.05);
  border: 1px solid rgba(255, 255, 255, 0.8);
  aspect-ratio: 1/1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  max-width: 380px;
  margin: 0 auto;
}

.sb-clipart-svg {
  width: 55%;
  height: 55%;
  position: relative;
  z-index: 1;
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.sb-image-wrapper:hover .sb-clipart-svg {
  transform: scale(1.1) translateY(-10px);
}

.sb-eyebrow {
  margin: 0 0 16px;
  color: var(--sb-primary);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.sb-gradient-text { color: var(--sb-ink); }

.sb-hero h1, .sb-section-heading h2, .sb-cta h2 {
  margin: 0;
  letter-spacing: -0.5px;
  line-height: 1.1;
}

.sb-hero h1 { font-size: 56px; font-weight: 800; }

.sb-hero-copy, .sb-section-heading p, .sb-cta p {
  color: var(--sb-muted);
  font-size: 18px;
  font-weight: 400;
  line-height: 1.6;
}

.sb-hero-copy { margin: 24px 0; }

.sb-hero-actions, .sb-cta-actions {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
  margin-top: 32px;
}

.sb-btn-pill {
  background: var(--sb-primary);
  color: #fff;
  padding: 14px 32px;
  border-radius: 9999px;
  font-size: 15px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 137, 90, 0.3);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.sb-btn-pill:hover { box-shadow: 0 8px 25px rgba(0, 137, 90, 0.5); }

.hover-lift:hover { transform: translateY(-3px); }
.hover-lift:active { transform: translateY(1px); }

.sb-btn-small { padding: 10px 20px; font-size: 13px; box-shadow: none; }

.sb-btn-link {
  color: var(--sb-primary);
  font-size: 15px;
  font-weight: 600;
  border-bottom: 2px solid transparent;
  padding: 10px 0;
  transition: all 0.2s ease;
}

.sb-btn-link:hover { border-bottom-color: var(--sb-primary); }

.sb-badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 32px;
}

.sb-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  color: var(--sb-ink);
  border: 1px solid rgba(255,255,255,1);
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 14px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  transition: transform 0.3s ease;
}

.hover-float:hover { transform: translateY(-4px); }

.sb-stats { padding: 48px 0; }

.sb-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 22px;
}

.sb-stat {
  text-align: center;
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.hover-scale:hover { transform: scale(1.1); }

.sb-stat strong {
  display: block;
  color: #fff;
  font-size: 42px;
  font-weight: 800;
  line-height: 1;
}

.sb-stat span {
  display: block;
  margin-top: 10px;
  color: var(--sb-muted-dark);
  font-size: 14px;
  font-weight: 500;
}

.sb-section-heading {
  max-width: 680px;
  margin: 0 auto 50px;
}

.sb-section-heading h2 { font-size: 40px; font-weight: 700; }
.sb-heading-dark p:not(.sb-eyebrow), .sb-cta p { color: var(--sb-muted-dark); }

/* --- SIDE-BY-SIDE PROCESS CARDS --- */
.sb-process-grid, .sb-feature-grid, .sb-testimonial-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.sb-feature-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }

.interactive-card, .sb-step-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.02);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.sb-icon-glass {
  width: 72px;
  height: 72px;
  margin: 0 auto 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.04);
  color: var(--sb-primary);
}

.sb-icon-glass svg { width: 32px; height: 32px; }

.sb-icon-glass-sm {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  color: var(--sb-primary);
}

.sb-icon-glass-sm svg { width: 24px; height: 24px; }

.sb-step-number-sm {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  margin-bottom: 16px;
  background: rgba(0, 137, 90, 0.1);
  color: var(--sb-primary);
}

.interactive-card::after, .sb-step-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  height: 4px;
  width: 0%;
  background: var(--sb-primary);
  transition: width 0.4s ease;
}

.interactive-card:hover::after, .sb-step-card:hover::after { width: 100%; }

.interactive-card:hover, .sb-step-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.9);
}

.interactive-card-dark {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 32px;
  transition: all 0.4s ease;
}

.interactive-card-dark:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-6px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.sb-card h3, .sb-step-card h3 {
  margin: 0 0 12px;
  color: var(--sb-ink);
  font-size: 22px;
  font-weight: 700;
  line-height: 1.2;
}

.sb-card p, .sb-step-card p, .sb-testimonial-card p, .sb-footer p, .sb-footer a, .sb-legal {
  font-size: 15px;
  line-height: 1.6;
}

.sb-card p, .sb-step-card p { margin: 0; color: var(--sb-muted); }
.sb-quote { margin: 0 0 32px; color: #f8fafc; font-size: 16px; font-style: italic; }

.sb-person { display: flex; align-items: center; gap: 16px; }

.sb-person-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
}

.sb-person-info strong {
  display: block;
  font-size: 15px;
  color: #fff;
  line-height: 1.2;
}

.sb-person-info span {
  display: block;
  margin-top: 4px;
  color: var(--sb-muted-dark);
  font-size: 13px;
}

.sb-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  font-size: 14px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* --- FAQ & ACCORDION --- */
.sb-faq-shell { max-width: 820px; }
.sb-accordion { border-top: 1px solid var(--sb-divider); }
.sb-accordion-item { border-bottom: 1px solid var(--sb-divider); }

.sb-accordion-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 28px 0;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.35;
  text-align: left;
  transition: color 0.2s ease;
}

.sb-accordion-trigger:hover { color: var(--sb-primary); }

.sb-accordion-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid rgba(0,0,0,0.1);
  color: var(--sb-ink);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 20px;
  line-height: 1;
  transition: transform 0.3s ease, background 0.3s ease;
}

.rotate-icon {
  transform: rotate(45deg);
  background: var(--sb-primary);
  color: white;
  border-color: var(--sb-primary);
}

.sb-accordion-answer { overflow: hidden; }
.sb-accordion-answer p { margin: 0; padding: 0 42px 28px 0; color: var(--sb-muted); font-size: 16px; line-height: 1.6; }

.sb-accordion-panel-enter-active, .sb-accordion-panel-leave-active {
  transition: max-height 0.3s ease, opacity 0.3s ease; max-height: 200px;
}
.sb-accordion-panel-enter-from, .sb-accordion-panel-leave-to { max-height: 0; opacity: 0; }
.sb-accordion-panel-enter-to, .sb-accordion-panel-leave-from { max-height: 200px; opacity: 1; }

.sb-btn-outline-dark {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 9999px;
  padding: 14px 32px;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.sb-btn-outline-dark:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.8);
}

.sb-footer {
  padding: 80px 0 32px;
  background: rgba(255, 255, 255, 0.4);
}

.sb-footer-grid {
  display: grid;
  grid-template-columns: 1.5fr repeat(3, 1fr);
  gap: 48px;
}

.sb-footer h3, .sb-footer h4 {
  margin: 0 0 16px;
  color: var(--sb-ink);
  font-size: 14px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.sb-footer p { max-width: 280px; margin: 0; color: var(--sb-muted); }
.sb-footer a { display: block; color: var(--sb-muted); text-decoration: none; line-height: 2.4; transition: color 0.2s ease; }
.footer-link-hover:hover { color: var(--sb-primary); transform: translateX(2px); }

.sb-legal {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-top: 60px;
  padding-top: 24px;
  border-top: 1px solid var(--sb-divider);
  color: var(--sb-muted);
  line-height: 2.2;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-in-up { animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

@media (max-width: 991px) {
  .sb-split { grid-template-columns: 1fr; gap: 40px; }
  .text-left { text-align: center !important; }
  .text-left .sb-eyebrow { justify-content: center; }
  .sb-hero-actions, .sb-badge-row, .sb-section-heading { justify-content: center !important; margin-left: auto !important; margin-right: auto !important; }
  .sb-hero-copy { margin-left: auto !important; margin-right: auto !important; }
  .sb-image-wrapper { max-width: 300px; }
}

@media (max-width: 767px) {
  .sb-nav-inner, .sb-shell { width: min(100% - 32px, 1120px); }
  .sb-hero h1 { font-size: 42px; }
  .sb-stats-grid, .sb-process-grid, .sb-feature-grid, .sb-testimonial-grid, .sb-footer-grid { grid-template-columns: 1fr; }
  .sb-legal { align-items: flex-start; flex-direction: column; gap: 8px; }
}
</style>
