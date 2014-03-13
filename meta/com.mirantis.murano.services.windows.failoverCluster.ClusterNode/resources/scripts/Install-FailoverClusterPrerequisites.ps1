function Install-FailoverClusterPrerequisites {
    begin {
        Show-InvocationInfo $MyInvocation
    }
    end {
        Show-InvocationInfo $MyInvocation -End
    }
    process {
        trap {
            &$TrapHandler
        }

        Add-WindowsFeature Failover-Clustering, RSAT-Clustering-PowerShell
    }
}