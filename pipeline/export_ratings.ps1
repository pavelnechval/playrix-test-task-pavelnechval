<#
Reads a filled rating workbook (made by build_rating_workbook.ps1) with Excel itself, read-only, and
exports the ratings, comments and set picks to JSON for rating_report.py. The workbook is not changed.

    powershell -ExecutionPolicy Bypass -File pipeline\export_ratings.ps1 -Path sets\ratings\card_ratings_v1.xlsx -OutJson sets\ratings\pavel_ratings.json
#>
param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)][string]$OutJson
)
$ErrorActionPreference = "Stop"
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
try {
    $wb = $xl.Workbooks.Open([System.IO.Path]::GetFullPath($Path), 0, $true)   # UpdateLinks = 0, ReadOnly
    $ws = $wb.Worksheets.Item("Ratings")
    $last = $ws.Cells.Item($ws.Rows.Count, 1).End(-4162).Row   # xlUp
    $rows = @()
    for ($r = 2; $r -le $last; $r++) {
        $rating = $ws.Cells.Item($r, 9).Value2
        $rows += [ordered]@{
            code = [string]$ws.Cells.Item($r, 1).Text
            set = [string]$ws.Cells.Item($r, 2).Text
            variant = [string]$ws.Cells.Item($r, 3).Text
            card = [string]$ws.Cells.Item($r, 5).Text
            name = [string]$ws.Cells.Item($r, 6).Text
            category = [int]$ws.Cells.Item($r, 7).Value2
            rating = $(if ($null -eq $rating -or [string]$rating -eq "") { $null } else { [double]$rating })
            comment = [string]$ws.Cells.Item($r, 10).Text
        }
    }
    $picks = $wb.Worksheets.Item("Set picks")
    $pickRows = @()
    for ($r = 2; [string]$picks.Cells.Item($r, 1).Text -ne ""; $r++) {
        $pickRows += [ordered]@{ set = [string]$picks.Cells.Item($r, 1).Text; pick = [string]$picks.Cells.Item($r, 5).Text; notes = [string]$picks.Cells.Item($r, 6).Text }
    }
    $data = [ordered]@{ source = [System.IO.Path]::GetFileName($Path); ratings = $rows; picks = $pickRows }
    [System.IO.File]::WriteAllText([System.IO.Path]::GetFullPath($OutJson), ($data | ConvertTo-Json -Depth 5), (New-Object System.Text.UTF8Encoding($false)))
    $wb.Close($false)
    "Exported $($rows.Count) ratings ($(@($rows | Where-Object { $null -ne $_.rating }).Count) filled) and $($pickRows.Count) set picks -> $OutJson"
}
catch {
    Write-Output "FAILED at line $($_.InvocationInfo.ScriptLineNumber): $($_.InvocationInfo.Line.Trim())"
    Write-Output $_.Exception.Message
    exit 1
}
finally {
    $xl.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
