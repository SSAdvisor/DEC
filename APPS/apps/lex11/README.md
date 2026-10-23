# LEX-11 V2.4 (EEC Systems, Inc.)

**LEX-11** was a widely deployed multi-user word processing, desk calculator, glossary expansion, and mass-mailing office automation suite for **DEC PDP-11 RSTS/E** (and RSX-11M / RT-11), developed by **EEC Systems, Inc.** of Millis, Massachusetts.

## Key Capabilities
- **Document Catalog (`DIR`, `SELECT`, `CREATE`, `READ`, `COPY`, `DELETE`, `PURGE`)**: Organizes office documents in `LEXDOC.DAT` across `CORP`, `LEGAL`, `MEMO`, and `WASTEBASKET` folders.
- **Built-in Desk Calculator (`CALC <a op b>`, `PASTECALC`)**: Evaluates commercial arithmetic expressions (`+`, `-`, `*`, `/`) into the LEX-11 Paste Register (`REG$`) and substitutes `<CALC>` into active documents.
- **Abbreviation Glossary (`GLOSSARY`, `GLOSSADD <key>, <phrase>`, `EXPAND`)**: Expands shorthand office glossary macros (e.g., `@EEC`, `@RSTS`, `@DEC`) throughout the active document.
- **Mass-Mailing Generator (`MAILLIST`, `MAILADD`, `MERGE`)**: Merges recipient records (`<NAME>`, `<COMPANY>`, `<SYSTEM>`) with form letters.
- **Ruler & Document Formatting (`RULER`, `HEADER`, `FOOTER`, `FORMAT`, `PRINT ON`, `EXPORT`)**.
