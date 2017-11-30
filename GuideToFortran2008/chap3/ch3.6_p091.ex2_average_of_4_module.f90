module average_of_4_module

implicit none

contains
function avg(a,b,c,d) result(average)
real, intent(in)::a,b,c,d
real::average

average=(a+b+c+d)/4.0
end function avg

end module average_of_4_module
