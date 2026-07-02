# API Settings Dokumentation

## Endpunkte

- POST /settings
  - Sendet die allgemeinen Einstellungen des Panels.
  - Body-Beispiel:
    {
      "panelName": "GamePanel",
      "language": "Deutsch",
      "emailNotifications": true,
      "darkMode": false,
      "autoSaveInterval": 15
    }

- POST /password
  - Sendet die Passwort-Änderung und den 2FA-Status.
  - Body-Beispiel:
    {
      "newPassword": "geheim",
      "twoFactorEnabled": true
    }

## Konfiguration

Die API-Ziele sind in der Datei panel/js/settings.js festgelegt:

- API_BASE_URL = https://example-api.local
- SETTINGS_ENDPOINT = https://example-api.local/settings
- PASSWORD_ENDPOINT = https://example-api.local/password

Ersetze die URL durch den tatsächlichen API-Server, falls nötig.
