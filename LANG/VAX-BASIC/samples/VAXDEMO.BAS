PROGRAM VAXDEMO
    ! ==========================================================================
    ! DEC VAX BASIC V3.5 Structured Programming Sample (VAX/VMS V5.5-2)
    ! Demonstrates RECORD structures, SELECT/CASE, SUB, FUNCTION, & WHEN ERROR
    ! ==========================================================================
    %TITLE "DEC VAX BASIC V3.5 Employee & Engineering Benchmark"
    %IDENT "V03-05"
    OPTION TYPE = EXPLICIT

    RECORD EMPLOYEE_REC
        STRING NAME
        LONG   DEPT_CODE
        LONG   BASE_SALARY
        LONG   BONUS
    END RECORD EMPLOYEE_REC

    DECLARE EMPLOYEE_REC EMP
    DECLARE STRING DEPT_TITLE$
    DECLARE LONG TOTAL_COMP, BONUS_CALC

    FUNCTION LONG CALC_BONUS(LONG SAL, LONG PCT)
        CALC_BONUS = INT((SAL * PCT) / 100)
    END FUNCTION

    SUB PRINT_BANNER(STRING HEADER_TEXT$)
        PRINT "============================================================"
        PRINT "  "; HEADER_TEXT$
        PRINT "============================================================"
    END SUB

    CALL PRINT_BANNER("DEC VAX BASIC V3.5 ON VAX/VMS V5.5-2")

    EMP::NAME = "DR. GORDON BELL"
    EMP::DEPT_CODE = 20
    EMP::BASE_SALARY = 85000

    SELECT EMP::DEPT_CODE
        CASE 10
            DEPT_TITLE$ = "PDP-11 SYSTEMS ENGINEERING"
        CASE 20
            DEPT_TITLE$ = "VAX ARCHITECTURE & VMS KERNEL"
        CASE ELSE
            DEPT_TITLE$ = "CORPORATE RESEARCH"
    END SELECT

    EMP::BONUS = CALC_BONUS(EMP::BASE_SALARY, 15)
    TOTAL_COMP = EMP::BASE_SALARY + EMP::BONUS

    PRINT "EMPLOYEE:   "; EMP::NAME
    PRINT "DEPARTMENT: "; DEPT_TITLE$
    PRINT "TOTAL COMP: "; TOTAL_COMP
END PROGRAM
