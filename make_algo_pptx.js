const pptxgen = require('pptxgenjs')

const pres = new pptxgen()
pres.layout = 'LAYOUT_16x9'
pres.title = 'StudyBuddy Recommendation Algorithm'

const C = {
  navyDark: '0F2744',
  navy: '1E3A5F',
  teal: '0D9488',
  tealLight: '14B8A6',
  amber: 'F59E0B',
  white: 'FFFFFF',
  offWhite: 'F8FAFC',
  slate: '1E293B',
  slateLight: '64748B',
  slateXLight: 'E2E8F0',
  blue: '3B82F6',
  green: '10B981',
  purple: '8B5CF6',
}

const makeShadow = () => ({ type: 'outer', color: '000000', blur: 8, offset: 3, angle: 135, opacity: 0.12 })

// ============================================================
// SLIDE 1: TITLE
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.navyDark }

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.08, fill: { color: C.teal }, line: { color: C.teal } })

  s.addText('StudyBuddy', {
    x: 0.7, y: 0.95, w: 8.6, h: 0.9,
    fontSize: 48, fontFace: 'Calibri', bold: true, color: C.white, align: 'left', margin: 0
  })
  s.addText('Recommendation Algorithm', {
    x: 0.7, y: 1.82, w: 8.6, h: 0.65,
    fontSize: 30, fontFace: 'Calibri', color: C.tealLight, align: 'left', margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 2.6, w: 3.2, h: 0.05, fill: { color: C.amber }, line: { color: C.amber } })
  s.addText('How CBF + CF combine into a Hybrid scoring system\nthat ranks tutors for every student on the platform', {
    x: 0.7, y: 2.75, w: 8.6, h: 1.0,
    fontSize: 15, fontFace: 'Calibri', color: 'A0B4CC', align: 'left', margin: 0
  })

  const chips = ['Content-Based Filtering', 'Collaborative Filtering', 'Hybrid Scoring']
  chips.forEach((label, i) => {
    const cx = 0.7 + i * 3.05
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: 4.4, w: 2.8, h: 0.45, fill: { color: C.teal, transparency: 75 }, line: { color: C.teal, width: 1 } })
    s.addText(label, { x: cx, y: 4.4, w: 2.8, h: 0.45, fontSize: 12, fontFace: 'Calibri', color: C.tealLight, align: 'center', valign: 'middle', margin: 0 })
  })

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.38, w: 10, h: 0.24, fill: { color: C.teal }, line: { color: C.teal } })
  s.addText('Central Philippine University  —  Peer-to-Peer Tutoring Platform', {
    x: 0, y: 5.38, w: 10, h: 0.24, fontSize: 10, fontFace: 'Calibri', color: C.white, align: 'center', valign: 'middle', margin: 0
  })
}

// ============================================================
// SLIDE 2: SYSTEM OVERVIEW
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.offWhite }

  s.addText('Algorithm Architecture Overview', {
    x: 0.5, y: 0.22, w: 9, h: 0.55, fontSize: 28, fontFace: 'Calibri', bold: true, color: C.slate, align: 'left', margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.79, w: 9, h: 0.04, fill: { color: C.teal }, line: { color: C.teal } })

  const boxes = [
    { title: 'Content-Based\nFiltering (CBF)', sub: 'Matches tutor attributes to student profile.\nNo ratings needed.', color: C.teal, x: 0.4 },
    { title: 'Collaborative\nFiltering (CF)', sub: 'Finds similar students,\npredicts unseen ratings.', color: C.blue, x: 3.6 },
    { title: 'Hybrid\nScoring', sub: 'Weighted blend of\nCBF (70%) + CF (30%).', color: C.amber, x: 6.8 },
  ]
  boxes.forEach(b => {
    s.addShape(pres.shapes.RECTANGLE, { x: b.x, y: 0.95, w: 2.95, h: 2.25, fill: { color: C.white }, line: { color: b.color, width: 2 }, shadow: makeShadow() })
    s.addShape(pres.shapes.RECTANGLE, { x: b.x, y: 0.95, w: 2.95, h: 0.42, fill: { color: b.color }, line: { color: b.color } })
    s.addText(b.title, { x: b.x, y: 0.95, w: 2.95, h: 0.42, fontSize: 12, fontFace: 'Calibri', bold: true, color: C.white, align: 'center', valign: 'middle', margin: 0 })
    s.addText(b.sub, { x: b.x + 0.12, y: 1.45, w: 2.72, h: 1.6, fontSize: 12, fontFace: 'Calibri', color: C.slate, align: 'center', valign: 'top', margin: 0 })
  })

  s.addText('→', { x: 3.35, y: 1.68, w: 0.3, h: 0.38, fontSize: 22, color: C.slateLight, align: 'center', margin: 0 })
  s.addText('→', { x: 6.55, y: 1.68, w: 0.3, h: 0.38, fontSize: 22, color: C.slateLight, align: 'center', margin: 0 })

  s.addShape(pres.shapes.RECTANGLE, { x: 1.2, y: 3.4, w: 7.6, h: 0.9, fill: { color: C.navy }, line: { color: C.navy }, shadow: makeShadow() })
  s.addText([
    { text: 'hybrid_score', options: { bold: true, color: C.amber } },
    { text: '  =  0.7 × ', options: { color: C.white } },
    { text: 'cbf_score', options: { bold: true, color: C.tealLight } },
    { text: '  +  0.3 × (', options: { color: C.white } },
    { text: 'cf_score', options: { bold: true, color: C.green } },
    { text: ' ÷ 5)', options: { color: C.white } },
  ], { x: 1.2, y: 3.4, w: 7.6, h: 0.9, fontSize: 20, fontFace: 'Consolas', align: 'center', valign: 'middle', margin: 0 })

  s.addText('CBF handles cold-start and profile matching. CF adds personalization from past ratings. Hybrid blends both.', {
    x: 0.5, y: 4.45, w: 9, h: 0.45, fontSize: 12, fontFace: 'Calibri', color: C.slateLight, align: 'center', italic: true, margin: 0
  })
}

