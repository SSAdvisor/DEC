# DECwindows CDA Viewer V3.0 (`DECW$CDAVIEWER` / `dxvdoc`)

**DECwindows CDA Viewer V3.0** is a faithful native DEC BASIC-PLUS-2 implementation of the Digital Equipment Corporation DECwindows Compound Document Architecture (CDA) Viewer (`DECW$CDAVIEWER` on VAX/VMS and OpenVMS, `dxvdoc` on ULTRIX and DEC OSF/1, 1988–1995).

CDA Viewer inspects, validates, and renders multi-segment compound documents encoded in **DDIF** (Digital Document Interchange Format), **DTIF** (Digital Table Interchange Format), **DOTS** (Data Object Transport Syntax), and PostScript.

---

## Features

- **Alpha AXP Compound Document Sample (`SAMPLE` / `DEMO`)**:
  - Loads `ALPHA_SPEC.DDIF` (`DDIF V1.2 (Compound Document)`, authored by `DEC Alpha Architecture Group (MRO)`, DOTS status `PACKED (External Links Resolved)`).
  - Contains 6 multi-type compound segments across 3 pages (`HEADER`, `TEXT`, `GRAPHIC` ISL/Sixel pipeline diagram, `TABLE` DTIF 4x3 specification matrix, and `FOOTER`).
- **CDA Segment Inspector (`ELEMENTS [type]` / `SEGMENTS` / `LIST`)**:
  - Displays all compound segments or filters by segment type (`HEADER`, `TEXT`, `TABLE`, `GRAPHIC`, `FOOTER`) with Segment #, Page #, Type, DDIF/DTIF aggregate descriptor (`DDIF$S_SEG_TXT`, `DTIF$S_TBL_SPEC`, `DDIF$S_SEG_ISL`, etc.), and content preview.
- **Multi-Page Compound Renderer (`PAGE <n>`, `NEXT`, `PREV`, `PAGES`)**:
  - Renders individual pages or the complete compound document with framed `DTIF` tables and `ISL/Sixel` graphic viewports.
- **Segment Editing (`ADDSEG`, `DELSEG`)**:
  - Dynamically adds new compound segments (`ADDSEG <page|type|descriptor|content>`) or deletes existing segments (`DELSEG <seg#>`).
- **DDIF / DTIF / DOTS Structural Conformance Audit (`INSPECT` / `ANALYZE` / `CHECK`)**:
  - Counts `TEXT`, `TABLE`, `GRAPHIC`, and `HEADER`/`FOOTER` segments across all pages and validates ASN.1 TLV & DDIF/DTIF aggregate descriptor conformance.
- **Full-Text & Descriptor Search (`SEARCH <kw>` / `FIND <kw>`)**:
  - Case-insensitive search across segment types, DDIF/DTIF descriptors, and segment content.
- **Motif / XUI Window Renderer (`DISPLAY [ON <file>]`, `EXPORT <file>`)**:
  - Renders the 78-column DECwindows CDA Viewer Motif/XUI window chrome with title bar, menu bar, DOTS transport status bar, active page segment viewport, and conformance status bar.
- **Data Interchange (`SAVE <file>`, `LOAD <file>`)**:
  - Saves and restores compound documents in pipe-delimited `.cda` format.

---

## Building and Testing

```bash
make -C apps/decwindows/cdaviewer build
pytest apps/decwindows/cdaviewer/tests/
```
