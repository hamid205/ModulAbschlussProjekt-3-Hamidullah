# Active Directory Modul importieren
Import-Module ActiveDirectory

# Liste für neu erstellte Benutzer
$neuErstellteBenutzer = @()

# CSV-Datei einlesen
Import-Csv "\\Admin-Server\Logging\interessenten.csv" | ForEach-Object {

    $DisplayName = "$($_.Anrede) $($_.Vorname) $($_.Nachname)"
    $SamAccountName = $_.Benutzeranmeldename

    # Prüfen, ob der Benutzer bereits existiert
    $ExistingUser = Get-ADUser -Filter { SamAccountName -eq $SamAccountName } -ErrorAction SilentlyContinue

    if ($ExistingUser) {
        # Benutzer existiert
        Write-Host "Benutzer '$SamAccountName' existiert bereits." -ForegroundColor Cyan
    } else {
        # Neuen Benutzer erstellen
        New-ADUser `
            -Name $DisplayName `
            -GivenName $_.Vorname `
            -Surname $_.Nachname `
            -SamAccountName $SamAccountName `
            -UserPrincipalName "$($SamAccountName)@M-zukunftsmotor.local" `
            -EmailAddress $_.EMail `
            -Department $_.Abteilung `
            -Office $_.Standort `
            -StreetAddress $_.Adresse_Standort `
            -Enabled $true `
            -AccountPassword (ConvertTo-SecureString -String "InitialPassword!" -AsPlainText -Force) `
            -ChangePasswordAtLogon $true

        # Benutzer zur Liste hinzufügen
        $neuErstellteBenutzer += $SamAccountName

        Write-Host "Benutzer '$SamAccountName' wurde erstellt." -ForegroundColor Green
    }
}

# Am Ende: neu erstellte Benutzer anzeigen
if ($neuErstellteBenutzer.Count -gt 0) {
    Write-Host "`nListe der neu erstellten Benutzer:" -ForegroundColor Magenta
    $neuErstellteBenutzer | ForEach-Object { Write-Host $_ -ForegroundColor White }
} else {
    Write-Host "`nEs wurden keine neuen Benutzer erstellt." -ForegroundColor Yellow
}
