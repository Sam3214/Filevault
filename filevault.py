"""Authenticated file encryption and password-protected local key storage."""
    def __init__(self, root: Path):
        self.root = Path(root)
        self.key_path = self.root.joinpath("master_key.json")
        self.files_dir = self.root.joinpath("files")

    def has_key(self) -> bool:
        return self.key_path.exists() or self.key_path.is_symlink()

    def initialize(self, password: str) -> bytes:
        if self.has_key():
            raise FileVaultError("A master key already exists. Unlock the vault instead.")
        if self.list_files():
            raise FileVaultError("Encrypted files already exist. Restore the original key backup instead.")
        master_key, backup = create_key_backup(password)
        _write_new_file(self.key_path, backup)
        return master_key

    def restore(self, backup: bytes, password: str) -> bytes:
        if self.has_key():
            raise FileVaultError("A master key already exists and will not be overwritten.")
        master_key = unlock_key_backup(backup, password)
        _write_new_file(self.key_path, backup)
        return master_key

    def unlock(self, password: str) -> bytes:
        return unlock_key_backup(self.key_backup(), password)

    def key_backup(self) -> bytes:
        return _read_file(self.key_path, MAX_KEY_BACKUP_SIZE)

    def store(self, master_key: bytes, filename: str, data: bytes) -> Path:
        if not self.has_key():
            raise FileVaultError("Create or restore the vault before saving files.")
        if self.files_dir.is_symlink():
            raise FileVaultError("The vault storage directory must not be a symbolic link.")
        encrypted = encrypt_file(master_key, filename, data)
        path = self.files_dir.joinpath(uuid.uuid4().hex + ".fvault")
        _write_new_file(path, encrypted)
        return path

    def list_files(self) -> list[Path]:
        if self.files_dir.is_symlink():
            raise FileVaultError("The vault storage directory must not be a symbolic link.")
        if not self.files_dir.exists():
            return []
        files = [path for path in self.files_dir.iterdir() if ENTRY_PATTERN.fullmatch(path.name) and path.is_file() and not path.is_symlink()]
        return sorted(files, key=lambda path: path.stat().st_mtime_ns, reverse=True)

    def read_encrypted(self, filename: str) -> bytes:
        if not ENTRY_PATTERN.fullmatch(filename) or self.files_dir.is_symlink():
            raise FileVaultError("The vault entry is invalid.")
        return _read_file(self.files_dir.joinpath(filename), MAX_ENCRYPTED_SIZE)
