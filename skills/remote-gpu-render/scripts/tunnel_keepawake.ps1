# PC side (Windows): keep the machine awake and the reverse SSH tunnel up. UNTESTED TEMPLATE.
# usage (PowerShell, run in its own window or as a scheduled task at logon):
#   powershell -ExecutionPolicy Bypass -File tunnel_keepawake.ps1 -Server user@server.example -Port 52122 -Key $env:USERPROFILE\.ssh\id_tunnel
param([Parameter(Mandatory)][string]$Server, [int]$Port = 52122, [Parameter(Mandatory)][string]$Key)

# ES_CONTINUOUS | ES_SYSTEM_REQUIRED: no sleep while this script runs (display may still turn off)
Add-Type -Namespace W -Name P -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);'
[W.P]::SetThreadExecutionState(0x80000001) | Out-Null

while ($true) {
  $t = Get-Date -Format s
  Write-Host "$t tunnel up -> $Server (remote port $Port)"
  # ExitOnForwardFailure: die (and get restarted) if the server-side port is taken instead of hanging half-open
  ssh -N -i $Key -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 `
      -R "${Port}:localhost:22" $Server
  Write-Host "$(Get-Date -Format s) tunnel dropped (exit $LASTEXITCODE); retry in 15 s"
  Start-Sleep -Seconds 15
}
