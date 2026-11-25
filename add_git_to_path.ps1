$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($currentPath -notlike '*C:\Program Files\Git\cmd*') {
    [Environment]::SetEnvironmentVariable('Path', $currentPath + ';C:\Program Files\Git\cmd', 'User')
    Write-Host 'Git successfully added to User PATH!'
} else {
    Write-Host 'Git is already in User PATH.'
}

