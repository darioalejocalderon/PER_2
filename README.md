# ICMP Dashboard

Real-time ICMP (ping) monitoring dashboard for Windows with live statistics and packet loss tracking.

## Features

- 🔄 Real-time ping monitoring
- 📊 Live statistics panel showing:
  - Total pings sent
  - Successful and failed pings
  - Packet loss percentage
  - Average, minimum, and maximum response times
- 🎨 Color-coded output for easy status identification
- ⏱️ Timestamp for each ping result
- 📈 Continuous monitoring until stopped
- 📋 **Lost ping tracking**: After stopping (Ctrl+C), displays a detailed summary of lost ping periods with timestamps
  - Groups consecutive lost pings together (e.g., "5 lost pings from 2025-11-06 15:06:09 to 15:06:13")
  - Shows individual timestamps for isolated packet losses

## Versions

### PowerShell Version (Recommended)

The PowerShell version (`ICMP-Dashboard.ps1`) provides a rich, interactive dashboard with:
- Split-screen layout with statistics panel
- Color-coded results (green for success, red for failures, yellow for warnings)
- Professional UI with borders and formatting
- Scrolling ping results
- Configurable target and ping interval

### CMD/Batch Version

The batch version (`ICMP-Dashboard.bat`) provides a simpler alternative that:
- Works on any Windows system without PowerShell
- Updates statistics in real-time
- Shows basic statistics and ping results
- Simpler interface but full functionality

## Usage

### PowerShell Version

**Basic usage (ping www.google.com):**
```powershell
.\ICMP-Dashboard.ps1
```

**Ping a custom target:**
```powershell
.\ICMP-Dashboard.ps1 -Target "8.8.8.8"
```

**Custom target with custom interval (in milliseconds):**
```powershell
.\ICMP-Dashboard.ps1 -Target "cloudflare.com" -PingInterval 2000
```

**Note:** You may need to adjust the PowerShell execution policy to run the script:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### CMD/Batch Version

**Basic usage:**
```cmd
ICMP-Dashboard.bat
```

To change the target, edit the `TARGET` variable at the beginning of the batch file.

## Dashboard Layout

### PowerShell Version Layout

```
================================================================================
                 ICMP DASHBOARD - Monitoring: www.google.com
================================================================================

 PING RESULTS:                          ╔══════════════════════════════════════╗
                                        ║ STATISTICS                           ║
 [14:30:45] Reply from 142.250...      ╠══════════════════════════════════════╣
 [14:30:46] Reply from 142.250...      ║ Total Pings: 150                     ║
 [14:30:47] Reply from 142.250...      ║ Successful: 148                      ║
 [14:30:48] Request timed out.         ║ Failed: 2                            ║
 [14:30:49] Reply from 142.250...      ║                                      ║
                                        ║ Packet Loss: 1.33%                   ║
                                        ║                                      ║
                                        ║ Avg Time: 23.45ms                    ║
                                        ║ Min Time: 18ms                       ║
                                        ║ Max Time: 156ms                      ║
                                        ║                                      ║
                                        ║ Last Update:                         ║
                                        ║  14:30:49                            ║
                                        ╚══════════════════════════════════════╝

 Press Ctrl+C to exit
```

## Statistics Explained

- **Total Pings**: Number of ICMP echo requests sent
- **Successful**: Number of replies received
- **Failed**: Number of timeouts or failed requests
- **Packet Loss**: Percentage of failed pings (color-coded: green=0%, yellow>0%, red>5%)
- **Avg Time**: Average round-trip time for successful pings
- **Min Time**: Fastest response time recorded
- **Max Time**: Slowest response time recorded

## Color Coding (PowerShell Version)

- 🟢 **Green**: Successful pings, good response times (<100ms)
- 🟡 **Yellow**: Warning state (response time >100ms, or low packet loss)
- 🔴 **Red**: Failed pings, high packet loss (>5%)
- ⚪ **Cyan/White**: Headers and informational text
- ⚫ **Gray**: Labels and secondary information

