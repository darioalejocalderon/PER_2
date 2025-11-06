<#
.SYNOPSIS
    ICMP Dashboard - Real-time ping monitoring to www.google.com
.DESCRIPTION
    Displays a real-time dashboard showing ping results and statistics including
    average response time and packet loss percentage.
.EXAMPLE
    .\ICMP-Dashboard.ps1
#>

param(
    [string]$Target = "www.google.com",
    [int]$PingInterval = 1000  # milliseconds
)

# Clear the console and hide cursor
Clear-Host
[Console]::CursorVisible = $false

# Initialize variables
$script:PingResults = @()
$script:TotalPings = 0
$script:SuccessfulPings = 0
$script:FailedPings = 0
$script:TotalResponseTime = 0
$script:MinResponseTime = [int]::MaxValue
$script:MaxResponseTime = 0
$script:LastPingTime = $null
$script:LastPingStatus = ""

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
    $width = [Console]::WindowWidth
    [Console]::SetCursorPosition(0, 0)
    Write-Host ("=" * $width) -ForegroundColor $Colors.Header -NoNewline
    [Console]::SetCursorPosition(0, 1)
    $title = " ICMP DASHBOARD - Monitoring: $Target "
    $padding = [math]::Max(0, ($width - $title.Length) / 2)
    Write-Host (" " * $padding + $title) -ForegroundColor $Colors.Header -NoNewline
    [Console]::SetCursorPosition(0, 2)
    Write-Host ("=" * $width) -ForegroundColor $Colors.Header -NoNewline
}

