program median_of_3
implicit none
integer:: a,b,c,d

read *,a,b,c


if ((a .ge. b) .and. (a .le. c)) then
	d = a
	end if
if ((a .ge. c) .and. (a .le. b)) then
	d = a
	end if
if((b .ge. a) .and. (b .le. c)) then
	d = b
	end if
if ((b .ge. c) .and. (b .le. a)) then
	d = b
	end  if
if((c .ge. b) .and. (c .le. a)) then
	d = c
	end if
if ((c .ge. a) .and. (c .le. b)) then
	d = c
	end if
print *,d

end program median_of_3
