module nonadaptive_integral_module
implicit none
private
public::integral_na

contains
function integral_na(f,a,b,n) result(integral_result)


interface
	function f(x) result(f_result)	
	real, intent(in) :: x
	real :: f_result
end function f
	end interface
	real, intent(in) :: a,b
	real::integral_result	
	real::h,total
integer, intent(in) :: n
integer::i
h = (b-a)/n
total = 0.5*(f(a)+f(b))
do i = 1, n-1
total = total + f(a+i*h)
end do

end function integral_na
end module nonadaptive_integral_module
