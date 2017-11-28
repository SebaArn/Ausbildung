module editedrngmodule
implicit none
private
public :: rng
public::init
contains 

subroutine init
integer,dimension(8)::tarray
real::tempr
integer::tempi,f,i
integer, allocatable::seed(:)
!seed groesse festlegen
call random_seed(size = i)
allocate(seed(i))
call date_and_time(values=tarray)
tempi = tarray(8)
seed = tempi + 37 * (/ (f-1, f = 1, i)/)
!seeden
call random_seed(put = seed)
deallocate (seed)

end subroutine init


function rng(high) result (res)
integer, intent(in)::high
integer::res
real::tempr
call random_number(tempr)
!anpassen der generierten float an gegebene min und max werte
res = tempr*high
!print *,tempr
end function rng

function rng(high,low)result (res)
integer, intent(in)::high,low
integer::res
real::tempr
call random_number(tempr)
!anpassen der generierten float an gegebene min und max werte
res = tempr*(high-low)+low
!print *,tempr
end function rng

end module editedrngmodule
