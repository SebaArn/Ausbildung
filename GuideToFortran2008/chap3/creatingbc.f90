program creatingbc
use bcmodule
integer :: a,b

print *, "N, über K, bitte N eingeben"
read *,a
print *, "Bitte K eingeben"
read *,b

a = bc(a,b)

print*, a

end program
