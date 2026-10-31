# COUPON - Legacy Computing Systems SYSTEM Discount Coupon Manager

A native DEC **BASIC-PLUS-2** system management utility (`COUPON.BAS`) for **Legacy Computing Systems** on **DEC PDP-11 RSTS/E V10.1-L** (`[1,2] SYSTEM`) and **DEC VAX/VMS V5.5-2** (`[1,4] SYSTEM`). It manages 6-character alphanumeric + special-character promotional discount coupons with 100ths-percent (`0.01%`–`100.00%`) precision and 1-year maximum expiration policies (`NEVER`, `DAYS 1..365`, `MONTHS 1..12`), backed by `COUPON.DAT` and synchronized with the HTTPS `/signup` and `/admin` provisioning engine (`COUPONS.JSON`).

---

## 1. Overview & Security Model

- **Program Name**: `COUPON` (`LCSSYS`, `CPNMGR`)
- **System Privilege Requirement**:
  - **RSTS/E V10.1-L**: Restricted to the privileged `[1,2] SYSTEM` account. Non-privileged accounts receive `?Protection violation — COUPON requires privileged [1,2] SYSTEM account`.
  - **VAX/VMS V5.5-2**: Restricted to the `SYSTEM` (`[1,4]`) account with `SYSPRV` / `BYPASS`. Non-privileged accounts receive `%CLI-E-NOPRIV, insufficient privilege or object protection violation (SYSTEM required)`.
  - **HTTPS Web Admin (`/admin`)**: Accessible via `/api/v1/admin/coupon-cli` only after `SYSTEM` login at the terminal or `/api/v1/admin/login`.
- **Dialect & Toolchain**: Native DEC BASIC-PLUS-2 compiled with `basicc` and linked with `basiclink` for the `rsts_vm` virtual machine runtime.

---

## 2. Coupon Code & Policy Enforcement

1. **6-Character Alphanumeric + Special Code**:
   - Every coupon code must be exactly **6 characters** long and contain at least one letter (`A–Z`, `a–z`), at least one digit (`0–9`), and at least one special character (`!@#$%*-_+=~?`).
2. **Percentage Discount Precision (`0.01%`–`100.00%`)**:
   - Supports fractional percentage discounts up to the **100ths place** (`0.01%`), stored internally as integer basis points (`1`..`10000`) and formatted as `XX.XX%`.
3. **Expiration Policy (`<= 1 Year`)**:
   - `NEVER` — Non-expiring promotional coupon (`0` duration).
   - `DAYS <1..365>` — Expires after `1` to `365` days (`> 365` rejected).
   - `MONTHS <1..12>` — Expires after `1` to `12` months (`> 12` rejected).

---

## 3. Directory Layout

```
apps/coupon/
├── README.md           # Sub-project documentation
├── Makefile            # Build, test, run, and clean automation
├── bin/
│   ├── coupon          # Compiled native ELF binary
│   ├── lcssys          # Symlink alias -> coupon
│   └── cpnmgr          # Symlink alias -> coupon
├── build/
│   └── coupon.obj      # Intermediate BASIC-PLUS-2 object
├── src/
│   └── coupon.bas      # Native DEC BASIC-PLUS-2 source code
└── tests/
    └── test_coupon.py  # Automated pytest test suite (6 test cases)
```

---

## 4. Command Reference & Syntax

| Command | Aliases | Description |
|---|---|---|
| `SAMPLE` | `DEMO` | Loads 3 sample 6-character promotional coupons (`R7$k!2`, `V9#m*4`, `B5@p~8`) and saves `COUPON.DAT`. |
| `LIST` | `DIR`, `SHOW` | Displays the formatted table of all coupons in `COUPON.DAT`. |
| `CREATE <code6>, <pct>, <NEVER\|DAYS\|MONTHS>, <val>, <desc>` | `ADD` | Validates and creates/updates a 6-character discount coupon and persists to `COUPON.DAT`. |
| `GENERATE <pct>, <NEVER\|DAYS\|MONTHS>, <val>, <desc>` | `GEN` | Auto-generates a 6-character alphanumeric+special code and persists the coupon to `COUPON.DAT`. |
| `VALIDATE <code6>, <plan>` | `CHECK` | Validates a 6-character coupon against `LCS_RSTS_10` (`$10`), `LCS_VMS_10` (`$10`), `LCS_BUNDLE_15` (`$15`), or `LCS_ENTERPRISE` (`$199`). |
| `REVOKE <code6>` | `DELETE`, `DEL` | Marks a coupon as `REVOKED` and persists to `COUPON.DAT`. |
| `SAVE [file]` | - | Writes the coupon table to `COUPON.DAT` (or custom file). |
| `LOAD [file]` | - | Loads the coupon table from `COUPON.DAT` (or custom file). |
| `CLEAR` | `RESET` | Clears all in-memory coupon records. |
| `HELP` | `?` | Displays summary of all available `COUPON` commands. |
| `EXIT` | `QUIT`, `BYE` | Exits the `COUPON` utility. |

---

## 5. Build, Test, and Execution

Compile with native DEC BASIC-PLUS-2 toolchain:
```bash
make -C apps/coupon clean build
```

Run test suite:
```bash
make -C apps/coupon test
# or directly:
pytest apps/coupon/tests/
```

Run interactive session:
```bash
make -C apps/coupon run
```
