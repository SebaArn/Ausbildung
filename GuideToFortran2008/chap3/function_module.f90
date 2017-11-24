module function_module
use math_module
implicit none
public
contains
function f(x) result(y)
real, intent(in) :: x
real :: y

y= (e**(-1*(x*x)))

end function f

end module function_module
