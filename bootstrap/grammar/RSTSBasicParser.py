# Generated from bootstrap/grammar/RSTSBasic.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,85,404,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,1,0,5,0,
        28,8,0,10,0,12,0,31,9,0,1,0,1,0,3,0,35,8,0,1,0,1,0,1,0,5,0,40,8,
        0,10,0,12,0,43,9,0,3,0,45,8,0,1,0,1,0,1,1,1,1,3,1,51,8,1,1,1,1,1,
        1,1,5,1,56,8,1,10,1,12,1,59,9,1,3,1,61,8,1,1,1,1,1,1,2,1,2,1,2,1,
        3,1,3,1,4,1,4,1,5,1,5,1,6,3,6,75,8,6,1,6,1,6,1,6,3,6,80,8,6,1,7,
        1,7,1,7,1,7,1,7,1,7,1,7,5,7,89,8,7,10,7,12,7,92,9,7,1,7,1,7,1,7,
        1,7,3,7,98,8,7,3,7,100,8,7,1,7,1,7,1,7,1,7,3,7,106,8,7,1,7,1,7,3,
        7,110,8,7,1,7,5,7,113,8,7,10,7,12,7,116,9,7,1,7,3,7,119,8,7,3,7,
        121,8,7,1,7,3,7,124,8,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,
        1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,3,7,144,8,7,1,7,1,7,3,7,148,8,7,
        1,7,1,7,1,7,1,7,5,7,154,8,7,10,7,12,7,157,9,7,1,7,1,7,1,7,1,7,5,
        7,163,8,7,10,7,12,7,166,9,7,1,7,1,7,1,7,3,7,171,8,7,1,7,1,7,1,7,
        1,7,3,7,177,8,7,1,7,3,7,180,8,7,1,7,3,7,183,8,7,3,7,185,8,7,1,7,
        1,7,1,7,1,7,1,7,3,7,192,8,7,1,7,1,7,1,7,3,7,197,8,7,3,7,199,8,7,
        1,7,1,7,1,7,3,7,204,8,7,1,7,1,7,3,7,208,8,7,1,7,1,7,3,7,212,8,7,
        1,7,1,7,1,7,1,7,3,7,218,8,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,3,7,
        228,8,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,5,7,237,8,7,10,7,12,7,240,9,
        7,1,7,1,7,1,7,1,7,3,7,246,8,7,1,7,1,7,3,7,250,8,7,1,7,1,7,1,7,1,
        7,5,7,256,8,7,10,7,12,7,259,9,7,1,7,1,7,1,7,1,7,1,7,1,7,5,7,267,
        8,7,10,7,12,7,270,9,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,3,
        7,282,8,7,1,7,3,7,285,8,7,1,7,3,7,288,8,7,1,7,1,7,1,7,3,7,293,8,
        7,1,7,1,7,1,7,1,7,3,7,299,8,7,1,7,1,7,3,7,303,8,7,1,7,1,7,1,7,1,
        7,1,7,5,7,310,8,7,10,7,12,7,313,9,7,3,7,315,8,7,1,8,1,8,1,9,3,9,
        320,8,9,1,9,1,9,3,9,324,8,9,1,10,3,10,327,8,10,1,10,1,10,3,10,331,
        8,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,3,10,341,8,10,1,10,
        1,10,1,10,3,10,346,8,10,1,10,3,10,349,8,10,1,11,1,11,1,11,1,11,1,
        11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,3,
        11,368,8,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,
        11,1,11,5,11,382,8,11,10,11,12,11,385,9,11,1,12,1,12,3,12,389,8,
        12,1,12,1,12,1,12,1,12,5,12,395,8,12,10,12,12,12,398,9,12,1,12,1,
        12,3,12,402,8,12,1,12,0,1,22,13,0,2,4,6,8,10,12,14,16,18,20,22,24,
        0,13,1,0,1,2,2,0,80,80,83,83,1,0,3,8,2,0,12,12,15,15,2,0,9,9,30,
        30,1,0,42,43,1,0,52,53,1,0,80,81,2,0,26,26,58,59,1,0,64,65,2,0,9,
        9,66,70,1,0,71,72,1,0,75,76,494,0,29,1,0,0,0,2,50,1,0,0,0,4,64,1,
        0,0,0,6,67,1,0,0,0,8,69,1,0,0,0,10,71,1,0,0,0,12,74,1,0,0,0,14,314,
        1,0,0,0,16,316,1,0,0,0,18,323,1,0,0,0,20,348,1,0,0,0,22,367,1,0,
        0,0,24,386,1,0,0,0,26,28,3,2,1,0,27,26,1,0,0,0,28,31,1,0,0,0,29,
        27,1,0,0,0,29,30,1,0,0,0,30,44,1,0,0,0,31,29,1,0,0,0,32,35,3,6,3,
        0,33,35,3,4,2,0,34,32,1,0,0,0,34,33,1,0,0,0,34,35,1,0,0,0,35,36,
        1,0,0,0,36,41,3,14,7,0,37,38,7,0,0,0,38,40,3,14,7,0,39,37,1,0,0,
        0,40,43,1,0,0,0,41,39,1,0,0,0,41,42,1,0,0,0,42,45,1,0,0,0,43,41,
        1,0,0,0,44,34,1,0,0,0,44,45,1,0,0,0,45,46,1,0,0,0,46,47,5,0,0,1,
        47,1,1,0,0,0,48,51,3,6,3,0,49,51,3,4,2,0,50,48,1,0,0,0,50,49,1,0,
        0,0,50,51,1,0,0,0,51,60,1,0,0,0,52,57,3,14,7,0,53,54,7,0,0,0,54,
        56,3,14,7,0,55,53,1,0,0,0,56,59,1,0,0,0,57,55,1,0,0,0,57,58,1,0,
        0,0,58,61,1,0,0,0,59,57,1,0,0,0,60,52,1,0,0,0,60,61,1,0,0,0,61,62,
        1,0,0,0,62,63,5,84,0,0,63,3,1,0,0,0,64,65,5,83,0,0,65,66,5,1,0,0,
        66,5,1,0,0,0,67,68,5,80,0,0,68,7,1,0,0,0,69,70,7,1,0,0,70,9,1,0,
        0,0,71,72,7,2,0,0,72,11,1,0,0,0,73,75,3,10,5,0,74,73,1,0,0,0,74,
        75,1,0,0,0,75,76,1,0,0,0,76,79,3,24,12,0,77,78,5,9,0,0,78,80,5,80,
        0,0,79,77,1,0,0,0,79,80,1,0,0,0,80,13,1,0,0,0,81,82,5,10,0,0,82,
        315,5,83,0,0,83,84,5,11,0,0,84,85,3,10,5,0,85,90,3,24,12,0,86,87,
        5,12,0,0,87,89,3,24,12,0,88,86,1,0,0,0,89,92,1,0,0,0,90,88,1,0,0,
        0,90,91,1,0,0,0,91,315,1,0,0,0,92,90,1,0,0,0,93,99,5,13,0,0,94,95,
        5,14,0,0,95,97,5,80,0,0,96,98,7,3,0,0,97,96,1,0,0,0,97,98,1,0,0,
        0,98,100,1,0,0,0,99,94,1,0,0,0,99,100,1,0,0,0,100,105,1,0,0,0,101,
        102,5,16,0,0,102,103,3,22,11,0,103,104,5,15,0,0,104,106,1,0,0,0,
        105,101,1,0,0,0,105,106,1,0,0,0,106,120,1,0,0,0,107,114,3,16,8,0,
        108,110,7,3,0,0,109,108,1,0,0,0,109,110,1,0,0,0,110,111,1,0,0,0,
        111,113,3,16,8,0,112,109,1,0,0,0,113,116,1,0,0,0,114,112,1,0,0,0,
        114,115,1,0,0,0,115,118,1,0,0,0,116,114,1,0,0,0,117,119,7,3,0,0,
        118,117,1,0,0,0,118,119,1,0,0,0,119,121,1,0,0,0,120,107,1,0,0,0,
        120,121,1,0,0,0,121,315,1,0,0,0,122,124,5,17,0,0,123,122,1,0,0,0,
        123,124,1,0,0,0,124,125,1,0,0,0,125,126,3,24,12,0,126,127,5,9,0,
        0,127,128,3,22,11,0,128,315,1,0,0,0,129,130,5,18,0,0,130,315,3,8,
        4,0,131,132,5,19,0,0,132,315,3,8,4,0,133,315,5,20,0,0,134,315,5,
        21,0,0,135,136,5,22,0,0,136,137,3,24,12,0,137,138,5,9,0,0,138,139,
        3,22,11,0,139,140,5,23,0,0,140,143,3,22,11,0,141,142,5,24,0,0,142,
        144,3,22,11,0,143,141,1,0,0,0,143,144,1,0,0,0,144,315,1,0,0,0,145,
        147,5,25,0,0,146,148,3,24,12,0,147,146,1,0,0,0,147,148,1,0,0,0,148,
        315,1,0,0,0,149,150,5,26,0,0,150,155,3,24,12,0,151,152,5,12,0,0,
        152,154,3,24,12,0,153,151,1,0,0,0,154,157,1,0,0,0,155,153,1,0,0,
        0,155,156,1,0,0,0,156,315,1,0,0,0,157,155,1,0,0,0,158,159,5,27,0,
        0,159,164,3,18,9,0,160,161,5,12,0,0,161,163,3,18,9,0,162,160,1,0,
        0,0,163,166,1,0,0,0,164,162,1,0,0,0,164,165,1,0,0,0,165,315,1,0,
        0,0,166,164,1,0,0,0,167,170,5,28,0,0,168,169,5,14,0,0,169,171,5,
        80,0,0,170,168,1,0,0,0,170,171,1,0,0,0,171,184,1,0,0,0,172,173,5,
        12,0,0,173,176,5,29,0,0,174,175,5,14,0,0,175,177,5,80,0,0,176,174,
        1,0,0,0,176,177,1,0,0,0,177,182,1,0,0,0,178,180,7,4,0,0,179,178,
        1,0,0,0,179,180,1,0,0,0,180,181,1,0,0,0,181,183,3,22,11,0,182,179,
        1,0,0,0,182,183,1,0,0,0,183,185,1,0,0,0,184,172,1,0,0,0,184,185,
        1,0,0,0,185,315,1,0,0,0,186,187,5,31,0,0,187,188,3,22,11,0,188,191,
        5,32,0,0,189,192,3,14,7,0,190,192,3,8,4,0,191,189,1,0,0,0,191,190,
        1,0,0,0,192,198,1,0,0,0,193,196,5,33,0,0,194,197,3,14,7,0,195,197,
        3,8,4,0,196,194,1,0,0,0,196,195,1,0,0,0,197,199,1,0,0,0,198,193,
        1,0,0,0,198,199,1,0,0,0,199,315,1,0,0,0,200,201,5,31,0,0,201,203,
        3,22,11,0,202,204,5,32,0,0,203,202,1,0,0,0,203,204,1,0,0,0,204,315,
        1,0,0,0,205,207,5,32,0,0,206,208,3,14,7,0,207,206,1,0,0,0,207,208,
        1,0,0,0,208,315,1,0,0,0,209,211,5,33,0,0,210,212,3,14,7,0,211,210,
        1,0,0,0,211,212,1,0,0,0,212,315,1,0,0,0,213,214,5,34,0,0,214,315,
        5,31,0,0,215,217,5,34,0,0,216,218,5,10,0,0,217,216,1,0,0,0,217,218,
        1,0,0,0,218,315,1,0,0,0,219,315,5,77,0,0,220,315,5,78,0,0,221,222,
        5,35,0,0,222,223,5,36,0,0,223,224,5,18,0,0,224,315,3,8,4,0,225,227,
        5,37,0,0,226,228,3,8,4,0,227,226,1,0,0,0,227,228,1,0,0,0,228,315,
        1,0,0,0,229,230,5,38,0,0,230,231,5,39,0,0,231,232,3,24,12,0,232,
        233,5,40,0,0,233,238,3,12,6,0,234,235,5,12,0,0,235,237,3,12,6,0,
        236,234,1,0,0,0,237,240,1,0,0,0,238,236,1,0,0,0,238,239,1,0,0,0,
        239,315,1,0,0,0,240,238,1,0,0,0,241,242,5,41,0,0,242,245,3,22,11,
        0,243,244,5,22,0,0,244,246,7,5,0,0,245,243,1,0,0,0,245,246,1,0,0,
        0,246,247,1,0,0,0,247,249,5,44,0,0,248,250,5,45,0,0,249,248,1,0,
        0,0,249,250,1,0,0,0,250,251,1,0,0,0,251,252,5,14,0,0,252,257,5,80,
        0,0,253,254,5,12,0,0,254,256,3,20,10,0,255,253,1,0,0,0,256,259,1,
        0,0,0,257,255,1,0,0,0,257,258,1,0,0,0,258,315,1,0,0,0,259,257,1,
        0,0,0,260,261,5,46,0,0,261,262,5,14,0,0,262,268,5,80,0,0,263,264,
        5,12,0,0,264,265,5,14,0,0,265,267,5,80,0,0,266,263,1,0,0,0,267,270,
        1,0,0,0,268,266,1,0,0,0,268,269,1,0,0,0,269,315,1,0,0,0,270,268,
        1,0,0,0,271,272,5,47,0,0,272,273,5,14,0,0,273,315,5,80,0,0,274,275,
        5,48,0,0,275,276,5,14,0,0,276,287,5,80,0,0,277,278,5,12,0,0,278,
        281,5,29,0,0,279,280,5,14,0,0,280,282,5,80,0,0,281,279,1,0,0,0,281,
        282,1,0,0,0,282,284,1,0,0,0,283,285,7,4,0,0,284,283,1,0,0,0,284,
        285,1,0,0,0,285,286,1,0,0,0,286,288,3,22,11,0,287,277,1,0,0,0,287,
        288,1,0,0,0,288,315,1,0,0,0,289,290,5,49,0,0,290,315,5,82,0,0,291,
        293,5,50,0,0,292,291,1,0,0,0,292,293,1,0,0,0,293,294,1,0,0,0,294,
        298,5,42,0,0,295,296,5,14,0,0,296,297,5,80,0,0,297,299,7,3,0,0,298,
        295,1,0,0,0,298,299,1,0,0,0,299,302,1,0,0,0,300,301,5,82,0,0,301,
        303,7,3,0,0,302,300,1,0,0,0,302,303,1,0,0,0,303,304,1,0,0,0,304,
        315,3,24,12,0,305,306,5,51,0,0,306,311,3,24,12,0,307,308,5,12,0,
        0,308,310,3,24,12,0,309,307,1,0,0,0,310,313,1,0,0,0,311,309,1,0,
        0,0,311,312,1,0,0,0,312,315,1,0,0,0,313,311,1,0,0,0,314,81,1,0,0,
        0,314,83,1,0,0,0,314,93,1,0,0,0,314,123,1,0,0,0,314,129,1,0,0,0,
        314,131,1,0,0,0,314,133,1,0,0,0,314,134,1,0,0,0,314,135,1,0,0,0,
        314,145,1,0,0,0,314,149,1,0,0,0,314,158,1,0,0,0,314,167,1,0,0,0,
        314,186,1,0,0,0,314,200,1,0,0,0,314,205,1,0,0,0,314,209,1,0,0,0,
        314,213,1,0,0,0,314,215,1,0,0,0,314,219,1,0,0,0,314,220,1,0,0,0,
        314,221,1,0,0,0,314,225,1,0,0,0,314,229,1,0,0,0,314,241,1,0,0,0,
        314,260,1,0,0,0,314,271,1,0,0,0,314,274,1,0,0,0,314,289,1,0,0,0,
        314,292,1,0,0,0,314,305,1,0,0,0,315,15,1,0,0,0,316,317,3,22,11,0,
        317,17,1,0,0,0,318,320,7,6,0,0,319,318,1,0,0,0,319,320,1,0,0,0,320,
        321,1,0,0,0,321,324,7,7,0,0,322,324,5,82,0,0,323,319,1,0,0,0,323,
        322,1,0,0,0,324,19,1,0,0,0,325,327,5,54,0,0,326,325,1,0,0,0,326,
        327,1,0,0,0,327,328,1,0,0,0,328,330,5,55,0,0,329,331,5,56,0,0,330,
        329,1,0,0,0,330,331,1,0,0,0,331,349,1,0,0,0,332,333,5,57,0,0,333,
        349,7,8,0,0,334,335,5,60,0,0,335,349,5,61,0,0,336,337,5,38,0,0,337,
        349,3,24,12,0,338,340,5,62,0,0,339,341,5,29,0,0,340,339,1,0,0,0,
        340,341,1,0,0,0,341,342,1,0,0,0,342,349,3,24,12,0,343,345,5,63,0,
        0,344,346,5,29,0,0,345,344,1,0,0,0,345,346,1,0,0,0,346,347,1,0,0,
        0,347,349,3,24,12,0,348,326,1,0,0,0,348,332,1,0,0,0,348,334,1,0,
        0,0,348,336,1,0,0,0,348,338,1,0,0,0,348,343,1,0,0,0,349,21,1,0,0,
        0,350,351,6,11,-1,0,351,352,7,6,0,0,352,368,3,22,11,12,353,368,5,
        73,0,0,354,355,5,74,0,0,355,356,5,39,0,0,356,357,3,22,11,0,357,358,
        5,40,0,0,358,368,1,0,0,0,359,368,5,80,0,0,360,368,5,81,0,0,361,368,
        5,82,0,0,362,368,3,24,12,0,363,364,5,39,0,0,364,365,3,22,11,0,365,
        366,5,40,0,0,366,368,1,0,0,0,367,350,1,0,0,0,367,353,1,0,0,0,367,
        354,1,0,0,0,367,359,1,0,0,0,367,360,1,0,0,0,367,361,1,0,0,0,367,
        362,1,0,0,0,367,363,1,0,0,0,368,383,1,0,0,0,369,370,10,11,0,0,370,
        371,7,9,0,0,371,382,3,22,11,12,372,373,10,10,0,0,373,374,7,6,0,0,
        374,382,3,22,11,11,375,376,10,9,0,0,376,377,7,10,0,0,377,382,3,22,
        11,10,378,379,10,8,0,0,379,380,7,11,0,0,380,382,3,22,11,9,381,369,
        1,0,0,0,381,372,1,0,0,0,381,375,1,0,0,0,381,378,1,0,0,0,382,385,
        1,0,0,0,383,381,1,0,0,0,383,384,1,0,0,0,384,23,1,0,0,0,385,383,1,
        0,0,0,386,388,5,83,0,0,387,389,7,12,0,0,388,387,1,0,0,0,388,389,
        1,0,0,0,389,401,1,0,0,0,390,391,5,39,0,0,391,396,3,22,11,0,392,393,
        5,12,0,0,393,395,3,22,11,0,394,392,1,0,0,0,395,398,1,0,0,0,396,394,
        1,0,0,0,396,397,1,0,0,0,397,399,1,0,0,0,398,396,1,0,0,0,399,400,
        5,40,0,0,400,402,1,0,0,0,401,390,1,0,0,0,401,402,1,0,0,0,402,25,
        1,0,0,0,61,29,34,41,44,50,57,60,74,79,90,97,99,105,109,114,118,120,
        123,143,147,155,164,170,176,179,182,184,191,196,198,203,207,211,
        217,227,238,245,249,257,268,281,284,287,292,298,302,311,314,319,
        323,326,330,340,345,348,367,381,383,388,396,401
    ]

