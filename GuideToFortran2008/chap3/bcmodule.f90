module bcmodule
implicit none



contains


recursive function bc(n,k) result(res)
integer, intent(in) :: n,k
integer :: res
if(k .le. 0)then
res= 1
else if(k .gt. n)then
res = 1
else
res =  (bc(n-1,k-1) +  bc(n-1,k))
end if
end function bc

end module bcmodule
