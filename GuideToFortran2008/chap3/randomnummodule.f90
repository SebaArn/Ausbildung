module randomnumbermodule
implicit none


contains
subroutine random_int(random_result, low, high)

integer, intent(out) :: random_result
integer, intent(in) :: low, high

real:: uniform_random_value

call random_number(uniform_random_value)

random_result = int((high - low + 1) * uniform_random_value + low)

end subroutine random_int

end module randomnumbermodule
