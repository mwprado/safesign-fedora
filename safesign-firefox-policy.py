#!/usr/bin/python3
"""Merge SafeSign into the system Firefox policy without replacing other policies."""
import json
import os
import pathlib
import stat
import sys
import tempfile

path = pathlib.Path("/etc/firefox/policies/policies.json")
name = "SafeSign G+D"
module = "/usr/lib64/libaetpkss.so"

def main():
    if path.is_symlink():
        raise ValueError("policies.json is a symlink; configure manually")
    exists = path.exists()
    data = json.loads(path.read_text(encoding="utf-8")) if exists else {}
    if not isinstance(data, dict):
        raise ValueError("invalid policy root")
    policies = data.setdefault("policies", {})
    devices = policies.setdefault("SecurityDevices", {})
    if not isinstance(devices, dict):
        raise ValueError("invalid SecurityDevices policy")
    if set(devices) - {"Add", "Delete"}:
        raise ValueError("legacy SecurityDevices policy; merge manually")
    additions = devices.setdefault("Add", {})
    if not isinstance(additions, dict):
        raise ValueError("invalid SecurityDevices.Add policy")
    if name in devices.get("Delete", []):
        raise ValueError("administrator explicitly disables SafeSign")
    if name in additions and additions[name] != module:
        raise ValueError("conflicting SafeSign policy")
    if module in additions.values():
        return
    additions[name] = module
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".safesign-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(data, out, indent=2, ensure_ascii=False)
            out.write("\n")
            if exists:
                old = path.stat()
                os.fchown(out.fileno(), old.st_uid, old.st_gid)
                os.fchmod(out.fileno(), stat.S_IMODE(old.st_mode))
            else:
                os.fchmod(out.fileno(), 0o644)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        print("SafeSign: Firefox policy not changed:", exc, file=sys.stderr)
        sys.exit(1)
