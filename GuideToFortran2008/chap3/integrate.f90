program integrate
use nonadaptive_integral_module
implicit none

intrinsic :: sin
print *, integral_na(sin, a=0.0, b=3.14159, n=100)

end program integrate
