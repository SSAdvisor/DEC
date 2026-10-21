# DEC RSTS/E BASIC-PLUS-2 User Guide & Quick Start

Welcome to the **DEC RSTS/E BASIC-PLUS-2** modern environment for Linux! This guide covers everything you need to know to get started writing, compiling, linking, running, and managing applications.

---

## 1. Quick Start

### 1.1 Setting Up Your Environment
After installing the distribution kit, activate the DEC environment:
```bash
# Source the environment variables (or add to your ~/.bashrc):
source /usr/local/dec-basic2/bin/basic_env.sh
```

To verify your installation:
```bash
basicc --help
basiclink --help
dcl "SHOW SYSTEM"
```

---

## 2. Writing Your First BASIC-PLUS-2 Program

Create a file named `hello.bas`:
```basic
10 ! HELLO.BAS - Sample Program
20 PRINT "Welcome to DEC BASIC-PLUS-2 on Linux!"
30 PRINT "Current Date: "; DATE$(0%); " Time: "; TIME$(0%)
40 FOR I% = 1% TO 5%
50   PRINT "Iteration "; I%; " Squared: "; I% * I%
60 NEXT I%
70 END
```

### 2.1 Compiling with `basicc`
Compile the program to a RSTS/E bytecode object module (`hello.obj`):
```bash
basicc hello.bas -o hello.obj
```

### 2.2 Linking with `basiclink`
Link the object module into a standalone native Linux executable:
```bash
basiclink hello.obj -o hello
```

### 2.3 Running Your Program
Execute the resulting binary directly:
```bash
./hello
```
Output:
```
Welcome to DEC BASIC-PLUS-2 on Linux!
Current Date: 14-Oct-26 Time: 11:45:12
Iteration 1 Squared: 1
Iteration 2 Squared: 4
Iteration 3 Squared: 9
Iteration 4 Squared: 16
Iteration 5 Squared: 25
```

---

## 3. Working with Overlays (ODL)

For large modular applications, use Overlay Description Language (`.odl`) files:
1. `main.bas`: Root program segment.
2. `func1.bas`, `func2.bas`: Subroutines compiled as overlay segments with `--module`:
   ```bash
   basicc main.bas -o main.obj
   basicc func1.bas -o func1.obj --module FUNC1
   basicc func2.bas -o func2.obj --module FUNC2
   ```
3. `app.odl`:
   ```odl
   .ROOT MAIN-O1
   O1: .FCTR FUNC1,FUNC2
   .END
   ```
4. Link all segments together:
   ```bash
   basiclink main.obj func1.obj func2.obj app.odl -o my_app
   ./my_app
   ```

---

## 4. Using the DIGITAL Command Language (DCL)

Launch the interactive DCL shell:
```bash
dcl
```

Inside DCL:
```dcl
$ SHOW SYSTEM
$ DIRECTORY *.bas
$ BASIC hello.bas
$ LINK hello
$ RUN hello
$ EXIT
```

Or execute automated batch command procedures:
```bash
dcl @samples/office/sales_batch.com
```

---

## 5. Editing with the DEC EDT Editor V3.0

Edit files using the authentic DEC EDT editor:
```bash
edt hello.bas
```
- At the `*` prompt (Line Mode):
  - `T WHOLE`: Type entire file.
  - `I`: Enter Insert Mode (terminate with `.` or `Ctrl-Z`).
  - `D 1:5`: Delete lines 1 through 5.
  - `S /old/new/`: Substitute string.
  - `CHANGE`: Enter VT100 full-screen screen editing mode.
  - `EXIT`: Save and exit.
  - `QUIT`: Abort without saving.

---

## 6. Print & Batch Services (PBS)

Submit files to background print queues:
```bash
dcl "PRINT hello.bas /QUEUE=LP0: /NAME=HELLO_JOB"
dcl "SHOW QUEUE LP0:"
```

Start the network print queue daemon:
```bash
dec-printq start
dec-printq status
```