// ============================================================
// SLIDE 3: CBF OVERVIEW
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.offWhite }

  s.addText('Content-Based Filtering (CBF)', {
    x: 0.5, y: 0.22, w: 9, h: 0.55, fontSize: 28, fontFace: 'Calibri', bold: true, color: C.slate, align: 'left', margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.79, w: 9, h: 0.04, fill: { color: C.teal }, line: { color: C.teal } })

  s.addText('What it does', { x: 0.5, y: 0.97, w: 5.4, h: 0.3, fontSize: 14, bold: true, color: C.slate, margin: 0 })
  s.addText([
    { text: 'Compares student profile attributes to tutor profile attributes.', options: { bullet: true, breakLine: true } },
    { text: 'Produces a score from 0.0 to 1.0  (1 = perfect attribute match).', options: { bullet: true, breakLine: true } },
    { text: 'Works even for brand-new students — no prior ratings required (cold-start safe).', options: { bullet: true, breakLine: true } },
    { text: 'Called inside hybrid_prediction() for every candidate tutor.', options: { bullet: true } },
  ], { x: 0.5, y: 1.3, w: 5.5, h: 1.5, fontSize: 12, fontFace: 'Calibri', color: C.slate })

  // Side panel
  s.addShape(pres.shapes.RECTANGLE, { x: 6.3, y: 0.95, w: 3.3, h: 4.3, fill: { color: C.white }, line: { color: C.teal, width: 1.5 }, shadow: makeShadow() })
  s.addShape(pres.shapes.RECTANGLE, { x: 6.3, y: 0.95, w: 3.3, h: 0.4, fill: { color: C.teal }, line: { color: C.teal } })
  s.addText('Inputs & Output', { x: 6.3, y: 0.95, w: 3.3, h: 0.4, fontSize: 12, bold: true, color: C.white, align: 'center', valign: 'middle', margin: 0 })

  const ioItems = [
    ['INPUTS', null],
    ['student_profile', 'course, year_level'],
    ['student_subjects', 'from Preference model'],
    ['requested_subject', 'subject being searched'],
    ['tutor.profile', 'course, year_level'],
    ['tutorsubjects_set', 'subject + expertise_level'],
    ['OUTPUT', null],
    ['CBF Score', '0.0 – 1.0'],
  ]
  ioItems.forEach((item, i) => {
    const y = 1.45 + i * 0.46
    if (item[1] === null) {
      s.addText(item[0], { x: 6.45, y, w: 3.0, h: 0.3, fontSize: 10, bold: true, color: C.teal, margin: 0 })
    } else {
      s.addText(item[0], { x: 6.45, y, w: 1.5, h: 0.3, fontSize: 10, fontFace: 'Consolas', color: C.slate, margin: 0 })
      s.addText(item[1], { x: 7.98, y, w: 1.5, h: 0.3, fontSize: 9, fontFace: 'Calibri', color: C.slateLight, italic: true, margin: 0 })
    }
  })

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.0, w: 5.6, h: 0.65, fill: { color: C.navy }, line: { color: C.navy }, shadow: makeShadow() })
  s.addText('File: backend/studybuddy/recommender/cbf.py\nFunction: compute_cbf_score(student_profile, tutor, requested_subject)', {
    x: 0.5, y: 3.0, w: 5.6, h: 0.65, fontSize: 10, fontFace: 'Consolas', color: C.tealLight, align: 'left', valign: 'middle', margin: 6
  })

  s.addText('Mode Filtering', { x: 0.5, y: 3.82, w: 5.4, h: 0.28, fontSize: 13, bold: true, color: C.slate, margin: 0 })
  s.addText([
    { text: 'recommend_tutors() pre-filters the queryset by preferred_mode before scoring:', options: { breakLine: true } },
    { text: 'can_online=True', options: { bold: true, color: C.teal } },
    { text: ' for Online sessions  /  ', options: {} },
    { text: 'can_f2f=True', options: { bold: true, color: C.teal } },
    { text: ' for Face-to-face.', options: {} },
  ], { x: 0.5, y: 4.12, w: 5.5, h: 0.9, fontSize: 11, fontFace: 'Calibri', color: C.slate, margin: 0 })
}

// ============================================================
// SLIDE 4: CBF WEIGHTS
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.offWhite }

  s.addText('CBF: The 5 Scoring Factors & Weights', {
    x: 0.5, y: 0.22, w: 9, h: 0.55, fontSize: 28, fontFace: 'Calibri', bold: true, color: C.slate, align: 'left', margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.79, w: 9, h: 0.04, fill: { color: C.teal }, line: { color: C.teal } })

  const factors = [
    { name: 'Subject Match', var: 's_subject', weight: '35%', const: 'W_SUBJECT = 0.35', logic: '1.0 if tutor teaches any of the student\'s requested/preference subjects, else 0.0', color: C.teal, col: 0, row: 0 },
    { name: 'Expertise Level', var: 's_expertise', weight: '20%', const: 'W_EXPERTISE = 0.20', logic: 'Average expertise_level (1–5) of matching subjects, divided by 5 to normalize to 0–1', color: C.blue, col: 0, row: 1 },
    { name: 'Course Match', var: 's_course', weight: '20%', const: 'W_COURSE = 0.20', logic: '1.0 = same course  |  0.5 = same strand  |  0.0 = different', color: C.green, col: 0, row: 2 },
    { name: 'Year Proximity', var: 's_year', weight: '15%', const: 'W_YEAR = 0.15', logic: '1 ÷ (1 + |student_year_level − tutor_year_level|)', color: C.amber, col: 1, row: 0 },
    { name: 'Teaching Level', var: 's_level', weight: '10%', const: 'W_LEVEL = 0.10', logic: '0.0 if tutor is SHS-only and student year_level > 12, otherwise 1.0', color: C.purple, col: 1, row: 1 },
  ]

  factors.forEach(f => {
    const x = f.col === 0 ? 0.3 : 5.2
    const y = 1.0 + f.row * 1.27
    const w = 4.6

    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h: 1.1, fill: { color: C.white }, line: { color: f.color, width: 1.5 }, shadow: makeShadow() })
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.08, h: 1.1, fill: { color: f.color }, line: { color: f.color } })
    s.addShape(pres.shapes.RECTANGLE, { x: x + w - 0.82, y: y + 0.09, w: 0.68, h: 0.28, fill: { color: f.color }, line: { color: f.color } })
    s.addText(f.weight, { x: x + w - 0.82, y: y + 0.09, w: 0.68, h: 0.28, fontSize: 12, bold: true, color: C.white, align: 'center', valign: 'middle', margin: 0 })
    s.addText(f.name, { x: x + 0.18, y: y + 0.04, w: 3.0, h: 0.3, fontSize: 13, fontFace: 'Calibri', bold: true, color: C.slate, margin: 0 })
    s.addText(f.var + '  ·  ' + f.const, { x: x + 0.18, y: y + 0.33, w: 3.9, h: 0.22, fontSize: 9, fontFace: 'Consolas', color: C.slateLight, margin: 0 })
    s.addText(f.logic, { x: x + 0.18, y: y + 0.55, w: 3.9, h: 0.5, fontSize: 10, fontFace: 'Calibri', color: C.slate, margin: 0 })
  })

  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 4.82, w: 9.4, h: 0.5, fill: { color: C.navy }, line: { color: C.navy } })
  s.addText('score = 0.35·s_subject + 0.20·s_expertise + 0.20·s_course + 0.15·s_year + 0.10·s_level', {
    x: 0.3, y: 4.82, w: 9.4, h: 0.5, fontSize: 13, fontFace: 'Consolas', bold: true, color: C.tealLight, align: 'center', valign: 'middle', margin: 0
  })
}

