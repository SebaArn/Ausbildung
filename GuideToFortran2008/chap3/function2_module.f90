module function2_module
use math_module
implicit none
public
contains
function f(x) result(y)
real, intent(in) :: x
real :: y

y=( (e**x)-sin(2*x))

end function f

end module function2_module
