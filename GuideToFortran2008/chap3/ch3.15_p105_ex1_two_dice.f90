program rolling2or3or12
!use randomnumbermodule
use rngmodule
implicit none

integer, parameter :: number_of_rolls =1000
integer :: die1, die2, dice, i, wins
!integer::die1sum, die2sum
!use rngmodule

integer::f

!initialisierung der speicherwerte
wins = 0
!die1sum=0
!die2sum=0
!sorgt dafür, dass mit der aktuellen Zeit einmalig geseedet wird
call init

do i = 1, number_of_rolls
	dice = 0
	die1 = rng(0,1,6)
	die2 = rng(2,1,6)
	!die1sum=die1sum+die1
	!die2sum = die2sum+die2
	dice = die1+die2
	!print *,die1,die2,dice qualität von zufallszahlen sammlung
	select case (dice)
		case (2)
		wins = wins +1 
		case (3)		
		wins = wins + 1
		case (12)
		wins = wins + 1
		case default
		end select
	end do
!Rückgabe Prozentsatz der 12,2,3 Erwartungswehrt ~11 (%)
print *, 100.0*real(wins)/real(number_of_rolls)
!print *, die1sum, die2sum Zufallszahlenqualität rückgabe


end program rolling2or3or12

