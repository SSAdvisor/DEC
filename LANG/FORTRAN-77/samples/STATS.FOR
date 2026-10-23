C     DEC PDP-11 FORTRAN-77 V5.0 NUMERICAL SERIES BENCHMARK
      PROGRAM STATS
      INTEGER I, N, ISUM, ISQ
      N = 10
      ISUM = 0
      ISQ = 0
      DO 100 I = 1, N
         ISUM = ISUM + I
         ISQ = ISQ + (I * I)
 100  CONTINUE
      WRITE(6,*) 'DEC PDP-11 FORTRAN-77 V5.0 RESULTS:'
      WRITE(6,*) 'SUM(1..10) = ', ISUM
      WRITE(6,*) 'SUMSQ(1..10) = ', ISQ
      STOP
      END
