<#
.SYNOPSIS
    Internet Speed Dashboard - Tests website load times and internet speed
.DESCRIPTION
    Displays a real-time dashboard that tests website load times for specified URLs,
    then measures internet download/upload speed using Speedtest CLI.
.PARAMETER Websites
    Array of websites to test load times (default: google.com, davivienda.com, nasa.gov, eltiempo.com, disneyplus.com)
.PARAMETER SkipSpeedtest
    Skip the speedtest portion and only test website load times
.EXAMPLE
    .\Internet-Speed-Dashboard.ps1
.EXAMPLE
    .\Internet-Speed-Dashboard.ps1 -Websites @("www.google.com", "www.github.com")
.EXAMPLE
    .\Internet-Speed-Dashboard.ps1 -SkipSpeedtest
.NOTES
    Requires Speedtest CLI by Ookla. Download from: https://www.speedtest.net/apps/cli
    If speedtest is not installed, the script will provide download instructions.
#>

param(
    [string[]]$Websites = @(
        "www.google.com",
        "www.davivienda.com",
        "www.nasa.gov",
        "www.eltiempo.com",
        "www.disneyplus.com"
    ),
    [switch]$SkipSpeedtest
)

# Clear the console and hide cursor
Clear-Host
[Console]::CursorVisible = $false

# Initialize variables
$script:WebsiteResults = @()
$script:SpeedtestResult = $null
$script:CurrentPhase = "website-test"  # website-test or speedtest
$script:SpeedtestProgress = "Initializing..."

# Color scheme
$Colors = @{
    Header = 'Cyan'
    Success = 'Green'
    Warning = 'Yellow'
    Error = 'Red'
    Info = 'White'
    Label = 'Gray'
}

function Test-SpeedtestInstalled {
    try {
        $result = Get-Command speedtest -ErrorAction SilentlyContinue
        return $null -ne $result
    } catch {
        return $false
    }
}

function Draw-Header {
    param([string]$Phase)

    $width = [Console]::WindowWidth
    [Console]::SetCursorPosition(0, 0)
    Write-Host ("=" * $width) -ForegroundColor $Colors.Header -NoNewline
    [Console]::SetCursorPosition(0, 1)

    if ($Phase -eq "website-test") {
        $title = " INTERNET SPEED DASHBOARD - Website Load Time Testing "
    } else {
        $title = " INTERNET SPEED DASHBOARD - Speed Test "
    }

    $padding = [math]::Max(0, ($width - $title.Length) / 2)
    Write-Host (" " * $padding + $title) -ForegroundColor $Colors.Header -NoNewline
    [Console]::SetCursorPosition(0, 2)
    $subtitle = " For Private Use Only "
    $subPadding = [math]::Max(0, ($width - $subtitle.Length) / 2)
    Write-Host (" " * $subPadding + $subtitle) -ForegroundColor $Colors.Warning -NoNewline
    [Console]::SetCursorPosition(0, 3)
    Write-Host ("=" * $width) -ForegroundColor $Colors.Header -NoNewline
}

function Test-WebsiteLoadTime {
    param([string]$Website)

    $result = @{
        Website = $Website
        Timestamp = Get-Date
        Success = $false
        LoadTime = 0
        StatusCode = 0
        Error = ""
    }

    try {
        $url = if ($Website -notmatch "^https?://") { "https://$Website" } else { $Website }

        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        $stopwatch.Stop()

        $result.Success = $true
        $result.LoadTime = $stopwatch.ElapsedMilliseconds
        $result.StatusCode = [int]$response.StatusCode

    } catch {
        $result.Error = $_.Exception.Message
        if ($_.Exception.Response) {
            $result.StatusCode = [int]$_.Exception.Response.StatusCode
        }
    }

    return $result
}

function Format-Speed {
    param([double]$Mbps)

    if ($Mbps -lt 1) {
        return "$([math]::Round($Mbps * 1000, 2)) Kbps"
    } else {
        return "$([math]::Round($Mbps, 2)) Mbps"
    }
}

