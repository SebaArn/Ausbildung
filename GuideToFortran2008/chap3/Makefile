# Definitionen


# Default regel
all: exercise3.5_5.exe exercise3.5_0.exe


# Anderen regeln

########################################################
# Exercise #5 Page xx
########################################################
loanmodule.mod: loanmodule.f90
	gfortran -fsyntax-only $<

loanmodule.o: loanmodule.f90
	gfortran -c $< -o $@

loan.o: loan.f90 loanmodule.mod
	gfortran -c loan.f90 -o $@

exercise3.5_5.exe: loanmodule.o loan.o
	gfortran -o $@ loan.o loanmodule.o

test_exercise3.5_5:	exercise3.5_5.exe input_exercise3.5_5.txt
	./exercise3.5_5.exe < input_exercise3.5_5.txt

input_exercise3.5_5.txt:
	@echo "106500" > $@
	@echo "0.075" >> $@
	@echo "240" >> $@


exe3_5: exercise3.5_5.exe
 

########################################################
# Example #1 
########################################################
exercise3.5_0.exe: main.c
	gcc -o exercise3.5_0.exe main.c


clean:
	rm exercise3.5_1.exe exercise3.5_0.exe -f
	rm loanmodule.mod -f 
	rm input_exercise3.5_5.txt -f
#exercise3.5_5.exe: loanmodule.mod loan.f90 loanmodule.f90
#	gfortran -o $@ loan.f90 loanmodule.f90
