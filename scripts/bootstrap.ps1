$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

docker compose up -d
do {
    docker exec pg_jd_demo pg_isready -U jd_user -d jd_library *> $null
    if ($LASTEXITCODE -ne 0) { Start-Sleep -Seconds 2 }
} while ($LASTEXITCODE -ne 0)

$migrationPrefixes = "000", "010", "020", "030", "040", "050", "060", "070", "080", "090", "100", "110", "120", "900", "999"
$files = foreach ($prefix in $migrationPrefixes) {
    Get-ChildItem "infra/migrations/$prefix`_*.sql"
}
$sql = ($files | ForEach-Object { Get-Content -Raw $_.FullName }) -join "`n"
$sql | docker exec -i pg_jd_demo psql -v ON_ERROR_STOP=1 -v schema=smarthire -U jd_user -d jd_library

& .\.venv\Scripts\python.exe scripts\seed_users.py
Write-Host "Infrastructure and database are ready."
