# FileVault

A personal, local Streamlit app for dragging and dropping a file, encrypting it, and saving a password-protected master key.

## Run on Windows

Use Python 3.10 or newer. From this project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://127.0.0.1:8501`. No environment activation is needed. The included configuration binds the app only to your machine and disables usage telemetry.

## Use FileVault

1. Create your vault with a strong password or passphrase of at least 12 characters.
2. Immediately use **Download encrypted key backup** in the sidebar. Keep the backup somewhere separate from the vault, and retain your password securely.
3. In **Encrypt a file**, drag and drop a file and click **Encrypt and save**.
4. In **My vault**, select a saved entry to download its encrypted copy, or choose **Decrypt selected file** and download the original content.
5. Use **Decrypt a file** to decrypt a previously downloaded `.fvault` file with this same vault's key.
6. Click **Lock vault** when finished. It clears the current session's key, upload, and decrypted-result references.

Your original files are never modified or deleted. Decrypted content is available as a browser download; it is not written into the server's vault.

## What is saved

The default storage folder is `vault` next to `app.py`:

```text
vault\
  master_key.json
  files\
    <random-id>.fvault
```

- File contents and their original filenames are encrypted together with **AES-256-GCM**, which also detects tampering. Each encryption uses a new random nonce.
- A random 256-bit master key is wrapped with AES-256-GCM using a password-derived **scrypt** key (N=131072, r=8, p=1, random salt). Only the encrypted master key is saved in `master_key.json`; neither the password nor the plaintext master key is saved there.
- Saved entries have random identifiers so their original names are not exposed on disk. Encrypted sizes and filesystem timestamps remain visible.
- New files never overwrite an existing master key or vault entry. If encrypted entries exist but the key is missing, the app requires restoration rather than generating a replacement key.

To use another storage folder, set `FILEVAULT_DIR` before starting the app:

```powershell
$env:FILEVAULT_DIR = 'C:\MyPrivateVault'
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Restore a backup

To restore on another machine or into an empty vault folder, open **Restore key backup**, upload your encrypted master-key JSON backup, and enter its original password. Copy your saved entries into the new vault's `files` folder, retaining their random `.fvault` filenames, or decrypt your downloaded `.fvault` files in the app.

An existing key is never replaced by the restore operation. Back up both your encrypted files and the encrypted key. **If you forget the password or lose every copy of the master key, the files cannot be recovered.** There is no password-reset bypass.

## Limits and safety

- This is a **single-user local app**, not a hosted or multi-user storage service. Keep it bound to `127.0.0.1`. The unlock password protects the encryption key, not a network account.
- Plaintext files can be up to 200 MiB each. The uploader allows 201 MiB to accommodate encrypted-file overhead. Encryption and downloads operate in memory, so larger files require more RAM.
- Locking removes session references; Python and Streamlit do not guarantee secure erasure of memory. Downloaded plaintext is outside the vault and must be protected separately.
- Encryption does not protect against malware or an attacker controlling your machine while the vault is unlocked. This app has not undergone an independent security audit.

## Tests

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Tests use temporary vaults and do not initialize or modify your real vault.
