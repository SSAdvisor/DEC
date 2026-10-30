import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
BIN_PATH = APP_DIR / "bin" / "coupon"


def run_coupon(commands: list[str], cwd: Path) -> subprocess.CompletedProcess:
    input_text = "\n".join(commands) + "\n"
    return subprocess.run(
        [str(BIN_PATH)],
        input=input_text,
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=10,
    )


def test_coupon_binary_exists():
    assert BIN_PATH.exists()


def test_coupon_sample_list_validate_and_status(tmp_path):
    res = run_coupon(
        [
            "SAMPLE",
            "LIST",
            "VALIDATE K9$m#2, 15",
            "DISABLE K9$m#2",
            "VALIDATE K9$m#2, 15",
            "ENABLE K9$m#2",
            "STATUS",
            "EXIT",
        ],
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[Sample SYSTEM Coupon dataset loaded - 3 promotional codes]" in out
    assert "Code: K9$m#2 | 25.50% OFF | DAYS: 30 | [ACTIVE]" in out
    assert "[COUPON VALIDATED] Code: K9$m#2 (25.50% OFF" in out
    assert "[Coupon K9$m#2 status set to DISABLED]" in out
    assert "COUPON: Code K9$m#2 is currently DISABLED" in out
    assert "[Coupon K9$m#2 status set to ACTIVE]" in out


def test_coupon_create_generate_save_load_delete(tmp_path):
    res = run_coupon(
        [
            "CREATE A1#b$9, 33.33, MONTHS, 6, Custom 6-Month Promo",
            "GENERATE 12.75, DAYS, 90, Auto 90-Day Promo",
            "SAVE COUPON.DAT",
            "CLEAR",
            "LOAD COUPON.DAT",
            "LIST",
            "DELETE A1#b$9",
            "STATUS",
            "EXIT",
        ],
        tmp_path,
    )
    assert res.returncode == 0
    out = res.stdout
    assert "[Coupon Created: A1#b$9 | 33.33% OFF | Duration=MONTHS (6) | Status=ACTIVE]" in out
    assert "12.75% OFF | Duration=DAYS (90) | Status=ACTIVE]" in out
    assert "[2 coupon records saved to COUPON.DAT]" in out
    assert "[2 coupon records loaded from COUPON.DAT]" in out
    assert "[Coupon A1#b$9 deleted]" in out
    assert "Coupons: 1" in out
