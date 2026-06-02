# src/core/rollback/RollbackManager.psm1

class RollbackManager {
    hidden static [System.Collections.Stack] $Operations = [System.Collections.Stack]::new()

    static [void] RegisterOperation([scriptblock]$UndoAction) {
        [RollbackManager]::$Operations.Push($UndoAction)
    }

    static [void] RollbackAll() {
        Write-Log "Starting rollback of $($Operations.Count) operations..." -Level "WARN"
        while ([RollbackManager]::$Operations.Count -gt 0) {
            $undo = [RollbackManager]::$Operations.Pop()
            try {
                & $undo
                Write-Log "Rolled back an operation" -Level "INFO"
            } catch {
                Write-Log "Failed to rollback: $_" -Level "ERROR"
            }
        }
    }
}

Export-ModuleMember -Class RollbackManager
