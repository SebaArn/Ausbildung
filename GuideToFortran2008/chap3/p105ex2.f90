program p105ex2
use rngmodule
implicit none

integer, parameter :: number_of_rolls = 1000
integer :: die_1, die_2, dice, i, wins4, wins7, longest, current

!read *, wins4
!initialisiert den Seedvorgang
call init

!call random_seed()
wins4 = 0
wins7 = 0
longest = 0
current = 0
do i= 1, number_of_rolls
	die_1 = rng(0, 1,6)
	die_2 = rng(0,1,6)
	dice = die_1 + die_2
	if(dice .eq. 7)then
		wins7 = wins7 + 1
	if (current .gt. longest)then
		longest = current	
		current = 0
	end if
	else if(dice .eq. 4) then
		wins4 = wins4 + 1
		if (current .gt. longest)then
			longest = current
			current = 0
		end if
	else
 	current = current +1
	end if
end do


print *, wins4, " mal die 4 vor 7"
print *, wins7, " mal die 7 vor 4"
print *, "und die längste durststrecke( es wurde lange werder 4 noch 7 gewürftelt) war: ",longest








end program p105ex2
