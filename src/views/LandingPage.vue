<template>
  <div class="sb-landing">
    <!-- ① Navbar -->
    <nav class="sb-nav" aria-label="Main navigation">
      <div class="sb-nav-inner">
        <button class="sb-brand" type="button" @click="router.push('/')">
          <span class="sb-brand-mark" aria-hidden="true">S</span>
          <span>StudyBuddy</span>
        </button>
        <div class="sb-nav-actions">
          <button class="sb-nav-link" type="button" @click="router.push('/login')">Log in</button>
          <button class="sb-btn-pill sb-btn-small" type="button" @click="router.push('/register')">
            Get started
          </button>
        </div>
      </div>
    </nav>

    <!-- ② Hero -->
    <section class="sb-tile sb-tile-white sb-hero">
      <div class="sb-shell sb-hero-inner">
        <p class="sb-eyebrow">University peer tutoring network</p>
        <h1>Learn better, together.</h1>
        <p class="sb-hero-copy">
          Connect with trusted peer tutors, book around your schedule, and keep every session
          organized in one calm StudyBuddy workspace.
        </p>
        <div class="sb-hero-actions" aria-label="Primary actions">
          <button class="sb-btn-pill" type="button" @click="router.push('/register')">
            Get started
          </button>
          <button class="sb-btn-link" type="button" @click="router.push('/login')">Log in</button>
        </div>
        <div class="sb-badge-row" aria-label="StudyBuddy highlights">
          <span class="sb-badge">Smart matching</span>
          <span class="sb-badge">Flexible booking</span>
          <span class="sb-badge">Tutor earnings</span>
          <span class="sb-badge">Progress reports</span>
        </div>
      </div>
    </section>

    <!-- ③ Stats -->
    <section class="sb-tile sb-tile-dark sb-stats" aria-label="StudyBuddy stats">
      <div class="sb-shell sb-stats-grid">
        <div v-for="stat in stats" :key="stat.label" class="sb-stat">
          <strong>{{ stat.value }}</strong>
          <span>{{ stat.label }}</span>
        </div>
      </div>
    </section>

    <!-- ④ How it works -->
    <section class="sb-tile sb-tile-parchment">
      <div class="sb-shell">
        <div class="sb-section-heading">
          <p class="sb-eyebrow">How it works</p>
          <h2>From stuck to scheduled in minutes.</h2>
          <p>
            StudyBuddy keeps the flow simple for students and tutors, from the first search to the
            post-session recap.
          </p>
        </div>
        <div class="sb-process-grid">
          <article v-for="step in steps" :key="step.title" class="sb-step-card">
            <span class="sb-step-number">{{ step.number }}</span>
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
          </article>
        </div>
      </div>
    </section>

    <!-- ⑤ Features -->
    <section class="sb-tile sb-tile-white">
      <div class="sb-shell">
        <div class="sb-section-heading">
          <p class="sb-eyebrow">Platform tools</p>
          <h2>Everything the tutoring loop needs.</h2>
          <p>
            Built for peer learning programs that need matching, scheduling, reporting, and fair
            tutor visibility.
          </p>
        </div>
        <div class="sb-feature-grid">
          <article v-for="feature in features" :key="feature.title" class="sb-card">
            <div class="sb-card-icon" aria-hidden="true">{{ feature.icon }}</div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </article>
        </div>
      </div>
    </section>

    <!-- ⑥ Testimonials -->
    <section class="sb-tile sb-tile-dark">
      <div class="sb-shell">
        <div class="sb-section-heading sb-heading-dark">
          <p class="sb-eyebrow">Student voices</p>
          <h2>Peer support that feels close by.</h2>
          <p>Students and tutors get a focused place to meet, prepare, and keep learning moving.</p>
        </div>
        <div class="sb-testimonial-grid">
          <article
            v-for="testimonial in testimonials"
            :key="testimonial.name"
            class="sb-testimonial-card"
          >
            <p class="sb-quote">"{{ testimonial.quote }}"</p>
            <div class="sb-person">
              <div class="sb-avatar" aria-hidden="true">{{ testimonial.initials }}</div>
              <div>
                <strong>{{ testimonial.name }}</strong>
                <span>{{ testimonial.role }}</span>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- ⑦ FAQ -->
    <section class="sb-tile sb-tile-parchment">
      <div class="sb-shell sb-faq-shell">
        <div class="sb-section-heading">
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
              <span class="sb-accordion-icon" aria-hidden="true">
                {{ openFaq === i ? '-' : '+' }}
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

    <!-- ⑧ CTA -->
    <section class="sb-tile sb-tile-dark sb-cta">
      <div class="sb-shell">
        <p class="sb-eyebrow">Ready when you are</p>
        <h2>Build your next study session around the right peer tutor.</h2>
        <p>Join StudyBuddy and make academic support easier to find, book, and track.</p>
        <div class="sb-cta-actions">
          <button class="sb-btn-pill" type="button" @click="router.push('/register')">
            Sign up free
          </button>
          <button class="sb-btn-outline-dark" type="button" @click="router.push('/login')">
            Log in
          </button>
        </div>
      </div>
    </section>

    <!-- ⑨ Footer -->
    <footer class="sb-tile sb-tile-parchment sb-footer">
      <div class="sb-shell">
        <div class="sb-footer-grid">
          <div>
            <h3>StudyBuddy</h3>
            <p>Peer tutoring made easier for students, tutors, and learning programs.</p>
          </div>
          <div v-for="group in footerLinks" :key="group.title">
            <h4>{{ group.title }}</h4>
            <a v-for="link in group.links" :key="link" href="#top">{{ link }}</a>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
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

