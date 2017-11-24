module fofxmodule
implicit none

contains
recursive function f(x) result (y)
integer, intent (in)  ::  x
integer ::  y
if (x .le. 0) then
y = 0
else if(x .le. 2) then
y = 1
else
y = (2*f(x-1) + f(x-2) + 2* f(x-3))
end if
end function f

end module fofxmodule