// ============================================================
// SLIDE 5: CBF WORKED EXAMPLE
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.offWhite }

  s.addText('CBF: Worked Example', {
    x: 0.5, y: 0.18, w: 9, h: 0.5, fontSize: 28, fontFace: 'Calibri', bold: true, color: C.slate, align: 'left', margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.7, w: 9, h: 0.04, fill: { color: C.teal }, line: { color: C.teal } })

  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 0.8, w: 9.4, h: 0.95, fill: { color: C.navy }, line: { color: C.navy }, shadow: makeShadow() })
  s.addText([
    { text: 'Student: ', options: { bold: true, color: C.amber } },
    { text: 'Ana Reyes  ·  BS Computer Science  ·  Year 2  ·  Subjects: CS101, MATH101', options: { color: C.white } },
    { text: '\n', options: {} },
    { text: 'Tutor: ', options: { bold: true, color: C.tealLight } },
    { text: 'Marco Cruz  ·  BS Computer Science  ·  Year 4  ·  Teaches: CS101 (expertise 4/5) + MATH101 (expertise 3/5)  ·  Level: College', options: { color: C.white } },
  ], { x: 0.5, y: 0.84, w: 9, h: 0.87, fontSize: 11, fontFace: 'Calibri', margin: 0 })

  // Column headers
  const headers = ['Factor', 'Calculation', 'Raw Value', 'Weight', 'Contribution']
  const colX = [0.3, 1.6, 7.0, 7.8, 8.65]
  const colW = [1.2, 5.3, 0.75, 0.75, 0.95]
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.84, w: 9.4, h: 0.38, fill: { color: C.slate }, line: { color: C.slate } })
  headers.forEach((h, i) => {
    s.addText(h, { x: colX[i], y: 1.84, w: colW[i], h: 0.38, fontSize: 10, bold: true, color: C.white, align: i > 1 ? 'center' : 'left', valign: 'middle', margin: 4 })
  })

  const rows = [
    { factor: 's_subject', calc: 'Tutor teaches CS101 + MATH101 → matching_expertise = [4, 3] → not empty', raw: '1.0', weight: '×0.35', contrib: '0.350', color: C.teal },
    { factor: 's_expertise', calc: 'avg([4, 3]) = 3.5  →  3.5 ÷ 5 = 0.700', raw: '0.700', weight: '×0.20', contrib: '0.140', color: C.blue },
    { factor: 's_course', calc: 'student.course == tutor.course (both BS CompSci) → same course', raw: '1.0', weight: '×0.20', contrib: '0.200', color: C.green },
    { factor: 's_year', calc: '|year 2 − year 4| = 2  →  1 ÷ (1 + 2) = 0.333', raw: '0.333', weight: '×0.15', contrib: '0.050', color: C.amber },
    { factor: 's_level', calc: 'tutor.teaching_level = "College", student year 2 — SHS check skipped → 1.0', raw: '1.0', weight: '×0.10', contrib: '0.100', color: C.purple },
  ]
  rows.forEach((r, i) => {
    const y = 2.22 + i * 0.52
    const bg = i % 2 === 0 ? C.white : 'F1F5F9'
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y, w: 0.08, h: 0.48, fill: { color: r.color }, line: { color: r.color } })
    s.addShape(pres.shapes.RECTANGLE, { x: 0.38, y, w: 9.32, h: 0.48, fill: { color: bg }, line: { color: C.slateXLight, width: 0.5 } })
    s.addText(r.factor, { x: 0.45, y: y + 0.09, w: 1.1, h: 0.3, fontSize: 10, fontFace: 'Consolas', bold: true, color: r.color, margin: 0 })
    s.addText(r.calc, { x: 1.62, y: y + 0.09, w: 5.3, h: 0.3, fontSize: 10, fontFace: 'Calibri', color: C.slate, margin: 0 })
    s.addText(r.raw, { x: 7.02, y: y + 0.09, w: 0.72, h: 0.3, fontSize: 10, fontFace: 'Consolas', bold: true, color: C.slate, align: 'center', margin: 0 })
    s.addText(r.weight, { x: 7.8, y: y + 0.09, w: 0.72, h: 0.3, fontSize: 10, fontFace: 'Consolas', color: C.slateLight, align: 'center', margin: 0 })
    s.addText(r.contrib, { x: 8.65, y: y + 0.09, w: 0.95, h: 0.3, fontSize: 10, fontFace: 'Consolas', bold: true, color: C.teal, align: 'right', margin: 0 })
  })

  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 4.86, w: 9.4, h: 0.45, fill: { color: C.teal }, line: { color: C.teal } })
  s.addText('CBF Score  =  0.350 + 0.140 + 0.200 + 0.050 + 0.100  =  0.840  (out of 1.0)', {
    x: 0.3, y: 4.86, w: 9.4, h: 0.45, fontSize: 14, fontFace: 'Consolas', bold: true, color: C.white, align: 'center', valign: 'middle', margin: 0
  })
}

