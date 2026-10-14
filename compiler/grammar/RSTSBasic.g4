grammar RSTSBasic;

// RSTS/E BASIC-PLUS-2 Grammar

program: line* ((lineNumber | labelDef)? statement ((':' | '\\') statement)*)? EOF;

line: (lineNumber | labelDef)? (statement ((':' | '\\') statement)*)? NEWLINE;

labelDef: ID ':';
lineNumber: INT;
target: INT | ID;

dataType: 'WORD' | 'SINGLE' | 'DOUBLE' | 'BYTE' | 'LONG' | 'STRING';

mapItem: dataType? variable ('=' INT)?;

statement
    : 'PROGRAM' ID                                                # programStmt
    | 'DECLARE' dataType variable (',' variable)*                 # declareStmt
    | 'PRINT' ('#' INT (',' | ';')?)? ('USING' formatExpr=expression ';')? (printItem ((',' | ';')? printItem)* (',' | ';')?)? # printStmt
    | 'LET'? variable '=' expression                              # letStmt
    | 'GOTO' target                                               # gotoStmt
    | 'RANDOMIZE'                                                 # randomizeStmt
    | 'FOR' variable '=' fromExpr=expression 'TO' toExpr=expression ('STEP' stepExpr=expression)? # forStmt
    | 'NEXT' variable?                                            # nextStmt
    | 'READ' variable (',' variable)*                             # readStmt
    | 'DATA' dataItem (',' dataItem)*                             # dataStmt
    | 'RESTORE' ('#' INT)? (',' 'KEY' ('#' INT)? (('EQ' | '=')? expression)?)? # restoreStmt
    | 'IF' expression 'THEN' (thenStmt=statement | thenTarget=target) ('ELSE' (elseStmt=statement | elseTarget=target))? # ifStmt
    | 'IF' expression ('THEN')?                                   # ifBlockStmt
    | 'THEN' statement?                                           # thenStmt
    | 'ELSE' statement?                                           # elseStmt
    | 'END' 'IF'                                                  # endIfStmt
    | 'END' 'PROGRAM'?                                            # endStmt
    | REM_COMMENT                                                 # remStmt
    | BANG_COMMENT                                                # bangRemStmt
    | 'ON' 'ERROR' 'GOTO' target                                  # onErrorStmt
    | 'RESUME' target?                                            # resumeStmt
    | 'MAP' '(' variable ')' mapItem (',' mapItem)*               # mapStmt
    | 'OPEN' expression ('FOR' ('INPUT' | 'OUTPUT'))? 'AS' 'FILE'? '#' INT (',' openClause)* # openAnyStmt
    | 'CLOSE' '#' INT (',' '#' INT)*                              # closeStmt
    | 'PUT' '#' INT                                               # putStmt
    | 'GET' '#' INT (',' 'KEY' ('#' INT)? ('EQ' | '=')? expression)?  # getStmt
    | 'CALL' STRING                                               # callStmt
    | 'LINE'? 'INPUT' ('#' INT (',' | ';'))? (STRING (';' | ','))? variable # inputStmt
    | 'DIM' variable (',' variable)*                              # dimStmt
    ;

printItem
    : expression
    ;

dataItem
    : ('+' | '-')? (INT | FLOAT)
    | STRING
    ;

openClause
    : 'ORGANIZATION'? 'INDEXED' 'FIXED'?
    | 'ACCESS' ('MODIFY' | 'READ' | 'WRITE')
    | 'ALLOW' 'NONE'
    | 'MAP' variable
    | 'PRIMARY' 'KEY'? variable
    | 'ALTERNATE' 'KEY'? variable
    ;

expression
    : op=('+'|'-') expression                                     # unaryExpr
    | left=expression op=('*'|'/') right=expression               # mulDivExpr
    | left=expression op=('+'|'-') right=expression               # addSubExpr
    | left=expression op=('<'|'>'|'='|'<='|'>='|'<>') right=expression # relExpr
    | left=expression op=('AND'|'OR') right=expression            # logicalExpr
    | 'INKEY$'                                                    # inkeyExpr
    | 'CHR$' '(' expression ')'                                   # chrExpr
    | INT                                                         # intExpr
    | FLOAT                                                       # floatExpr
    | STRING                                                      # strExpr
    | variable                                                    # varExpr
    | '(' expression ')'                                          # parensExpr
    ;

variable: ID ('%' | '$')? ('(' expression (',' expression)* ')')?; // % for integer, $ for string

// Lexer Rules
REM_COMMENT: 'REM' ~[\r\n]*;
BANG_COMMENT: '!' ~[\r\n]*;
LINE_CONT: '&' [ \t]* '\r'? '\n' -> skip;
INT: [0-9]+ '%'?;
FLOAT: [0-9]+ '.' [0-9]+;
STRING: '"' ~["]* '"';
ID: [A-Z] [A-Z0-9_]*;
NEWLINE: '\r'? '\n';
WS: [ \t]+ -> skip;
