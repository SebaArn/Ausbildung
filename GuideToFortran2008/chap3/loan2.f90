program loan2
use loanmodule
implicit none
integer::i,m
real(kind=4) :: p,rannual,res,maxzahlung
real(kind=16):: kind
p=0
rannual=0
m=1000
res = 0
print *, "Darlehensbetrag eingeben"
read *,p
print *, "Jaehrliche Belastung eingeben"
read *,rannual
print *,"Maximale Monatszahlung eingeben"
read *,maxzahlung

call loanf_(p,rannual,m,res)

kind =(p*rannual)/12.0
print "(a,f12.2,a)","Der Monatliche Beitrag sollte über ",kind,"€ liegen." 
if (kind >= maxzahlung)then
        print*, "Der Kunde kann sich den Kredit bei der aktuellen Maximalzahlung nicht leisten"
	else
	print*, "Alles in Ordnung."
	end if
	
!print *,res
end program loan2
