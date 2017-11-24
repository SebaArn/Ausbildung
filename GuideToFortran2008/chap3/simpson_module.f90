module simpson_module
use function3_module
implicit none

recursive function simpson(x,a,h) result y

y = (h/3)*( f(a-h)+4*f(a)+f(a+h)))

end function simpson

end module simpson_module