function Draw-StatisticsPanel {
    param([int]$StartRow)

    $panelWidth = 40
    $consoleWidth = [Console]::WindowWidth
    $startCol = $consoleWidth - $panelWidth - 2

    if ($startCol -lt 0) { $startCol = 0 }

    # Calculate statistics
    $avgTime = if ($script:SuccessfulPings -gt 0) {
        [math]::Round($script:TotalResponseTime / $script:SuccessfulPings, 2)
    } else {
        0
    }

    $lossPercent = if ($script:TotalPings -gt 0) {
        [math]::Round(($script:FailedPings / $script:TotalPings) * 100, 2)
    } else {
        0
    }

    $minTime = if ($script:MinResponseTime -eq [int]::MaxValue) { 0 } else { $script:MinResponseTime }

    # Draw panel border
    [Console]::SetCursorPosition($startCol, $StartRow)
    Write-Host ("╔" + ("═" * ($panelWidth - 2)) + "╗") -ForegroundColor $Colors.Header

    # Panel title
    $row = $StartRow + 1
    [Console]::SetCursorPosition($startCol, $row)
    Write-Host "║" -ForegroundColor $Colors.Header -NoNewline
    Write-Host (" STATISTICS".PadRight($panelWidth - 2)) -ForegroundColor $Colors.Info -NoNewline
    Write-Host "║" -ForegroundColor $Colors.Header

    # Separator
    $row++
    [Console]::SetCursorPosition($startCol, $row)
    Write-Host ("╠" + ("═" * ($panelWidth - 2)) + "╣") -ForegroundColor $Colors.Header

    # Statistics content
    $stats = @(
        @{ Label = "Total Pings"; Value = $script:TotalPings; Color = $Colors.Info },
        @{ Label = "Successful"; Value = $script:SuccessfulPings; Color = $Colors.Success },
        @{ Label = "Failed"; Value = $script:FailedPings; Color = if ($script:FailedPings -gt 0) { $Colors.Error } else { $Colors.Success } },
        @{ Label = ""; Value = ""; Color = $Colors.Info },
        @{ Label = "Packet Loss"; Value = "$lossPercent%"; Color = if ($lossPercent -gt 5) { $Colors.Error } elseif ($lossPercent -gt 0) { $Colors.Warning } else { $Colors.Success } },
        @{ Label = ""; Value = ""; Color = $Colors.Info },
        @{ Label = "Avg Time"; Value = "${avgTime}ms"; Color = if ($avgTime -gt 100) { $Colors.Warning } else { $Colors.Success } },
        @{ Label = "Min Time"; Value = "${minTime}ms"; Color = $Colors.Success },
        @{ Label = "Max Time"; Value = "$($script:MaxResponseTime)ms"; Color = if ($script:MaxResponseTime -gt 100) { $Colors.Warning } else { $Colors.Success } },
        @{ Label = ""; Value = ""; Color = $Colors.Info },
        @{ Label = "Last Update"; Value = ""; Color = $Colors.Info },
        @{ Label = ""; Value = $(Get-Date -Format "HH:mm:ss"); Color = $Colors.Label }
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
}

function Draw-PingResults {
    param([int]$StartRow, [int]$MaxRows)

    $consoleWidth = [Console]::WindowWidth
    $panelWidth = 40
    $resultsWidth = $consoleWidth - $panelWidth - 5

    # Results header
    [Console]::SetCursorPosition(0, $StartRow)
    Write-Host " PING RESULTS:" -ForegroundColor $Colors.Header

    # Draw recent results
    $startIndex = [math]::Max(0, $script:PingResults.Count - $MaxRows)
    $row = $StartRow + 1

    for ($i = $startIndex; $i -lt $script:PingResults.Count; $i++) {
        $result = $script:PingResults[$i]
        [Console]::SetCursorPosition(0, $row)

        $timestamp = $result.Timestamp.ToString("HH:mm:ss")

        if ($result.Success) {
            $message = " [$timestamp] Reply from $($result.Address): bytes=$($result.BufferSize) time=$($result.ResponseTime)ms TTL=$($result.Ttl)"
            if ($message.Length -gt $resultsWidth) {
                $message = $message.Substring(0, $resultsWidth - 3) + "..."
            }
            Write-Host $message.PadRight($resultsWidth) -ForegroundColor $Colors.Success
        } else {
            $message = " [$timestamp] Request timed out."
            Write-Host $message.PadRight($resultsWidth) -ForegroundColor $Colors.Error
        }

        $row++
    }

    # Clear any remaining lines
    for ($i = $row; $i -lt $StartRow + $MaxRows + 1; $i++) {
        [Console]::SetCursorPosition(0, $i)
        Write-Host (" " * $resultsWidth)
    }
}

function Perform-Ping {
    param([string]$Target)

    $script:TotalPings++

    try {
        $ping = New-Object System.Net.NetworkInformation.Ping
        $timeout = 5000
        $buffer = New-Object byte[] 32

        $reply = $ping.Send($Target, $timeout, $buffer)

        if ($reply.Status -eq 'Success') {
            $script:SuccessfulPings++
            $responseTime = $reply.RoundtripTime
            $script:TotalResponseTime += $responseTime

            if ($responseTime -lt $script:MinResponseTime) {
                $script:MinResponseTime = $responseTime
            }
            if ($responseTime -gt $script:MaxResponseTime) {
                $script:MaxResponseTime = $responseTime
            }

            $result = @{
                Success = $true
                Timestamp = Get-Date
                Address = $reply.Address.ToString()
                ResponseTime = $responseTime
                BufferSize = $reply.Buffer.Length
                Ttl = $reply.Options.Ttl
            }
        } else {
            $script:FailedPings++
            $result = @{
                Success = $false
                Timestamp = Get-Date
            }
        }

        $script:PingResults += $result

        # Keep only last 1000 results to prevent memory issues
        if ($script:PingResults.Count -gt 1000) {
            $script:PingResults = $script:PingResults[-1000..-1]
        }

    } catch {
        $script:FailedPings++
        $result = @{
            Success = $false
            Timestamp = Get-Date
        }
        $script:PingResults += $result
    }
}

function Get-LostPingSummary {
    # Group consecutive failed pings together
    $lostPingGroups = @()
    $currentGroup = $null

    foreach ($result in $script:PingResults) {
        if (-not $result.Success) {
            if ($null -eq $currentGroup) {
                # Start new group
                $currentGroup = @{
                    StartTime = $result.Timestamp
                    EndTime = $result.Timestamp
                    Count = 1
                }
            } else {
                # Continue existing group
                $currentGroup.EndTime = $result.Timestamp
                $currentGroup.Count++
            }
        } else {
            # Success ping - close current group if exists
            if ($null -ne $currentGroup) {
                $lostPingGroups += $currentGroup
                $currentGroup = $null
            }
        }
    }

    # Don't forget the last group if it exists
    if ($null -ne $currentGroup) {
        $lostPingGroups += $currentGroup
    }

    return $lostPingGroups
}

function Update-Dashboard {
    Draw-Header

    $headerRows = 3
    $statsStartRow = $headerRows + 1
    $resultsStartRow = $headerRows + 1
    $maxResultRows = [Console]::WindowHeight - $headerRows - 3

    Draw-StatisticsPanel -StartRow $statsStartRow
    Draw-PingResults -StartRow $resultsStartRow -MaxRows $maxResultRows

    # Instructions at bottom
    $bottomRow = [Console]::WindowHeight - 1
    [Console]::SetCursorPosition(0, $bottomRow)
    Write-Host " Press Ctrl+C to exit" -ForegroundColor $Colors.Label -NoNewline
}

# Main loop
try {
    Write-Host "Initializing ICMP Dashboard..." -ForegroundColor $Colors.Info
    Write-Host "Target: $Target" -ForegroundColor $Colors.Info
    Write-Host "Starting in 2 seconds..." -ForegroundColor $Colors.Info
    Start-Sleep -Seconds 2

    Clear-Host

    while ($true) {
        Perform-Ping -Target $Target
        Update-Dashboard
        Start-Sleep -Milliseconds $PingInterval
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
    Write-Host "`nFinal Statistics:" -ForegroundColor $Colors.Header
    Write-Host "  Total Pings: $script:TotalPings" -ForegroundColor $Colors.Info
    Write-Host "  Successful: $script:SuccessfulPings" -ForegroundColor $Colors.Success
    Write-Host "  Failed: $script:FailedPings" -ForegroundColor $(if ($script:FailedPings -gt 0) { $Colors.Error } else { $Colors.Success })

    if ($script:TotalPings -gt 0) {
        $finalLoss = [math]::Round(($script:FailedPings / $script:TotalPings) * 100, 2)
        Write-Host "  Packet Loss: $finalLoss%" -ForegroundColor $(if ($finalLoss -gt 0) { $Colors.Warning } else { $Colors.Success })
    }

    if ($script:SuccessfulPings -gt 0) {
        $finalAvg = [math]::Round($script:TotalResponseTime / $script:SuccessfulPings, 2)
        $finalMin = if ($script:MinResponseTime -eq [int]::MaxValue) { 0 } else { $script:MinResponseTime }
        Write-Host "  Avg Response Time: ${finalAvg}ms" -ForegroundColor $Colors.Success
        Write-Host "  Min Response Time: ${finalMin}ms" -ForegroundColor $Colors.Success
        Write-Host "  Max Response Time: $($script:MaxResponseTime)ms" -ForegroundColor $Colors.Success
    }

    # Display lost ping summary if there were any failures
    if ($script:FailedPings -gt 0) {
        $lostPingGroups = Get-LostPingSummary

        if ($lostPingGroups.Count -gt 0) {
            Write-Host "`nLost Ping Periods:" -ForegroundColor $Colors.Header

            foreach ($group in $lostPingGroups) {
                $startTime = $group.StartTime.ToString("yyyy-MM-dd HH:mm:ss")
                $endTime = $group.EndTime.ToString("HH:mm:ss")
                $count = $group.Count

                if ($count -eq 1) {
                    Write-Host "  1 lost ping at $startTime" -ForegroundColor $Colors.Error
                } else {
                    # Check if same date
                    if ($group.StartTime.Date -eq $group.EndTime.Date) {
                        Write-Host "  $count lost pings from $startTime to $endTime" -ForegroundColor $Colors.Error
                    } else {
                        $endTimeWithDate = $group.EndTime.ToString("yyyy-MM-dd HH:mm:ss")
                        Write-Host "  $count lost pings from $startTime to $endTimeWithDate" -ForegroundColor $Colors.Error
                    }
                }
            }
        }
    }

    Write-Host ""
}
