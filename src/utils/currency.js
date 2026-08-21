// Shared money and count formatting for admin/report surfaces.
//
// Replaces four copy-pasted `formatMoney`/`formatCompact` helpers that had drifted apart. Two
// problems they shared, both fixed here:
//
// 1. `notation: 'compact'` was applied to *currency*, so a revenue card read "PHP 1.2K" while the
//    table right below it read "PHP 1,234.56" for the same figure -- and up to PHP 999 of
//    precision was hidden with no way to see the real number. Reports are read to reconcile
//    against actual money, so every peso figure is now shown in full.
// 2. They passed `undefined` as the locale, making output depend on the viewer's browser locale
//    ("1,2 Mio." in de-DE). The locale is pinned to en-PH, matching the only two formatters in
//    the app that were already doing it correctly (TutorDetails.vue, BudgetRangeSlider.vue).

const PHP_FORMATTER = new Intl.NumberFormat('en-PH', {
  style: 'currency',
  currency: 'PHP',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const COUNT_FORMATTER = new Intl.NumberFormat('en-PH', {
  maximumFractionDigits: 0,
})

const toNumber = (value) => {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

// "₱1,234,567.89". Never abbreviated -- see note 1 above.
export const formatPhp = (value) => PHP_FORMATTER.format(toNumber(value))

// Whole counts with thousands separators: "1,284".
export const formatCount = (value) => COUNT_FORMATTER.format(toNumber(value))

// Fixed-decimal figures that are not money (ratings, percentages).
export const formatDecimal = (value, digits = 1) =>
  toNumber(value).toLocaleString('en-PH', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })
