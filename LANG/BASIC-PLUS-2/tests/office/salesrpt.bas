PROGRAM SALESRPT

! RMS indexed-file record layout (32 bytes)
MAP (SALES) WORD ITEM_ID, &
            STRING ITEM_NAME = 24, &
            WORD QTY, &
            SINGLE UNIT_PRICE

DECLARE WORD I
DECLARE SINGLE LINE_TOTAL, GRAND_TOTAL

ON ERROR GOTO ERROR_HANDLER

! Recreate and initialize the RMS indexed file.
OPEN "SALES.IDX" FOR OUTPUT AS FILE #1%, &
     ORGANIZATION INDEXED FIXED, &
     ACCESS WRITE, &
     PRIMARY KEY ITEM_ID, &
     MAP SALES

FOR I = 1% TO 8%
    READ ITEM_ID, ITEM_NAME, QTY, UNIT_PRICE
    PUT #1%
NEXT I
CLOSE #1%

! Reopen the RMS file by its primary key and make a printable report file.
OPEN "SALES.IDX" FOR INPUT AS FILE #1%, &
     ORGANIZATION INDEXED FIXED, &
     ACCESS READ, &
     PRIMARY KEY ITEM_ID, &
     MAP SALES

! Omitting ORGANIZATION makes this a terminal-format file for PRINT statements.
OPEN "SALES.RPT" FOR OUTPUT AS FILE #2%

PRINT #2%, "                         SALES INVENTORY REPORT"
PRINT #2%, "                         RUN DATE: "; DATE$(0%)
PRINT #2%
PRINT #2%, "ITEM  DESCRIPTION                 QTY   UNIT PRICE   EXTENDED"
PRINT #2%, "----  ------------------------   ----  ----------   -----------"

GRAND_TOTAL = 0.0
RESTORE #1%, KEY #0%

REPORT_LOOP:
    GET #1%
    LINE_TOTAL = QTY * UNIT_PRICE
    GRAND_TOTAL = GRAND_TOTAL + LINE_TOTAL
    PRINT #2%, USING "####  \                      \  ####  $$####.##  $$######.##"; &
                     ITEM_ID, ITEM_NAME, QTY, UNIT_PRICE, LINE_TOTAL
    GOTO REPORT_LOOP

REPORT_DONE:
PRINT #2%, "----  ------------------------   ----  ----------   -----------"
PRINT #2%, USING "                                      REPORT TOTAL: $$######.##"; &
                 GRAND_TOTAL
CLOSE #1%, #2%
PRINT "SALES.RPT created. Submit it to the configured network print queue."
GOTO PROGRAM_EXIT

ERROR_HANDLER:
    IF ERR = 11%
    THEN
        RESUME REPORT_DONE
    ELSE
        ON ERROR GOTO 0
    END IF

DATA 1001, "Widget A",       12, 19.95
DATA 1002, "Widget B",        5, 42.50
DATA 1003, "Service Kit",     8, 11.75
DATA 1004, "Cable Assembly", 20,  6.25
DATA 1005, "Control Module",  3, 89.00
DATA 1006, "Mounting Plate", 14,  8.40
DATA 1007, "Power Supply",    4, 64.95
DATA 1008, "Spare Fuse Pack",25,  3.10

PROGRAM_EXIT:
END PROGRAM

