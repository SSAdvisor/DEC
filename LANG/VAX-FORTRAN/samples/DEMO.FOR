C     ==================================================================
C     DEC VAX FORTRAN V5.5 SCIENTIFIC & STRUCTURED BENCHMARK (DEMO.FOR)
C     Digital Equipment Corporation VAX/VMS V5.5-2
C     ==================================================================
      PROGRAM VAXFORDEMO
      IMPLICIT NONE
      INTEGER*4 MAX_N
      PARAMETER (MAX_N = 5)

      STRUCTURE /SENSOR_REC/
          INTEGER*4 ID
          CHARACTER*20 LABEL
          INTEGER*4 READING
      END STRUCTURE

      RECORD /SENSOR_REC/ SENS
      INTEGER*4 ARR(5), I, TOTAL, FACT5
      CHARACTER*16 STATUS

      SENS.ID = 101 ! Assign sensor ID
      SENS.LABEL = 'VAX-11/780 CORE'
      SENS.READING = 42

      TOTAL = 0
      DO I = 1, MAX_N
          ARR(I) = I * 10
          TOTAL = TOTAL + ARR(I)
      END DO

      CALL COMPUTE_FACT(5, FACT5)

      SELECT CASE (TOTAL)
          CASE (150)
              STATUS = 'NOMINAL'
          CASE DEFAULT
              STATUS = 'FAULT'
      END SELECT

      PRINT *, 'DEC VAX FORTRAN V5.5 ON VAX/VMS V5.5-2'
      PRINT *, 'SENSOR: ', SENS.LABEL, ' ID=', SENS.ID
      PRINT *, 'ARRAY TOTAL=', TOTAL, ' FACT(5)=', FACT5
      PRINT *, 'STATUS=', STATUS
      STOP
      END

      SUBROUTINE COMPUTE_FACT(N, RES)
      INTEGER*4 N, RES, K
      RES = 1
      K = 1
      DO WHILE (K .LE. N)
          RES = RES * K
          K = K + 1
      END DO
      RETURN
      END
