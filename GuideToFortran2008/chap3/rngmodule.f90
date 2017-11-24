module rngmodule
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


function rng(n,low,high) result (res)
integer, intent(in)::low,high,n
integer::res
real::tempr
call random_number(tempr)
!anpassen der generierten float an gegebene min und max werte
res = tempr*(high+1-low)+low+0.0
!print *,tempr
end function rng

end module rngmodule