## Requirements

### PowerShell Version
- Windows PowerShell 5.1 or later (pre-installed on Windows 10/11)
- Or PowerShell Core 7+ (cross-platform)

### Batch Version
- Any Windows version with cmd.exe

## Stopping the Dashboard

Press **Ctrl+C** to stop the monitoring. The dashboard will display final statistics before exiting, including a summary of any lost pings.

### Example Final Statistics Output (PowerShell)

```
Dashboard stopped.

Final Statistics:
  Total Pings: 150
  Successful: 145
  Failed: 5
  Packet Loss: 3.33%
  Avg Response Time: 23.45ms
  Min Response Time: 18ms
  Max Response Time: 156ms

Lost Ping Periods:
  2 lost pings from 2025-11-06 15:06:09 to 15:06:10
  1 lost ping at 2025-11-06 15:08:45
  2 lost pings from 2025-11-06 15:12:30 to 15:12:31
```

This feature helps you identify exactly when connection issues occurred, making it easier to:
- Correlate network issues with specific events
- Identify patterns in packet loss
- Document network outages with precise timestamps
- Troubleshoot intermittent connectivity problems

## Troubleshooting

### PowerShell: "Execution of scripts is disabled on this system"

Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Firewall Issues

Ensure ICMP (ping) is not blocked by your firewall. The dashboard requires outbound ICMP echo request packets.

### Target Unreachable

If the target is consistently unreachable:
1. Verify internet connectivity
2. Try a different target (e.g., `8.8.8.8`, `1.1.1.1`)
3. Check if ICMP is blocked by network policy

## Use Cases

- 🌐 **Network troubleshooting**: Monitor connection stability
- 📡 **ISP monitoring**: Track packet loss and latency to detect issues
- 🔧 **Diagnostic tool**: Real-time feedback during network configuration
- 📊 **Performance testing**: Measure network performance over time
- 🏢 **Server monitoring**: Keep track of server availability

## Examples

### Monitor Google DNS
```powershell
.\ICMP-Dashboard.ps1 -Target "8.8.8.8"
```

### Monitor with slower interval (every 5 seconds)
```powershell
.\ICMP-Dashboard.ps1 -Target "cloudflare.com" -PingInterval 5000
```

### Monitor local gateway
```powershell
.\ICMP-Dashboard.ps1 -Target "192.168.1.1"
```

## License

This project is open source and available for personal and commercial use.

---

# Music Steganography and Cryptography System

A comprehensive Python system for hiding secret messages in sheet music using MusicXML format. Combines steganography with musical cipher encryption.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate example files
python examples/generate_examples.py

# Encode a message
python -m music_steg.cli encode -i examples/twinkle_twinkle.musicxml -m "Secret!" -o encoded.musicxml

# Decode a message
python -m music_steg.cli decode -i encoded.musicxml --try-all

# Run comprehensive demo
python demo.py
```

## Features

- **Steganography**: Hide messages using dynamic markings, stem directions, articulations, and ornaments
- **Musical Cipher**: Use music as an encryption key
- **Visualization**: Compare before/after sheet music
- **Analysis**: Capacity estimation and technique detection

## Documentation

- 📖 **Full Documentation**: See [MUSIC_STEG_README.md](MUSIC_STEG_README.md)
- 📚 **User Guide**: See [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- 🎬 **Demo**: Run `python demo.py` for a complete demonstration

## Example Usage

```bash
# Analyze capacity
python -m music_steg.cli analyze -i examples/longer_piece.musicxml

# Encode with specific techniques
python -m music_steg.cli encode -i input.musicxml -m "Message" -o output.musicxml -t dynamics,stem

# Encrypt with musical cipher
python -m music_steg.cli cipher -k examples/jazz_key.musicxml -m "Secret" --mode encrypt
```

---

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