class RSTSBasicParser ( Parser ):

    grammarFileName = "RSTSBasic.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "':'", "'\\'", "'WORD'", "'SINGLE'", "'DOUBLE'", 
                     "'BYTE'", "'LONG'", "'STRING'", "'='", "'PROGRAM'", 
                     "'DECLARE'", "','", "'PRINT'", "'#'", "';'", "'USING'", 
                     "'LET'", "'GOTO'", "'GOSUB'", "'RETURN'", "'RANDOMIZE'", 
                     "'FOR'", "'TO'", "'STEP'", "'NEXT'", "'READ'", "'DATA'", 
                     "'RESTORE'", "'KEY'", "'EQ'", "'IF'", "'THEN'", "'ELSE'", 
                     "'END'", "'ON'", "'ERROR'", "'RESUME'", "'MAP'", "'('", 
                     "')'", "'OPEN'", "'INPUT'", "'OUTPUT'", "'AS'", "'FILE'", 
                     "'CLOSE'", "'PUT'", "'GET'", "'CALL'", "'LINE'", "'DIM'", 
                     "'+'", "'-'", "'ORGANIZATION'", "'INDEXED'", "'FIXED'", 
                     "'ACCESS'", "'MODIFY'", "'WRITE'", "'ALLOW'", "'NONE'", 
                     "'PRIMARY'", "'ALTERNATE'", "'*'", "'/'", "'<'", "'>'", 
                     "'<='", "'>='", "'<>'", "'AND'", "'OR'", "'INKEY$'", 
                     "'CHR$'", "'%'", "'$'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "REM_COMMENT", "BANG_COMMENT", "LINE_CONT", 
                      "INT", "FLOAT", "STRING", "ID", "NEWLINE", "WS" ]

    RULE_program = 0
    RULE_line = 1
    RULE_labelDef = 2
    RULE_lineNumber = 3
    RULE_target = 4
    RULE_dataType = 5
    RULE_mapItem = 6
    RULE_statement = 7
    RULE_printItem = 8
    RULE_dataItem = 9
    RULE_openClause = 10
    RULE_expression = 11
    RULE_variable = 12

    ruleNames =  [ "program", "line", "labelDef", "lineNumber", "target", 
                   "dataType", "mapItem", "statement", "printItem", "dataItem", 
                   "openClause", "expression", "variable" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    T__23=24
    T__24=25
    T__25=26
    T__26=27
    T__27=28
    T__28=29
    T__29=30
    T__30=31
    T__31=32
    T__32=33
    T__33=34
    T__34=35
    T__35=36
    T__36=37
    T__37=38
    T__38=39
    T__39=40
    T__40=41
    T__41=42
    T__42=43
    T__43=44
    T__44=45
    T__45=46
    T__46=47
    T__47=48
    T__48=49
    T__49=50
    T__50=51
    T__51=52
    T__52=53
    T__53=54
    T__54=55
    T__55=56
    T__56=57
    T__57=58
    T__58=59
    T__59=60
    T__60=61
    T__61=62
    T__62=63
    T__63=64
    T__64=65
    T__65=66
    T__66=67
    T__67=68
    T__68=69
    T__69=70
    T__70=71
    T__71=72
    T__72=73
    T__73=74
    T__74=75
    T__75=76
    REM_COMMENT=77
    BANG_COMMENT=78
    LINE_CONT=79
    INT=80
    FLOAT=81
    STRING=82
    ID=83
    NEWLINE=84
    WS=85

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(RSTSBasicParser.EOF, 0)

        def line(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.LineContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.LineContext,i)


        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.StatementContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.StatementContext,i)


        def lineNumber(self):
            return self.getTypedRuleContext(RSTSBasicParser.LineNumberContext,0)


        def labelDef(self):
            return self.getTypedRuleContext(RSTSBasicParser.LabelDefContext,0)


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProgram" ):
                return visitor.visitProgram(self)
            else:
                return visitor.visitChildren(self)




    def program(self):

        localctx = RSTSBasicParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,0,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 26
                    self.line() 
                self.state = 31
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,0,self._ctx)

            self.state = 44
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4440307353398272) != 0) or ((((_la - 77)) & ~0x3f) == 0 and ((1 << (_la - 77)) & 75) != 0):
                self.state = 34
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
                if la_ == 1:
                    self.state = 32
                    self.lineNumber()

                elif la_ == 2:
                    self.state = 33
                    self.labelDef()


                self.state = 36
                self.statement()
                self.state = 41
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==1 or _la==2:
                    self.state = 37
                    _la = self._input.LA(1)
                    if not(_la==1 or _la==2):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 38
                    self.statement()
                    self.state = 43
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 46
            self.match(RSTSBasicParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(RSTSBasicParser.NEWLINE, 0)

        def lineNumber(self):
            return self.getTypedRuleContext(RSTSBasicParser.LineNumberContext,0)


        def labelDef(self):
            return self.getTypedRuleContext(RSTSBasicParser.LabelDefContext,0)


        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.StatementContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.StatementContext,i)


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_line

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLine" ):
                listener.enterLine(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLine" ):
                listener.exitLine(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLine" ):
                return visitor.visitLine(self)
            else:
                return visitor.visitChildren(self)




    def line(self):

        localctx = RSTSBasicParser.LineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_line)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 50
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.state = 48
                self.lineNumber()

            elif la_ == 2:
                self.state = 49
                self.labelDef()


            self.state = 60
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4440307353398272) != 0) or ((((_la - 77)) & ~0x3f) == 0 and ((1 << (_la - 77)) & 67) != 0):
                self.state = 52
                self.statement()
                self.state = 57
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==1 or _la==2:
                    self.state = 53
                    _la = self._input.LA(1)
                    if not(_la==1 or _la==2):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 54
                    self.statement()
                    self.state = 59
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 62
            self.match(RSTSBasicParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LabelDefContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(RSTSBasicParser.ID, 0)

        def getRuleIndex(self):
            return RSTSBasicParser.RULE_labelDef

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLabelDef" ):
                listener.enterLabelDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLabelDef" ):
                listener.exitLabelDef(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLabelDef" ):
                return visitor.visitLabelDef(self)
            else:
                return visitor.visitChildren(self)




    def labelDef(self):

        localctx = RSTSBasicParser.LabelDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_labelDef)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 64
            self.match(RSTSBasicParser.ID)
            self.state = 65
            self.match(RSTSBasicParser.T__0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LineNumberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)

        def getRuleIndex(self):
            return RSTSBasicParser.RULE_lineNumber

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLineNumber" ):
                listener.enterLineNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLineNumber" ):
                listener.exitLineNumber(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLineNumber" ):
                return visitor.visitLineNumber(self)
            else:
                return visitor.visitChildren(self)




    def lineNumber(self):

        localctx = RSTSBasicParser.LineNumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_lineNumber)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 67
            self.match(RSTSBasicParser.INT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TargetContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)

        def ID(self):
            return self.getToken(RSTSBasicParser.ID, 0)

        def getRuleIndex(self):
            return RSTSBasicParser.RULE_target

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTarget" ):
                listener.enterTarget(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTarget" ):
                listener.exitTarget(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTarget" ):
                return visitor.visitTarget(self)
            else:
                return visitor.visitChildren(self)




    def target(self):

        localctx = RSTSBasicParser.TargetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_target)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 69
            _la = self._input.LA(1)
            if not(_la==80 or _la==83):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DataTypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_dataType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDataType" ):
                listener.enterDataType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDataType" ):
                listener.exitDataType(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDataType" ):
                return visitor.visitDataType(self)
            else:
                return visitor.visitChildren(self)




    def dataType(self):

        localctx = RSTSBasicParser.DataTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_dataType)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 71
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 504) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MapItemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)


        def dataType(self):
            return self.getTypedRuleContext(RSTSBasicParser.DataTypeContext,0)


        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)

        def getRuleIndex(self):
            return RSTSBasicParser.RULE_mapItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMapItem" ):
                listener.enterMapItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMapItem" ):
                listener.exitMapItem(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMapItem" ):
                return visitor.visitMapItem(self)
            else:
                return visitor.visitChildren(self)




    def mapItem(self):

        localctx = RSTSBasicParser.MapItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_mapItem)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 74
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 504) != 0):
                self.state = 73
                self.dataType()


            self.state = 76
            self.variable()
            self.state = 79
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==9:
                self.state = 77
                self.match(RSTSBasicParser.T__8)
                self.state = 78
                self.match(RSTSBasicParser.INT)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_statement

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class RemStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def REM_COMMENT(self):
            return self.getToken(RSTSBasicParser.REM_COMMENT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRemStmt" ):
                listener.enterRemStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRemStmt" ):
                listener.exitRemStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRemStmt" ):
                return visitor.visitRemStmt(self)
            else:
                return visitor.visitChildren(self)


    class EndIfStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEndIfStmt" ):
                listener.enterEndIfStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEndIfStmt" ):
                listener.exitEndIfStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEndIfStmt" ):
                return visitor.visitEndIfStmt(self)
            else:
                return visitor.visitChildren(self)


    class LetStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLetStmt" ):
                listener.enterLetStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLetStmt" ):
                listener.exitLetStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLetStmt" ):
                return visitor.visitLetStmt(self)
            else:
                return visitor.visitChildren(self)


    class ElseStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def statement(self):
            return self.getTypedRuleContext(RSTSBasicParser.StatementContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterElseStmt" ):
                listener.enterElseStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitElseStmt" ):
                listener.exitElseStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitElseStmt" ):
                return visitor.visitElseStmt(self)
            else:
                return visitor.visitChildren(self)


    class BangRemStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BANG_COMMENT(self):
            return self.getToken(RSTSBasicParser.BANG_COMMENT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBangRemStmt" ):
                listener.enterBangRemStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBangRemStmt" ):
                listener.exitBangRemStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBangRemStmt" ):
                return visitor.visitBangRemStmt(self)
            else:
                return visitor.visitChildren(self)


    class GosubStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def target(self):
            return self.getTypedRuleContext(RSTSBasicParser.TargetContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGosubStmt" ):
                listener.enterGosubStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGosubStmt" ):
                listener.exitGosubStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitGosubStmt" ):
                return visitor.visitGosubStmt(self)
            else:
                return visitor.visitChildren(self)


    class InputStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)
        def STRING(self):
            return self.getToken(RSTSBasicParser.STRING, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInputStmt" ):
                listener.enterInputStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInputStmt" ):
                listener.exitInputStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInputStmt" ):
                return visitor.visitInputStmt(self)
            else:
                return visitor.visitChildren(self)


    class DeclareStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def dataType(self):
            return self.getTypedRuleContext(RSTSBasicParser.DataTypeContext,0)

        def variable(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.VariableContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.VariableContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDeclareStmt" ):
                listener.enterDeclareStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDeclareStmt" ):
                listener.exitDeclareStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDeclareStmt" ):
                return visitor.visitDeclareStmt(self)
            else:
                return visitor.visitChildren(self)


    class ProgramStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def ID(self):
            return self.getToken(RSTSBasicParser.ID, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgramStmt" ):
                listener.enterProgramStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgramStmt" ):
                listener.exitProgramStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProgramStmt" ):
                return visitor.visitProgramStmt(self)
            else:
                return visitor.visitChildren(self)


    class IfBlockStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIfBlockStmt" ):
                listener.enterIfBlockStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIfBlockStmt" ):
                listener.exitIfBlockStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIfBlockStmt" ):
                return visitor.visitIfBlockStmt(self)
            else:
                return visitor.visitChildren(self)


    class ThenStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def statement(self):
            return self.getTypedRuleContext(RSTSBasicParser.StatementContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterThenStmt" ):
                listener.enterThenStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitThenStmt" ):
                listener.exitThenStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitThenStmt" ):
                return visitor.visitThenStmt(self)
            else:
                return visitor.visitChildren(self)


    class MapStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)

        def mapItem(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.MapItemContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.MapItemContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMapStmt" ):
                listener.enterMapStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMapStmt" ):
                listener.exitMapStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMapStmt" ):
                return visitor.visitMapStmt(self)
            else:
                return visitor.visitChildren(self)


    class RestoreStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INT(self, i:int=None):
            if i is None:
                return self.getTokens(RSTSBasicParser.INT)
            else:
                return self.getToken(RSTSBasicParser.INT, i)
        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRestoreStmt" ):
                listener.enterRestoreStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRestoreStmt" ):
                listener.exitRestoreStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRestoreStmt" ):
                return visitor.visitRestoreStmt(self)
            else:
                return visitor.visitChildren(self)


    class PutStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPutStmt" ):
                listener.enterPutStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPutStmt" ):
                listener.exitPutStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPutStmt" ):
                return visitor.visitPutStmt(self)
            else:
                return visitor.visitChildren(self)


    class CloseStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INT(self, i:int=None):
            if i is None:
                return self.getTokens(RSTSBasicParser.INT)
            else:
                return self.getToken(RSTSBasicParser.INT, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCloseStmt" ):
                listener.enterCloseStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCloseStmt" ):
                listener.exitCloseStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCloseStmt" ):
                return visitor.visitCloseStmt(self)
            else:
                return visitor.visitChildren(self)


    class ResumeStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def target(self):
            return self.getTypedRuleContext(RSTSBasicParser.TargetContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterResumeStmt" ):
                listener.enterResumeStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitResumeStmt" ):
                listener.exitResumeStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitResumeStmt" ):
                return visitor.visitResumeStmt(self)
            else:
                return visitor.visitChildren(self)


    class OnErrorStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def target(self):
            return self.getTypedRuleContext(RSTSBasicParser.TargetContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOnErrorStmt" ):
                listener.enterOnErrorStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOnErrorStmt" ):
                listener.exitOnErrorStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOnErrorStmt" ):
                return visitor.visitOnErrorStmt(self)
            else:
                return visitor.visitChildren(self)


    class ForStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.fromExpr = None # ExpressionContext
            self.toExpr = None # ExpressionContext
            self.stepExpr = None # ExpressionContext
            self.copyFrom(ctx)

        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterForStmt" ):
                listener.enterForStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitForStmt" ):
                listener.exitForStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitForStmt" ):
                return visitor.visitForStmt(self)
            else:
                return visitor.visitChildren(self)


    class RandomizeStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRandomizeStmt" ):
                listener.enterRandomizeStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRandomizeStmt" ):
                listener.exitRandomizeStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRandomizeStmt" ):
                return visitor.visitRandomizeStmt(self)
            else:
                return visitor.visitChildren(self)


    class GotoStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def target(self):
            return self.getTypedRuleContext(RSTSBasicParser.TargetContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGotoStmt" ):
                listener.enterGotoStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGotoStmt" ):
                listener.exitGotoStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitGotoStmt" ):
                return visitor.visitGotoStmt(self)
            else:
                return visitor.visitChildren(self)


    class ReturnStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReturnStmt" ):
                listener.enterReturnStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReturnStmt" ):
                listener.exitReturnStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitReturnStmt" ):
                return visitor.visitReturnStmt(self)
            else:
                return visitor.visitChildren(self)


    class OpenAnyStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)
        def openClause(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.OpenClauseContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.OpenClauseContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOpenAnyStmt" ):
                listener.enterOpenAnyStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOpenAnyStmt" ):
                listener.exitOpenAnyStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOpenAnyStmt" ):
                return visitor.visitOpenAnyStmt(self)
            else:
                return visitor.visitChildren(self)


    class DataStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def dataItem(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.DataItemContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.DataItemContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDataStmt" ):
                listener.enterDataStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDataStmt" ):
                listener.exitDataStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDataStmt" ):
                return visitor.visitDataStmt(self)
            else:
                return visitor.visitChildren(self)


    class EndStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEndStmt" ):
                listener.enterEndStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEndStmt" ):
                listener.exitEndStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEndStmt" ):
                return visitor.visitEndStmt(self)
            else:
                return visitor.visitChildren(self)


    class PrintStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.formatExpr = None # ExpressionContext
            self.copyFrom(ctx)

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)
        def printItem(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.PrintItemContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.PrintItemContext,i)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrintStmt" ):
                listener.enterPrintStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrintStmt" ):
                listener.exitPrintStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrintStmt" ):
                return visitor.visitPrintStmt(self)
            else:
                return visitor.visitChildren(self)


    class CallStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STRING(self):
            return self.getToken(RSTSBasicParser.STRING, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCallStmt" ):
                listener.enterCallStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCallStmt" ):
                listener.exitCallStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCallStmt" ):
                return visitor.visitCallStmt(self)
            else:
                return visitor.visitChildren(self)


    class DimStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def variable(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.VariableContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.VariableContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDimStmt" ):
                listener.enterDimStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDimStmt" ):
                listener.exitDimStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDimStmt" ):
                return visitor.visitDimStmt(self)
            else:
                return visitor.visitChildren(self)


    class ReadStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def variable(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.VariableContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.VariableContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReadStmt" ):
                listener.enterReadStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReadStmt" ):
                listener.exitReadStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitReadStmt" ):
                return visitor.visitReadStmt(self)
            else:
                return visitor.visitChildren(self)


    class IfStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.thenStmt = None # StatementContext
            self.thenTarget = None # TargetContext
            self.elseStmt = None # StatementContext
            self.elseTarget = None # TargetContext
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.StatementContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.StatementContext,i)

        def target(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.TargetContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.TargetContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIfStmt" ):
                listener.enterIfStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIfStmt" ):
                listener.exitIfStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIfStmt" ):
                return visitor.visitIfStmt(self)
            else:
                return visitor.visitChildren(self)


    class GetStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INT(self, i:int=None):
            if i is None:
                return self.getTokens(RSTSBasicParser.INT)
            else:
                return self.getToken(RSTSBasicParser.INT, i)
        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGetStmt" ):
                listener.enterGetStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGetStmt" ):
                listener.exitGetStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitGetStmt" ):
                return visitor.visitGetStmt(self)
            else:
                return visitor.visitChildren(self)


    class NextStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNextStmt" ):
                listener.enterNextStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNextStmt" ):
                listener.exitNextStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNextStmt" ):
                return visitor.visitNextStmt(self)
            else:
                return visitor.visitChildren(self)



    def statement(self):

        localctx = RSTSBasicParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_statement)
        self._la = 0 # Token type
        try:
            self.state = 314
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,47,self._ctx)
            if la_ == 1:
                localctx = RSTSBasicParser.ProgramStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 81
                self.match(RSTSBasicParser.T__9)
                self.state = 82
                self.match(RSTSBasicParser.ID)
                pass

            elif la_ == 2:
                localctx = RSTSBasicParser.DeclareStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 83
                self.match(RSTSBasicParser.T__10)
                self.state = 84
                self.dataType()
                self.state = 85
                self.variable()
                self.state = 90
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 86
                    self.match(RSTSBasicParser.T__11)
                    self.state = 87
                    self.variable()
                    self.state = 92
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 3:
                localctx = RSTSBasicParser.PrintStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 93
                self.match(RSTSBasicParser.T__12)
                self.state = 99
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==14:
                    self.state = 94
                    self.match(RSTSBasicParser.T__13)
                    self.state = 95
                    self.match(RSTSBasicParser.INT)
                    self.state = 97
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==12 or _la==15:
                        self.state = 96
                        _la = self._input.LA(1)
                        if not(_la==12 or _la==15):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()




                self.state = 105
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==16:
                    self.state = 101
                    self.match(RSTSBasicParser.T__15)
                    self.state = 102
                    localctx.formatExpr = self.expression(0)
                    self.state = 103
                    self.match(RSTSBasicParser.T__14)


                self.state = 120
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if ((((_la - 39)) & ~0x3f) == 0 and ((1 << (_la - 39)) & 33036888465409) != 0):
                    self.state = 107
                    self.printItem()
                    self.state = 114
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,14,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 109
                            self._errHandler.sync(self)
                            _la = self._input.LA(1)
                            if _la==12 or _la==15:
                                self.state = 108
                                _la = self._input.LA(1)
                                if not(_la==12 or _la==15):
                                    self._errHandler.recoverInline(self)
                                else:
                                    self._errHandler.reportMatch(self)
                                    self.consume()


                            self.state = 111
                            self.printItem() 
                        self.state = 116
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,14,self._ctx)

                    self.state = 118
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==12 or _la==15:
                        self.state = 117
                        _la = self._input.LA(1)
                        if not(_la==12 or _la==15):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()




                pass

            elif la_ == 4:
                localctx = RSTSBasicParser.LetStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 123
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==17:
                    self.state = 122
                    self.match(RSTSBasicParser.T__16)


                self.state = 125
                self.variable()
                self.state = 126
                self.match(RSTSBasicParser.T__8)
                self.state = 127
                self.expression(0)
                pass

            elif la_ == 5:
                localctx = RSTSBasicParser.GotoStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 129
                self.match(RSTSBasicParser.T__17)
                self.state = 130
                self.target()
                pass

            elif la_ == 6:
                localctx = RSTSBasicParser.GosubStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 131
                self.match(RSTSBasicParser.T__18)
                self.state = 132
                self.target()
                pass

            elif la_ == 7:
                localctx = RSTSBasicParser.ReturnStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 133
                self.match(RSTSBasicParser.T__19)
                pass

            elif la_ == 8:
                localctx = RSTSBasicParser.RandomizeStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 8)
                self.state = 134
                self.match(RSTSBasicParser.T__20)
                pass

            elif la_ == 9:
                localctx = RSTSBasicParser.ForStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 9)
                self.state = 135
                self.match(RSTSBasicParser.T__21)
                self.state = 136
                self.variable()
                self.state = 137
                self.match(RSTSBasicParser.T__8)
                self.state = 138
                localctx.fromExpr = self.expression(0)
                self.state = 139
                self.match(RSTSBasicParser.T__22)
                self.state = 140
                localctx.toExpr = self.expression(0)
                self.state = 143
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==24:
                    self.state = 141
                    self.match(RSTSBasicParser.T__23)
                    self.state = 142
                    localctx.stepExpr = self.expression(0)


                pass

            elif la_ == 10:
                localctx = RSTSBasicParser.NextStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 10)
                self.state = 145
                self.match(RSTSBasicParser.T__24)
                self.state = 147
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==83:
                    self.state = 146
                    self.variable()


                pass

            elif la_ == 11:
                localctx = RSTSBasicParser.ReadStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 11)
                self.state = 149
                self.match(RSTSBasicParser.T__25)
                self.state = 150
                self.variable()
                self.state = 155
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 151
                    self.match(RSTSBasicParser.T__11)
                    self.state = 152
                    self.variable()
                    self.state = 157
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 12:
                localctx = RSTSBasicParser.DataStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 12)
                self.state = 158
                self.match(RSTSBasicParser.T__26)
                self.state = 159
                self.dataItem()
                self.state = 164
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 160
                    self.match(RSTSBasicParser.T__11)
                    self.state = 161
                    self.dataItem()
                    self.state = 166
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 13:
                localctx = RSTSBasicParser.RestoreStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 13)
                self.state = 167
                self.match(RSTSBasicParser.T__27)
                self.state = 170
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==14:
                    self.state = 168
                    self.match(RSTSBasicParser.T__13)
                    self.state = 169
                    self.match(RSTSBasicParser.INT)


                self.state = 184
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==12:
                    self.state = 172
                    self.match(RSTSBasicParser.T__11)
                    self.state = 173
                    self.match(RSTSBasicParser.T__28)
                    self.state = 176
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==14:
                        self.state = 174
                        self.match(RSTSBasicParser.T__13)
                        self.state = 175
                        self.match(RSTSBasicParser.INT)


                    self.state = 182
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if (((_la) & ~0x3f) == 0 and ((1 << _la) & 13511349711667712) != 0) or ((((_la - 73)) & ~0x3f) == 0 and ((1 << (_la - 73)) & 1923) != 0):
                        self.state = 179
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==9 or _la==30:
                            self.state = 178
                            _la = self._input.LA(1)
                            if not(_la==9 or _la==30):
                                self._errHandler.recoverInline(self)
                            else:
                                self._errHandler.reportMatch(self)
                                self.consume()


                        self.state = 181
                        self.expression(0)




                pass

            elif la_ == 14:
                localctx = RSTSBasicParser.IfStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 14)
                self.state = 186
                self.match(RSTSBasicParser.T__30)
                self.state = 187
                self.expression(0)
                self.state = 188
                self.match(RSTSBasicParser.T__31)
                self.state = 191
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,27,self._ctx)
                if la_ == 1:
                    self.state = 189
                    localctx.thenStmt = self.statement()
                    pass

                elif la_ == 2:
                    self.state = 190
                    localctx.thenTarget = self.target()
                    pass


                self.state = 198
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,29,self._ctx)
                if la_ == 1:
                    self.state = 193
                    self.match(RSTSBasicParser.T__32)
                    self.state = 196
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,28,self._ctx)
                    if la_ == 1:
                        self.state = 194
                        localctx.elseStmt = self.statement()
                        pass

                    elif la_ == 2:
                        self.state = 195
                        localctx.elseTarget = self.target()
                        pass




                pass

            elif la_ == 15:
                localctx = RSTSBasicParser.IfBlockStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 15)
                self.state = 200
                self.match(RSTSBasicParser.T__30)
                self.state = 201
                self.expression(0)
                self.state = 203
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==32:
                    self.state = 202
                    self.match(RSTSBasicParser.T__31)


                pass

            elif la_ == 16:
                localctx = RSTSBasicParser.ThenStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 16)
                self.state = 205
                self.match(RSTSBasicParser.T__31)
                self.state = 207
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,31,self._ctx)
                if la_ == 1:
                    self.state = 206
                    self.statement()


                pass

            elif la_ == 17:
                localctx = RSTSBasicParser.ElseStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 17)
                self.state = 209
                self.match(RSTSBasicParser.T__32)
                self.state = 211
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,32,self._ctx)
                if la_ == 1:
                    self.state = 210
                    self.statement()


                pass

            elif la_ == 18:
                localctx = RSTSBasicParser.EndIfStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 18)
                self.state = 213
                self.match(RSTSBasicParser.T__33)
                self.state = 214
                self.match(RSTSBasicParser.T__30)
                pass

            elif la_ == 19:
                localctx = RSTSBasicParser.EndStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 19)
                self.state = 215
                self.match(RSTSBasicParser.T__33)
                self.state = 217
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==10:
                    self.state = 216
                    self.match(RSTSBasicParser.T__9)


                pass

            elif la_ == 20:
                localctx = RSTSBasicParser.RemStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 20)
                self.state = 219
                self.match(RSTSBasicParser.REM_COMMENT)
                pass

            elif la_ == 21:
                localctx = RSTSBasicParser.BangRemStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 21)
                self.state = 220
                self.match(RSTSBasicParser.BANG_COMMENT)
                pass

            elif la_ == 22:
                localctx = RSTSBasicParser.OnErrorStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 22)
                self.state = 221
                self.match(RSTSBasicParser.T__34)
                self.state = 222
                self.match(RSTSBasicParser.T__35)
                self.state = 223
                self.match(RSTSBasicParser.T__17)
                self.state = 224
                self.target()
                pass

            elif la_ == 23:
                localctx = RSTSBasicParser.ResumeStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 23)
                self.state = 225
                self.match(RSTSBasicParser.T__36)
                self.state = 227
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==80 or _la==83:
                    self.state = 226
                    self.target()


                pass

            elif la_ == 24:
                localctx = RSTSBasicParser.MapStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 24)
                self.state = 229
                self.match(RSTSBasicParser.T__37)
                self.state = 230
                self.match(RSTSBasicParser.T__38)
                self.state = 231
                self.variable()
                self.state = 232
                self.match(RSTSBasicParser.T__39)
                self.state = 233
                self.mapItem()
                self.state = 238
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 234
                    self.match(RSTSBasicParser.T__11)
                    self.state = 235
                    self.mapItem()
                    self.state = 240
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 25:
                localctx = RSTSBasicParser.OpenAnyStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 25)
                self.state = 241
                self.match(RSTSBasicParser.T__40)
                self.state = 242
                self.expression(0)
                self.state = 245
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==22:
                    self.state = 243
                    self.match(RSTSBasicParser.T__21)
                    self.state = 244
                    _la = self._input.LA(1)
                    if not(_la==42 or _la==43):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()


                self.state = 247
                self.match(RSTSBasicParser.T__43)
                self.state = 249
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==45:
                    self.state = 248
                    self.match(RSTSBasicParser.T__44)


                self.state = 251
                self.match(RSTSBasicParser.T__13)
                self.state = 252
                self.match(RSTSBasicParser.INT)
                self.state = 257
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 253
                    self.match(RSTSBasicParser.T__11)
                    self.state = 254
                    self.openClause()
                    self.state = 259
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 26:
                localctx = RSTSBasicParser.CloseStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 26)
                self.state = 260
                self.match(RSTSBasicParser.T__45)
                self.state = 261
                self.match(RSTSBasicParser.T__13)
                self.state = 262
                self.match(RSTSBasicParser.INT)
                self.state = 268
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 263
                    self.match(RSTSBasicParser.T__11)
                    self.state = 264
                    self.match(RSTSBasicParser.T__13)
                    self.state = 265
                    self.match(RSTSBasicParser.INT)
                    self.state = 270
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 27:
                localctx = RSTSBasicParser.PutStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 27)
                self.state = 271
                self.match(RSTSBasicParser.T__46)
                self.state = 272
                self.match(RSTSBasicParser.T__13)
                self.state = 273
                self.match(RSTSBasicParser.INT)
                pass

            elif la_ == 28:
                localctx = RSTSBasicParser.GetStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 28)
                self.state = 274
                self.match(RSTSBasicParser.T__47)
                self.state = 275
                self.match(RSTSBasicParser.T__13)
                self.state = 276
                self.match(RSTSBasicParser.INT)
                self.state = 287
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==12:
                    self.state = 277
                    self.match(RSTSBasicParser.T__11)
                    self.state = 278
                    self.match(RSTSBasicParser.T__28)
                    self.state = 281
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==14:
                        self.state = 279
                        self.match(RSTSBasicParser.T__13)
                        self.state = 280
                        self.match(RSTSBasicParser.INT)


                    self.state = 284
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==9 or _la==30:
                        self.state = 283
                        _la = self._input.LA(1)
                        if not(_la==9 or _la==30):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()


                    self.state = 286
                    self.expression(0)


                pass

            elif la_ == 29:
                localctx = RSTSBasicParser.CallStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 29)
                self.state = 289
                self.match(RSTSBasicParser.T__48)
                self.state = 290
                self.match(RSTSBasicParser.STRING)
                pass

            elif la_ == 30:
                localctx = RSTSBasicParser.InputStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 30)
                self.state = 292
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==50:
                    self.state = 291
                    self.match(RSTSBasicParser.T__49)


                self.state = 294
                self.match(RSTSBasicParser.T__41)
                self.state = 298
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==14:
                    self.state = 295
                    self.match(RSTSBasicParser.T__13)
                    self.state = 296
                    self.match(RSTSBasicParser.INT)
                    self.state = 297
                    _la = self._input.LA(1)
                    if not(_la==12 or _la==15):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()


                self.state = 302
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==82:
                    self.state = 300
                    self.match(RSTSBasicParser.STRING)
                    self.state = 301
                    _la = self._input.LA(1)
                    if not(_la==12 or _la==15):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()


                self.state = 304
                self.variable()
                pass

            elif la_ == 31:
                localctx = RSTSBasicParser.DimStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 31)
                self.state = 305
                self.match(RSTSBasicParser.T__50)
                self.state = 306
                self.variable()
                self.state = 311
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 307
                    self.match(RSTSBasicParser.T__11)
                    self.state = 308
                    self.variable()
                    self.state = 313
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PrintItemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_printItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrintItem" ):
                listener.enterPrintItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrintItem" ):
                listener.exitPrintItem(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrintItem" ):
                return visitor.visitPrintItem(self)
            else:
                return visitor.visitChildren(self)




    def printItem(self):

        localctx = RSTSBasicParser.PrintItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_printItem)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 316
            self.expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DataItemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)

        def FLOAT(self):
            return self.getToken(RSTSBasicParser.FLOAT, 0)

        def STRING(self):
            return self.getToken(RSTSBasicParser.STRING, 0)

        def getRuleIndex(self):
            return RSTSBasicParser.RULE_dataItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDataItem" ):
                listener.enterDataItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDataItem" ):
                listener.exitDataItem(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDataItem" ):
                return visitor.visitDataItem(self)
            else:
                return visitor.visitChildren(self)




    def dataItem(self):

        localctx = RSTSBasicParser.DataItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_dataItem)
        self._la = 0 # Token type
        try:
            self.state = 323
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [52, 53, 80, 81]:
                self.enterOuterAlt(localctx, 1)
                self.state = 319
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==52 or _la==53:
                    self.state = 318
                    _la = self._input.LA(1)
                    if not(_la==52 or _la==53):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()


                self.state = 321
                _la = self._input.LA(1)
                if not(_la==80 or _la==81):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass
            elif token in [82]:
                self.enterOuterAlt(localctx, 2)
                self.state = 322
                self.match(RSTSBasicParser.STRING)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OpenClauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_openClause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOpenClause" ):
                listener.enterOpenClause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOpenClause" ):
                listener.exitOpenClause(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOpenClause" ):
                return visitor.visitOpenClause(self)
            else:
                return visitor.visitChildren(self)




    def openClause(self):

        localctx = RSTSBasicParser.OpenClauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_openClause)
        self._la = 0 # Token type
        try:
            self.state = 348
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [54, 55]:
                self.enterOuterAlt(localctx, 1)
                self.state = 326
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==54:
                    self.state = 325
                    self.match(RSTSBasicParser.T__53)


                self.state = 328
                self.match(RSTSBasicParser.T__54)
                self.state = 330
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==56:
                    self.state = 329
                    self.match(RSTSBasicParser.T__55)


                pass
            elif token in [57]:
                self.enterOuterAlt(localctx, 2)
                self.state = 332
                self.match(RSTSBasicParser.T__56)
                self.state = 333
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 864691128522244096) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass
            elif token in [60]:
                self.enterOuterAlt(localctx, 3)
                self.state = 334
                self.match(RSTSBasicParser.T__59)
                self.state = 335
                self.match(RSTSBasicParser.T__60)
                pass
            elif token in [38]:
                self.enterOuterAlt(localctx, 4)
                self.state = 336
                self.match(RSTSBasicParser.T__37)
                self.state = 337
                self.variable()
                pass
            elif token in [62]:
                self.enterOuterAlt(localctx, 5)
                self.state = 338
                self.match(RSTSBasicParser.T__61)
                self.state = 340
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==29:
                    self.state = 339
                    self.match(RSTSBasicParser.T__28)


                self.state = 342
                self.variable()
                pass
            elif token in [63]:
                self.enterOuterAlt(localctx, 6)
                self.state = 343
                self.match(RSTSBasicParser.T__62)
                self.state = 345
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==29:
                    self.state = 344
                    self.match(RSTSBasicParser.T__28)


                self.state = 347
                self.variable()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_expression

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class StrExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STRING(self):
            return self.getToken(RSTSBasicParser.STRING, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStrExpr" ):
                listener.enterStrExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStrExpr" ):
                listener.exitStrExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStrExpr" ):
                return visitor.visitStrExpr(self)
            else:
                return visitor.visitChildren(self)


    class FloatExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def FLOAT(self):
            return self.getToken(RSTSBasicParser.FLOAT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFloatExpr" ):
                listener.enterFloatExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFloatExpr" ):
                listener.exitFloatExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFloatExpr" ):
                return visitor.visitFloatExpr(self)
            else:
                return visitor.visitChildren(self)


    class VarExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVarExpr" ):
                listener.enterVarExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVarExpr" ):
                listener.exitVarExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVarExpr" ):
                return visitor.visitVarExpr(self)
            else:
                return visitor.visitChildren(self)


    class UnaryExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUnaryExpr" ):
                listener.enterUnaryExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUnaryExpr" ):
                listener.exitUnaryExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUnaryExpr" ):
                return visitor.visitUnaryExpr(self)
            else:
                return visitor.visitChildren(self)


    class IntExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIntExpr" ):
                listener.enterIntExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIntExpr" ):
                listener.exitIntExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIntExpr" ):
                return visitor.visitIntExpr(self)
            else:
                return visitor.visitChildren(self)


    class AddSubExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.left = None # ExpressionContext
            self.op = None # Token
            self.right = None # ExpressionContext
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddSubExpr" ):
                listener.enterAddSubExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddSubExpr" ):
                listener.exitAddSubExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddSubExpr" ):
                return visitor.visitAddSubExpr(self)
            else:
                return visitor.visitChildren(self)


    class LogicalExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.left = None # ExpressionContext
            self.op = None # Token
            self.right = None # ExpressionContext
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalExpr" ):
                listener.enterLogicalExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalExpr" ):
                listener.exitLogicalExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLogicalExpr" ):
                return visitor.visitLogicalExpr(self)
            else:
                return visitor.visitChildren(self)


    class ChrExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterChrExpr" ):
                listener.enterChrExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitChrExpr" ):
                listener.exitChrExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitChrExpr" ):
                return visitor.visitChrExpr(self)
            else:
                return visitor.visitChildren(self)


    class ParensExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParensExpr" ):
                listener.enterParensExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParensExpr" ):
                listener.exitParensExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParensExpr" ):
                return visitor.visitParensExpr(self)
            else:
                return visitor.visitChildren(self)


    class RelExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.left = None # ExpressionContext
            self.op = None # Token
            self.right = None # ExpressionContext
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelExpr" ):
                listener.enterRelExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelExpr" ):
                listener.exitRelExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelExpr" ):
                return visitor.visitRelExpr(self)
            else:
                return visitor.visitChildren(self)


    class MulDivExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.left = None # ExpressionContext
            self.op = None # Token
            self.right = None # ExpressionContext
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMulDivExpr" ):
                listener.enterMulDivExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMulDivExpr" ):
                listener.exitMulDivExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMulDivExpr" ):
                return visitor.visitMulDivExpr(self)
            else:
                return visitor.visitChildren(self)


    class InkeyExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInkeyExpr" ):
                listener.enterInkeyExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInkeyExpr" ):
                listener.exitInkeyExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInkeyExpr" ):
                return visitor.visitInkeyExpr(self)
            else:
                return visitor.visitChildren(self)



    def expression(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = RSTSBasicParser.ExpressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 22
        self.enterRecursionRule(localctx, 22, self.RULE_expression, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 367
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [52, 53]:
                localctx = RSTSBasicParser.UnaryExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 351
                localctx.op = self._input.LT(1)
                _la = self._input.LA(1)
                if not(_la==52 or _la==53):
                    localctx.op = self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 352
                self.expression(12)
                pass
            elif token in [73]:
                localctx = RSTSBasicParser.InkeyExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 353
                self.match(RSTSBasicParser.T__72)
                pass
            elif token in [74]:
                localctx = RSTSBasicParser.ChrExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 354
                self.match(RSTSBasicParser.T__73)
                self.state = 355
                self.match(RSTSBasicParser.T__38)
                self.state = 356
                self.expression(0)
                self.state = 357
                self.match(RSTSBasicParser.T__39)
                pass
            elif token in [80]:
                localctx = RSTSBasicParser.IntExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 359
                self.match(RSTSBasicParser.INT)
                pass
            elif token in [81]:
                localctx = RSTSBasicParser.FloatExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 360
                self.match(RSTSBasicParser.FLOAT)
                pass
            elif token in [82]:
                localctx = RSTSBasicParser.StrExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 361
                self.match(RSTSBasicParser.STRING)
                pass
            elif token in [83]:
                localctx = RSTSBasicParser.VarExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 362
                self.variable()
                pass
            elif token in [39]:
                localctx = RSTSBasicParser.ParensExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 363
                self.match(RSTSBasicParser.T__38)
                self.state = 364
                self.expression(0)
                self.state = 365
                self.match(RSTSBasicParser.T__39)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 383
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,57,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 381
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,56,self._ctx)
                    if la_ == 1:
                        localctx = RSTSBasicParser.MulDivExprContext(self, RSTSBasicParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 369
                        if not self.precpred(self._ctx, 11):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 11)")
                        self.state = 370
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==64 or _la==65):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 371
                        localctx.right = self.expression(12)
                        pass

                    elif la_ == 2:
                        localctx = RSTSBasicParser.AddSubExprContext(self, RSTSBasicParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 372
                        if not self.precpred(self._ctx, 10):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 10)")
                        self.state = 373
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==52 or _la==53):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 374
                        localctx.right = self.expression(11)
                        pass

                    elif la_ == 3:
                        localctx = RSTSBasicParser.RelExprContext(self, RSTSBasicParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 375
                        if not self.precpred(self._ctx, 9):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 9)")
                        self.state = 376
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(((((_la - 9)) & ~0x3f) == 0 and ((1 << (_la - 9)) & 4467570830351532033) != 0)):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 377
                        localctx.right = self.expression(10)
                        pass

                    elif la_ == 4:
                        localctx = RSTSBasicParser.LogicalExprContext(self, RSTSBasicParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 378
                        if not self.precpred(self._ctx, 8):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 8)")
                        self.state = 379
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==71 or _la==72):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 380
                        localctx.right = self.expression(9)
                        pass

             
                self.state = 385
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,57,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class VariableContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(RSTSBasicParser.ID, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,i)


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_variable

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVariable" ):
                listener.enterVariable(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVariable" ):
                listener.exitVariable(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVariable" ):
                return visitor.visitVariable(self)
            else:
                return visitor.visitChildren(self)




    def variable(self):

        localctx = RSTSBasicParser.VariableContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_variable)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 386
            self.match(RSTSBasicParser.ID)
            self.state = 388
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,58,self._ctx)
            if la_ == 1:
                self.state = 387
                _la = self._input.LA(1)
                if not(_la==75 or _la==76):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


            self.state = 401
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,60,self._ctx)
            if la_ == 1:
                self.state = 390
                self.match(RSTSBasicParser.T__38)
                self.state = 391
                self.expression(0)
                self.state = 396
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 392
                    self.match(RSTSBasicParser.T__11)
                    self.state = 393
                    self.expression(0)
                    self.state = 398
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 399
                self.match(RSTSBasicParser.T__39)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[11] = self.expression_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expression_sempred(self, localctx:ExpressionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 11)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 10)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 9)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 8)
         




