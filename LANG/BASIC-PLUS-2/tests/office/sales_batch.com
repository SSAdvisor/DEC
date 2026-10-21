$ ! SALES_BATCH.COM - Automatic batch report procedure
$ WRITE SYS$OUTPUT "Starting Sales Inventory Report Batch Job..."
$ BASIC tests/office/salesrpt.bas
$ LINK tests/office/salesrpt
$ RUN tests/office/salesrpt
$ PRINT tests/office/SALES.RPT /QUEUE=LP0: /NAME=SALES_NIGHTLY
$ SHOW QUEUE LP0:
$ WRITE SYS$OUTPUT "Sales Inventory Report Batch Job Finished Successfully."
$ EXIT
