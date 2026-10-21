10 DIM A$(10)
20 A$(0) = "John Doe"
30 A$(1) = "Jane Smith"
40 A$(2) = "Bob"
50 PRINT "\033[2J\033[H";
60 PRINT "========================="
70 PRINT "   Advanced TUI          "
80 PRINT "========================="
90 PRINT "0: ";A$(0)
100 PRINT "1: ";A$(1)
110 PRINT "2: ";A$(2)
120 PRINT "Press q to quit, any other key to refresh"
130 K$ = INKEY$
140 IF K$ = "q" THEN GOTO 200
150 GOTO 50
200 PRINT "\033[2J\033[HExiting..."
210 END
