10  ! Program to demonstrate RMS Indexed file I/O in BASIC-PLUS-2
    ON ERROR GOTO 19000

    ! Define the layout of our record buffer using a MAP statement
    MAP (EMP_BUF) STRING EMP_NAME$ = 30%, &
                 STRING EMP_ID$   = 6%,  &
                 STRING JOB_DESC$ = 20%

20  ! ----------------------------------------------------
    ! PHASE 1: Create and write to an RMS Indexed File
    ! ----------------------------------------------------
    PRINT "Creating indexed database file..."
    OPEN "EMP_DATA.DAT" FOR OUTPUT AS FILE #1%,                   &
        ORGANIZATION INDEXED FIXED,                                &
        ACCESS MODIFY,                                             &
        ALLOW NONE,                                                &
        MAP EMP_BUF,                                               &
        PRIMARY EMP_NAME$,                                         &
        ALTERNATE EMP_ID$

30  ! Loop to input record data from the user
    INPUT "Enter Employee Name (or blank to stop): "; EMP_NAME$
    IF EMP_NAME$ = "" THEN 50

40  INPUT "Enter 6-digit Employee ID: "; EMP_ID$
    INPUT "Enter Job Description: "; JOB_DESC$
    
    ! PUT explicitly passes the MAP buffer data to the RMS storage layer
    PUT #1% 
    PRINT "--- Record written via RMS ---"
    GOTO 30

50  CLOSE #1%
    PRINT "File closed successfully."

60  ! ----------------------------------------------------
    ! PHASE 2: Open for reading and query by Alternate Key
    ! ----------------------------------------------------
    PRINT "Re-opening file for query mode..."
    OPEN "EMP_DATA.DAT" FOR INPUT AS FILE #1%,                    &
        ORGANIZATION INDEXED FIXED,                                &
        ACCESS READ,                                               &
        MAP EMP_BUF,                                               &
        PRIMARY EMP_NAME$,                                         &
        ALTERNATE EMP_ID$

70  PRINT "Query via Alternate Key (Employee ID)"
    INPUT "Enter ID to search for (or blank to quit): "; SEARCH_ID$
    IF SEARCH_ID$ = "" THEN 32767

80  ! GET uses KEY #1% (the alternate key, EMP_ID$) to look up records
    GET #1%, KEY #1% EQ SEARCH_ID$
    
    PRINT "Record Found!"
    PRINT "Name: "; EMP_NAME$
    PRINT "ID:   "; EMP_ID$
    PRINT "Job:  "; JOB_DESC$
    GOTO 70

19000 ! Simple Error Handling Block
    IF ERR = 155% THEN &
        PRINT "Error: Record not found!" \ RESUME 70
    
    PRINT "RMS/Runtime Error Code: "; ERR; " at line "; ERL
    RESUME 32767

32767 CLOSE #1%
    END

