module loanmodule
implicit none
public
contains

subroutine loanf_(p,rannual,m,res)
real, intent(in out):: p,rannual,res
integer,intent(in out):: m
real :: r,d,e,f
!real, intent(in out)::res
r = (rannual)/12
d = r + 1
!res = 100
e=d**m
e=e*p
e=e*r
f=d**m
f= f-1


res = e/d

end subroutine loanf_

end module loanmodule
