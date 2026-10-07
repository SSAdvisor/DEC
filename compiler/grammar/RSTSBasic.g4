grammar RSTSBasic;

// RSTS/E BASIC-PLUS-2 Grammar Sketch

program: line* EOF;

line: (lineNumber)? statement (':' statement)* (NEWLINE | EOF);

lineNumber: INT;

statement
    : 'PRINT' expression (',' expression | ';' expression)* (';')?  # printStmt
    | 'LET'? variable '=' expression                              # letStmt
    | 'GOTO' lineNumber                                           # gotoStmt
    | 'IF' expression 'THEN' statement ('ELSE' statement)?        # ifStmt
    | 'END'                                                       # endStmt
    | 'REM' .*? (NEWLINE | EOF)                                   # remStmt
    | 'OPEN' expression 'FOR' ('INPUT' | 'OUTPUT') 'AS' 'FILE' '#' INT # openSeqStmt
    | 'OPEN' expression 'AS' 'FILE' '#' INT ',' 'INDEXED' ',' 'PRIMARY' 'KEY' variable # openIdxStmt
    | 'CLOSE' '#' INT                                             # closeStmt
    | 'PUT' '#' INT                                               # putStmt
    | 'GET' '#' INT (',' 'KEY' variable)?                         # getStmt
    | 'CALL' STRING                                               # callStmt
    | 'INPUT' variable                                            # inputStmt
    | 'DIM' variable (',' variable)*                              # dimStmt
    ;

expression
    : left=expression op=('*'|'/') right=expression               # mulDivExpr
    | left=expression op=('+'|'-') right=expression               # addSubExpr
    | left=expression op=('<'|'>'|'='|'<='|'>='|'<>') right=expression # relExpr
    | 'INKEY$'                                                    # inkeyExpr
    | 'CHR$' '(' expression ')'                                   # chrExpr
    | INT                                                         # intExpr
    | FLOAT                                                       # floatExpr
    | STRING                                                      # strExpr
    | variable                                                    # varExpr
    | '(' expression ')'                                          # parensExpr
    ;

variable: ID ('%' | '$')? ('(' expression ')')?; // % for integer, $ for string


// Lexer Rules
INT: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]+;
STRING: '"' ~["]* '"';
ID: [A-Z] [A-Z0-9]*;
NEWLINE: '\r'? '\n';
WS: [ \t]+ -> skip;
