module gcdmodule
implicit none



contains


recursive function gcd(a,b) result(c)
integer, intent (in)  :: a,b
integer :: c

if(Mod(a,b) .eq. 0)then 
c = b
else
c = (gcd(b, (Mod (a,b))))
end if
end function gcd



end module gcdmodule
