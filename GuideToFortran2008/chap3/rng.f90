program rng
!use date_and_time
real::r(5,5),num
real:: tempr
integer,Dimension(:), Allocatable::seed
integer::tempi,n
integer,dimension(8) :: tarray
character(len=1)::x
!call date_and_time(VALUES=tarray)
!tempi = tarray(8)

call random_seed(size = n)
allocate(seed(n))
call date_and_time(values=tarray)
tempi = tarray(8)
seed= tempi + 37 * (/ (i-1, i = 1, n)/)

call random_seed(put = seed)
deallocate (seed)
call random_number(tempr)
!print *,tempr

end program rng
