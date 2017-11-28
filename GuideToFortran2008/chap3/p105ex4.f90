program poker
use rngmodule
use swapmodule
implicit none

real::first,second,third,fourth,fifth

call init
!zufallszahlen zuweisen, das inkrementieren zusammen mit verringertem hochwert 
!verhindert doppelbelegung
first = rng(1,1,52)
second= rng(1,1,51)
if (second .ge. first) then
	second = second + 1
	end if
third = rng(1,1,50)
if (third .ge. first) then
	third = third +1
	end if
if (third .ge. second)then
	third = third +1
	end if
fourth= rng(1,1,49)
if (fourth .ge. first) then
	fourth = fourth +1
	end if
if (fourth .ge. second)then
	fourth = fourth + 1
	end if
if (fourth .ge. third)then
	fourth = fourth +1
	end if
fifth = rng(1,1,48)
if (fifth .ge. first) then
       fifth = fifth +1
	end if
if (fifth .ge. second)then
        fifth = fifth + 1
	end if
if (fifth .ge. third)then
        fifth = fifth +1
	end if
if(fifth .ge. fourth)then
	fifth= fifth + 1
	end if


!call sortc
!call reroll
!call sortc
!call reroll
!call sortc

print *, face_value(first)
print *, suit(first)
print *, face_value(second)
print *,  suit(second)
print *, face_value(third)
print *, suit(third)
print *, face_value(fourth)
print *,  suit(fourth)
print *, face_value(fifth)
print *, suit(fifth)

contains 
!sortiert
subroutine sortc()
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
end subroutine

!veraltet, wird nicht mehr verwendet
subroutine reroll
if(first .eq. second)then
	second= rng(1,1,51)
	if (second .ge. first) then
		second = second + 1
	end if
end if
if (second .eq. third) then
	third = rng(1,1,51)
	if (second .ge. third) then
                third = third + 1
        end if
end if
if(third .eq. fourth) then
	fourth = rng(1,1,51)
	if (third .ge. fourth) then
                fourth = fourth + 1
        end if

end if
if(fourth .eq. fifth) then
	fifth = rng (1,1,52)
end if
end subroutine

!gibt Ass bis King für die jeweiligen Werte aus
function face_value(n)result(re)
real, intent(in)::n
character(len=8)::re
select case (Int(mod(n,13.0)))
	case (1)
	re="Ace"
	case(2)
	re="2"
	case(3)
	re="3"
	case(4)
	re="4"
	case(5)
	re="5"
	case(6)
	re="6"
	case(7)
        re="7"
        case(8)
        re="8"
        case(9)
        re="9"
        case(10)
        re="10"
        case(11)
        re="Jack"
        case(12)
        re="Queen"
        case(0)
        re="King"
	case default
	re="Error"	
	end select
end function face_value
!gibt die Farbe karo,kreuz,herz,pik aus
function suit(m)result(res)
real, intent(in)::m
character(len=8)::res
select case(INT((m-1)/13.0))
	case(0)
	res="Diamonds"
	case(1)
	res="Clubs"
	case(2)
	res="Hearts"
	case(3)
	res="Spades"
!	case(4)
!	re="Diamonds"
	case default
	res="Error"
	end select
end function suit

end program poker