// ============================================================
// SLIDE 6: CF OVERVIEW
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.offWhite }

  s.addText('Collaborative Filtering (CF)', {
    x: 0.5, y: 0.22, w: 9, h: 0.55, fontSize: 28, fontFace: 'Calibri', bold: true, color: C.slate, align: 'left', margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.79, w: 9, h: 0.04, fill: { color: C.blue }, line: { color: C.blue } })

  const steps = [
    { n: '1', title: 'Build Rating Matrix', body: 'Load all Rating records from the DB.\nRows = students, columns = tutors,\ncells = rating_score (integer 1–5).', color: C.blue },
    { n: '2', title: 'Pearson Similarity', body: 'For each pair of students compute\nPearson correlation over their set\nof commonly-rated tutors (top-k=5).', color: C.tealLight },
    { n: '3', title: 'Predict Rating', body: 'Weighted sum of neighbor deviations\nfrom their own mean, added to the\ncurrent student\'s mean rating.', color: C.green },
  ]
  steps.forEach((st, i) => {
    const x = 0.35 + i * 3.1
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.0, w: 2.95, h: 2.7, fill: { color: C.white }, line: { color: st.color, width: 2 }, shadow: makeShadow() })
    s.addShape(pres.shapes.OVAL, { x: x + 1.12, y: 1.0, w: 0.7, h: 0.7, fill: { color: st.color }, line: { color: st.color } })
    s.addText(st.n, { x: x + 1.12, y: 1.0, w: 0.7, h: 0.7, fontSize: 20, bold: true, color: C.white, align: 'center', valign: 'middle', margin: 0 })
    s.addText(st.title, { x: x + 0.1, y: 1.82, w: 2.75, h: 0.38, fontSize: 13, bold: true, color: C.slate, align: 'center', margin: 0 })
    s.addText(st.body, { x: x + 0.15, y: 2.25, w: 2.65, h: 1.35, fontSize: 11, fontFace: 'Calibri', color: C.slateLight, align: 'left', margin: 0 })
    if (i < 2) {
      s.addText('→', { x: x + 2.95, y: 2.0, w: 0.15, h: 0.45, fontSize: 22, color: C.slateLight, align: 'center', margin: 0 })
    }
  })

  s.addText('Key Design Notes', { x: 0.5, y: 3.85, w: 5, h: 0.3, fontSize: 13, bold: true, color: C.slate, margin: 0 })
  s.addText([
    { text: 'Already-rated tutors are skipped — CF only predicts tutors the student has NOT yet rated.', options: { bullet: true, breakLine: true } },
    { text: 'New student (no ratings yet) → CF returns None → treated as 0 in the hybrid formula (graceful cold-start).', options: { bullet: true, breakLine: true } },
    { text: 'k = 5 neighbors by default. CF score is on the 1–5 star scale (normalized before blending).', options: { bullet: true } },
  ], { x: 0.5, y: 4.18, w: 9, h: 1.0, fontSize: 12, fontFace: 'Calibri', color: C.slate })

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.38, w: 10, h: 0.24, fill: { color: C.blue }, line: { color: C.blue } })
  s.addText('File: backend/studybuddy/recommender/CF.py', {
    x: 0, y: 5.38, w: 10, h: 0.24, fontSize: 10, fontFace: 'Consolas', color: C.white, align: 'center', valign: 'middle', margin: 0
  })
}

// ============================================================
// SLIDE 7: PEARSON SIMILARITY
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.offWhite }

  s.addText('CF: Pearson Similarity Formula', {
    x: 0.5, y: 0.22, w: 9, h: 0.55, fontSize: 28, fontFace: 'Calibri', bold: true, color: C.slate, align: 'left', margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.79, w: 9, h: 0.04, fill: { color: C.blue }, line: { color: C.blue } })

  s.addShape(pres.shapes.RECTANGLE, { x: 1.0, y: 1.0, w: 8.0, h: 1.35, fill: { color: C.navy }, line: { color: C.navy }, shadow: makeShadow() })
  s.addText([
    { text: 'sim(u, v)', options: { bold: true, color: C.amber } },
    { text: '  =  ', options: { color: C.white } },
    { text: 'Σᵢ∈I (rᵤᵢ − r̄ᵤ)(rᵥᵢ − r̄ᵥ)', options: { color: C.white } },
  ], { x: 1.0, y: 1.0, w: 8, h: 0.58, fontSize: 16, fontFace: 'Consolas', align: 'center', valign: 'bottom', margin: 0 })
  s.addShape(pres.shapes.LINE, { x: 3.5, y: 1.58, w: 3.0, h: 0, line: { color: 'AAAAAA', width: 1 } })
  s.addText('sqrt( Σᵢ (rᵤᵢ − r̄ᵤ)² )  ×  sqrt( Σᵢ (rᵥᵢ − r̄ᵥ)² )', {
    x: 1.0, y: 1.6, w: 8, h: 0.62, fontSize: 13, fontFace: 'Consolas', color: 'A0B4CC', align: 'center', valign: 'top', margin: 0
  })

  const legend = [
    ['u, v', 'Two students being compared for similarity'],
    ['I', 'Set of tutors rated by BOTH u and v  (common items only)'],
    ['rᵤᵢ', "Student u's rating for tutor i  (integer 1–5)"],
    ['r̄ᵤ', "Student u's mean rating, computed over common items only"],
    ['Result', 'Range −1.0 to +1.0.  Positive = similar taste.  0 = no correlation.  −1 = opposite.'],
  ]
  legend.forEach((row, i) => {
    const y = 2.52 + i * 0.56
    s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y, w: 9.2, h: 0.5, fill: { color: i % 2 === 0 ? C.white : 'F1F5F9' }, line: { color: C.slateXLight, width: 0.5 } })
    s.addText(row[0], { x: 0.55, y: y + 0.1, w: 1.3, h: 0.3, fontSize: 13, fontFace: 'Consolas', bold: true, color: C.blue, margin: 0 })
    s.addText(row[1], { x: 1.95, y: y + 0.1, w: 7.5, h: 0.3, fontSize: 12, fontFace: 'Calibri', color: C.slate, valign: 'middle', margin: 0 })
  })
}

