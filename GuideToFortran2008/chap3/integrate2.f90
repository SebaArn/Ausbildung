program integrate2
use integral_module
use function_module
use math_module, only : pi
implicit none

real:: x_min, x_max
real:: answer

x_min = -0
x_max = 2*pi

answer = integral(f,x_min,x_max,0.01)
print "(a,f11.6)","The integral is aproximately", answer
print"(a,f11.6)", "The exact answer is      ", sqrt(pi)

end program integrate2
