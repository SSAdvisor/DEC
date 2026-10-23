{ ============================================================================== }
{ DEC VAX Pascal V4.3 Demonstration Program (DEMO.PAS)                           }
{ Digital Equipment Corporation VAX/VMS V5.5-2                                   }
{ ============================================================================== }
[IDENT('V04-03')]
PROGRAM VAXPASDEMO(INPUT, OUTPUT);

CONST
    BONUS_RATE = 15;
    MAX_ITEMS  = 5;

TYPE
    EMP_REC = RECORD
        ID     : INTEGER;
        NAME   : VARYING [40] OF CHAR;
        DEPT   : VARYING [40] OF CHAR;
        SALARY : INTEGER;
    END;

VAR
    EMP        : EMP_REC;
    SCORES     : ARRAY[1..5] OF INTEGER;
    I, TOTAL   : INTEGER;
    BONUS, COMP: INTEGER;
    GRADE      : VARYING [20] OF CHAR;

FUNCTION CALC_BONUS(BASE_SAL : INTEGER; PCT : INTEGER) : INTEGER;
BEGIN
    CALC_BONUS := (BASE_SAL * PCT) DIV 100;
END;

PROCEDURE PRINT_BANNER;
BEGIN
    WRITELN('============================================================');
    WRITELN('  DEC VAX PASCAL V4.3 ON VAX/VMS V5.5-2                     ');
    WRITELN('============================================================');
END;

BEGIN
    CALL_INIT:
    PRINT_BANNER;

    EMP.ID     := 1042;
    EMP.NAME   := 'DR. NIKLAUS WIRTH';
    EMP.DEPT   := 'VAX PASCAL COMPILER ENGINEERING';
    EMP.SALARY := 84000;

    BONUS := CALC_BONUS(EMP.SALARY, BONUS_RATE);
    COMP  := EMP.SALARY + BONUS;

    TOTAL := 0;
    FOR I := 1 TO MAX_ITEMS DO
    BEGIN
        SCORES[I] := I * 10;
        TOTAL := TOTAL + SCORES[I];
    END;

    CASE TOTAL OF
        150: GRADE := 'OUTSTANDING';
        100..149: GRADE := 'EXCEEDS';
        OTHERWISE GRADE := 'STANDARD';
    END;

    WRITELN('EMPLOYEE ID: ', EMP.ID);
    WRITELN('EMPLOYEE:    ', EMP.NAME);
    WRITELN('DEPARTMENT:  ', EMP.DEPT);
    WRITELN('BASE SALARY: ', EMP.SALARY);
    WRITELN('BONUS:       ', BONUS);
    WRITELN('TOTAL COMP:  ', COMP);
    WRITELN('SCORE SUM:   ', TOTAL, ' (', GRADE, ')');
    WRITELN('============================================================');
END.