const steps = [
  {
    number: '01',
    title: 'Share what you need',
    description: 'Choose a subject, topic, and goal so StudyBuddy can surface the right peers.',
  },
  {
    number: '02',
    title: 'Match and book',
    description: 'Compare tutor fit, availability, and ratings, then reserve a time that works.',
  },
  {
    number: '03',
    title: 'Learn and track',
    description: 'Wrap each session with history, compensation, and progress details in place.',
  },
]

const features = [
  {
    icon: 'M',
    title: 'Smart tutor matching',
    description: 'Rank peer tutors by subject fit, ratings, availability, and workload balance.',
  },
  {
    icon: 'S',
    title: 'Flexible scheduling',
    description: 'Book around real tutor availability and keep upcoming sessions easy to scan.',
  },
  {
    icon: 'R',
    title: 'Reports and earnings',
    description: 'Track completed sessions, tutor compensation, and program-level performance.',
  },
  {
    icon: 'B',
    title: 'Balanced workloads',
    description:
      'Protect session quality by keeping tutor demand visible before calendars fill up.',
  },
]

const testimonials = [
  {
    initials: 'AM',
    name: 'Alyssa M.',
    role: 'Computer science student',
    quote:
      'I found someone who had taken the same professor and understood exactly where I was stuck.',
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
    answer:
      'Approved students with strong subject knowledge can offer help in the courses they know best.',
  },
  {
    question: 'How are tutors recommended?',
    answer: 'StudyBuddy weighs subject fit, availability, tutor ratings, and workload signals.',
  },
  {
    question: 'Can tutors manage their schedules?',
    answer:
      'Yes. Tutors can keep availability visible so students book sessions at realistic times.',
  },
  {
    question: 'Does StudyBuddy track completed sessions?',
    answer:
      'Session history, earnings, and reporting data stay organized for review after tutoring ends.',
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
  --sb-dark: #0a1916;
  --sb-canvas: #ffffff;
  --sb-parchment: #f5f5f7;
  --sb-ink: #1d1d1f;
  --sb-muted: #6e6e73;
  --sb-muted-dark: #ababab;
  --sb-divider: #f0f0f0;
  --sb-green-tint: #edf7f3;
  --sb-green-border: #b8dece;

  min-height: 100vh;
  background: var(--sb-canvas);
  color: var(--sb-ink);
  font-family:
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    sans-serif;
  text-rendering: optimizeLegibility;
}

.sb-landing *,
.sb-landing *::before,
.sb-landing *::after {
  box-sizing: border-box;
}

.sb-nav {
  position: sticky;
  top: 0;
  z-index: 20;
  min-height: 52px;
  background: rgba(255, 255, 255, 0.78);
  border-bottom: 1px solid rgba(240, 240, 240, 0.72);
  backdrop-filter: blur(20px) saturate(180%);
}

.sb-nav-inner,
.sb-shell {
  width: min(100% - 40px, 1120px);
  margin: 0 auto;
}

.sb-nav-inner {
  min-height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.sb-brand,
.sb-nav-link,
.sb-btn-link,
.sb-btn-pill,
.sb-btn-outline-dark,
.sb-accordion-trigger {
  font-family: inherit;
}

.sb-brand,
.sb-nav-link,
.sb-btn-link {
  border: 0;
  background: transparent;
  cursor: pointer;
}

.sb-brand {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  color: var(--sb-ink);
  font-size: 14px;
  font-weight: 700;
  padding: 0;
}

.sb-brand-mark {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--sb-primary);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.sb-nav-actions {
  display: flex;
  align-items: center;
  gap: 18px;
}

.sb-nav-link {
  color: var(--sb-ink);
  font-size: 12px;
  padding: 8px 0;
}

.sb-nav-link:hover,
.sb-btn-link:hover,
.sb-footer a:hover {
  color: var(--sb-primary-hover);
}

.sb-tile {
  margin: 0;
}

.sb-tile-white {
  background: var(--sb-canvas);
  color: var(--sb-ink);
}

.sb-tile-dark {
  background: var(--sb-dark);
  color: #fff;
}

.sb-tile-parchment {
  background: var(--sb-parchment);
  color: var(--sb-ink);
}

.sb-tile:not(.sb-stats):not(.sb-hero):not(.sb-footer) {
  padding: 80px 0;
}

.sb-hero {
  padding: 96px 0 80px;
}

.sb-hero-inner,
.sb-section-heading,
.sb-cta {
  text-align: center;
}

.sb-hero-inner {
  max-width: 880px;
}

.sb-eyebrow {
  margin: 0 0 14px;
  color: var(--sb-primary);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0;
  text-transform: uppercase;
}

.sb-hero h1,
.sb-section-heading h2,
.sb-cta h2 {
  margin: 0;
  letter-spacing: 0;
  line-height: 1.05;
}

.sb-hero h1 {
  max-width: 760px;
  margin: 0 auto;
  font-size: 56px;
  font-weight: 700;
}

.sb-hero-copy,
.sb-section-heading p,
.sb-cta p {
  color: var(--sb-muted);
  font-size: 17px;
  font-weight: 400;
  letter-spacing: 0;
  line-height: 1.58;
}

.sb-hero-copy {
  max-width: 650px;
  margin: 20px auto 0;
}

.sb-hero-actions,
.sb-cta-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  flex-wrap: wrap;
  margin-top: 30px;
}

.sb-btn-pill {
  background: var(--sb-primary);
  color: #fff;
  padding: 11px 28px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  transition:
    background 0.15s ease,
    transform 0.15s ease;
  cursor: pointer;
}

.sb-btn-pill:hover {
  background: var(--sb-primary-hover);
}

.sb-btn-pill:active,
.sb-btn-link:active,
.sb-btn-outline-dark:active,
.sb-nav-link:active,
.sb-brand:active,
.sb-accordion-trigger:active {
  transform: scale(0.95);
}

.sb-btn-small {
  padding: 8px 18px;
  font-size: 12px;
}

.sb-btn-link {
  color: var(--sb-primary);
  font-size: 14px;
  border-bottom: 1px solid var(--sb-primary);
  padding: 11px 0;
  transition:
    color 0.15s ease,
    transform 0.15s ease;
}

.sb-badge-row {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 26px;
}

.sb-badge {
  display: inline-block;
  background: var(--sb-green-tint);
  color: var(--sb-primary);
  border: 1px solid var(--sb-green-border);
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 500;
  padding: 3px 10px;
  margin: 2px;
}

.sb-stats {
  padding: 36px 0;
}

.sb-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 22px;
}

