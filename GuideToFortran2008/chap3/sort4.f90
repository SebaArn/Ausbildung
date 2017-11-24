module sort4
use swapmodule
implicit none

contains
subroutine sort_4_numbers(i1,i2,i3,i4)
real, intent(in out) :: i1,i2,i3,i4
if(i1 .gt. i2) then
call swap(i1,i2)
end if
if(i1 .gt. i3) then
call swap(i1,i2)
end if
if(i1 .gt. i4) then
call swap(i1,i2)
end if
if(i2 .gt. i3) then
call swap(i1,i2)
end if
if(i2 .gt. i4) then
call swap(i1,i2)
end if
if(i3 .gt. i4) then
call swap(i1,i2)
end if

end subroutine sort_4_numbers

end module sort4
