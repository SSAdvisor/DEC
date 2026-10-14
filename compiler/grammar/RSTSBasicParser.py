# Generated from compiler/grammar/RSTSBasic.g4 by ANTLR 4.13.1
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
        4,1,83,401,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,1,0,5,0,
        28,8,0,10,0,12,0,31,9,0,1,0,1,0,3,0,35,8,0,1,0,1,0,1,0,5,0,40,8,
        0,10,0,12,0,43,9,0,3,0,45,8,0,1,0,1,0,1,1,1,1,3,1,51,8,1,1,1,1,1,
        1,1,5,1,56,8,1,10,1,12,1,59,9,1,3,1,61,8,1,1,1,1,1,1,2,1,2,1,2,1,
        3,1,3,1,4,1,4,1,5,1,5,1,6,3,6,75,8,6,1,6,1,6,1,6,3,6,80,8,6,1,7,
        1,7,1,7,1,7,1,7,1,7,1,7,5,7,89,8,7,10,7,12,7,92,9,7,1,7,1,7,1,7,
        1,7,3,7,98,8,7,3,7,100,8,7,1,7,1,7,1,7,1,7,3,7,106,8,7,1,7,1,7,3,
        7,110,8,7,1,7,5,7,113,8,7,10,7,12,7,116,9,7,1,7,3,7,119,8,7,3,7,
        121,8,7,1,7,3,7,124,8,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,
        1,7,1,7,1,7,1,7,1,7,3,7,141,8,7,1,7,1,7,3,7,145,8,7,1,7,1,7,1,7,
        1,7,5,7,151,8,7,10,7,12,7,154,9,7,1,7,1,7,1,7,1,7,5,7,160,8,7,10,
        7,12,7,163,9,7,1,7,1,7,1,7,3,7,168,8,7,1,7,1,7,1,7,1,7,3,7,174,8,
        7,1,7,3,7,177,8,7,1,7,3,7,180,8,7,3,7,182,8,7,1,7,1,7,1,7,1,7,1,
        7,3,7,189,8,7,1,7,1,7,1,7,3,7,194,8,7,3,7,196,8,7,1,7,1,7,1,7,3,
        7,201,8,7,1,7,1,7,3,7,205,8,7,1,7,1,7,3,7,209,8,7,1,7,1,7,1,7,1,
        7,3,7,215,8,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,3,7,225,8,7,1,7,1,
        7,1,7,1,7,1,7,1,7,1,7,5,7,234,8,7,10,7,12,7,237,9,7,1,7,1,7,1,7,
        1,7,3,7,243,8,7,1,7,1,7,3,7,247,8,7,1,7,1,7,1,7,1,7,5,7,253,8,7,
        10,7,12,7,256,9,7,1,7,1,7,1,7,1,7,1,7,1,7,5,7,264,8,7,10,7,12,7,
        267,9,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,3,7,279,8,7,1,7,
        3,7,282,8,7,1,7,3,7,285,8,7,1,7,1,7,1,7,3,7,290,8,7,1,7,1,7,1,7,
        1,7,3,7,296,8,7,1,7,1,7,3,7,300,8,7,1,7,1,7,1,7,1,7,1,7,5,7,307,
        8,7,10,7,12,7,310,9,7,3,7,312,8,7,1,8,1,8,1,9,3,9,317,8,9,1,9,1,
        9,3,9,321,8,9,1,10,3,10,324,8,10,1,10,1,10,3,10,328,8,10,1,10,1,
        10,1,10,1,10,1,10,1,10,1,10,1,10,3,10,338,8,10,1,10,1,10,1,10,3,
        10,343,8,10,1,10,3,10,346,8,10,1,11,1,11,1,11,1,11,1,11,1,11,1,11,
        1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,3,11,365,8,11,
        1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,5,11,
        379,8,11,10,11,12,11,382,9,11,1,12,1,12,3,12,386,8,12,1,12,1,12,
        1,12,1,12,5,12,392,8,12,10,12,12,12,395,9,12,1,12,1,12,3,12,399,
        8,12,1,12,0,1,22,13,0,2,4,6,8,10,12,14,16,18,20,22,24,0,13,1,0,1,
        2,2,0,78,78,81,81,1,0,3,8,2,0,12,12,15,15,2,0,9,9,28,28,1,0,40,41,
        1,0,50,51,1,0,78,79,2,0,24,24,56,57,1,0,62,63,2,0,9,9,64,68,1,0,
        69,70,1,0,73,74,489,0,29,1,0,0,0,2,50,1,0,0,0,4,64,1,0,0,0,6,67,
        1,0,0,0,8,69,1,0,0,0,10,71,1,0,0,0,12,74,1,0,0,0,14,311,1,0,0,0,
        16,313,1,0,0,0,18,320,1,0,0,0,20,345,1,0,0,0,22,364,1,0,0,0,24,383,
        1,0,0,0,26,28,3,2,1,0,27,26,1,0,0,0,28,31,1,0,0,0,29,27,1,0,0,0,
        29,30,1,0,0,0,30,44,1,0,0,0,31,29,1,0,0,0,32,35,3,6,3,0,33,35,3,
        4,2,0,34,32,1,0,0,0,34,33,1,0,0,0,34,35,1,0,0,0,35,36,1,0,0,0,36,
        41,3,14,7,0,37,38,7,0,0,0,38,40,3,14,7,0,39,37,1,0,0,0,40,43,1,0,
        0,0,41,39,1,0,0,0,41,42,1,0,0,0,42,45,1,0,0,0,43,41,1,0,0,0,44,34,
        1,0,0,0,44,45,1,0,0,0,45,46,1,0,0,0,46,47,5,0,0,1,47,1,1,0,0,0,48,
        51,3,6,3,0,49,51,3,4,2,0,50,48,1,0,0,0,50,49,1,0,0,0,50,51,1,0,0,
        0,51,60,1,0,0,0,52,57,3,14,7,0,53,54,7,0,0,0,54,56,3,14,7,0,55,53,
        1,0,0,0,56,59,1,0,0,0,57,55,1,0,0,0,57,58,1,0,0,0,58,61,1,0,0,0,
        59,57,1,0,0,0,60,52,1,0,0,0,60,61,1,0,0,0,61,62,1,0,0,0,62,63,5,
        82,0,0,63,3,1,0,0,0,64,65,5,81,0,0,65,66,5,1,0,0,66,5,1,0,0,0,67,
        68,5,78,0,0,68,7,1,0,0,0,69,70,7,1,0,0,70,9,1,0,0,0,71,72,7,2,0,
        0,72,11,1,0,0,0,73,75,3,10,5,0,74,73,1,0,0,0,74,75,1,0,0,0,75,76,
        1,0,0,0,76,79,3,24,12,0,77,78,5,9,0,0,78,80,5,78,0,0,79,77,1,0,0,
        0,79,80,1,0,0,0,80,13,1,0,0,0,81,82,5,10,0,0,82,312,5,81,0,0,83,
        84,5,11,0,0,84,85,3,10,5,0,85,90,3,24,12,0,86,87,5,12,0,0,87,89,
        3,24,12,0,88,86,1,0,0,0,89,92,1,0,0,0,90,88,1,0,0,0,90,91,1,0,0,
        0,91,312,1,0,0,0,92,90,1,0,0,0,93,99,5,13,0,0,94,95,5,14,0,0,95,
        97,5,78,0,0,96,98,7,3,0,0,97,96,1,0,0,0,97,98,1,0,0,0,98,100,1,0,
        0,0,99,94,1,0,0,0,99,100,1,0,0,0,100,105,1,0,0,0,101,102,5,16,0,
        0,102,103,3,22,11,0,103,104,5,15,0,0,104,106,1,0,0,0,105,101,1,0,
        0,0,105,106,1,0,0,0,106,120,1,0,0,0,107,114,3,16,8,0,108,110,7,3,
        0,0,109,108,1,0,0,0,109,110,1,0,0,0,110,111,1,0,0,0,111,113,3,16,
        8,0,112,109,1,0,0,0,113,116,1,0,0,0,114,112,1,0,0,0,114,115,1,0,
        0,0,115,118,1,0,0,0,116,114,1,0,0,0,117,119,7,3,0,0,118,117,1,0,
        0,0,118,119,1,0,0,0,119,121,1,0,0,0,120,107,1,0,0,0,120,121,1,0,
        0,0,121,312,1,0,0,0,122,124,5,17,0,0,123,122,1,0,0,0,123,124,1,0,
        0,0,124,125,1,0,0,0,125,126,3,24,12,0,126,127,5,9,0,0,127,128,3,
        22,11,0,128,312,1,0,0,0,129,130,5,18,0,0,130,312,3,8,4,0,131,312,
        5,19,0,0,132,133,5,20,0,0,133,134,3,24,12,0,134,135,5,9,0,0,135,
        136,3,22,11,0,136,137,5,21,0,0,137,140,3,22,11,0,138,139,5,22,0,
        0,139,141,3,22,11,0,140,138,1,0,0,0,140,141,1,0,0,0,141,312,1,0,
        0,0,142,144,5,23,0,0,143,145,3,24,12,0,144,143,1,0,0,0,144,145,1,
        0,0,0,145,312,1,0,0,0,146,147,5,24,0,0,147,152,3,24,12,0,148,149,
        5,12,0,0,149,151,3,24,12,0,150,148,1,0,0,0,151,154,1,0,0,0,152,150,
        1,0,0,0,152,153,1,0,0,0,153,312,1,0,0,0,154,152,1,0,0,0,155,156,
        5,25,0,0,156,161,3,18,9,0,157,158,5,12,0,0,158,160,3,18,9,0,159,
        157,1,0,0,0,160,163,1,0,0,0,161,159,1,0,0,0,161,162,1,0,0,0,162,
        312,1,0,0,0,163,161,1,0,0,0,164,167,5,26,0,0,165,166,5,14,0,0,166,
        168,5,78,0,0,167,165,1,0,0,0,167,168,1,0,0,0,168,181,1,0,0,0,169,
        170,5,12,0,0,170,173,5,27,0,0,171,172,5,14,0,0,172,174,5,78,0,0,
        173,171,1,0,0,0,173,174,1,0,0,0,174,179,1,0,0,0,175,177,7,4,0,0,
        176,175,1,0,0,0,176,177,1,0,0,0,177,178,1,0,0,0,178,180,3,22,11,
        0,179,176,1,0,0,0,179,180,1,0,0,0,180,182,1,0,0,0,181,169,1,0,0,
        0,181,182,1,0,0,0,182,312,1,0,0,0,183,184,5,29,0,0,184,185,3,22,
        11,0,185,188,5,30,0,0,186,189,3,14,7,0,187,189,3,8,4,0,188,186,1,
        0,0,0,188,187,1,0,0,0,189,195,1,0,0,0,190,193,5,31,0,0,191,194,3,
        14,7,0,192,194,3,8,4,0,193,191,1,0,0,0,193,192,1,0,0,0,194,196,1,
        0,0,0,195,190,1,0,0,0,195,196,1,0,0,0,196,312,1,0,0,0,197,198,5,
        29,0,0,198,200,3,22,11,0,199,201,5,30,0,0,200,199,1,0,0,0,200,201,
        1,0,0,0,201,312,1,0,0,0,202,204,5,30,0,0,203,205,3,14,7,0,204,203,
        1,0,0,0,204,205,1,0,0,0,205,312,1,0,0,0,206,208,5,31,0,0,207,209,
        3,14,7,0,208,207,1,0,0,0,208,209,1,0,0,0,209,312,1,0,0,0,210,211,
        5,32,0,0,211,312,5,29,0,0,212,214,5,32,0,0,213,215,5,10,0,0,214,
        213,1,0,0,0,214,215,1,0,0,0,215,312,1,0,0,0,216,312,5,75,0,0,217,
        312,5,76,0,0,218,219,5,33,0,0,219,220,5,34,0,0,220,221,5,18,0,0,
        221,312,3,8,4,0,222,224,5,35,0,0,223,225,3,8,4,0,224,223,1,0,0,0,
        224,225,1,0,0,0,225,312,1,0,0,0,226,227,5,36,0,0,227,228,5,37,0,
        0,228,229,3,24,12,0,229,230,5,38,0,0,230,235,3,12,6,0,231,232,5,
        12,0,0,232,234,3,12,6,0,233,231,1,0,0,0,234,237,1,0,0,0,235,233,
        1,0,0,0,235,236,1,0,0,0,236,312,1,0,0,0,237,235,1,0,0,0,238,239,
        5,39,0,0,239,242,3,22,11,0,240,241,5,20,0,0,241,243,7,5,0,0,242,
        240,1,0,0,0,242,243,1,0,0,0,243,244,1,0,0,0,244,246,5,42,0,0,245,
        247,5,43,0,0,246,245,1,0,0,0,246,247,1,0,0,0,247,248,1,0,0,0,248,
        249,5,14,0,0,249,254,5,78,0,0,250,251,5,12,0,0,251,253,3,20,10,0,
        252,250,1,0,0,0,253,256,1,0,0,0,254,252,1,0,0,0,254,255,1,0,0,0,
        255,312,1,0,0,0,256,254,1,0,0,0,257,258,5,44,0,0,258,259,5,14,0,
        0,259,265,5,78,0,0,260,261,5,12,0,0,261,262,5,14,0,0,262,264,5,78,
        0,0,263,260,1,0,0,0,264,267,1,0,0,0,265,263,1,0,0,0,265,266,1,0,
        0,0,266,312,1,0,0,0,267,265,1,0,0,0,268,269,5,45,0,0,269,270,5,14,
        0,0,270,312,5,78,0,0,271,272,5,46,0,0,272,273,5,14,0,0,273,284,5,
        78,0,0,274,275,5,12,0,0,275,278,5,27,0,0,276,277,5,14,0,0,277,279,
        5,78,0,0,278,276,1,0,0,0,278,279,1,0,0,0,279,281,1,0,0,0,280,282,
        7,4,0,0,281,280,1,0,0,0,281,282,1,0,0,0,282,283,1,0,0,0,283,285,
        3,22,11,0,284,274,1,0,0,0,284,285,1,0,0,0,285,312,1,0,0,0,286,287,
        5,47,0,0,287,312,5,80,0,0,288,290,5,48,0,0,289,288,1,0,0,0,289,290,
        1,0,0,0,290,291,1,0,0,0,291,295,5,40,0,0,292,293,5,14,0,0,293,294,
        5,78,0,0,294,296,7,3,0,0,295,292,1,0,0,0,295,296,1,0,0,0,296,299,
        1,0,0,0,297,298,5,80,0,0,298,300,7,3,0,0,299,297,1,0,0,0,299,300,
        1,0,0,0,300,301,1,0,0,0,301,312,3,24,12,0,302,303,5,49,0,0,303,308,
        3,24,12,0,304,305,5,12,0,0,305,307,3,24,12,0,306,304,1,0,0,0,307,
        310,1,0,0,0,308,306,1,0,0,0,308,309,1,0,0,0,309,312,1,0,0,0,310,
        308,1,0,0,0,311,81,1,0,0,0,311,83,1,0,0,0,311,93,1,0,0,0,311,123,
        1,0,0,0,311,129,1,0,0,0,311,131,1,0,0,0,311,132,1,0,0,0,311,142,
        1,0,0,0,311,146,1,0,0,0,311,155,1,0,0,0,311,164,1,0,0,0,311,183,
        1,0,0,0,311,197,1,0,0,0,311,202,1,0,0,0,311,206,1,0,0,0,311,210,
        1,0,0,0,311,212,1,0,0,0,311,216,1,0,0,0,311,217,1,0,0,0,311,218,
        1,0,0,0,311,222,1,0,0,0,311,226,1,0,0,0,311,238,1,0,0,0,311,257,
        1,0,0,0,311,268,1,0,0,0,311,271,1,0,0,0,311,286,1,0,0,0,311,289,
        1,0,0,0,311,302,1,0,0,0,312,15,1,0,0,0,313,314,3,22,11,0,314,17,
        1,0,0,0,315,317,7,6,0,0,316,315,1,0,0,0,316,317,1,0,0,0,317,318,
        1,0,0,0,318,321,7,7,0,0,319,321,5,80,0,0,320,316,1,0,0,0,320,319,
        1,0,0,0,321,19,1,0,0,0,322,324,5,52,0,0,323,322,1,0,0,0,323,324,
        1,0,0,0,324,325,1,0,0,0,325,327,5,53,0,0,326,328,5,54,0,0,327,326,
        1,0,0,0,327,328,1,0,0,0,328,346,1,0,0,0,329,330,5,55,0,0,330,346,
        7,8,0,0,331,332,5,58,0,0,332,346,5,59,0,0,333,334,5,36,0,0,334,346,
        3,24,12,0,335,337,5,60,0,0,336,338,5,27,0,0,337,336,1,0,0,0,337,
        338,1,0,0,0,338,339,1,0,0,0,339,346,3,24,12,0,340,342,5,61,0,0,341,
        343,5,27,0,0,342,341,1,0,0,0,342,343,1,0,0,0,343,344,1,0,0,0,344,
        346,3,24,12,0,345,323,1,0,0,0,345,329,1,0,0,0,345,331,1,0,0,0,345,
        333,1,0,0,0,345,335,1,0,0,0,345,340,1,0,0,0,346,21,1,0,0,0,347,348,
        6,11,-1,0,348,349,7,6,0,0,349,365,3,22,11,12,350,365,5,71,0,0,351,
        352,5,72,0,0,352,353,5,37,0,0,353,354,3,22,11,0,354,355,5,38,0,0,
        355,365,1,0,0,0,356,365,5,78,0,0,357,365,5,79,0,0,358,365,5,80,0,
        0,359,365,3,24,12,0,360,361,5,37,0,0,361,362,3,22,11,0,362,363,5,
        38,0,0,363,365,1,0,0,0,364,347,1,0,0,0,364,350,1,0,0,0,364,351,1,
        0,0,0,364,356,1,0,0,0,364,357,1,0,0,0,364,358,1,0,0,0,364,359,1,
        0,0,0,364,360,1,0,0,0,365,380,1,0,0,0,366,367,10,11,0,0,367,368,
        7,9,0,0,368,379,3,22,11,12,369,370,10,10,0,0,370,371,7,6,0,0,371,
        379,3,22,11,11,372,373,10,9,0,0,373,374,7,10,0,0,374,379,3,22,11,
        10,375,376,10,8,0,0,376,377,7,11,0,0,377,379,3,22,11,9,378,366,1,
        0,0,0,378,369,1,0,0,0,378,372,1,0,0,0,378,375,1,0,0,0,379,382,1,
        0,0,0,380,378,1,0,0,0,380,381,1,0,0,0,381,23,1,0,0,0,382,380,1,0,
        0,0,383,385,5,81,0,0,384,386,7,12,0,0,385,384,1,0,0,0,385,386,1,
        0,0,0,386,398,1,0,0,0,387,388,5,37,0,0,388,393,3,22,11,0,389,390,
        5,12,0,0,390,392,3,22,11,0,391,389,1,0,0,0,392,395,1,0,0,0,393,391,
        1,0,0,0,393,394,1,0,0,0,394,396,1,0,0,0,395,393,1,0,0,0,396,397,
        5,38,0,0,397,399,1,0,0,0,398,387,1,0,0,0,398,399,1,0,0,0,399,25,
        1,0,0,0,61,29,34,41,44,50,57,60,74,79,90,97,99,105,109,114,118,120,
        123,140,144,152,161,167,173,176,179,181,188,193,195,200,204,208,
        214,224,235,242,246,254,265,278,281,284,289,295,299,308,311,316,
        320,323,327,337,342,345,364,378,380,385,393,398
    ]

