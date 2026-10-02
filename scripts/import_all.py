import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_URL = os.environ.get("PATCHGUARD_API_URL", "http://localhost:8000/api")
SAMPLES = {
    "assets": "windows_servers.csv",
    "patches": "wsus_patch_report.csv",
    "vulnerabilities": "vulnerabilities.csv",
    "ad_issues": "ad_health_report.csv",
    "vms": "vcenter_vm_inventory.csv",
    "backups": "rubrik_backup_report.csv",
}


def upload(entity: str, path: Path) -> dict:
    boundary = "----PatchGuardImportBoundary"
    file_bytes = path.read_bytes()
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\n"
        "Content-Type: text/csv\r\n\r\n"
    ).encode() + file_bytes + f"\r\n--{boundary}--\r\n".encode()
    request = urllib.request.Request(
        f"{API_URL}/imports?{urllib.parse.urlencode({'entity': entity})}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def main() -> None:
    try:
        for entity, filename in SAMPLES.items():
            result = upload(entity, ROOT / "data_samples" / filename)
            print(f"{entity}: imported {result['imported']} records")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Import failed ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Cannot reach PatchGuard API at {API_URL}: {exc.reason}") from exc


if __name__ == "__main__":
    main()