// ============================================================
// SLIDE 8: CF PREDICT RATING
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.offWhite }

  s.addText('CF: Predicting a Rating', {
    x: 0.5, y: 0.22, w: 9, h: 0.55, fontSize: 28, fontFace: 'Calibri', bold: true, color: C.slate, align: 'left', margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.79, w: 9, h: 0.04, fill: { color: C.blue }, line: { color: C.blue } })

  s.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 0.95, w: 8.4, h: 0.9, fill: { color: C.navy }, line: { color: C.navy }, shadow: makeShadow() })
  s.addText([
    { text: 'pred(u, i)', options: { bold: true, color: C.amber } },
    { text: '  =  r̄ᵤ  +  ', options: { color: C.white } },
    { text: 'Σₙ sim(u,n)×(rₙᵢ − r̄ₙ)', options: { bold: true, color: C.tealLight } },
    { text: '  ÷  ', options: { color: C.white } },
    { text: 'Σₙ |sim(u,n)|', options: { bold: true, color: C.green } },
  ], { x: 0.8, y: 0.95, w: 8.4, h: 0.9, fontSize: 16, fontFace: 'Consolas', align: 'center', valign: 'middle', margin: 0 })

  const steps = [
    { n: '1', title: "Compute student's mean  (r̄ᵤ)", body: 'Mean of all ratings the current student has already given. This is the baseline — adjustments are relative to it.', color: C.blue },
    { n: '2', title: 'Find top-5 neighbors', body: 'Sort all other students by Pearson similarity; take top k=5. These neighbors influence the prediction.', color: C.teal },
    { n: '3', title: 'Aggregate weighted deviations', body: 'For each neighbor who has rated tutor i: add sim(u,n) × (rₙᵢ − r̄ₙ) to numerator, |sim(u,n)| to denominator.', color: C.green },
    { n: '4', title: 'Normalize & shift', body: 'Divide weighted deviations by total abs-similarity, then add to r̄ᵤ. Result is on the 1–5 star scale.', color: C.amber },
    { n: '5', title: 'No data → None (returns 0)', body: 'If denominator = 0 (no neighbor rated tutor i) → compute_cf_score returns None → hybrid treats it as 0.', color: C.purple },
  ]
  steps.forEach((st, i) => {
    const y = 2.05 + i * 0.7
    s.addShape(pres.shapes.OVAL, { x: 0.35, y: y + 0.08, w: 0.42, h: 0.42, fill: { color: st.color }, line: { color: st.color } })
    s.addText(st.n, { x: 0.35, y: y + 0.08, w: 0.42, h: 0.42, fontSize: 14, bold: true, color: C.white, align: 'center', valign: 'middle', margin: 0 })
    s.addText(st.title, { x: 0.9, y: y + 0.02, w: 3.8, h: 0.3, fontSize: 12, fontFace: 'Calibri', bold: true, color: C.slate, margin: 0 })
    s.addText(st.body, { x: 0.9, y: y + 0.32, w: 8.7, h: 0.35, fontSize: 11, fontFace: 'Calibri', color: C.slateLight, margin: 0 })
  })
}

// ============================================================
// SLIDE 9: CF WORKED EXAMPLE
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.offWhite }

  s.addText('CF: Worked Example', {
    x: 0.5, y: 0.18, w: 9, h: 0.5, fontSize: 28, fontFace: 'Calibri', bold: true, color: C.slate, align: 'left', margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.7, w: 9, h: 0.04, fill: { color: C.blue }, line: { color: C.blue } })

  s.addText('Goal: predict Ana\'s rating for Tutor C (she hasn\'t rated them yet)', {
    x: 0.4, y: 0.82, w: 9, h: 0.28, fontSize: 12, bold: true, color: C.blue, margin: 0
  })

  // Rating matrix table
  const tableData = [
    [
      { text: 'Student', options: { bold: true, fill: { color: C.navy }, color: C.white } },
      { text: 'Tutor A', options: { bold: true, fill: { color: C.navy }, color: C.white } },
      { text: 'Tutor B', options: { bold: true, fill: { color: C.navy }, color: C.white } },
      { text: 'Tutor C', options: { bold: true, fill: { color: C.navy }, color: C.white } },
      { text: 'Tutor D', options: { bold: true, fill: { color: C.navy }, color: C.white } },
    ],
    ['Ana (target)', '5', '3', ' — ', '4'],
    ['Ben (neighbor 1)', '4', '3', '5', ' — '],
    ['Cara (neighbor 2)', '5', '2', '4', '3'],
  ]
  s.addTable(tableData, {
    x: 0.4, y: 1.13, w: 6.0, h: 1.2,
    border: { pt: 1, color: C.slateXLight },
    colW: [1.6, 1.1, 1.1, 1.1, 1.1],
    fontSize: 11, fontFace: 'Calibri', align: 'center',
  })

  // Steps
  const calcs = [
    { label: 'Ana\'s mean', text: 'Rated tutors: A=5, B=3, D=4  →  r̄_Ana = (5+3+4)/3 = 4.00' },
    { label: 'sim(Ana, Ben)', text: 'Common items: {A, B}.  r̄_Ana_AB = 4.0,  r̄_Ben_AB = 3.5\n  numerator = (5−4.0)(4−3.5) + (3−4.0)(3−3.5) = 0.5+0.5 = 1.0\n  denom = √(1²+1²) × √(0.5²+0.5²) = 1.414 × 0.707 = 1.00  →  sim = 1.00' },
    { label: 'sim(Ana, Cara)', text: 'Common items: {A, B}.  r̄_Ana_AB = 4.0,  r̄_Cara_AB = 3.5\n  numerator = (5−4.0)(5−3.5) + (3−4.0)(2−3.5) = 1.5+1.5 = 3.0\n  denom = √(1²+1²) × √(1.5²+1.5²) = 1.414 × 2.121 = 3.0  →  sim = 1.00' },
    { label: 'pred(Ana, C)', text: 'Ben rated C=5 (r̄_Ben=4.0),  Cara rated C=4 (r̄_Cara=3.5)\n  = 4.00 + [1.00×(5−4.0) + 1.00×(4−3.5)] / [1.00+1.00]\n  = 4.00 + (1.0 + 0.5)/2.0  =  4.00 + 0.75  =  4.75' },
  ]
  calcs.forEach((c, i) => {
    const y = 2.44 + i * 0.71
    s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y, w: 0.08, h: 0.62, fill: { color: C.blue }, line: { color: C.blue } })
    s.addText(c.label, { x: 0.58, y: y + 0.02, w: 1.4, h: 0.28, fontSize: 10, fontFace: 'Consolas', bold: true, color: C.blue, margin: 0 })
    s.addText(c.text, { x: 0.58, y: y + 0.28, w: 9.05, h: 0.4, fontSize: 9.5, fontFace: 'Calibri', color: C.slate, margin: 0 })
  })

  s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y: 5.17, w: 9.2, h: 0.38, fill: { color: C.blue }, line: { color: C.blue } })
  s.addText('CF predicts Ana would rate Tutor C  ≈  4.75 / 5.0  (on the 1–5 star scale)', {
    x: 0.4, y: 5.17, w: 9.2, h: 0.38, fontSize: 13, fontFace: 'Calibri', bold: true, color: C.white, align: 'center', valign: 'middle', margin: 0
  })
}

