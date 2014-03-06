Function Set-DomainUserPassword {
    param (
        [String] $DomainName,
        [String] $Username,
        [String] $Password,
        [String] $AuthUsername,
        [String] $AuthPassword,
        [String] $AuthServer = $Env:ComputerName
    )
    begin {
        Show-InvocationInfo $MyInvocation
    }
    end {
        Show-InvocationInfo $MyInvocation -End
    }
    process {
        $script:Return = @()
        $null = & {
            trap {
                &$TrapHandler
            }

            if ($AuthUser -ne '' -and $AuthPassword -ne '') {
                $AuthCredential = New-Credential `
                    -Username $AuthUsername `
                    -Password $AuthPassword
                }

            if ($AuthCredential) {
                $adUser = Get-ADUser `
                    -Filter "SamAccountName -eq `"$Username`"" `
                    -Server $AuthServer `
                    -Credential $AuthCredential
            }
            else {
                $adUser = Get-ADUser `
                    -Filter "SamAccountName -eq `"$Username`"" `
                    -Server $AuthServer `
            }

            if ($adUser -eq $null) {
                throw "No user '$Username' found."
            }

            $securePassword = ConvertTo-SecureString `
                -String $Password `
                -AsPlainText `
                -Force

            if ($AuthCredential) {
                Set-ADAccountPassword `
                    -Identity $adUser `
                    -NewPassword $securePassword `
                    -Server $AuthServer `
                    -Reset `
                    -Credential $AuthCredential
            }
            else {
                Set-ADAccountPassword `
                    -Identity $adUser `
                    -NewPassword $securePassword `
                    -Server $AuthServer `
                    -Reset
            }
        }
        $script:Return
    }
}