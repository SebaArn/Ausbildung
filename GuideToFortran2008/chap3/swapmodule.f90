module swapmodule
implicit none
public

contains

subroutine swap(a,b)
real, intent(in out) :: a,b
real::temp
temp = a
a = b
b = temp
end subroutine swap
end module swapmodule
