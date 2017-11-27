program square_of_n
implicit none
integer, dimension(:),allocatable ::squares
integer::s_size,i

read *, s_size
allocate(squares(s_size))
do i=0,s_size
	squares(i)=i*i
	print *, squares(i)
end do



end program square_of_n
