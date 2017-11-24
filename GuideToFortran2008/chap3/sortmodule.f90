module sortmodule
use swapmodule
implicit none
contains
subroutine sort_the_numbers(n1,n2,n3)
real, intent(in out) :: n1,n2,n3
if (n1 .GT. n2) then
call swap(n1, n2)
end if
if (n1 .gt. n3) then
call swap (n1, n3)
end if
if (n2 .gt. n3) then
call swap (n2, n3)
end if
end subroutine sort_the_numbers

end module sortmodule
