
program rounding
implicit none

real(kind=16)::Input,y
integer:: Stellen,z
character(len=30)::formt
character(len=10)::temp

!character(len=*),parameter::formt="    "


read *,Input
read *,Stellen
temp = char(Stellen)
formt = "(3f."//temp//")"
y = Input * (0.1**(Stellen))  
!sort für aufrunden falls >0.5
y = y + 0.5
!
z = INT(y)
!print *,z
y = z
y =  y* (10.0**(Stellen))
print *, formt
!print formt, y

end program rounding
