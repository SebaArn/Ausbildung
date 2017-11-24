program p105ex3
use rngmodule
implicit none

integer, parameter :: number_of_rolls = 1000
integer ::  c1,c2,c3,c4,c5,c6,c7,c8,c9,c10, i,heads,head5


call init
head5 = 0

!10 coinflips
do i= 1, number_of_rolls
heads=0
	c1 = rng(0,0,1)
	c2 = rng(0,0,1)
	c3 = rng(0,0,1)
	c4 = rng(0,0,1)
	c5 = rng(0,0,1)
	c6 = rng(0,0,1)
	c7 = rng(0,0,1)
	c8 = rng(0,0,1)
	c9 = rng(0,0,1)
	c10 = rng(0,0,1)


	heads = c1+c2+c3+c4+c5+c6+c7+c8+c9+c10
	if(heads .eq. 5)then
		head5 = head5 + 1
		end if
	end do

print *,head5

end program p105ex3