function Draw-WebsiteResults {
    param([int]$StartRow)

    $consoleWidth = [Console]::WindowWidth

    [Console]::SetCursorPosition(0, $StartRow)
    Write-Host " WEBSITE LOAD TIME RESULTS:" -ForegroundColor $Colors.Header

    $row = $StartRow + 1

    foreach ($result in $script:WebsiteResults) {
        [Console]::SetCursorPosition(0, $row)

        $timestamp = $result.Timestamp.ToString("HH:mm:ss")

        if ($result.Success) {
            $loadTimeColor = if ($result.LoadTime -lt 500) { $Colors.Success }
                           elseif ($result.LoadTime -lt 2000) { $Colors.Warning }
                           else { $Colors.Error }

            $message = " [$timestamp] $($result.Website.PadRight(30)) - $($result.LoadTime)ms (HTTP $($result.StatusCode))"
            Write-Host $message.PadRight($consoleWidth) -ForegroundColor $loadTimeColor
        } else {
            $errorMsg = if ($result.Error.Length -gt 40) { $result.Error.Substring(0, 40) + "..." } else { $result.Error }
            $message = " [$timestamp] $($result.Website.PadRight(30)) - FAILED: $errorMsg"
            Write-Host $message.PadRight($consoleWidth) -ForegroundColor $Colors.Error
        }

        $row++
    }

    return $row
}

function Draw-SpeedtestResults {
    param([int]$StartRow)

    $panelWidth = 60
    $consoleWidth = [Console]::WindowWidth
    $startCol = [math]::Max(0, ($consoleWidth - $panelWidth) / 2)

    # Draw panel border
    [Console]::SetCursorPosition($startCol, $StartRow)
    Write-Host ("╔" + ("═" * ($panelWidth - 2)) + "╗") -ForegroundColor $Colors.Header

    # Panel title
    $row = $StartRow + 1
    [Console]::SetCursorPosition($startCol, $row)
    Write-Host "║" -ForegroundColor $Colors.Header -NoNewline
    Write-Host (" INTERNET SPEED TEST RESULTS".PadRight($panelWidth - 2)) -ForegroundColor $Colors.Info -NoNewline
    Write-Host "║" -ForegroundColor $Colors.Header

    # Separator
    $row++
    [Console]::SetCursorPosition($startCol, $row)
    Write-Host ("╠" + ("═" * ($panelWidth - 2)) + "╣") -ForegroundColor $Colors.Header

    if ($null -eq $script:SpeedtestResult) {
        # Show progress
        $row++
        [Console]::SetCursorPosition($startCol, $row)
        Write-Host "║" -ForegroundColor $Colors.Header -NoNewline
        Write-Host (" " + $script:SpeedtestProgress).PadRight($panelWidth - 2) -ForegroundColor $Colors.Info -NoNewline
        Write-Host "║" -ForegroundColor $Colors.Header

        $row++
        [Console]::SetCursorPosition($startCol, $row)
        Write-Host "║" -ForegroundColor $Colors.Header -NoNewline
        Write-Host (" Please wait...").PadRight($panelWidth - 2) -ForegroundColor $Colors.Label -NoNewline
        Write-Host "║" -ForegroundColor $Colors.Header
    } else {
        $result = $script:SpeedtestResult

        # Server information
        $stats = @(
            @{ Label = "Server"; Value = $result.ServerName; Color = $Colors.Info },
            @{ Label = "Location"; Value = $result.ServerLocation; Color = $Colors.Label },
            @{ Label = ""; Value = ""; Color = $Colors.Info },
            @{ Label = "Ping"; Value = "$($result.Ping) ms"; Color = if ($result.Ping -lt 50) { $Colors.Success } elseif ($result.Ping -lt 100) { $Colors.Warning } else { $Colors.Error } },
            @{ Label = "Jitter"; Value = "$($result.Jitter) ms"; Color = $Colors.Label },
            @{ Label = ""; Value = ""; Color = $Colors.Info },
            @{ Label = "Download Speed"; Value = Format-Speed $result.DownloadSpeed; Color = $Colors.Success },
            @{ Label = "Upload Speed"; Value = Format-Speed $result.UploadSpeed; Color = $Colors.Warning },
            @{ Label = ""; Value = ""; Color = $Colors.Info },
            @{ Label = "Result URL"; Value = ""; Color = $Colors.Info }
        )

        foreach ($stat in $stats) {
            $row++
            [Console]::SetCursorPosition($startCol, $row)
            Write-Host "║" -ForegroundColor $Colors.Header -NoNewline

            if ($stat.Label -ne "") {
                $line = " $($stat.Label): $($stat.Value)".PadRight($panelWidth - 2)
            } else {
                $line = " $($stat.Value)".PadRight($panelWidth - 2)
            }

            Write-Host $line -ForegroundColor $stat.Color -NoNewline
            Write-Host "║" -ForegroundColor $Colors.Header
        }

        # Result URL (truncated if needed)
        $row++
        [Console]::SetCursorPosition($startCol, $row)
        Write-Host "║" -ForegroundColor $Colors.Header -NoNewline
        $maxUrlLength = $panelWidth - 4
        $displayUrl = if ($result.ResultUrl.Length -gt $maxUrlLength) {
            $result.ResultUrl.Substring(0, $maxUrlLength - 3) + "..."
        } else {
            $result.ResultUrl
        }
        Write-Host (" " + $displayUrl).PadRight($panelWidth - 2) -ForegroundColor $Colors.Label -NoNewline
        Write-Host "║" -ForegroundColor $Colors.Header
    }

    # Bottom border
    $row++
    [Console]::SetCursorPosition($startCol, $row)
    Write-Host ("╚" + ("═" * ($panelWidth - 2)) + "╝") -ForegroundColor $Colors.Header

    return $row
}

