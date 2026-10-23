-- ============================================================================
-- DEC VAX Ada V2.2 Demonstration Program (DEMO.ADA)
-- Digital Equipment Corporation VAX/VMS V5.5-2
-- ============================================================================
with TEXT_IO;
use TEXT_IO;

procedure VAXADADEMO is
    pragma IDENT("V02-02");

    BONUS_PCT : constant Integer := 18;

    type Employee_Record is record
        ID     : Integer;
        Name   : String(1 .. 40);
        Dept   : String(1 .. 40);
        Salary : Integer;
    end record;

    subtype Score_Index is Positive range 1 .. 5;

    Emp        : Employee_Record;
    Bonus      : Integer := 0;
    Total_Comp : Integer := 0;
    Acc_Score  : Natural := 0;
    Classification : String(1 .. 20);

    function Compute_Bonus(Base_Sal : Integer; Pct : Integer) return Integer is
    begin
        return (Base_Sal * Pct) / 100;
    end Compute_Bonus;

    procedure Print_Banner is
    begin
        Put_Line("============================================================");
        Put_Line("  DEC VAX ADA V2.2 ON VAX/VMS V5.5-2                        ");
        Put_Line("============================================================");
    end Print_Banner;

begin
    Print_Banner;

    Emp.ID     := 3015;
    Emp.Name   := "DR. JEAN ICHBIAH";
    Emp.Dept   := "VAX ADA COMPILER & ACS LIBRARY";
    Emp.Salary := 95000;

    Bonus      := Compute_Bonus(Emp.Salary, BONUS_PCT);
    Total_Comp := Emp.Salary + Bonus;

    for I in 1 .. 5 loop
        Acc_Score := Acc_Score + (I * 20);
    end loop;

    case Acc_Score is
        when 300 =>
            Classification := "MIL-STD-1815A GRADE A";
        when 200 .. 299 =>
            Classification := "MIL-STD-1815A GRADE B";
        when others =>
            Classification := "STANDARD";
    end case;

    Put_Line("EMPLOYEE ID: " & Integer'Image(Emp.ID));
    Put_Line("EMPLOYEE:    " & Emp.Name);
    Put_Line("DEPARTMENT:  " & Emp.Dept);
    Put_Line("BASE SALARY: " & Integer'Image(Emp.Salary));
    Put_Line("BONUS:       " & Integer'Image(Bonus));
    Put_Line("TOTAL COMP:  " & Integer'Image(Total_Comp));
    Put_Line("AUDIT SCORE: " & Integer'Image(Acc_Score) & " (" & Classification & ")");
    Put_Line("============================================================");
end VAXADADEMO;
