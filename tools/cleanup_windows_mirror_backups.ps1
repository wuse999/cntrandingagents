[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "Medium")]
param(
    [string]$BackupRoot,
    [ValidateRange(1, 1000)]
    [int]$RetainCount = 3,
    [string]$Prefix = "windows-mirror-align-"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent $repoRoot

if (-not $BackupRoot) {
    $BackupRoot = Join-Path $workspaceRoot "_bootstrap_backup"
}

if (-not (Test-Path -LiteralPath $BackupRoot -PathType Container)) {
    Write-Output "Backup root not found: $BackupRoot"
    exit 0
}

$candidateDirs = @(Get-ChildItem -LiteralPath $BackupRoot -Directory | Where-Object {
    $_.Name -like "$Prefix*"
})

$managedBackups = @()
$skippedBackups = @()

foreach ($dir in $candidateDirs) {
    $snapshotFile = Join-Path $dir.FullName "mirror-snapshot.tgz"
    if (Test-Path -LiteralPath $snapshotFile -PathType Leaf) {
        $managedBackups += $dir
    }
    else {
        $skippedBackups += $dir
    }
}

$managedBackups = @($managedBackups | Sort-Object LastWriteTimeUtc, Name -Descending)

Write-Output "Backup root: $BackupRoot"
Write-Output "Retention count: $RetainCount"
Write-Output "Managed complete backups: $($managedBackups.Count)"
Write-Output "Skipped incomplete backups: $($skippedBackups.Count)"

foreach ($dir in $skippedBackups) {
    Write-Output "SKIP   $($dir.Name)"
}

if ($managedBackups.Count -eq 0) {
    Write-Output "No complete backups matched the retention policy."
    exit 0
}

$keepBackups = @($managedBackups | Select-Object -First $RetainCount)
$removeBackups = @($managedBackups | Select-Object -Skip $RetainCount)

foreach ($dir in $keepBackups) {
    Write-Output "KEEP   $($dir.Name)"
}

if ($removeBackups.Count -eq 0) {
    Write-Output "Nothing to remove."
    exit 0
}

foreach ($dir in $removeBackups) {
    if ($PSCmdlet.ShouldProcess($dir.FullName, "Remove old Windows mirror backup")) {
        Remove-Item -LiteralPath $dir.FullName -Recurse -Force
        Write-Output "REMOVE $($dir.Name)"
    }
}

$remainingManaged = @(Get-ChildItem -LiteralPath $BackupRoot -Directory | Where-Object {
    $_.Name -like "$Prefix*" -and (Test-Path -LiteralPath (Join-Path $_.FullName "mirror-snapshot.tgz") -PathType Leaf)
})

Write-Output "Remaining managed backups: $($remainingManaged.Count)"