function Update-WebsiteTestDashboard {
    Draw-Header -Phase "website-test"

    $headerRows = 4
    $resultsStartRow = $headerRows + 2

    $nextRow = Draw-WebsiteResults -StartRow $resultsStartRow

    # Clear remaining area
    $consoleWidth = [Console]::WindowWidth
    for ($i = $nextRow; $i -lt [Console]::WindowHeight - 2; $i++) {
        [Console]::SetCursorPosition(0, $i)
        Write-Host (" " * $consoleWidth)
    }

    # Instructions at bottom
    $bottomRow = [Console]::WindowHeight - 1
    [Console]::SetCursorPosition(0, $bottomRow)
    Write-Host " Press Ctrl+C to exit" -ForegroundColor $Colors.Label -NoNewline
}

function Update-SpeedtestDashboard {
    Draw-Header -Phase "speedtest"

    $headerRows = 4
    $resultsStartRow = $headerRows + 2

    $nextRow = Draw-SpeedtestResults -StartRow $resultsStartRow

    # Clear remaining area
    $consoleWidth = [Console]::WindowWidth
    for ($i = $nextRow; $i -lt [Console]::WindowHeight - 2; $i++) {
        [Console]::SetCursorPosition(0, $i)
        Write-Host (" " * $consoleWidth)
    }

    # Instructions at bottom
    $bottomRow = [Console]::WindowHeight - 1
    [Console]::SetCursorPosition(0, $bottomRow)
    Write-Host " Press Ctrl+C to exit" -ForegroundColor $Colors.Label -NoNewline
}

function Start-Speedtest {
    try {
        $script:SpeedtestProgress = "Selecting best server..."
        Update-SpeedtestDashboard

        # Run speedtest with JSON output
        $speedtestOutput = speedtest --accept-license --accept-gdpr --format=json 2>&1 | Out-String

        # Parse JSON result
        $speedtestData = $speedtestOutput | ConvertFrom-Json

        $script:SpeedtestResult = @{
            ServerName = $speedtestData.server.name
            ServerLocation = "$($speedtestData.server.location), $($speedtestData.server.country)"
            Ping = [math]::Round($speedtestData.ping.latency, 2)
            Jitter = [math]::Round($speedtestData.ping.jitter, 2)
            DownloadSpeed = [math]::Round($speedtestData.download.bandwidth / 125000, 2)  # Convert to Mbps
            UploadSpeed = [math]::Round($speedtestData.upload.bandwidth / 125000, 2)  # Convert to Mbps
            ResultUrl = $speedtestData.result.url
        }

    } catch {
        $script:SpeedtestResult = @{
            ServerName = "Error"
            ServerLocation = "N/A"
            Ping = 0
            Jitter = 0
            DownloadSpeed = 0
            UploadSpeed = 0
            ResultUrl = "Test failed: $($_.Exception.Message)"
        }
    }
}