// ============================================================
// SLIDE 10: HYBRID FORMULA (dark slide)
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.navyDark }

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.08, fill: { color: C.amber }, line: { color: C.amber } })

  s.addText('The Hybrid Formula', {
    x: 0.6, y: 0.28, w: 8.8, h: 0.65, fontSize: 34, fontFace: 'Calibri', bold: true, color: C.white, margin: 0
  })

  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.1, w: 8.8, h: 1.05, fill: { color: '1A3050' }, line: { color: C.amber, width: 2 }, shadow: makeShadow() })
  s.addText([
    { text: 'hybrid_score', options: { bold: true, color: C.amber } },
    { text: '  =  ', options: { color: C.white } },
    { text: '0.7', options: { bold: true, color: C.tealLight } },
    { text: ' × cbf_score', options: { color: C.white } },
    { text: '  +  ', options: { color: C.white } },
    { text: '0.3', options: { bold: true, color: C.green } },
    { text: ' × (cf_score ÷ 5)', options: { color: C.white } },
  ], { x: 0.6, y: 1.1, w: 8.8, h: 1.05, fontSize: 22, fontFace: 'Consolas', align: 'center', valign: 'middle', margin: 0 })

  const parts = [
    { title: 'CBF Component  (weight: 70%)', code: '0.7 × cbf_score', body: 'cbf_score is already 0–1 (normalized).\nDominates ranking to ensure subject fit and\nprofile match come first.', color: C.tealLight, x: 0.5 },
    { title: 'CF Component  (weight: 30%)', code: '0.3 × (cf_score ÷ 5)', body: 'cf_score is on the 1–5 star scale.\nDivide by 5 → normalize to 0–1 before blending.\nIf no ratings exist, cf_score → 0 (graceful).', color: C.green, x: 5.2 },
  ]
  parts.forEach(p => {
    s.addShape(pres.shapes.RECTANGLE, { x: p.x, y: 2.4, w: 4.4, h: 2.45, fill: { color: '1A3050' }, line: { color: p.color, width: 1.5 }, shadow: makeShadow() })
    s.addShape(pres.shapes.RECTANGLE, { x: p.x, y: 2.4, w: 4.4, h: 0.38, fill: { color: p.color }, line: { color: p.color } })
    s.addText(p.title, { x: p.x, y: 2.4, w: 4.4, h: 0.38, fontSize: 12, bold: true, color: C.navyDark, align: 'center', valign: 'middle', margin: 0 })
    s.addText(p.code, { x: p.x + 0.15, y: 2.88, w: 4.1, h: 0.35, fontSize: 12, fontFace: 'Consolas', color: p.color, margin: 0 })
    s.addText(p.body, { x: p.x + 0.15, y: 3.28, w: 4.1, h: 1.42, fontSize: 12, fontFace: 'Calibri', color: 'A0B4CC', margin: 0 })
  })

  s.addText('File: backend/studybuddy/recommender/hybrid.py  ·  Function: hybrid_prediction()', {
    x: 0.6, y: 5.22, w: 8.8, h: 0.25, fontSize: 10, fontFace: 'Consolas', color: '506070', align: 'center', margin: 0
  })
}

