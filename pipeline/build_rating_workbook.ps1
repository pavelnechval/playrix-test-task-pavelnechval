<#
Builds the rating workbook with Excel itself (COM): one row per card with an embedded thumbnail,
a 1-5 dropdown and an optional comment. Also creates a set-picks sheet, a formula summary and
a reference sheet.

    powershell -ExecutionPolicy Bypass -File pipeline\build_rating_workbook.ps1 -Manifest sets\ratings\manifest.json -Out sets\ratings\card_ratings_v1.xlsx

Input: manifest.json from pipeline/review_pack.py. Needs Microsoft Excel installed (Windows).
#>
param(
    [Parameter(Mandatory = $true)][string]$Manifest,
    [Parameter(Mandatory = $true)][string]$Out
)
$ErrorActionPreference = "Stop"
$manifestData = Get-Content -Raw -Encoding UTF8 $Manifest | ConvertFrom-Json
$cards = @($manifestData.cards)
$refs = @($manifestData.references)
$n = $cards.Count
$last = $n + 1
$OutPath = [System.IO.Path]::GetFullPath($Out)

function Rgb([int]$r, [int]$g, [int]$b) { return $r + 256 * $g + 65536 * $b }
$YELLOW = Rgb 255 242 102
$LIGHT = Rgb 255 250 205
$HEADER = Rgb 217 217 217

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
# Dropdown lists are parsed with the local list separator (";" in Russian Excel): "1,2,3,4,5" would be one option.
$sep = [string]$xl.International(5)   # xlListSeparator
try {
    $wb = $xl.Workbooks.Add()
    $wb.Styles.Item("Normal").Font.Name = "Arial"
    $wb.Styles.Item("Normal").Font.Size = 10
    while ($wb.Worksheets.Count -lt 5) { [void]$wb.Worksheets.Add([Type]::Missing, $wb.Worksheets.Item($wb.Worksheets.Count)) }
    $howTo = $wb.Worksheets.Item(1); $howTo.Name = "How to rate"
    $ws = $wb.Worksheets.Item(2); $ws.Name = "Ratings"
    $picks = $wb.Worksheets.Item(3); $picks.Name = "Set picks"
    $sum = $wb.Worksheets.Item(4); $sum.Name = "Summary"
    $refSheet = $wb.Worksheets.Item(5); $refSheet.Name = "References"

    # ---------- How to rate
    $lines = @(
        @("Card set ratings: Cinema collection (4 sets x 3 variants x 10 cards = 120 cards)", ""),
        @("", ""),
        @("What to fill", "On the Ratings sheet: column I 'Rating (1-5)' (yellow, dropdown) and column J 'Comment' (light yellow, optional). On the Set picks sheet: your pick per set and any swaps or redos."),
        @("Scale", "5 = indistinguishable from the real cards; 4 = minor difference; 3 = noticeable difference; 2 = clearly different in places; 1 = different style."),
        @("Judge", "Rendering (shapes, shading, materials, outlines), colour (warmth, saturation, contrast), composition (angle, size in frame, background) and whether the object fits the set."),
        @("Full size", "Thumbnails are 200x223 px. Click 'open' in column K to see the 430x480 card."),
        @("Codes", "LC = Love in the City, PP = Picture-Perfect Suburbia, OG = Once Upon a Garden, LI = The Lost Island. The Summary sheet averages your ratings automatically."),
        @("", ""),
        @("Example (format only; not a real rating)", "")
    )
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $howTo.Cells.Item($i + 1, 1).Value2 = [string]$lines[$i][0]
        $howTo.Cells.Item($i + 1, 2).Value2 = [string]$lines[$i][1]
    }
    $howTo.Range("A1").Font.Bold = $true; $howTo.Range("A1").Font.Size = 14
    $howTo.Range("A3:A9").Font.Bold = $true
    $exampleHeader = @("Code", "Name", "Rating (1-5)", "Comment (optional)")
    $exampleRow = @("LC-A01", "Rose Bouquet", "Bow a little too glossy; otherwise matches the real cards.")
    for ($c = 0; $c -lt 4; $c++) { $howTo.Cells.Item(10, $c + 1).Value2 = [string]$exampleHeader[$c] }
    # Numbers taken out of a PowerShell array reach COM wrapped and fail to convert, so cast explicitly.
    $howTo.Cells.Item(11, 1).Value2 = [string]$exampleRow[0]
    $howTo.Cells.Item(11, 2).Value2 = [string]$exampleRow[1]
    $howTo.Cells.Item(11, 3).Value2 = [double]4
    $howTo.Cells.Item(11, 4).Value2 = [string]$exampleRow[2]
    $howTo.Range("A10:D10").Font.Bold = $true; $howTo.Range("A10:D10").Interior.Color = $HEADER
    $howTo.Range("C11").Interior.Color = $YELLOW; $howTo.Range("D11").Interior.Color = $LIGHT
    $howTo.Range("A11:D11").Font.Italic = $true
    $howTo.Columns.Item(1).ColumnWidth = 22; $howTo.Columns.Item(2).ColumnWidth = 110; $howTo.Columns.Item(3).ColumnWidth = 14; $howTo.Columns.Item(4).ColumnWidth = 60
    $howTo.Range("B3:B7").WrapText = $true

    # ---------- Ratings
    $headers = @("Code", "Set", "Variant", "Concept", "Card", "Name", "Category", "Image", "Rating (1-5)", "Comment (optional)", "Full size")
    for ($c = 0; $c -lt $headers.Count; $c++) { $ws.Cells.Item(1, $c + 1).Value2 = [string]$headers[$c] }
    $hdr = $ws.Range("A1:K1"); $hdr.Font.Bold = $true; $hdr.Interior.Color = $HEADER; $hdr.WrapText = $true
    for ($i = 0; $i -lt $n; $i++) {
        # Values go cell by cell with explicit casts: PowerShell hands wrapped objects to COM otherwise.
        $card = $cards[$i]
        $row = $i + 2
        $ws.Cells.Item($row, 1).Value2 = [string]$card.code
        $ws.Cells.Item($row, 2).Value2 = [string]$card.set
        $ws.Cells.Item($row, 3).Value2 = [string]$card.variant
        $ws.Cells.Item($row, 4).Value2 = [string]$card.concept
        $ws.Cells.Item($row, 5).Value2 = [string]$card.card
        $ws.Cells.Item($row, 6).Value2 = [string]$card.name
        $ws.Cells.Item($row, 7).Value2 = [double]$card.category
    }
    $widths = @(9, 20, 8, 30, 7, 18, 9, 28, 12, 48, 9)
    for ($c = 0; $c -lt $widths.Count; $c++) { $ws.Columns.Item($c + 1).ColumnWidth = [double]$widths[$c] }
    $ws.Range("A2:K$last").RowHeight = 172
    $ws.Range("A1:K$last").VerticalAlignment = -4108   # xlCenter
    $ws.Range("D2:D$last").WrapText = $true
    $ws.Range("J2:J$last").WrapText = $true
    $ws.Range("I2:I$last").HorizontalAlignment = -4108
    $ws.Range("I2:I$last").Interior.Color = $YELLOW
    $ws.Range("J2:J$last").Interior.Color = $LIGHT
    $ws.Range("I2:I$last").Font.Size = 14; $ws.Range("I2:I$last").Font.Bold = $true
    for ($i = 0; $i -lt $n; $i++) {
        $row = $i + 2
        $cell = $ws.Cells.Item($row, 8)
        $pic = $ws.Shapes.AddPicture([string]$cards[$i].thumb, 0, -1, $cell.Left + 3, $cell.Top + 2, 150, 167.25)
        $pic.Placement = 1   # move and size with the cell, so sorting and filtering keep the picture with its row
        [void]$ws.Hyperlinks.Add($ws.Cells.Item($row, 11), [string]$cards[$i].final, "", "Open the full-size card", "open")
    }
    $validation = $ws.Range("I2:I$last").Validation
    $validation.Delete()
    $validation.Add(3, 1, 1, [string]((1..5) -join $sep))   # xlValidateList, xlValidAlertStop, xlBetween
    $validation.IgnoreBlank = $true; $validation.InCellDropdown = $true
    $validation.InputTitle = "Rating"; $validation.InputMessage = "5 = indistinguishable from the real cards ... 1 = different style"
    $scale = $ws.Range("I2:I$last").FormatConditions.AddColorScale(3)
    $points = @(@(1, (Rgb 248 105 107)), @(3, (Rgb 255 235 132)), @(5, (Rgb 99 190 123)))
    for ($k = 0; $k -lt 3; $k++) {
        $criterion = $scale.ColorScaleCriteria.Item($k + 1)
        $criterion.Type = 0; $criterion.Value = [double]$points[$k][0]; $criterion.FormatColor.Color = [double]$points[$k][1]
    }
    [void]$ws.Range("A1:K$last").AutoFilter()
    try { $ws.Activate(); $xl.ActiveWindow.SplitRow = 1; $xl.ActiveWindow.SplitColumn = 0; $xl.ActiveWindow.FreezePanes = $true }
    catch { Write-Warning "Could not freeze the header row (no active window): $($_.Exception.Message)" }

    # ---------- Set picks
    $sets = @($cards | ForEach-Object { $_.set } | Select-Object -Unique)
    $pickHeaders = @("Set", "Variant A", "Variant B", "Variant C", "Your pick", "Cards to swap in/out or redo (optional)")
    for ($c = 0; $c -lt $pickHeaders.Count; $c++) { $picks.Cells.Item(1, $c + 1).Value2 = [string]$pickHeaders[$c] }
    for ($s = 0; $s -lt $sets.Count; $s++) {
        $picks.Cells.Item($s + 2, 1).Value2 = [string]$sets[$s]
        foreach ($v in @("A", "B", "C")) {
            $concept = ($cards | Where-Object { $_.set -eq $sets[$s] -and $_.variant -eq $v } | Select-Object -First 1).concept
            $picks.Cells.Item($s + 2, [int][char]$v - 63).Value2 = [string]$concept
        }
    }
    $pickRange = "E2:E$($sets.Count + 1)"
    $pv = $picks.Range($pickRange).Validation; $pv.Delete(); $pv.Add(3, 1, 1, [string](@("A", "B", "C", "Mix") -join $sep)); $pv.InCellDropdown = $true
    $picks.Range($pickRange).Interior.Color = $YELLOW
    $picks.Range("F2:F$($sets.Count + 1)").Interior.Color = $LIGHT
    $picks.Range("A1:F1").Font.Bold = $true; $picks.Range("A1:F1").Interior.Color = $HEADER
    $pickWidths = @(26, 34, 34, 34, 11, 60)
    for ($c = 0; $c -lt $pickWidths.Count; $c++) { $picks.Columns.Item($c + 1).ColumnWidth = [double]$pickWidths[$c] }
    $picks.Range("A2:F$($sets.Count + 1)").WrapText = $true; $picks.Range("A2:F$($sets.Count + 1)").VerticalAlignment = -4108

    # ---------- Summary (formulas over the Ratings sheet)
    $sumHeaders = @("Set", "Variant", "Cards", "Rated", "Average rating", "Rated 4-5", "Share 4-5 of rated")
    for ($c = 0; $c -lt $sumHeaders.Count; $c++) { $sum.Cells.Item(1, $c + 1).Value2 = [string]$sumHeaders[$c] }
    $B = "Ratings!`$B`$2:`$B`$$last"; $C = "Ratings!`$C`$2:`$C`$$last"; $I = "Ratings!`$I`$2:`$I`$$last"
    $r = 2
    foreach ($set in $sets) {
        foreach ($v in @("A", "B", "C", "all")) {
            $sum.Cells.Item($r, 1).Value2 = [string]$set
            $sum.Cells.Item($r, 2).Value2 = [string]$v
            if ($v -eq "all") {
                $crit = "$B,`$A$r"
                $sum.Range("A${r}:G$r").Font.Bold = $true
            } else {
                $crit = "$B,`$A$r,$C,`$B$r"
            }
            $sum.Cells.Item($r, 3).Formula = "=COUNTIFS($crit)"
            $sum.Cells.Item($r, 4).Formula = "=COUNTIFS($crit,$I,`">=1`")"
            $sum.Cells.Item($r, 5).Formula = "=IFERROR(AVERAGEIFS($I,$crit),`"`")"
            $sum.Cells.Item($r, 6).Formula = "=COUNTIFS($crit,$I,`">=4`")"
            $sum.Cells.Item($r, 7).Formula = "=IFERROR(F$r/D$r,`"`")"
            $r++
        }
    }
    $sum.Cells.Item($r, 1).Value2 = "All sets"; $sum.Cells.Item($r, 2).Value2 = "all"
    $sum.Cells.Item($r, 3).Formula = "=COUNTA(Ratings!`$A`$2:`$A`$$last)"
    $sum.Cells.Item($r, 4).Formula = "=COUNTIFS($I,`">=1`")"
    $sum.Cells.Item($r, 5).Formula = "=IFERROR(AVERAGE($I),`"`")"
    $sum.Cells.Item($r, 6).Formula = "=COUNTIFS($I,`">=4`")"
    $sum.Cells.Item($r, 7).Formula = "=IFERROR(F$r/D$r,`"`")"
    $sum.Range("A${r}:G$r").Font.Bold = $true
    # Localized Excel (e.g. Russian) can reject English decimal formats over COM; fall back to the local separator.
    try { $sum.Range("E2:E$r").NumberFormat = "0.0" } catch { $sum.Range("E2:E$r").NumberFormatLocal = "0" + [string]$xl.International(3) + "0" }
    $sum.Range("G2:G$r").NumberFormat = "0%"
    $sum.Range("A1:G1").Font.Bold = $true; $sum.Range("A1:G1").Interior.Color = $HEADER
    $sumWidths = @(26, 9, 8, 8, 15, 10, 18)
    for ($c = 0; $c -lt $sumWidths.Count; $c++) { $sum.Columns.Item($c + 1).ColumnWidth = [double]$sumWidths[$c] }
    $sum.Cells.Item($r + 2, 1).Value2 = "Formulas count and average the Ratings sheet (column I). Empty until ratings are entered."
    $sum.Cells.Item($r + 2, 1).Font.Italic = $true

    # ---------- References (the 12 real cards sent with every generation)
    $refHeaders = @("ID", "Name", "Category", "Image")
    for ($c = 0; $c -lt 4; $c++) { $refSheet.Cells.Item(1, $c + 1).Value2 = [string]$refHeaders[$c] }
    $refSheet.Range("A1:D1").Font.Bold = $true; $refSheet.Range("A1:D1").Interior.Color = $HEADER
    $refSheet.Columns.Item(1).ColumnWidth = 6; $refSheet.Columns.Item(2).ColumnWidth = 18; $refSheet.Columns.Item(3).ColumnWidth = 9; $refSheet.Columns.Item(4).ColumnWidth = 28
    for ($i = 0; $i -lt $refs.Count; $i++) {
        $row = $i + 2
        $refSheet.Cells.Item($row, 1).Value2 = [string]$refs[$i].id
        $refSheet.Cells.Item($row, 2).Value2 = [string]$refs[$i].name
        $refSheet.Cells.Item($row, 3).Value2 = [double]$refs[$i].category
        $refSheet.Rows.Item($row).RowHeight = 172
        $cell = $refSheet.Cells.Item($row, 4)
        $pic = $refSheet.Shapes.AddPicture([string]$refs[$i].thumb, 0, -1, $cell.Left + 3, $cell.Top + 2, 150, 167.25)
        $pic.Placement = 1
    }
    $refSheet.Range("A2:D$($refs.Count + 1)").VerticalAlignment = -4108

    # ---------- Verify the dropdowns accept single options and the formulas evaluate, then save
    $probe = $ws.Range("I2"); $probe.Value2 = [double]3; $ratingOk = [bool]$probe.Validation.Value; $probe.ClearContents()
    $probe = $picks.Range("E2"); $probe.Value2 = "Mix"; $pickOk = [bool]$probe.Validation.Value; $probe.ClearContents()
    if (-not ($ratingOk -and $pickOk)) { throw "Dropdown check failed: a single option was rejected (rating 3: $ratingOk, pick Mix: $pickOk)" }
    $xl.CalculateFull()
    $bad = @()
    foreach ($cell in $sum.UsedRange.Cells) { if ($cell.Text -like "#*") { $bad += $cell.Address(0, 0) } }
    $ws.Activate()
    if (Test-Path $OutPath) { Remove-Item $OutPath -Force }
    $wb.SaveAs($OutPath, 51)   # xlOpenXMLWorkbook (.xlsx)
    $wb.Close($false)
    "Saved $OutPath : $n cards, $($refs.Count) references, $($sets.Count) sets; formula errors: $($bad.Count) $($bad -join ','); dropdowns OK (list separator '$sep')"
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
