10 ! ==============================================
20 ! HELLO.BAS - Simple DEC BASIC-PLUS-2 Test
30 ! ==============================================
40 PRINT "Hello from DEC BASIC-PLUS-2 on Linux!"
50 PRINT "System Date: "; DATE$(0%); " Time: "; TIME$(0%)
60 FOR I% = 1% TO 5%
70   PRINT "Loop iteration: "; I%; " Squared: "; I% * I%
80 NEXT I%
90 END
