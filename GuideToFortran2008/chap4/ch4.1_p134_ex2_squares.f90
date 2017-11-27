program squares
implicit none
integer, dimension(0:10)::squares_
integer::i,temp

squares_=[0,1,4,9,16,25,36,49,64,81,10]

do i= 0,10
	print *,squares_(i)
end do

end program

