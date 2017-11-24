program newfile
use sortmodule
implicit none

real:: a,b,c

a= 20.0
b= 30.0
c = 1.5


call sort_the_numbers(a,b,c)

print *, a,b,c



end program newfile
