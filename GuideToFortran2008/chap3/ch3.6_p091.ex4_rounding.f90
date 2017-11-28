
program rounding
implicit none

real(kind=16)::x,y
integer:: f,z

read *,x
read *,f
y = x * (0.1**(f))  
!sort für aufrunden falls >0.5
y = y + 0.5
!
z = INT(y)
!print *,z
y = z
y =  y* (10.0**(f))
x = y
write(*,20) x
20 format(3f15.2)

end program rounding
