
program rounding
implicit none

real(kind=16)::x,y
integer:: f,z
logical:: aufrunden
aufrunden = .FALSE.
read *,x
read *,f
y = x * (0.1**(f))  
print *,y
y = y+ 0.5
print *,y
z = INT(y)
print *,z
y = z
y =  y* (10.0**(f))
print *,y
x = y
write(*,20) x
20 format(3f15.2)
end program rounding
