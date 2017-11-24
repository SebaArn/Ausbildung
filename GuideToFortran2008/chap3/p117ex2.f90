program integrate

use function2_module
use integral_module
use math_module, only : pi
implicit none

real:: x_min, x_max
real:: answer

x_min = 0
x_max = 2* pi
answer = integral(f,x_min,x_max, 0.01)
print *,"The integral is ", answer

end program integrate

