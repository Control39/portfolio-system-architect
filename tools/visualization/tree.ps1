function tree {
    param(
        [string]$Path = ".",
        [int]$Levels = 2,
        [switch]$ShowFiles,
        [switch]$IncludeHidden,
        [switch]$Force,
        [switch]$Json,
        [switch]$GitStatus,
        [switch]$Size,
        [switch]$Icon,
        [string]$Filter = "*",
        [switch]$Modified
    )

    $resolvedPath = Resolve-Path $Path -ErrorAction Stop
    
    function Get-DirSize {
        param([string]$DirPath)
        try {
            (Get-ChildItem $DirPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        } catch { 0 }
    }
    
    function Get-GitStatus {
        param([string]$DirPath)
        pushd $DirPath
        $status = git status --porcelain 2>&1
        popd
        if ($LASTEXITCODE -ne 0) {
            return "⚠️ Error"
        }
        if ($status) { 
            if ($status -match "^ \?") { "🆕 Untracked" } 
            else { "⚡ Dirty" }
        } else { "✅ Clean" }
    }
    
    function Display-Tree {
        param($currentPath, $level, $prefix, $treeData)
        
        if (($level -gt $Levels) -and -not $Force) { return $treeData }
        
        $filterHash = @{ }
        if (-not $IncludeHidden) { $filterHash["Force"] = $false }
        $items = Get-ChildItem $currentPath $Filter @filterHash | Where-Object Name -like $Filter
        
        $dirs = $items | Where-Object PSIsContainer
        if ($ShowFiles) { 
            $allItems = $items | Sort-Object { -not $_.PSIsContainer }, Name 
        } else { 
            $allItems = $dirs | Sort-Object Name 
        }
        
        $node = @{
            name = Split-Path $currentPath -Leaf
            path = $currentPath
            type = "directory"
            children = @()
            size = if ($Size) { "$(Format-Bytes (Get-DirSize $currentPath))" } else { $null }
            git = if ($GitStatus) { Get-GitStatus $currentPath } else { $null }
            modified = if ($Modified) { 
                $latestFile = Get-ChildItem $currentPath -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
                if ($latestFile) { $latestFile.LastWriteTime } else { $null }
            } else { $null }
        }
        
        for ($i = 0; $i -lt $allItems.Count; $i++) {
            $item = $allItems[$i]
            $isLast = ($i -eq $allItems.Count - 1)
            $marker = if ($isLast) { "└── " } else { "├── " }
            $newPrefix = $prefix + $(if ($isLast) { "    " } else { "│   " })
            
            $itemIcon = if ($Icon) { if ($item.PSIsContainer) { "📁" } else { "📄" } } else { "" }
            $itemSize = if ($Size -and -not $item.PSIsContainer) { " ($(" + (Format-Bytes $item.Length) + ")" } else { "" }
            $itemGit = if ($GitStatus -and $item.PSIsContainer) { " [" + (Get-GitStatus $item.FullName) + "]" } else { "" }
            $itemMod = if ($Modified) { " ($($item.LastWriteTime.ToString('yyyy-MM-dd')))" } else { "" }
            
            $displayName = "$itemIcon$($item.Name)$itemSize$itemGit$itemMod"
            
            if (-not $Json) {
                $color = if ($item.PSIsContainer) { "Cyan" } else { "Gray" }
                Write-Host "$prefix$marker$displayName" -ForegroundColor $color
            }
            
            $childNode = @{
                name = $item.Name
                path = $item.FullName
                type = if ($item.PSIsContainer) { "directory" } else { "file" }
                size = if ($Size) { $item.Length } else { $null }
                git = if ($GitStatus -and $item.PSIsContainer) { Get-GitStatus $item.FullName } else { $null }
                modified = if ($Modified) { $item.LastWriteTime } else { $null }
            }
            
            if ($item.PSIsContainer) {
            $childNode.children = Display-Tree $item.FullName ($level + 1) $newPrefix $childNode.children
            }
            
            $node.children += $childNode
        }
        
        return $node.children
    }
    
    function Format-Bytes {
        param([long]$bytes)
        if ($bytes -lt 1KB) { "$bytes B" }
        elseif ($bytes -lt 1MB) { "{0:N1} KB" -f ($bytes/1KB) }
        else { "{0:N1} MB" -f ($bytes/1MB) }
    }
    
    $rootData = @{
        root = $resolvedPath
        children = Display-Tree $resolvedPath 0 "" @()
    }
    
    if ($Json) {
        $rootData | ConvertTo-Json -Depth 10
    } else {
        Write-Host "$resolvedPath" -ForegroundColor Green
        Display-Tree $resolvedPath 0 "" @()
        Write-Host "`nИспользование: tree [-Json] [-GitStatus] [-Size] [-Icon] [-Filter '*.ps1'] [-Modified]" -ForegroundColor Yellow
    }
}

# Автозагрузка если dot-sourced
# if ($MyInvocation.Line) { Export-ModuleMember tree }


