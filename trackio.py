WORKSPACE = Path(r"C:\Users\samarthdesai\Copilot\Code\Projects\FileVault")
ARTIFACTS = Path(__file__).resolve().parent
ROOTS = (WORKSPACE, ARTIFACTS)
LEDGER = ARTIFACTS.joinpath("written_files.json")
BEFORE = ARTIFACTS.joinpath("before_files.json")


def snapshot():
    result = {}
    for root in ROOTS:
        if not root.exists():
            continue
        for directory, subdirs, names in os.walk(root, followlinks=False):
            subdirs[:] = [name for name in subdirs if not Path(directory, name).is_symlink() and not os.path.isjunction(Path(directory, name))]
            for name in names:
                path = Path(directory, name)
                if path.is_symlink():
                    continue
                try:
                    stat = path.stat()
                    with path.open("rb") as source:
                        digest = hashlib.file_digest(source, "sha256").hexdigest()
                    result[str(path.absolute())] = [stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, digest]
                except FileNotFoundError:
                    continue
    return result


def inventory(paths):
    previous = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {"files": []}
    files = set(previous["files"])
    files.update(paths)
    files.update((str(Path(__file__).resolve()), str(LEDGER), str(BEFORE)))
    LEDGER.write_text(json.dumps({"files": sorted(files)}, indent=2), encoding="utf-8")


def capture():
    state = snapshot()
    BEFORE.write_text(json.dumps(state), encoding="utf-8")
    inventory(state)
    for root in ROOTS:
        print(f"Inventoried directory: {root}", flush=True)
    print(f"Before: {len(state)} files", flush=True)
    return state


def reconcile(before):
    after = snapshot()
    inventory(set(before) | set(after))
    added = set(after) - set(before)
    changed = {path for path in set(before) & set(after) if before[path] != after[path]}
    removed = set(before) - set(after)
    print(f"After: {len(after)} files; added={len(added)}, changed={len(changed)}, removed={len(removed)}", flush=True)


def environment():
    env = os.environ.copy()
    temp = ARTIFACTS.joinpath("tmp")
    home = ARTIFACTS.joinpath("home")
    temp.mkdir(exist_ok=True)
    home.mkdir(exist_ok=True)
    env.update({
        "TEMP": str(temp), "TMP": str(temp), "HOME": str(home), "USERPROFILE": str(home),
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1", "PYTHONUTF8": "1",
        "PIP_NO_CACHE_DIR": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1", "PIP_NO_INPUT": "1",
        "PIP_CONFIG_FILE": os.devnull, "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
    })
