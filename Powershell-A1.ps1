param(
    [string]$csvFolderPath= "\\Admin-Server\logging"
)

# Settings
$domain = "M-zukunftsmotor.local"
$baseOU = "OU=M-zukunftsmotor,DC=M-zukunftsmotor,DC=local"

# Find the CSV file (e.g., aduser_export*.csv)
$csvFile = Get-ChildItem -Path $csvFolderPath -Filter *.csv  
if (-not $csvFile) {
    Write-Host "Keine gültige CSV-Datei gefunden im Pfad: $csvFolderPath"
    exit
}

# Read the CSV file
$users = Import-Csv -Path $csvFile.FullName -Delimiter ','

foreach ($user in $users) {
    $username = "$($user.Vorname.Substring(0,1).ToLower())$($user.Nachname.ToLower())"
    $email = "$($user.Vorname.ToLower()).$($user.Nachname.ToLower())@$domain"
    $ouName = $user.Kurs
    $ouPath = "OU=$ouName,$baseOU"
    $userPrincipalName = "$username@$domain"

    # Check for an existing user
    $existingUser = Get-ADUser -Filter { UserPrincipalName -eq $userPrincipalName } -ErrorAction SilentlyContinue

    # Handle user actions based on the Status_code
    switch ($user.Status_code) {
        1 {
            if (-not $existingUser) {
                # Create new user (active)
                New-ADUser -Name "$($user.Vorname) $($user.Nachname)" `
                    -GivenName $user.Vorname `
                    -Surname $user.Nachname `
                    -UserPrincipalName $userPrincipalName `
                    -SamAccountName $username `
                    -EmailAddress $email `
                    -Department $user.Abteilung `
                    -StreetAddress $user.Strasse `
                    -PostalCode $user.PLZ `
                    -City $user.Ort `
                    -Path $ouPath `
                    -AccountPassword (ConvertTo-SecureString "Passw0rd!" -AsPlainText -Force) `
                    -Enabled $true
                Write-Host "Neuer Benutzer erstellt: $userPrincipalName"
            } else {
                # Update existing user + enable
                Set-ADUser $existingUser `
                    -Department $user.Abteilung `
                    -StreetAddress $user.Strasse `
                    -PostalCode $user.PLZ `
                    -City $user.Ort `
                    -EmailAddress $email
                Enable-ADAccount $existingUser
                Write-Host "Benutzer aktualisiert & aktiviert: $userPrincipalName"
            }
        }
        2 {
            if (-not $existingUser) {
                # Create inactive user
                New-ADUser -Name "$($user.Vorname) $($user.Nachname)" `
                    -GivenName $user.Vorname `
                    -Surname $user.Nachname `
                    -UserPrincipalName $userPrincipalName `
                    -SamAccountName $username `
                    -EmailAddress $email `
                    -Department $user.Abteilung `
                    -StreetAddress $user.Strasse `
                    -PostalCode $user.PLZ `
                    -City $user.Ort `
                    -Path $ouPath `
                    -AccountPassword (ConvertTo-SecureString "Passw0rd!" -AsPlainText -Force) `
                    -Enabled $false
                Write-Host "Inaktiver Benutzer erstellt: $userPrincipalName"
            } else {
                # Update existing user + disable
                Set-ADUser $existingUser `
                    -Department $user.Abteilung `
                    -StreetAddress $user.Strasse `
                    -PostalCode $user.PLZ `
                    -City $user.Ort `
                    -EmailAddress $email
                Disable-ADAccount $existingUser
                Write-Host "Benutzer deaktiviert: $userPrincipalName"
            }
        }
        3 {
            if ($existingUser) {
                # Remove user
                Remove-ADUser $existingUser -Confirm:$false
                Write-Host "Benutzer gelöscht: $userPrincipalName"
            } else {
                Write-Host "Benutzer nicht gefunden (zum Löschen): $userPrincipalName"
            }
        }
        default {
            Write-Warning "Unbekannter Status für $userPrincipalName"
        }
    }

    # Check if the user changed courses and needs to be moved to a different OU
    if ($existingUser -and $existingUser.DistinguishedName -ne "CN=$username,$ouPath") {
        # Move the user to the new OU (if the course has changed)
        Move-ADObject -Identity $existingUser.DistinguishedName -TargetPath $ouPath
        Write-Host "Benutzer verschoben in OU: $ouPath"
    }
}
