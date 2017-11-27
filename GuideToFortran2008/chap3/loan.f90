program loan
use loanmodule
implicit none
integer::i,m
real :: p,rannual,res

p=0
rannual=0
m=0
res = 0
print *, "Darlehensbetrag eingeben"
read *,p
print *, "Jaehrliche Belastung eingeben"
read *,rannual
print *,"Monate (dauer) eingeben"
read *,m

call loanf_(p,rannual,m,res)
        print"(a, i3,a, f10.2 ,a,f8.2,a,f8.2)", "Monat  ", 0,"  zu zahlen:",0.00,"€. Restbetrag: ", p+m*res-(i*res+i*p/m)

do i = 1,m
	print"(a, i3,a, f10.2 ,a,f8.2,a,f8.2)", "Monat  ", i ,"  zu zahlen:",(res+p/m),"€. Restbetrag: ", p+m*res-(i*res+i*p/m) 
end do	
!print *,res
end program loan
