;;; ==============================================================================
;;; DEC VAX LISP V3.1 — Symbolic Computation & Recursive Analytics Demo (DEMO.LSP)
;;; Digital Equipment Corporation VAX/VMS V5.5-2
;;; ==============================================================================

(defconstant *system-banner* "DEC VAX LISP V3.1 — SYMBOLIC PROCESSING ENGINE")

(defun factorial (n)
  (if (<= n 1)
      1
      (* n (factorial (1- n)))))

(defun fibonacci (n)
  (cond ((<= n 0) 0)
        ((= n 1) 1)
        (t (+ (fibonacci (- n 1)) (fibonacci (- n 2))))))

(defun sum-squares (lst)
  (apply #'+ (mapcar (lambda (x) (* x x)) lst)))

(format t "~A~%" *system-banner*)
(format t "FACTORIAL(6) = ~D~%" (factorial 6))
(format t "FIBONACCI(8) = ~D~%" (fibonacci 8))

(let* ((nums '(1 2 3 4 5))
       (rev  (reverse nums))
       (sq   (sum-squares nums)))
  (format t "REVERSED     = ~S~%" rev)
  (format t "SUM-SQUARES  = ~D~%" sq))
