# Windows PowerShell Script to generate 1 MB cryptographic random data
# CryptoLabX - Lab 7: OS RNG Evaluation (Group 07)
# Uses the .NET System.Security.Cryptography.RandomNumberGenerator (Windows CNG under the hood)

$outputFile = Join-Path $PSScriptRoot "..\data\windows_cng_1mb.bin"
$sizeInBytes = 1048576 # 1 MB

Write-Host "[*] Generating $sizeInBytes bytes of cryptographically secure random data using Windows CNG/.NET..."

$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$bytes = New-Object byte[] $sizeInBytes
$rng.GetBytes($bytes)

[System.IO.File]::WriteAllBytes($outputFile, $bytes)

Write-Host "[+] Successfully written 1 MB to: $outputFile"
