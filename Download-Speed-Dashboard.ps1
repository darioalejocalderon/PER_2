<#
.SYNOPSIS
    Download Speed Dashboard - Tests website load times and download speed
.DESCRIPTION
    Displays a real-time dashboard that first tests website load times for specified URLs,
    then measures download speed by downloading a file for a specified duration.
.PARAMETER TestDuration
    Duration in seconds to test download speed (default: 30)
.PARAMETER DownloadURL
    URL of the file to download for speed testing
.PARAMETER Websites
    Array of websites to test load times (default: google.com, davivienda.com, nasa.gov, eltiempo.com, disneyplus.com)
.EXAMPLE
    .\Download-Speed-Dashboard.ps1
.EXAMPLE
    .\Download-Speed-Dashboard.ps1 -TestDuration 60 -Websites @("www.google.com", "www.github.com")
#>

param(
    [int]$TestDuration = 30,  # seconds
    [string]$DownloadURL = "https://cdn.avid.com/Sibelius/Sibelius_Sounds/7.5.1/2354131F/Sibelius_Sounds_Win.zip",
    [string[]]$Websites = @(
        "www.google.com",
        "www.davivienda.com",
        "www.nasa.gov",
        "www.eltiempo.com",
        "www.disneyplus.com"
    )
)

# Clear the console and hide cursor
Clear-Host
[Console]::CursorVisible = $false

# Initialize variables
$script:WebsiteResults = @()
$script:DownloadResults = @()
$script:TotalBytesDownloaded = 0
$script:DownloadStartTime = $null
$script:DownloadEndTime = $null
$script:CurrentPhase = "website-test"  # website-test or download-test
$script:IsDownloading = $false
$script:CurrentSpeed = 0
$script:AverageSpeed = 0
$script:PeakSpeed = 0
$script:lastBytes = 0
$script:lastTime = Get-Date

# Color scheme
$Colors = @{
    Header = 'Cyan'
    Success = 'Green'
    Warning = 'Yellow'
    Error = 'Red'
    Info = 'White'
    Label = 'Gray'
}

