# Add journal notes scripts to all HTML templates
$templates = @(
    'dashboard\templates\analytics.html',
    'dashboard\templates\sessions.html',
    'dashboard\templates\risk.html',
    'dashboard\templates\settings.html',
    'dashboard\templates\help.html'
)

$scriptToAdd = @"
    <link rel="stylesheet" href="{{ url_for('static', filename='css/journal_notes.css') }}">
    <script src="{{ url_for('static', filename='js/journal_notes.js') }}"></script>
"@

foreach ($template in $templates) {
    if (Test-Path $template) {
        $content = Get-Content $template -Raw
        
        # Check if already added
        if ($content -notlike '*journal_notes.css*') {
            # Add before </body>
            $content = $content -replace '(</body>)', "$scriptToAdd`n`$1"
            Set-Content $template -Value $content -NoNewline
            Write-Host "✅ Updated $template"
        } else {
            Write-Host "⏭️  Skipped $template (already has journal notes scripts)"
        }
    }
}

Write-Host "`n🎉 All templates updated!"
