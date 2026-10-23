⍝ ==============================================================================
⍝ DEC VAX APL V3.1-00 — Vector & Matrix Analytics Demo (DEMO.APL)
⍝ Digital Equipment Corporation VAX/VMS V5.5-2
⍝ ==============================================================================
'DEC VAX APL V3.1-00 — VAX/VMS VECTOR ANALYTICS'

⍝ Define user function AVG using del (∇) notation
∇ Z ← AVG V
Z ← (+/ V) ÷ (⍴ V)
∇

⍝ Generate 1..10 vector and compute reductions
VEC ← ⍳ 10
⎕← VEC
SUM ← +/ VEC
⎕← SUM
FACT5 ← ×/ ⍳ 5
⎕← FACT5
MAXV ← ⌈/ 14 92 37 88 51
⎕← MAXV
MINV ← ⌊/ 14 92 37 88 51
⎕← MINV
REVV ← ⌽ ⍳ 5
⎕← REVV
MEAN ← AVG 10 20 30 40 50
⎕← MEAN
)OFF