function Draw-Header {
    param([string]$Phase)

    $width = [Console]::WindowWidth
    [Console]::SetCursorPosition(0, 0)
    Write-Host ("=" * $width) -ForegroundColor $Colors.Header -NoNewline
    [Console]::SetCursorPosition(0, 1)

    if ($Phase -eq "website-test") {
        $title = " DOWNLOAD SPEED DASHBOARD - Website Load Time Testing "
    } else {
        $title = " DOWNLOAD SPEED DASHBOARD - Download Speed Testing "
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
    param([double]$BytesPerSecond)

    if ($BytesPerSecond -lt 1KB) {
        return "$([math]::Round($BytesPerSecond, 2)) B/s"
    } elseif ($BytesPerSecond -lt 1MB) {
        return "$([math]::Round($BytesPerSecond / 1KB, 2)) KB/s"
    } elseif ($BytesPerSecond -lt 1GB) {
        return "$([math]::Round($BytesPerSecond / 1MB, 2)) MB/s"
    } else {
        return "$([math]::Round($BytesPerSecond / 1GB, 2)) GB/s"
    }
}

function Format-Size {
    param([long]$Bytes)

    if ($Bytes -lt 1KB) {
        return "$Bytes B"
    } elseif ($Bytes -lt 1MB) {
        return "$([math]::Round($Bytes / 1KB, 2)) KB"
    } elseif ($Bytes -lt 1GB) {
        return "$([math]::Round($Bytes / 1MB, 2)) MB"
    } else {
        return "$([math]::Round($Bytes / 1GB, 2)) GB"
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

            $message = " [$timestamp] $($result.Website.PadRight(30)) - ${$result.LoadTime}ms (HTTP $($result.StatusCode))"
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

function Draw-DownloadStatistics {
    param([int]$StartRow)

    $panelWidth = 50
    $consoleWidth = [Console]::WindowWidth
    $startCol = [math]::Max(0, ($consoleWidth - $panelWidth) / 2)

    # Calculate statistics
    $elapsedSeconds = if ($script:DownloadStartTime) {
        $endTime = if ($script:DownloadEndTime) { $script:DownloadEndTime } else { Get-Date }
        ($endTime - $script:DownloadStartTime).TotalSeconds
    } else {
        0
    }

    $avgSpeed = if ($elapsedSeconds -gt 0) {
        $script:TotalBytesDownloaded / $elapsedSeconds
    } else {
        0
    }

    # Draw panel border
    [Console]::SetCursorPosition($startCol, $StartRow)
    Write-Host ("╔" + ("═" * ($panelWidth - 2)) + "╗") -ForegroundColor $Colors.Header

    # Panel title
    $row = $StartRow + 1
    [Console]::SetCursorPosition($startCol, $row)
    Write-Host "║" -ForegroundColor $Colors.Header -NoNewline
    Write-Host (" DOWNLOAD STATISTICS".PadRight($panelWidth - 2)) -ForegroundColor $Colors.Info -NoNewline
    Write-Host "║" -ForegroundColor $Colors.Header

    # Separator
    $row++
    [Console]::SetCursorPosition($startCol, $row)
    Write-Host ("╠" + ("═" * ($panelWidth - 2)) + "╣") -ForegroundColor $Colors.Header

    # Statistics content
    $stats = @(
        @{ Label = "Total Downloaded"; Value = Format-Size $script:TotalBytesDownloaded; Color = $Colors.Info },
        @{ Label = "Elapsed Time"; Value = "$([math]::Round($elapsedSeconds, 1))s"; Color = $Colors.Info },
        @{ Label = ""; Value = ""; Color = $Colors.Info },
        @{ Label = "Current Speed"; Value = Format-Speed $script:CurrentSpeed; Color = $Colors.Success },
        @{ Label = "Average Speed"; Value = Format-Speed $avgSpeed; Color = $Colors.Info },
        @{ Label = "Peak Speed"; Value = Format-Speed $script:PeakSpeed; Color = $Colors.Warning },
        @{ Label = ""; Value = ""; Color = $Colors.Info },
        @{ Label = "Test Duration"; Value = "${TestDuration}s"; Color = $Colors.Label },
        @{ Label = "Time Remaining"; Value = "$([math]::Max(0, [math]::Round($TestDuration - $elapsedSeconds, 1)))s"; Color = $Colors.Label }
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

    # Bottom border
    $row++
    [Console]::SetCursorPosition($startCol, $row)
    Write-Host ("╚" + ("═" * ($panelWidth - 2)) + "╝") -ForegroundColor $Colors.Header

    return $row
}

function Draw-DownloadProgress {
    param([int]$StartRow)

    $consoleWidth = [Console]::WindowWidth
    $barWidth = [math]::Min(60, $consoleWidth - 10)
    $startCol = [math]::Max(0, ($consoleWidth - $barWidth - 8) / 2)

    $elapsedSeconds = if ($script:DownloadStartTime) {
        $endTime = if ($script:DownloadEndTime) { $script:DownloadEndTime } else { Get-Date }
        ($endTime - $script:DownloadStartTime).TotalSeconds
    } else {
        0
    }

    $progress = [math]::Min(100, ($elapsedSeconds / $TestDuration) * 100)
    $filledWidth = [math]::Floor(($progress / 100) * $barWidth)
    $emptyWidth = $barWidth - $filledWidth

    [Console]::SetCursorPosition($startCol, $StartRow)
    Write-Host "Progress: [" -ForegroundColor $Colors.Info -NoNewline
    Write-Host ("█" * $filledWidth) -ForegroundColor $Colors.Success -NoNewline
    Write-Host ("░" * $emptyWidth) -ForegroundColor $Colors.Label -NoNewline
    Write-Host "] $([math]::Round($progress, 1))%" -ForegroundColor $Colors.Info
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

function Update-DownloadTestDashboard {
    Draw-Header -Phase "download-test"

    $headerRows = 4
    $statsStartRow = $headerRows + 2

    $nextRow = Draw-DownloadStatistics -StartRow $statsStartRow

    Draw-DownloadProgress -StartRow ($nextRow + 2)

    # URL info
    $urlRow = $nextRow + 5
    [Console]::SetCursorPosition(0, $urlRow)
    $consoleWidth = [Console]::WindowWidth
    $urlLabel = " Downloading from: "
    $maxUrlLength = $consoleWidth - $urlLabel.Length - 2
    $displayUrl = if ($DownloadURL.Length -gt $maxUrlLength) {
        $DownloadURL.Substring(0, $maxUrlLength - 3) + "..."
    } else {
        $DownloadURL
    }
    Write-Host ($urlLabel + $displayUrl).PadRight($consoleWidth) -ForegroundColor $Colors.Label

    # Clear remaining area
    for ($i = $urlRow + 1; $i -lt [Console]::WindowHeight - 2; $i++) {
        [Console]::SetCursorPosition(0, $i)
        Write-Host (" " * $consoleWidth)
    }

    # Instructions at bottom
    $bottomRow = [Console]::WindowHeight - 1
    [Console]::SetCursorPosition(0, $bottomRow)
    Write-Host " Press Ctrl+C to exit" -ForegroundColor $Colors.Label -NoNewline
}

function Start-DownloadSpeedTest {
    $script:DownloadStartTime = Get-Date
    $script:IsDownloading = $true
    $script:lastBytes = 0
    $script:lastTime = Get-Date

    # Create a temporary file
    $tempFile = [System.IO.Path]::GetTempFileName()

    try {
        # Enable TLS 1.2 for HTTPS downloads
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

        # Create web client for download
        $webClient = New-Object System.Net.WebClient

        # Register event for download progress
        $progressHandler = Register-ObjectEvent -InputObject $webClient -EventName DownloadProgressChanged -Action {
            $script:TotalBytesDownloaded = $EventArgs.BytesReceived

            # Calculate current speed
            $now = Get-Date
            $timeDiff = ($now - $script:lastTime).TotalSeconds

            if ($timeDiff -ge 0.5) {  # Update speed every 0.5 seconds
                $bytesDiff = $script:TotalBytesDownloaded - $script:lastBytes
                $script:CurrentSpeed = $bytesDiff / $timeDiff

                if ($script:CurrentSpeed -gt $script:PeakSpeed) {
                    $script:PeakSpeed = $script:CurrentSpeed
                }

                $script:lastBytes = $script:TotalBytesDownloaded
                $script:lastTime = $now
            }
        }

        # Start async download
        $webClient.DownloadFileAsync($DownloadURL, $tempFile)

        # Wait a moment for download to start
        Start-Sleep -Milliseconds 500

        # Monitor download for specified duration
        $startTime = Get-Date
        while (((Get-Date) - $startTime).TotalSeconds -lt $TestDuration -and $script:IsDownloading) {
            Update-DownloadTestDashboard
            Start-Sleep -Milliseconds 500

            # Check if download completed
            if (-not $webClient.IsBusy) {
                break
            }
        }

        # Stop download
        if ($webClient.IsBusy) {
            $webClient.CancelAsync()
            Start-Sleep -Milliseconds 500
        }

        $script:DownloadEndTime = Get-Date

        # Unregister event
        if ($progressHandler) {
            Unregister-Event -SourceIdentifier $progressHandler.Name -ErrorAction SilentlyContinue
            Remove-Job -Id $progressHandler.Id -Force -ErrorAction SilentlyContinue
        }

        # Cleanup
        $webClient.Dispose()

    } catch {
        Write-Host "`nDownload Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:DownloadEndTime = Get-Date
    } finally {
        # Remove temp file
        if (Test-Path $tempFile) {
            Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
        }

        $script:IsDownloading = $false
    }
}

# Main execution
try {
    Write-Host "Initializing Download Speed Dashboard..." -ForegroundColor $Colors.Info
    Write-Host "Phase 1: Testing website load times..." -ForegroundColor $Colors.Info
    Start-Sleep -Seconds 2

    Clear-Host

    # Phase 1: Website Load Time Testing
    $script:CurrentPhase = "website-test"

    foreach ($website in $Websites) {
        Write-Host "Testing $website..." -ForegroundColor $Colors.Info
        $result = Test-WebsiteLoadTime -Website $website
        $script:WebsiteResults += $result
        Update-WebsiteTestDashboard
        Start-Sleep -Milliseconds 500
    }

    # Show website results for a moment
    Start-Sleep -Seconds 3

    # Phase 2: Download Speed Testing
    Write-Host "`nStarting download speed test..." -ForegroundColor $Colors.Info
    Write-Host "Duration: $TestDuration seconds" -ForegroundColor $Colors.Info
    Write-Host "URL: $DownloadURL" -ForegroundColor $Colors.Info
    Start-Sleep -Seconds 2

    Clear-Host
    $script:CurrentPhase = "download-test"

    Start-DownloadSpeedTest

    # Final update
    Update-DownloadTestDashboard

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

    # Display download statistics
    if ($script:TotalBytesDownloaded -gt 0) {
        Write-Host "`n=== DOWNLOAD SPEED RESULTS ===" -ForegroundColor $Colors.Header
        Write-Host "  Total Downloaded: $(Format-Size $script:TotalBytesDownloaded)" -ForegroundColor $Colors.Info

        $totalTime = if ($script:DownloadStartTime -and $script:DownloadEndTime) {
            ($script:DownloadEndTime - $script:DownloadStartTime).TotalSeconds
        } else {
            0
        }

        if ($totalTime -gt 0) {
            $avgSpeed = $script:TotalBytesDownloaded / $totalTime
            Write-Host "  Average Speed: $(Format-Speed $avgSpeed)" -ForegroundColor $Colors.Success
            Write-Host "  Peak Speed: $(Format-Speed $script:PeakSpeed)" -ForegroundColor $Colors.Warning
            Write-Host "  Test Duration: $([math]::Round($totalTime, 2))s" -ForegroundColor $Colors.Info
        }
    }

    Write-Host ""
}