.sb-stat {
  text-align: center;
}

.sb-stat strong {
  display: block;
  color: var(--sb-primary);
  font-size: 34px;
  font-weight: 700;
  line-height: 1;
}

.sb-stat span {
  display: block;
  margin-top: 8px;
  color: var(--sb-muted-dark);
  font-size: 13px;
}

.sb-section-heading {
  max-width: 680px;
  margin: 0 auto 42px;
}

.sb-section-heading h2 {
  font-size: 34px;
  font-weight: 600;
}

.sb-section-heading p {
  margin: 14px 0 0;
}

.sb-heading-dark p:not(.sb-eyebrow),
.sb-cta p {
  color: var(--sb-muted-dark);
}

.sb-process-grid,
.sb-testimonial-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.sb-feature-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.sb-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 18px;
  padding: 28px;
  transition:
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.sb-card:hover {
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.07);
}

.sb-card-icon,
.sb-step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--sb-green-tint);
  color: var(--sb-primary);
  font-size: 13px;
  font-weight: 700;
}

.sb-card h3,
.sb-step-card h3 {
  margin: 20px 0 9px;
  color: var(--sb-ink);
  font-size: 20px;
  font-weight: 600;
  line-height: 1.2;
}

.sb-card p,
.sb-step-card p,
.sb-testimonial-card p,
.sb-footer p,
.sb-footer a,
.sb-legal {
  font-size: 13px;
  line-height: 1.65;
}

.sb-card p,
.sb-step-card p {
  margin: 0;
  color: var(--sb-muted);
}

.sb-step-card {
  padding: 28px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(232, 232, 232, 0.8);
}