# Main execution
try {
    Write-Host "Initializing Internet Speed Dashboard..." -ForegroundColor $Colors.Info
    Write-Host "Phase 1: Testing website load times..." -ForegroundColor $Colors.Info
    Start-Sleep -Seconds 2

    Clear-Host

    # Phase 1: Website Load Time Testing
    $script:CurrentPhase = "website-test"
    Update-WebsiteTestDashboard

    foreach ($website in $Websites) {
        $result = Test-WebsiteLoadTime -Website $website
        $script:WebsiteResults += $result
        Update-WebsiteTestDashboard
        Start-Sleep -Milliseconds 500
    }

    # Show website results for a moment
    Start-Sleep -Seconds 3

    # Phase 2: Speed Test
    if (-not $SkipSpeedtest) {
        # Check if speedtest is installed
        if (-not (Test-SpeedtestInstalled)) {
            Clear-Host
            Write-Host "`n`n" -NoNewline
            Write-Host "  Phase 1 Complete: Website load times tested" -ForegroundColor $Colors.Success
            Write-Host "`n  ERROR: Speedtest CLI not found!" -ForegroundColor $Colors.Error
            Write-Host "`n  To use the speed test feature, please install Speedtest CLI:" -ForegroundColor $Colors.Info
            Write-Host "  1. Download from: https://www.speedtest.net/apps/cli" -ForegroundColor $Colors.Label
            Write-Host "  2. Install the executable to a location in your PATH" -ForegroundColor $Colors.Label
            Write-Host "  3. Or run this script with -SkipSpeedtest to skip speed testing" -ForegroundColor $Colors.Label
            Write-Host "`n  Press any key to exit..." -ForegroundColor $Colors.Warning
            [Console]::CursorVisible = $true
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            return
        }

        Clear-Host
        Write-Host "`n`n" -NoNewline
        Write-Host "  Phase 1 Complete: Website load times tested" -ForegroundColor $Colors.Success
        Write-Host "`n  Starting Phase 2: Internet speed test..." -ForegroundColor $Colors.Info
        Write-Host "`n  This will test your download and upload speeds" -ForegroundColor $Colors.Label
        Write-Host "  Starting test in 3 seconds..." -ForegroundColor $Colors.Warning
        Start-Sleep -Seconds 3

        Clear-Host
        $script:CurrentPhase = "speedtest"

        Update-SpeedtestDashboard
        Start-Speedtest
        Update-SpeedtestDashboard

        # Show results for a moment
        Start-Sleep -Seconds 5
    }

} catch {
    if ($_.Exception.Message -notmatch "pipeline") {
        Write-Host "`nError: $($_.Exception.Message)" -ForegroundColor Red
    }
} finally {
    # Cleanup
    [Console]::CursorVisible = $true
    [Console]::SetCursorPosition(0, [Console]::WindowHeight - 1)
    Write-Host "`n`nDashboard stopped." -ForegroundColor $Colors.Info

    # Display final statistics
    Write-Host "`n=== WEBSITE LOAD TIME RESULTS ===" -ForegroundColor $Colors.Header

    $successCount = ($script:WebsiteResults | Where-Object { $_.Success }).Count
    $failCount = ($script:WebsiteResults | Where-Object { -not $_.Success }).Count

    foreach ($result in $script:WebsiteResults) {
        if ($result.Success) {
            Write-Host "  $($result.Website.PadRight(30)) - $($result.LoadTime)ms" -ForegroundColor $Colors.Success
        } else {
            Write-Host "  $($result.Website.PadRight(30)) - FAILED" -ForegroundColor $Colors.Error
        }
    }

    Write-Host "`n  Success: $successCount / $($script:WebsiteResults.Count)" -ForegroundColor $(if ($successCount -eq $script:WebsiteResults.Count) { $Colors.Success } else { $Colors.Warning })

    if ($successCount -gt 0) {
        $avgLoadTime = ($script:WebsiteResults | Where-Object { $_.Success } | Measure-Object -Property LoadTime -Average).Average
        Write-Host "  Average Load Time: $([math]::Round($avgLoadTime, 2))ms" -ForegroundColor $Colors.Info
    }

    # Display speedtest results
    if (-not $SkipSpeedtest -and $null -ne $script:SpeedtestResult) {
        Write-Host "`n=== INTERNET SPEED TEST RESULTS ===" -ForegroundColor $Colors.Header
        Write-Host "  Server: $($script:SpeedtestResult.ServerName)" -ForegroundColor $Colors.Info
        Write-Host "  Location: $($script:SpeedtestResult.ServerLocation)" -ForegroundColor $Colors.Label
        Write-Host "  Ping: $($script:SpeedtestResult.Ping) ms" -ForegroundColor $Colors.Success
        Write-Host "  Download: $(Format-Speed $script:SpeedtestResult.DownloadSpeed)" -ForegroundColor $Colors.Success
        Write-Host "  Upload: $(Format-Speed $script:SpeedtestResult.UploadSpeed)" -ForegroundColor $Colors.Warning

        if ($script:SpeedtestResult.ResultUrl -notmatch "failed") {
            Write-Host "`n  Results: $($script:SpeedtestResult.ResultUrl)" -ForegroundColor $Colors.Label
        }
    }

    Write-Host ""
}
