program loan
use loanmodule
implicit none
integer::i,m
real(kind=4) :: p,rannual,res
real(kind=16):: kind
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
kind =p+m*res-(i*res+i*p/m)
        print"(a, i3,a, f14.2 ,a,f16.2)", "Monat  ", 0,"  zu zahlen:",0.00,"€. Restbetrag:   ", kind

do i = 1,m
kind=p+m*res-(i*res+i*p/m) 
	print"(a, i3,a,f16.2 ,a, f16.2)", "Monat  ", i ,"  zu zahlen:",(res+p/m),"€. Restbetrag:   ", kind
end do	
!print *,res
end program loan
