program hanoi
use towers_of_hanoi_module
implicit none

integer :: number_of_disks
read*, number_of_disks
print *, "Input data number_of_disks:", number_of_disks
print *
call hanoi_(number_of_disks,1,3) 


end program hanoi
