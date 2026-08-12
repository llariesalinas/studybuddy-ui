// Static analysis of the token layer. jsdom does not apply SFC `<style>` blocks, so nothing here
// can assert a computed colour -- these are text-level invariants over the CSS instead, which is
// the only automatable gate a styling refactor has.
//
// Companion plan: docs/plans/2026-08-11-authenticated-view-styling-consistency.md

import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'
import process from 'node:process'
import { describe, expect, it } from 'vitest'

// Vitest runs with the project root as cwd; `import.meta.url` is not a `file:` URL under its
// transform, so it cannot be used to locate the repo.
const ROOT = process.cwd()
const SRC = join(ROOT, 'src')
const MAIN_CSS = join(SRC, 'assets', 'main.css')

const stripComments = (css) => css.replace(/\/\*[\s\S]*?\*\//g, '')

const walk = (dir) =>
  readdirSync(dir).flatMap((entry) => {
    const full = join(dir, entry)
    if (statSync(full).isDirectory()) return entry === 'node_modules' ? [] : walk(full)
    return [full]
  })

const vueFiles = walk(SRC).filter((file) => file.endsWith('.vue'))
const rel = (file) => relative(ROOT, file).split('\\').join('/')

const mainCss = stripComments(readFileSync(MAIN_CSS, 'utf8'))

// Pull one top-level rule's body out by exact selector, counting braces so a nested block or an
// `@media` further down the file cannot terminate it early.
const ruleBody = (css, selector) => {
  const start = css.indexOf(`${selector} {`)
  if (start === -1) throw new Error(`selector not found in main.css: ${selector}`)

  let depth = 0
  for (let i = css.indexOf('{', start); i < css.length; i += 1) {
    if (css[i] === '{') depth += 1
    if (css[i] === '}') {
      depth -= 1
      if (depth === 0) return css.slice(css.indexOf('{', start) + 1, i)
    }
  }
  throw new Error(`unterminated rule: ${selector}`)
}

const declarationsIn = (block) => {
  const found = new Map()
  for (const [, name, value] of block.matchAll(/(--sb-[\w-]+)\s*:\s*([^;]+);/g)) {
    found.set(name, value.trim())
  }
  return found
}

const rootTokens = declarationsIn(ruleBody(mainCss, ':root'))
const darkTokens = declarationsIn(ruleBody(mainCss, '[data-sb-theme="dark"]'))

describe('token layer', () => {
  it('defines the semantic status ramp', () => {
    for (const status of ['success', 'warning', 'danger', 'info']) {
      for (const slot of ['', '-fg', '-surface', '-border']) {
        expect(rootTokens.has(`--sb-${status}${slot}`), `--sb-${status}${slot}`).toBe(true)
      }
    }
  })

  // The bug this whole refactor exists to prevent: StudyBuddyDesign.md documented `--sb-aurora-bg`
  // and a Material surface ramp that live only in the never-imported admin.css, so UI written
  // against the doc reached for tokens that resolve to `unset`. Any `--sb-*` a file reads must be
  // declared somewhere -- main.css for globals, or the component itself for a private namespace.
  it('never reads an --sb-* token that is declared nowhere', () => {
    const declared = new Set(rootTokens.keys())
    for (const name of darkTokens.keys()) declared.add(name)

    const sources = [[MAIN_CSS, mainCss]]
    for (const file of vueFiles) sources.push([file, stripComments(readFileSync(file, 'utf8'))])

    for (const [, text] of sources) {
      for (const [, name] of text.matchAll(/(--sb-[\w-]+)\s*:/g)) declared.add(name)
    }

    const dangling = []
    for (const [file, text] of sources) {
      for (const [, name] of text.matchAll(/var\(\s*(--sb-[\w-]+)/g)) {
        if (!declared.has(name)) dangling.push(`${rel(file)} reads ${name}`)
      }
    }

    expect(dangling).toEqual([])
  })

  // Token shadowing broke theming outright: Dashboard.vue re-pinned --sb-primary to a literal for
  // its whole subtree. A component may alias a token, but redefining a core one to a raw colour
  // makes every descendant immune to the theme.
  it('no component redefines a core token to a literal colour', () => {
    const CORE = [
      '--sb-primary',
      '--sb-primary-hover',
      '--sb-card-bg',
      '--sb-card-border',
      '--sb-text-main',
      '--sb-green-tint',
    ]

    // path -> tokens it may still redefine, each with the reason it is tolerated.
    const ALLOWED = {
      // Dark-mode workaround kept deliberately: light mode now inherits --sb-green-tint from
      // :root, but removing this override is a dark-only change and dark mode is deferred.
      'src/components/AppSidebar.vue': ['--sb-green-tint'],
    }

    const isLiteral = (value) => /#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(/.test(value)

    const offenders = []
    for (const file of vueFiles) {
      const declared = declarationsIn(stripComments(readFileSync(file, 'utf8')))
      for (const token of CORE) {
        if (!declared.has(token) || !isLiteral(declared.get(token))) continue
        if (ALLOWED[rel(file)]?.includes(token)) continue
        offenders.push(`${rel(file)} pins ${token} to ${declared.get(token)}`)
      }
    }

    expect(offenders).toEqual([])
  })

  // Dark mode is deferred -- see the "Dark mode: known gaps" section in StudyBuddyDesign.md.
  // Unskipping this test and making it pass IS the deferred pass; it needs a
  // `[data-sb-theme="dark"]` counterpart for every colour-valued token in `:root`.
  it.skip('every colour token in :root has a dark counterpart', () => {
    const isColour = (value) => {
      if (/#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(|\bcolor-mix\(/.test(value)) return true
      const alias = value.match(/^var\(\s*(--sb-[\w-]+)\s*\)$/)
      return Boolean(alias && rootTokens.has(alias[1]) && isColour(rootTokens.get(alias[1])))
    }

    const missing = [...rootTokens]
      .filter(([name, value]) => isColour(value) && !darkTokens.has(name))
      .map(([name]) => name)

    expect(missing).toEqual([])
  })
})