// ============================================================
// SLIDE 11: HYBRID WORKED EXAMPLE
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.offWhite }

  s.addText('Hybrid: Worked Example', {
    x: 0.5, y: 0.18, w: 9, h: 0.5, fontSize: 28, fontFace: 'Calibri', bold: true, color: C.slate, align: 'left', margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.7, w: 9, h: 0.04, fill: { color: C.amber }, line: { color: C.amber } })
  s.addText('Same scenario: Ana Reyes searching for a tutor for CS101', {
    x: 0.5, y: 0.82, w: 9, h: 0.28, fontSize: 12, fontFace: 'Calibri', italic: true, color: C.slateLight, margin: 0
  })

  const blocks = [
    { label: 'CBF Score', formula: 'compute_cbf_score(Ana, Tutor C, "CS101")  =  0.840', result: '0.840', color: C.teal },
    { label: 'CF Score', formula: 'compute_cf_score(ratings, Ana.id, TutorC.profile_id)  =  4.75  (1–5 scale)', result: '4.75', color: C.blue },
    { label: 'CF Normalized', formula: 'cf_score ÷ 5  =  4.75 ÷ 5  =  0.950', result: '0.950', color: C.blue },
    { label: 'Hybrid Score', formula: '0.7 × 0.840  +  0.3 × 0.950  =  0.588 + 0.285  =  0.873', result: '0.873', color: C.amber },
  ]
  blocks.forEach((b, i) => {
    const y = 1.22 + i * 0.9
    s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y, w: 9.2, h: 0.75, fill: { color: C.white }, line: { color: b.color, width: 1.5 }, shadow: makeShadow() })
    s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y, w: 1.75, h: 0.75, fill: { color: b.color }, line: { color: b.color } })
    s.addText(b.label, { x: 0.4, y, w: 1.75, h: 0.75, fontSize: 11, bold: true, color: C.white, align: 'center', valign: 'middle', margin: 0 })
    s.addText(b.formula, { x: 2.28, y: y + 0.18, w: 5.8, h: 0.42, fontSize: 12, fontFace: 'Consolas', color: C.slate, valign: 'middle', margin: 0 })
    s.addShape(pres.shapes.RECTANGLE, { x: 8.15, y: y + 0.12, w: 1.3, h: 0.5, fill: { color: b.color, transparency: 85 }, line: { color: b.color, width: 1 } })
    s.addText(b.result, { x: 8.15, y: y + 0.12, w: 1.3, h: 0.5, fontSize: 17, fontFace: 'Consolas', bold: true, color: b.color, align: 'center', valign: 'middle', margin: 0 })
  })

  s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y: 4.85, w: 9.2, h: 0.45, fill: { color: C.amber }, line: { color: C.amber } })
  s.addText('Tutor C earns a hybrid score of 0.873 out of 1.0 — highly ranked for Ana.', {
    x: 0.4, y: 4.85, w: 9.2, h: 0.45, fontSize: 14, fontFace: 'Calibri', bold: true, color: C.navyDark, align: 'center', valign: 'middle', margin: 0
  })
}

// ============================================================
// SLIDE 12: WHERE IT'S APPLIED
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.offWhite }

  s.addText('Where the Algorithm Is Applied', {
    x: 0.5, y: 0.22, w: 9, h: 0.55, fontSize: 28, fontFace: 'Calibri', bold: true, color: C.slate, align: 'left', margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.79, w: 9, h: 0.04, fill: { color: C.slateLight }, line: { color: C.slateLight } })

  const contexts = [
    {
      n: '1', label: 'Dashboard Recommendations', endpoint: 'GET /api/student-dashboard/',
      flow: [
        'Student opens tutee dashboard',
        'get_dashboard_recommendations(tutee) is called',
        'Cache hit? → return top 5 immediately',
        'Cache miss → build rating matrix, run hybrid on candidate tutors',
        'No subject preferences? → fallback (unranked list)',
        'Cache result for 10 min, return top 5',
      ],
      note: 'subject=None; hybrid scores tutors matching student Preference subjects. 10 min TTL cache.',
      color: C.teal, x: 0.35,
    },
    {
      n: '2', label: 'FindTutors Search', endpoint: 'POST /api/recommend-tutors/',
      flow: [
        'Student submits search (subject, mode, budget, date/time)',
        'get_recommendation_candidate_tutors() pre-filters queryset',
        'build_rating_matrix() loads all existing ratings',
        'recommend_tutors_hybrid(ratings, student, subject, candidate_qs)',
        'Returns top 10 scored tutors',
      ],
      note: 'Subject is required. Candidate set filtered BEFORE scoring to minimize computation.',
      color: C.blue, x: 5.1,
    },
  ]
  contexts.forEach(ctx => {
    s.addShape(pres.shapes.RECTANGLE, { x: ctx.x, y: 1.0, w: 4.55, h: 4.35, fill: { color: C.white }, line: { color: ctx.color, width: 2 }, shadow: makeShadow() })
    s.addShape(pres.shapes.RECTANGLE, { x: ctx.x, y: 1.0, w: 4.55, h: 0.42, fill: { color: ctx.color }, line: { color: ctx.color } })
    s.addText(`${ctx.n}.  ${ctx.label}`, { x: ctx.x + 0.1, y: 1.0, w: 4.35, h: 0.42, fontSize: 13, bold: true, color: C.white, valign: 'middle', margin: 0 })
    s.addText(ctx.endpoint, { x: ctx.x + 0.12, y: 1.5, w: 4.3, h: 0.28, fontSize: 10, fontFace: 'Consolas', color: ctx.color, margin: 0 })
    ctx.flow.forEach((step, i) => {
      const fy = 1.82 + i * 0.44
      s.addShape(pres.shapes.OVAL, { x: ctx.x + 0.12, y: fy + 0.08, w: 0.22, h: 0.22, fill: { color: ctx.color }, line: { color: ctx.color } })
      s.addText(step, { x: ctx.x + 0.42, y: fy + 0.02, w: 4.0, h: 0.4, fontSize: 10, fontFace: 'Calibri', color: C.slate, valign: 'middle', margin: 0 })
    })
    s.addShape(pres.shapes.RECTANGLE, { x: ctx.x + 0.12, y: 4.18, w: 4.3, h: 0.68, fill: { color: ctx.color, transparency: 88 }, line: { color: ctx.color, width: 0.5 } })
    s.addText(ctx.note, { x: ctx.x + 0.2, y: 4.22, w: 4.14, h: 0.64, fontSize: 9.5, fontFace: 'Calibri', italic: true, color: C.slate, margin: 0 })
  })
}

// ============================================================
// SLIDE 13: DASHBOARD CACHING
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.offWhite }

  s.addText('Dashboard: Caching & Fallback Strategy', {
    x: 0.5, y: 0.22, w: 9, h: 0.55, fontSize: 28, fontFace: 'Calibri', bold: true, color: C.slate, align: 'left', margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.79, w: 9, h: 0.04, fill: { color: C.teal }, line: { color: C.teal } })

  // Main flow: 7 steps center-column
  const flow = [
    { label: 'Request: get_dashboard_recommendations(tutee)', bg: C.navy, fg: C.white },
    { label: 'Cache HIT?\ndash_recs:v{N}:limit5:{tutee_id}', bg: C.teal, fg: C.white },
    { label: 'Has subject preferences set\n(Preference model)?', bg: C.amber, fg: C.navyDark },
    { label: 'Filter candidate tutors by\nstudent\'s subject codes', bg: C.slateXLight, fg: C.slate },
    { label: 'recommend_tutors_hybrid() → score + rank', bg: C.slateXLight, fg: C.slate },
    { label: 'Cache result  TTL = 600 s  (10 minutes)', bg: C.green, fg: C.white },
    { label: 'Return top 5 to dashboard', bg: C.navy, fg: C.white },
  ]
  flow.forEach((f, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x: 3.0, y: 0.98 + i * 0.64, w: 4.0, h: 0.52, fill: { color: f.bg }, line: { color: f.bg } })
    s.addText(f.label, { x: 3.0, y: 0.98 + i * 0.64, w: 4.0, h: 0.52, fontSize: 10, fontFace: 'Calibri', color: f.fg, align: 'center', valign: 'middle', margin: 4 })
    if (i < flow.length - 1) {
      s.addText('↓', { x: 4.82, y: 1.5 + i * 0.64, w: 0.36, h: 0.16, fontSize: 12, color: C.slateLight, align: 'center', margin: 0 })
    }
  })

  // Side annotation: cache hit
  s.addShape(pres.shapes.RECTANGLE, { x: 0.25, y: 1.38, w: 2.4, h: 0.5, fill: { color: C.teal, transparency: 88 }, line: { color: C.teal, width: 1 } })
  s.addText('YES → return cached immediately', { x: 0.25, y: 1.38, w: 2.4, h: 0.5, fontSize: 9, fontFace: 'Calibri', color: C.teal, align: 'center', valign: 'middle', margin: 4 })

  // Side annotation: no preferences fallback
  s.addShape(pres.shapes.RECTANGLE, { x: 7.35, y: 2.0, w: 2.3, h: 0.5, fill: { color: C.amber, transparency: 88 }, line: { color: C.amber, width: 1 } })
  s.addText('NO → fallback: return top tutors unranked', { x: 7.35, y: 2.0, w: 2.3, h: 0.5, fontSize: 9, fontFace: 'Calibri', color: C.amber, align: 'center', valign: 'middle', margin: 4 })

  s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y: 5.06, w: 9.2, h: 0.38, fill: { color: C.navy }, line: { color: C.navy } })
  s.addText('Cache key: "dash_recs:v{version}:limit5:{tutee_id}"  ·  bump_dashboard_recs_cache_version() on data changes  ·  File: recommender/dashboard.py', {
    x: 0.4, y: 5.06, w: 9.2, h: 0.38, fontSize: 9, fontFace: 'Consolas', color: C.tealLight, align: 'center', valign: 'middle', margin: 0
  })
}

// ============================================================
// SLIDE 14: KEY TAKEAWAYS (dark)
// ============================================================
{
  const s = pres.addSlide()
  s.background = { color: C.navyDark }

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.08, fill: { color: C.amber }, line: { color: C.amber } })
  s.addText('Key Takeaways', {
    x: 0.6, y: 0.22, w: 8.8, h: 0.65, fontSize: 34, fontFace: 'Calibri', bold: true, color: C.white, margin: 0
  })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 0.9, w: 2.8, h: 0.05, fill: { color: C.amber }, line: { color: C.amber } })

  const cards = [
    { stat: '70/30', label: 'Weight split', body: 'CBF dominates at 70% — profile fit matters more than peer history. CF adds personalization at 30% when ratings exist.', color: C.teal, col: 0, row: 0 },
    { stat: '5', label: 'CBF factors', body: 'Subject match (35%), expertise (20%), course (20%), year proximity (15%), teaching level (10%). Max = 1.0.', color: C.blue, col: 0, row: 1 },
    { stat: '5 ★', label: 'CF scale', body: 'CF predicts on the 1–5 star scale, then divides by 5 before blending. Cold-start → CF=0 (safe default).', color: C.green, col: 0, row: 2 },
    { stat: '10 min', label: 'Dashboard cache', body: 'Recommendations cached for 600 s per tutee. Version key enables instant invalidation when tutor data changes.', color: C.amber, col: 1, row: 0 },
    { stat: 'Top 10', label: 'Output size', body: 'FindTutors returns top 10. Dashboard returns top 5. Candidate pre-filtering reduces tutor set before scoring.', color: C.purple, col: 1, row: 1 },
  ]
  cards.forEach(c => {
    const x = c.col === 0 ? 0.5 : 5.3
    const y = 1.12 + c.row * 1.38
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.5, h: 1.15, fill: { color: '142236' }, line: { color: c.color, width: 1 }, shadow: makeShadow() })
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 1.1, h: 1.15, fill: { color: c.color }, line: { color: c.color } })
    s.addText(c.stat, { x, y, w: 1.1, h: 1.15, fontSize: 17, bold: true, color: C.white, align: 'center', valign: 'middle', margin: 0 })
    s.addText(c.label, { x: x + 1.2, y: y + 0.06, w: 3.1, h: 0.32, fontSize: 13, fontFace: 'Calibri', bold: true, color: c.color, margin: 0 })
    s.addText(c.body, { x: x + 1.2, y: y + 0.38, w: 3.2, h: 0.72, fontSize: 10, fontFace: 'Calibri', color: 'A0B4CC', margin: 0 })
  })

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.38, w: 10, h: 0.24, fill: { color: C.teal }, line: { color: C.teal } })
  s.addText('StudyBuddy  —  Central Philippine University  ·  backend/studybuddy/recommender/', {
    x: 0, y: 5.38, w: 10, h: 0.24, fontSize: 10, fontFace: 'Calibri', color: C.white, align: 'center', valign: 'middle', margin: 0
  })
}

pres.writeFile({ fileName: 'StudyBuddy_Algorithm_Explainer.pptx' })
  .then(() => console.log('Done: StudyBuddy_Algorithm_Explainer.pptx'))
  .catch(err => { console.error(err); process.exit(1) })
