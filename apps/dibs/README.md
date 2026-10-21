# DIBS - DEC Integrated Business System (DIBS-11)

A native DEC **BASIC-PLUS-2** implementation of Digital Equipment Corporation's **DIBS** (**DEC Integrated Business System** / **DIBS-11**), a commercial accounting, financial reporting, and business management suite originally distributed for **DEC PDP-11 (CTS-300, CTS-500, RSTS/E)** systems.

---

## 1. Historical Background & Heritage

- **Original Product**: DIBS-11 V3.0 (DEC Integrated Business System)
- **Manufacturer**: Digital Equipment Corporation (Maynard, Massachusetts)
- **Target Systems**: DEC PDP-11 (CTS-300, CTS-500, RSTS/E, RT-11)
- **Historical Significance**: Introduced in the mid-1970s and expanded through the 1980s on RSTS/E and CTS-500 commercial systems, **DIBS-11** was DEC's flagship commercial ERP and accounting package. It integrated **General Ledger (GL)**, **Accounts Receivable (AR)**, **Order Entry & Invoicing**, **Accounts Payable (AP)**, and **Inventory Control (IC)** into a unified multi-user business system.
- **Dialect & Toolchain**: Native DEC BASIC-PLUS-2 compiled with `basicc` and linked with `basiclink` for the RSTS/E virtual machine runtime.

---

## 2. Architecture & Accounting Modules

1. **General Ledger (`GL`) & Financial Statements**:
   - **Chart of Accounts (`COA`)**: Structured accounts across `ASSET` (Debit), `LIAB` (Credit), `EQUITY` (Credit), `REV` (Credit), and `EXP` (Debit).
   - **Double-Entry Journal Engine (`POST` / `JRNLIST`)**: Validates debit and credit accounts, updates normal balances, and records a complete audit trail in the Journal Entry Register.
   - **Financial Statements**:
     - `TRIAL` (`TB`): General Ledger Trial Balance verifying `Total Debits = Total Credits`.
     - `INCOME` (`PL`): Profit & Loss statement computing Total Revenue, Total Expenses, and Net Income.
     - `BALANCE` (`BS`): Balance Sheet reconciling Total Assets against Total Liabilities + Equity (including Current Period Net Income).

2. **Accounts Receivable (`AR`) & Invoicing**:
   - Tracks customer balances in the AR subledger (`AR` / `ARLIST`).
   - `INVOICE <cust_id>, <name>, <amount>`: Bills a customer in the AR subledger and automatically posts `DR 1100 (Accounts Receivable) / CR 4010 (Sales Revenue)` to the General Ledger.
   - `RECEIVE <cust_id>, <amount>`: Applies customer cash payment and automatically posts `DR 1010 (Cash) / CR 1100 (Accounts Receivable)`.

3. **Accounts Payable (`AP`) & Disbursements**:
   - Tracks vendor balances in the AP subledger (`AP` / `APLIST`).
   - `VOUCHER <vend_id>, <name>, <amount>`: Records a vendor payable voucher and automatically posts `DR 5010 (Cost of Goods Sold) / CR 2010 (Accounts Payable)`.
   - `PAY <vend_id>, <amount>`: Disburses vendor check payment and automatically posts `DR 2010 (Accounts Payable) / CR 1010 (Cash)`.

4. **Inventory Control (`INV`)**:
   - Tracks hardware/product SKUs, descriptions, quantities on hand, unit costs, extended item values, and total inventory valuation (`INV` / `ADDITEM`).

---

## 3. Directory Layout

```
apps/dibs/
├── README.md           # Sub-project documentation
├── Makefile            # Build, test, run, and clean automation
├── bin/
│   ├── dibs            # Compiled native ELF binary
│   ├── dibs11          # Symlink alias -> dibs
│   └── cts500          # Symlink alias -> dibs
├── build/
│   └── dibs.obj       # Intermediate BASIC-PLUS-2 object
├── src/
│   └── dibs.bas        # Native DEC BASIC-PLUS-2 source code (< 470 lines)
└── tests/
    ├── __init__.py     # Test package marker
    └── test_dibs.py    # Automated pytest test suite (14 test cases)
```

---

## 4. Command Reference & Syntax

| Command | Aliases | Description |
|---|---|---|
| `COA` | `GL`, `ACCOUNTS` | Lists the General Ledger Chart of Accounts and balances. |
| `ADDACCT <num>, <name>, <type>, <bal>` | - | Adds a new General Ledger account (`ASSET`, `LIAB`, `EQUITY`, `REV`, `EXP`). |
| `POST <dr>, <cr>, <amt> [, <memo>]` | `JOURNAL` | Posts a double-entry journal transaction to the General Ledger. |
| `JRNLIST` | `REGISTER` | Displays the General Ledger Journal Entry audit register. |
| `TRIAL` | `TB` | Generates the General Ledger Trial Balance (`DR = CR`). |
| `INCOME` | `PL` | Generates the Income Statement (Profit & Loss). |
| `BALANCE` | `BS` | Generates the Balance Sheet (`Assets = Liabilities + Equity`). |
| `AR` | `ARLIST` | Displays the Accounts Receivable customer subledger. |
| `INVOICE <id>, <name>, <amt>` | - | Bills a customer invoice and posts `DR 1100 / CR 4010` to GL. |
| `RECEIVE <id>, <amt>` | `CASH` | Records customer payment and posts `DR 1010 / CR 1100` to GL. |
| `AP` | `APLIST` | Displays the Accounts Payable vendor subledger. |
| `VOUCHER <id>, <name>, <amt>` | - | Records a vendor voucher and posts `DR 5010 / CR 2010` to GL. |
| `PAY <id>, <amt>` | - | Pays a vendor balance and posts `DR 2010 / CR 1010` to GL. |
| `INV` | `INVLIST` | Displays the Inventory Control item master and total valuation. |
| `ADDITEM <sku>, <desc>, <qty>, <cost>` | - | Adds a new item to the Inventory Control master. |
| `REPORT [ON <file>]` | `EXPORT <file>` | Displays or exports an executive financial report to disk. |
| `SAMPLE` | `DEMO` | Loads balanced DEC commercial dataset (GL, AR, AP, Inventory, Journal). |
| `SAVE [file]` | - | Saves the General Ledger chart of accounts in pipe-delimited format. |
| `LOAD [file]` | `IMPORT` | Loads General Ledger accounts from a disk file. |
| `SHOW` | `STATUS` | Displays DIBS-11 system status and record counts. |
| `CLEAR` | `RESET` | Clears all ledgers and subledgers from memory. |
| `HELP` | `?` | Displays summary of all available DIBS-11 commands. |
| `EXIT` | `QUIT`, `BYE` | Exits the DIBS-11 session. |

---

## 5. Build, Test, and Execution

Compile with native DEC BASIC-PLUS-2 toolchain:
```bash
make -C apps/dibs clean build
```

Run test suite:
```bash
make -C apps/dibs test
# or directly:
pytest apps/dibs/tests/
```

Run interactive session:
```bash
make -C apps/dibs run
```