class RSTSBasicParser ( Parser ):

    grammarFileName = "RSTSBasic.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "':'", "'\\'", "'WORD'", "'SINGLE'", "'DOUBLE'", 
                     "'BYTE'", "'LONG'", "'STRING'", "'='", "'PROGRAM'", 
                     "'DECLARE'", "','", "'PRINT'", "'#'", "';'", "'USING'", 
                     "'LET'", "'GOTO'", "'RANDOMIZE'", "'FOR'", "'TO'", 
                     "'STEP'", "'NEXT'", "'READ'", "'DATA'", "'RESTORE'", 
                     "'KEY'", "'EQ'", "'IF'", "'THEN'", "'ELSE'", "'END'", 
                     "'ON'", "'ERROR'", "'RESUME'", "'MAP'", "'('", "')'", 
                     "'OPEN'", "'INPUT'", "'OUTPUT'", "'AS'", "'FILE'", 
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
                      "<INVALID>", "<INVALID>", "<INVALID>", "REM_COMMENT", 
                      "BANG_COMMENT", "LINE_CONT", "INT", "FLOAT", "STRING", 
                      "ID", "NEWLINE", "WS" ]

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
    REM_COMMENT=75
    BANG_COMMENT=76
    LINE_CONT=77
    INT=78
    FLOAT=79
    STRING=80
    ID=81
    NEWLINE=82
    WS=83

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
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 1110076838259712) != 0) or ((((_la - 75)) & ~0x3f) == 0 and ((1 << (_la - 75)) & 75) != 0):
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
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 1110076838259712) != 0) or ((((_la - 75)) & ~0x3f) == 0 and ((1 << (_la - 75)) & 67) != 0):
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
            if not(_la==78 or _la==81):
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
            self.state = 311
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
                if ((((_la - 37)) & ~0x3f) == 0 and ((1 << (_la - 37)) & 33036888465409) != 0):
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
                localctx = RSTSBasicParser.RandomizeStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 131
                self.match(RSTSBasicParser.T__18)
                pass

            elif la_ == 7:
                localctx = RSTSBasicParser.ForStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 132
                self.match(RSTSBasicParser.T__19)
                self.state = 133
                self.variable()
                self.state = 134
                self.match(RSTSBasicParser.T__8)
                self.state = 135
                localctx.fromExpr = self.expression(0)
                self.state = 136
                self.match(RSTSBasicParser.T__20)
                self.state = 137
                localctx.toExpr = self.expression(0)
                self.state = 140
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==22:
                    self.state = 138
                    self.match(RSTSBasicParser.T__21)
                    self.state = 139
                    localctx.stepExpr = self.expression(0)


                pass

            elif la_ == 8:
                localctx = RSTSBasicParser.NextStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 8)
                self.state = 142
                self.match(RSTSBasicParser.T__22)
                self.state = 144
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==81:
                    self.state = 143
                    self.variable()


                pass

            elif la_ == 9:
                localctx = RSTSBasicParser.ReadStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 9)
                self.state = 146
                self.match(RSTSBasicParser.T__23)
                self.state = 147
                self.variable()
                self.state = 152
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 148
                    self.match(RSTSBasicParser.T__11)
                    self.state = 149
                    self.variable()
                    self.state = 154
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 10:
                localctx = RSTSBasicParser.DataStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 10)
                self.state = 155
                self.match(RSTSBasicParser.T__24)
                self.state = 156
                self.dataItem()
                self.state = 161
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 157
                    self.match(RSTSBasicParser.T__11)
                    self.state = 158
                    self.dataItem()
                    self.state = 163
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 11:
                localctx = RSTSBasicParser.RestoreStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 11)
                self.state = 164
                self.match(RSTSBasicParser.T__25)
                self.state = 167
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==14:
                    self.state = 165
                    self.match(RSTSBasicParser.T__13)
                    self.state = 166
                    self.match(RSTSBasicParser.INT)


                self.state = 181
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==12:
                    self.state = 169
                    self.match(RSTSBasicParser.T__11)
                    self.state = 170
                    self.match(RSTSBasicParser.T__26)
                    self.state = 173
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==14:
                        self.state = 171
                        self.match(RSTSBasicParser.T__13)
                        self.state = 172
                        self.match(RSTSBasicParser.INT)


                    self.state = 179
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if (((_la) & ~0x3f) == 0 and ((1 << _la) & 3377837427917312) != 0) or ((((_la - 71)) & ~0x3f) == 0 and ((1 << (_la - 71)) & 1923) != 0):
                        self.state = 176
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==9 or _la==28:
                            self.state = 175
                            _la = self._input.LA(1)
                            if not(_la==9 or _la==28):
                                self._errHandler.recoverInline(self)
                            else:
                                self._errHandler.reportMatch(self)
                                self.consume()


                        self.state = 178
                        self.expression(0)




                pass

            elif la_ == 12:
                localctx = RSTSBasicParser.IfStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 12)
                self.state = 183
                self.match(RSTSBasicParser.T__28)
                self.state = 184
                self.expression(0)
                self.state = 185
                self.match(RSTSBasicParser.T__29)
                self.state = 188
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,27,self._ctx)
                if la_ == 1:
                    self.state = 186
                    localctx.thenStmt = self.statement()
                    pass

                elif la_ == 2:
                    self.state = 187
                    localctx.thenTarget = self.target()
                    pass


                self.state = 195
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,29,self._ctx)
                if la_ == 1:
                    self.state = 190
                    self.match(RSTSBasicParser.T__30)
                    self.state = 193
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,28,self._ctx)
                    if la_ == 1:
                        self.state = 191
                        localctx.elseStmt = self.statement()
                        pass

                    elif la_ == 2:
                        self.state = 192
                        localctx.elseTarget = self.target()
                        pass




                pass

            elif la_ == 13:
                localctx = RSTSBasicParser.IfBlockStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 13)
                self.state = 197
                self.match(RSTSBasicParser.T__28)
                self.state = 198
                self.expression(0)
                self.state = 200
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==30:
                    self.state = 199
                    self.match(RSTSBasicParser.T__29)


                pass

            elif la_ == 14:
                localctx = RSTSBasicParser.ThenStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 14)
                self.state = 202
                self.match(RSTSBasicParser.T__29)
                self.state = 204
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,31,self._ctx)
                if la_ == 1:
                    self.state = 203
                    self.statement()


                pass

            elif la_ == 15:
                localctx = RSTSBasicParser.ElseStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 15)
                self.state = 206
                self.match(RSTSBasicParser.T__30)
                self.state = 208
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,32,self._ctx)
                if la_ == 1:
                    self.state = 207
                    self.statement()


                pass

            elif la_ == 16:
                localctx = RSTSBasicParser.EndIfStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 16)
                self.state = 210
                self.match(RSTSBasicParser.T__31)
                self.state = 211
                self.match(RSTSBasicParser.T__28)
                pass

            elif la_ == 17:
                localctx = RSTSBasicParser.EndStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 17)
                self.state = 212
                self.match(RSTSBasicParser.T__31)
                self.state = 214
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==10:
                    self.state = 213
                    self.match(RSTSBasicParser.T__9)


                pass

            elif la_ == 18:
                localctx = RSTSBasicParser.RemStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 18)
                self.state = 216
                self.match(RSTSBasicParser.REM_COMMENT)
                pass

            elif la_ == 19:
                localctx = RSTSBasicParser.BangRemStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 19)
                self.state = 217
                self.match(RSTSBasicParser.BANG_COMMENT)
                pass

            elif la_ == 20:
                localctx = RSTSBasicParser.OnErrorStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 20)
                self.state = 218
                self.match(RSTSBasicParser.T__32)
                self.state = 219
                self.match(RSTSBasicParser.T__33)
                self.state = 220
                self.match(RSTSBasicParser.T__17)
                self.state = 221
                self.target()
                pass

            elif la_ == 21:
                localctx = RSTSBasicParser.ResumeStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 21)
                self.state = 222
                self.match(RSTSBasicParser.T__34)
                self.state = 224
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==78 or _la==81:
                    self.state = 223
                    self.target()


                pass

            elif la_ == 22:
                localctx = RSTSBasicParser.MapStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 22)
                self.state = 226
                self.match(RSTSBasicParser.T__35)
                self.state = 227
                self.match(RSTSBasicParser.T__36)
                self.state = 228
                self.variable()
                self.state = 229
                self.match(RSTSBasicParser.T__37)
                self.state = 230
                self.mapItem()
                self.state = 235
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 231
                    self.match(RSTSBasicParser.T__11)
                    self.state = 232
                    self.mapItem()
                    self.state = 237
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 23:
                localctx = RSTSBasicParser.OpenAnyStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 23)
                self.state = 238
                self.match(RSTSBasicParser.T__38)
                self.state = 239
                self.expression(0)
                self.state = 242
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==20:
                    self.state = 240
                    self.match(RSTSBasicParser.T__19)
                    self.state = 241
                    _la = self._input.LA(1)
                    if not(_la==40 or _la==41):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()


                self.state = 244
                self.match(RSTSBasicParser.T__41)
                self.state = 246
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==43:
                    self.state = 245
                    self.match(RSTSBasicParser.T__42)


                self.state = 248
                self.match(RSTSBasicParser.T__13)
                self.state = 249
                self.match(RSTSBasicParser.INT)
                self.state = 254
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 250
                    self.match(RSTSBasicParser.T__11)
                    self.state = 251
                    self.openClause()
                    self.state = 256
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 24:
                localctx = RSTSBasicParser.CloseStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 24)
                self.state = 257
                self.match(RSTSBasicParser.T__43)
                self.state = 258
                self.match(RSTSBasicParser.T__13)
                self.state = 259
                self.match(RSTSBasicParser.INT)
                self.state = 265
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 260
                    self.match(RSTSBasicParser.T__11)
                    self.state = 261
                    self.match(RSTSBasicParser.T__13)
                    self.state = 262
                    self.match(RSTSBasicParser.INT)
                    self.state = 267
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 25:
                localctx = RSTSBasicParser.PutStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 25)
                self.state = 268
                self.match(RSTSBasicParser.T__44)
                self.state = 269
                self.match(RSTSBasicParser.T__13)
                self.state = 270
                self.match(RSTSBasicParser.INT)
                pass

            elif la_ == 26:
                localctx = RSTSBasicParser.GetStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 26)
                self.state = 271
                self.match(RSTSBasicParser.T__45)
                self.state = 272
                self.match(RSTSBasicParser.T__13)
                self.state = 273
                self.match(RSTSBasicParser.INT)
                self.state = 284
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==12:
                    self.state = 274
                    self.match(RSTSBasicParser.T__11)
                    self.state = 275
                    self.match(RSTSBasicParser.T__26)
                    self.state = 278
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==14:
                        self.state = 276
                        self.match(RSTSBasicParser.T__13)
                        self.state = 277
                        self.match(RSTSBasicParser.INT)


                    self.state = 281
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==9 or _la==28:
                        self.state = 280
                        _la = self._input.LA(1)
                        if not(_la==9 or _la==28):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()


                    self.state = 283
                    self.expression(0)


                pass

            elif la_ == 27:
                localctx = RSTSBasicParser.CallStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 27)
                self.state = 286
                self.match(RSTSBasicParser.T__46)
                self.state = 287
                self.match(RSTSBasicParser.STRING)
                pass

            elif la_ == 28:
                localctx = RSTSBasicParser.InputStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 28)
                self.state = 289
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==48:
                    self.state = 288
                    self.match(RSTSBasicParser.T__47)


                self.state = 291
                self.match(RSTSBasicParser.T__39)
                self.state = 295
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==14:
                    self.state = 292
                    self.match(RSTSBasicParser.T__13)
                    self.state = 293
                    self.match(RSTSBasicParser.INT)
                    self.state = 294
                    _la = self._input.LA(1)
                    if not(_la==12 or _la==15):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()


                self.state = 299
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==80:
                    self.state = 297
                    self.match(RSTSBasicParser.STRING)
                    self.state = 298
                    _la = self._input.LA(1)
                    if not(_la==12 or _la==15):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()


                self.state = 301
                self.variable()
                pass

            elif la_ == 29:
                localctx = RSTSBasicParser.DimStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 29)
                self.state = 302
                self.match(RSTSBasicParser.T__48)
                self.state = 303
                self.variable()
                self.state = 308
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 304
                    self.match(RSTSBasicParser.T__11)
                    self.state = 305
                    self.variable()
                    self.state = 310
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
            self.state = 313
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
            self.state = 320
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [50, 51, 78, 79]:
                self.enterOuterAlt(localctx, 1)
                self.state = 316
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==50 or _la==51:
                    self.state = 315
                    _la = self._input.LA(1)
                    if not(_la==50 or _la==51):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()


                self.state = 318
                _la = self._input.LA(1)
                if not(_la==78 or _la==79):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass
            elif token in [80]:
                self.enterOuterAlt(localctx, 2)
                self.state = 319
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
            self.state = 345
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [52, 53]:
                self.enterOuterAlt(localctx, 1)
                self.state = 323
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==52:
                    self.state = 322
                    self.match(RSTSBasicParser.T__51)


                self.state = 325
                self.match(RSTSBasicParser.T__52)
                self.state = 327
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==54:
                    self.state = 326
                    self.match(RSTSBasicParser.T__53)


                pass
            elif token in [55]:
                self.enterOuterAlt(localctx, 2)
                self.state = 329
                self.match(RSTSBasicParser.T__54)
                self.state = 330
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 216172782130561024) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass
            elif token in [58]:
                self.enterOuterAlt(localctx, 3)
                self.state = 331
                self.match(RSTSBasicParser.T__57)
                self.state = 332
                self.match(RSTSBasicParser.T__58)
                pass
            elif token in [36]:
                self.enterOuterAlt(localctx, 4)
                self.state = 333
                self.match(RSTSBasicParser.T__35)
                self.state = 334
                self.variable()
                pass
            elif token in [60]:
                self.enterOuterAlt(localctx, 5)
                self.state = 335
                self.match(RSTSBasicParser.T__59)
                self.state = 337
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==27:
                    self.state = 336
                    self.match(RSTSBasicParser.T__26)


                self.state = 339
                self.variable()
                pass
            elif token in [61]:
                self.enterOuterAlt(localctx, 6)
                self.state = 340
                self.match(RSTSBasicParser.T__60)
                self.state = 342
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==27:
                    self.state = 341
                    self.match(RSTSBasicParser.T__26)


                self.state = 344
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
            self.state = 364
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [50, 51]:
                localctx = RSTSBasicParser.UnaryExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 348
                localctx.op = self._input.LT(1)
                _la = self._input.LA(1)
                if not(_la==50 or _la==51):
                    localctx.op = self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 349
                self.expression(12)
                pass
            elif token in [71]:
                localctx = RSTSBasicParser.InkeyExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 350
                self.match(RSTSBasicParser.T__70)
                pass
            elif token in [72]:
                localctx = RSTSBasicParser.ChrExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 351
                self.match(RSTSBasicParser.T__71)
                self.state = 352
                self.match(RSTSBasicParser.T__36)
                self.state = 353
                self.expression(0)
                self.state = 354
                self.match(RSTSBasicParser.T__37)
                pass
            elif token in [78]:
                localctx = RSTSBasicParser.IntExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 356
                self.match(RSTSBasicParser.INT)
                pass
            elif token in [79]:
                localctx = RSTSBasicParser.FloatExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 357
                self.match(RSTSBasicParser.FLOAT)
                pass
            elif token in [80]:
                localctx = RSTSBasicParser.StrExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 358
                self.match(RSTSBasicParser.STRING)
                pass
            elif token in [81]:
                localctx = RSTSBasicParser.VarExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 359
                self.variable()
                pass
            elif token in [37]:
                localctx = RSTSBasicParser.ParensExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 360
                self.match(RSTSBasicParser.T__36)
                self.state = 361
                self.expression(0)
                self.state = 362
                self.match(RSTSBasicParser.T__37)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 380
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,57,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 378
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,56,self._ctx)
                    if la_ == 1:
                        localctx = RSTSBasicParser.MulDivExprContext(self, RSTSBasicParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 366
                        if not self.precpred(self._ctx, 11):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 11)")
                        self.state = 367
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==62 or _la==63):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 368
                        localctx.right = self.expression(12)
                        pass

                    elif la_ == 2:
                        localctx = RSTSBasicParser.AddSubExprContext(self, RSTSBasicParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 369
                        if not self.precpred(self._ctx, 10):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 10)")
                        self.state = 370
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==50 or _la==51):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 371
                        localctx.right = self.expression(11)
                        pass

                    elif la_ == 3:
                        localctx = RSTSBasicParser.RelExprContext(self, RSTSBasicParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 372
                        if not self.precpred(self._ctx, 9):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 9)")
                        self.state = 373
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(((((_la - 9)) & ~0x3f) == 0 and ((1 << (_la - 9)) & 1116892707587883009) != 0)):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 374
                        localctx.right = self.expression(10)
                        pass

                    elif la_ == 4:
                        localctx = RSTSBasicParser.LogicalExprContext(self, RSTSBasicParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 375
                        if not self.precpred(self._ctx, 8):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 8)")
                        self.state = 376
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==69 or _la==70):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 377
                        localctx.right = self.expression(9)
                        pass

             
                self.state = 382
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
            self.state = 383
            self.match(RSTSBasicParser.ID)
            self.state = 385
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,58,self._ctx)
            if la_ == 1:
                self.state = 384
                _la = self._input.LA(1)
                if not(_la==73 or _la==74):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


            self.state = 398
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,60,self._ctx)
            if la_ == 1:
                self.state = 387
                self.match(RSTSBasicParser.T__36)
                self.state = 388
                self.expression(0)
                self.state = 393
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 389
                    self.match(RSTSBasicParser.T__11)
                    self.state = 390
                    self.expression(0)
                    self.state = 395
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 396
                self.match(RSTSBasicParser.T__37)


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
         




