"""Run with: python -m streamlit run app.py"""
    st.title("🔐 FileVault")
    st.caption("Drag. Drop. Encrypt. Your files, protected on your machine.")
    vault = Vault(Path(os.environ.get("FILEVAULT_DIR", str(DEFAULT_VAULT))))

    with st.sidebar:
        st.header("Your vault")
        unlocked = "master_key" in st.session_state
        if unlocked:
            st.success("Vault unlocked")
            st.button("Lock vault", on_click=lock_vault, use_container_width=True)
        else:
            st.info("Vault locked")
        st.markdown("**AES-256-GCM encryption**  \nPassword-protected master key")
        st.warning("Keep your password and an encrypted key backup safe. Losing either the password or every copy of the key means losing access to your files.")
        with st.expander("Local storage"):
            st.code(str(vault.root), language=None)
        st.caption("Personal, local use only. Do not expose this app to a network.")

    if not unlocked:
        try:
            render_locked(vault)
        except (FileVaultError, OSError) as error:
            show_error(error)
        return

    master_key = st.session_state["master_key"]
    try:
        entries = vault.list_files()
        backup = vault.key_backup()
        encrypted_size = sum(path.stat().st_size for path in entries)
    except (FileVaultError, OSError) as error:
        show_error(error)
        return
    st.sidebar.download_button("Download encrypted key backup", data=backup, file_name="filevault-master-key.json", mime="application/json", on_click="ignore", use_container_width=True)
    notice = st.session_state.pop("notice", None)
    if notice:
        st.success(notice)
    count, size, protection = st.columns(3)
    count.metric("Encrypted files", len(entries))
    size.metric("Encrypted storage", f"{encrypted_size / (1024 * 1024):.2f} MB")
    protection.metric("Master key", "Password protected")
    encrypt_tab, saved_tab, decrypt_tab = st.tabs(["Encrypt a file", "My vault", "Decrypt a file"])
    with encrypt_tab:
        render_encrypt(vault, master_key)
    with saved_tab:
        render_saved(vault, master_key, entries)
    with decrypt_tab:
        render_decrypt_upload(master_key)


if __name__ == "__main__":
    main()
 
