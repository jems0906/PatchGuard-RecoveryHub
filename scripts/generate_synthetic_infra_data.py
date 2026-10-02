import argparse
import csv
import random
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data_samples" / "generated"


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate(output: Path, count: int, seed: int) -> None:
    rng = random.Random(seed)
    today = date.today()
    now = datetime.now(UTC)
    hosts = [f"LAB-SRV-{number:03d}" for number in range(1, count + 1)]
    assets = []
    patches = []
    vulnerabilities = []
    vms = []
    backups = []

    for index, hostname in enumerate(hosts, start=1):
        role = rng.choice(["Application Server", "File Server", "Database Server", "Web Server"])
        tier = rng.choice(["Gold", "Silver", "Bronze"])
        assets.append({
            "hostname": hostname,
            "os_version": rng.choice(["Windows Server 2019", "Windows Server 2022"]),
            "role": role,
            "ip_address": f"10.88.{(index - 1) // 250}.{(index - 1) % 250 + 1}",
            "domain": "lab.example.invalid",
            "forest": "lab.example.invalid",
            "site": rng.choice(["Lab-East", "Lab-West"]),
            "fsmo_roles": "",
            "last_boot": (today - timedelta(days=rng.randint(1, 45))).isoformat(),
            "asset_type": "Server",
            "app_name": role.replace(" Server", "") if role == "Application Server" else "",
            "service_status": "Running" if role == "Application Server" else "",
            "backup_policy": tier,
        })
        patches.append({
            "title": "Synthetic monthly security update",
            "kb_number": f"KB2099{index:04d}",
            "classification": rng.choice(["Critical", "Security"]),
            "approval_status": rng.choice(["approved", "not approved"]),
            "target_group": "Lab Servers",
            "asset_hostname": hostname,
            "installation_status": rng.choice(["installed", "needed", "failed", "reboot required"]),
            "wave": f"Wave {(index - 1) % 3 + 1}",
            "deployment_date": (today - timedelta(days=rng.randint(0, 20))).isoformat(),
        })
        if index % 2 == 0:
            vulnerabilities.append({
                "cve_id": f"CVE-2099-{10000 + index}",
                "severity": rng.choice(["critical", "high", "medium", "low"]),
                "affected_asset": hostname,
                "description": "Synthetic finding for development and UI testing only.",
                "remediation": "Apply the documented lab fix and validate with a fresh scan.",
                "patch_available": "true",
                "kb_number": f"KB2099{index:04d}",
                "registry_change_needed": "false",
                "registry_key": "",
                "registry_value": "",
                "status": rng.choice(["open", "scheduled", "in progress", "verified"]),
                "deadline": (today + timedelta(days=rng.randint(-5, 20))).isoformat(),
                "discovered_at": (today - timedelta(days=rng.randint(1, 30))).isoformat(),
                "verified_by": "",
                "verified_at": "",
            })
        memory_allocated = rng.choice([8, 16, 32])
        disk_provisioned = rng.choice([100, 250, 500])
        vms.append({
            "vm_name": hostname,
            "power_state": "poweredOn",
            "host_cluster": rng.choice(["Lab-Cluster-A", "Lab-Cluster-B"]),
            "datastore": f"LAB-DS-{(index - 1) % 4 + 1}",
            "vcpus": rng.choice([2, 4, 8]),
            "cpu_ready_percent": round(rng.uniform(0, 8), 1),
            "memory_allocated_gb": memory_allocated,
            "memory_active_gb": round(rng.uniform(1, memory_allocated), 1),
            "ballooning": str(rng.random() < 0.12).lower(),
            "disk_provisioned_gb": disk_provisioned,
            "disk_used_gb": rng.randint(20, disk_provisioned),
            "datastore_free_percent": rng.randint(8, 80),
            "tools_status": rng.choice(["current", "current", "outdated"]),
            "snapshot_name": "",
            "snapshot_size_gb": 0,
            "snapshot_created": "",
        })
        last_success = now - timedelta(hours=rng.randint(0, 72))
        backups.append({
            "job_name": f"{hostname}-Daily",
            "protected_system": hostname,
            "backup_type": "incremental",
            "sla_domain": tier,
            "last_successful_backup": last_success.isoformat(timespec="minutes"),
            "status": rng.choice(["success", "success", "success", "failed"]),
            "next_scheduled_backup": (last_success + timedelta(days=1)).isoformat(timespec="minutes"),
            "restore_test_date": (today - timedelta(days=rng.randint(1, 180))).isoformat() if index % 3 == 0 else "",
            "restore_test_result": "passed" if index % 3 == 0 else "",
            "tested_by": "Synthetic Operator" if index % 3 == 0 else "",
            "error_details": "",
        })

    ad_issues = [
        {
            "issue_type": "Replication",
            "username": "",
            "object_name": "",
            "domain_controller": "LAB-DC01",
            "dc_status": "online",
            "last_sync": (now - timedelta(hours=3)).isoformat(timespec="minutes"),
            "failed_partner": "LAB-DC02",
            "status": "open",
            "last_logon": "",
            "lockout_time": "",
            "last_modified": "",
            "source": "LAB-DC02",
            "details": "Synthetic replication error for development only.",
        }
    ]

    output.mkdir(parents=True, exist_ok=True)
    for filename, rows in (
        ("windows_servers.csv", assets),
        ("wsus_patch_report.csv", patches),
        ("vulnerabilities.csv", vulnerabilities),
        ("ad_health_report.csv", ad_issues),
        ("vcenter_vm_inventory.csv", vms),
        ("rubrik_backup_report.csv", backups),
    ):
        write_csv(output / filename, rows)
        print(f"{filename}: {len(rows)} records")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create deterministic, synthetic infrastructure CSVs.")
    parser.add_argument("--count", type=int, default=25, help="Number of synthetic servers to create (1-500).")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for reproducible records.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output directory for generated CSV files.")
    args = parser.parse_args()
    if not 1 <= args.count <= 500:
        parser.error("--count must be between 1 and 500.")
    generate(args.output, args.count, args.seed)


if __name__ == "__main__":
    main()
