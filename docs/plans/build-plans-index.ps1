# Regenerates docs/plans/index.html from plan frontmatter.
# Usage: powershell -File build-plans-index.ps1 [-PlansDir <path>]
# Copy this script into a repo's docs/plans/ on first plan creation; run it
# after every plan create/update/complete instead of hand-writing the HTML.
# PowerShell 5.1 compatible.

param(
    [string]$PlansDir = $PSScriptRoot
)

$statusOrder  = @('In Progress', 'Blocked', 'Approved', 'Draft', 'Done')
$statusSlugs  = @{
    'In Progress' = 'in-progress'
    'Blocked'     = 'blocked'
    'Approved'    = 'approved'
    'Draft'       = 'draft'
    'Done'        = 'done'
}

function HtmlEncode([string]$s) {
    if ($null -eq $s) { return '' }
    $s -replace '&', '&amp;' -replace '<', '&lt;' -replace '>', '&gt;' -replace '"', '&quot;'
}

# Files may predate the frontmatter convention. Never drop a plan just because
# it lacks a frontmatter block — fall back to the same signals a human would
# use: the first Markdown heading for a title, the filename's date prefix,
# and an inline "**Status:** X" line if one exists. Unknown status defaults to
# Draft (the existing fallback for frontmatter that omits `status:` too), so
# the dashboard stays visible rather than silently incomplete.
$plans = @()
Get-ChildItem -Path $PlansDir -Filter '*.md' |
    Where-Object { $_.Name -ne '_template.md' -and $_.Name -ne 'README.md' } |
    ForEach-Object {
        $file = $_
        # Read as UTF-8 explicitly - PowerShell 5.1's Get-Content mis-detects
        # BOM-less UTF-8 as the system codepage and mangles multi-byte
        # characters (em dashes become "â€”").
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        $lines = [System.Text.Encoding]::UTF8.GetString($bytes) -split "`r?`n"

        $fm = @{}
        $bodyStart = 0
        if ($lines.Count -ge 3 -and $lines[0].Trim() -eq '---') {
            for ($i = 1; $i -lt $lines.Count; $i++) {
                if ($lines[$i].Trim() -eq '---') { $bodyStart = $i + 1; break }
                if ($lines[$i] -match '^\s*([A-Za-z_]+)\s*:\s*(.*)$') {
                    # Strip trailing "# comment" from values like: status: Approved  # Draft | ...
                    $val = ($Matches[2] -split '\s+#')[0].Trim()
                    $fm[$Matches[1].ToLower()] = $val
                }
            }
        }

        $title = $fm['title']
        if (-not $title) {
            $headingLine = $lines | Where-Object { $_.Trim() -match '^#+\s+\S' } | Select-Object -First 1
            if ($headingLine) { $title = ($headingLine.Trim() -replace '^#+\s+', '') }
        }
        if (-not $title) { $title = $file.BaseName }

        $date = $fm['date']
        if (-not $date -and $file.BaseName -match '^(\d{4}-\d{2}-\d{2})-') { $date = $Matches[1] }

        $status = $fm['status']
        if (-not $status) {
            $scanLines = $lines | Select-Object -Skip $bodyStart -First 30
            $statusLine = $scanLines | Where-Object { $_ -match '\*\*Status:?\*\*\s*:?\s*(In Progress|Blocked|Approved|Draft|Done)' } | Select-Object -First 1
            if ($statusLine -and $statusLine -match '\*\*Status:?\*\*\s*:?\s*(In Progress|Blocked|Approved|Draft|Done)') {
                $status = $Matches[1]
            }
        }
        if (-not $status -or $statusOrder -notcontains $status) { $status = 'Draft' }

        $plans += [pscustomobject]@{
            Title   = $title
            Date    = $date
            Summary = $fm['summary']
            Status  = $status
            Path    = $file.FullName
        }
    }

