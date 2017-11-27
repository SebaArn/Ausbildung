program values
implicit none
real,dimension(0:99)::values_
integer::i


do i= 0, 99
	values_(i) = i-100
end do

do i=0,99
print*,values_(i)
end do

end program values 

