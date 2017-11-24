program poker
use rngmodule
use swapmodule
implicit none

real::first,second,third,fourth,fifth

call init

first = rng(1,1,52)
second= rng(1,1,52)
third = rng(1,1,52)
fourth= rng(1,1,52)
fifth = rng(1,1,52)



if(first .gt. second) then
	call swap(first,second)
end if
if(first .gt. third) then
	call swap(first,third)
end if
if(first .gt. fourth) then
	call swap(first,fourth)
end if
if (first .gt. fifth)then
	call swap(first, fifth)
end if
if(second .gt. third) then
	call swap(second,third)
end if
if(second .gt. fourth)then
	call swap(second,fourth)
end if
if(second .gt. fifth) then
	call swap(second,fifth)
end if
if (third .gt. fourth) then
	call swap(third,fourth)
end if
if(third .gt. fifth) then
	call swap (third,fifth)
end if
if(fourth .gt. fifth)then
	call swap(fourth,fifth)
end if


if(first .eq. second)then
second= rng(1,1,52)
end if
if (second .eq. third) then
third = rng(1,1,52)
end if
if(third .eq. fourth) then
fourth = rng(1,1,52)
end if
if(fourth .eq. fifth) then
fifth = rng (1,1,52)
end if


select case (Int(mod(first,13.0)))
	case (1)
	print*,"Ace"
	case(2)
	print *,"2"
	case(3)
	print*,"3"
	case(4)
	print*,"4"
	case(5)
	print*,"5"
	case(6)
	print*,"6"
	case(7)
        print*,"7"
        case(8)
        print*,"8"
        case(9)
        print*,"9"
        case(10)
        print*,"10"
        case(11)
        print*,"Jack"
        case(12)
        print*,"Queen"
        case(0)
        print*,"King"
	case default
	print*,"Error"	
	end select

select case(INT(first/13.0))
	case(0)
	print*,"Diamonds"
	case(1)
	print*,"Clubs"
	case(2)
	print*,"Hearts"
	case(3)
	print*,"Spades"
	case default
	print*,"Error"
	end select





end program poker