$html = New-Object System.Text.StringBuilder
[void]$html.AppendLine(@'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Studybuddy &mdash; Plan Dashboard</title>
<style>
  :root {
    --bg: #0d1117;
    --card: #161b22;
    --text: #e6edf3;
    --text-muted: #8b949e;
    --border: #30363d;
    --in-progress: #388bfd;
    --blocked: #f85149;
    --approved: #d29922;
    --draft: #6e7681;
    --done: #2ea043;
  }
  * { box-sizing: border-box; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    margin: 0;
    padding: 32px;
  }
  h1 {
    font-size: 22px;
    margin: 0 0 4px 0;
  }
  .subtitle {
    color: var(--text-muted);
    font-size: 13px;
    margin: 0 0 20px 0;
  }
  .badge-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 28px;
  }
  .badge-row .count {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 600;
  }
  .dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
  }
  .group {
    margin-bottom: 28px;
  }
  .group > summary, .group-title {
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 12px;
    cursor: pointer;
    list-style: none;
  }
  .group > summary::-webkit-details-marker { display: none; }
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 12px;
  }
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
  }
  .card a.title {
    color: var(--text);
    text-decoration: none;
    font-weight: 600;
    font-size: 14px;
    line-height: 1.4;
  }
  .card a.title:hover {
    text-decoration: underline;
  }
  .card .meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
    font-size: 12px;
    color: var(--text-muted);
  }
  .status-badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    color: #0d1117;
  }
  .status-in-progress { background: var(--in-progress); color: #fff; }
  .status-blocked { background: var(--blocked); color: #fff; }
  .status-approved { background: var(--approved); }
  .status-draft { background: var(--draft); color: #fff; }
  .status-done { background: var(--done); color: #fff; }
  .card .summary {
    margin-top: 8px;
    font-size: 12.5px;
    color: var(--text-muted);
    line-height: 1.5;
  }
</style>
</head>
<body>

<h1>Studybuddy &mdash; Plan Dashboard</h1>
'@)
[void]$html.AppendLine("<p class=""subtitle"">Regenerated $(Get-Date -Format 'yyyy-MM-dd')</p>")
[void]$html.AppendLine('')
[void]$html.AppendLine('<div class="badge-row">')
foreach ($s in $statusOrder) {
    $count = @($plans | Where-Object { $_.Status -eq $s }).Count
    [void]$html.AppendLine("  <span class=""count""><span class=""dot"" style=""background:var(--$($statusSlugs[$s]))""></span>$count $s</span>")
}
[void]$html.AppendLine('</div>')

foreach ($s in $statusOrder) {
    $group = @($plans | Where-Object { $_.Status -eq $s } | Sort-Object Date -Descending)
    if ($group.Count -eq 0) { continue }
    $isDone = ($s -eq 'Done')
    [void]$html.AppendLine('')
    if ($isDone) {
        [void]$html.AppendLine("<details class=""group"">")
        [void]$html.AppendLine("  <summary>$s ($($group.Count))</summary>")
    } else {
        [void]$html.AppendLine('<div class="group">')
        [void]$html.AppendLine("  <div class=""group-title"">$s ($($group.Count))</div>")
    }
    [void]$html.AppendLine('  <div class="cards">')
    foreach ($p in $group) {
        $vscodeHref = 'vscode://file/' + ($p.Path -replace '\\', '/')
        $slug = $statusSlugs[$p.Status]
        [void]$html.AppendLine('    <div class="card">')
        [void]$html.AppendLine("      <a class=""title"" href=""$vscodeHref"">$(HtmlEncode $p.Title)</a>")
        [void]$html.AppendLine("      <div class=""meta""><span class=""status-badge status-$slug"">$(HtmlEncode $p.Status)</span><span>$(HtmlEncode $p.Date)</span></div>")
        if ($p.Summary) { [void]$html.AppendLine("      <div class=""summary"">$(HtmlEncode $p.Summary)</div>") }
        [void]$html.AppendLine('    </div>')
    }
    [void]$html.AppendLine('  </div>')
    if ($isDone) { [void]$html.AppendLine('</details>') } else { [void]$html.AppendLine('</div>') }
}

[void]$html.AppendLine('')
[void]$html.AppendLine('</body>')
[void]$html.AppendLine('</html>')

$outPath = Join-Path $PlansDir 'index.html'
[System.IO.File]::WriteAllText($outPath, $html.ToString(), (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Wrote $outPath ($($plans.Count) plans)"