.sb-testimonial-card {
  min-height: 100%;
  padding: 28px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.06);
}

.sb-quote {
  margin: 0 0 26px;
  color: #fff;
}

.sb-person {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sb-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--sb-primary);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sb-person strong,
.sb-person span {
  display: block;
}

.sb-person strong {
  font-size: 13px;
  color: #fff;
}

.sb-person span {
  margin-top: 2px;
  color: var(--sb-muted-dark);
  font-size: 12px;
}

.sb-faq-shell {
  max-width: 820px;
}

.sb-accordion {
  border-top: 1px solid #dfdfe2;
}

.sb-accordion-item {
  border-bottom: 1px solid #dfdfe2;
}

.sb-accordion-trigger {
  width: 100%;
  border: 0;
  background: transparent;
  color: var(--sb-ink);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 22px 0;
  font-size: 17px;
  font-weight: 600;
  line-height: 1.35;
  text-align: left;
  cursor: pointer;
  transition:
    color 0.15s ease,
    transform 0.15s ease;
}

.sb-accordion-trigger:hover {
  color: var(--sb-primary);
}

.sb-accordion-icon {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid var(--sb-green-border);
  color: var(--sb-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
  line-height: 1;
}

.sb-accordion-answer {
  overflow: hidden;
}

.sb-accordion-answer p {
  margin: 0;
  padding: 0 42px 22px 0;
  color: var(--sb-muted);
  font-size: 15px;
  line-height: 1.6;
}

.sb-accordion-panel-enter-active,
.sb-accordion-panel-leave-active {
  transition:
    max-height 0.24s ease,
    opacity 0.2s ease;
  max-height: 180px;
}

.sb-accordion-panel-enter-from,
.sb-accordion-panel-leave-to {
  max-height: 0;
  opacity: 0;
}

.sb-accordion-panel-enter-to,
.sb-accordion-panel-leave-from {
  max-height: 180px;
  opacity: 1;
}

.sb-cta .sb-shell {
  max-width: 760px;
}

.sb-cta h2 {
  font-size: 40px;
  font-weight: 700;
}

.sb-cta p {
  margin: 16px auto 0;
  max-width: 560px;
}

.sb-btn-outline-dark {
  color: #fff;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 9999px;
  padding: 11px 28px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition:
    border-color 0.15s ease,
    background 0.15s ease,
    transform 0.15s ease;
}

.sb-btn-outline-dark:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.72);
}

.sb-footer {
  padding: 54px 0 28px;
}

.sb-footer-grid {
  display: grid;
  grid-template-columns: 1.5fr repeat(3, 1fr);
  gap: 36px;
}

.sb-footer h3,
.sb-footer h4 {
  margin: 0 0 12px;
  color: var(--sb-ink);
  font-size: 13px;
  font-weight: 700;
}

.sb-footer p {
  max-width: 280px;
  margin: 0;
  color: var(--sb-muted);
}

.sb-footer a {
  display: block;
  color: var(--sb-muted);
  text-decoration: none;
  line-height: 2.2;
}

.sb-legal {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-top: 42px;
  padding-top: 18px;
  border-top: 1px solid #dfdfe2;
  color: var(--sb-muted);
  line-height: 2.2;
}

@media (max-width: 767px) {
  .sb-nav-inner,
  .sb-shell {
    width: min(100% - 28px, 1120px);
  }

  .sb-nav-actions {
    gap: 12px;
  }

  .sb-hero {
    padding: 72px 0 58px;
  }

  .sb-tile:not(.sb-stats):not(.sb-hero):not(.sb-footer) {
    padding: 58px 0;
  }

  .sb-hero h1 {
    font-size: 34px;
  }

  .sb-section-heading h2,
  .sb-stat strong {
    font-size: 30px;
  }

  .sb-cta h2 {
    font-size: 32px;
  }

  .sb-hero-copy,
  .sb-section-heading p,
  .sb-cta p,
  .sb-accordion-trigger {
    font-size: 16px;
  }

  .sb-stats-grid,
  .sb-process-grid,
  .sb-feature-grid,
  .sb-testimonial-grid,
  .sb-footer-grid {
    grid-template-columns: 1fr;
  }

  .sb-stats-grid {
    gap: 26px;
  }

  .sb-footer {
    padding-top: 46px;
  }

  .sb-legal {
    align-items: flex-start;
    flex-direction: column;
    gap: 4px;
  }
}

@media (max-width: 420px) {
  .sb-brand span:last-child {
    display: none;
  }

  .sb-btn-small {
    padding: 8px 14px;
  }
}
</style>
