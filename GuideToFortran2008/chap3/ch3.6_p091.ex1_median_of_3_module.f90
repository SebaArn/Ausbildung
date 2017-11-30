module median_of_3_module
implicit none

contains
function media3(a,b,c) result(median)
	integer,intent(in)::a,b,c
	integer::median
	if ((a .ge. b) .and. (a .le. c)) then
		median = a
		end if
	if ((a .ge. c) .and. (a .le. b)) then
		median = a
		end if
	if((b .ge. a) .and. (b .le. c)) then
		median = b
		end if
	if ((b .ge. c) .and. (b .le. a)) then
		median = b
		end  if
	if((c .ge. b) .and. (c .le. a)) then
		median = c
		end if
	if ((c .ge. a) .and. (c .le. b)) then
		median = c
		end if
	end function

end module median_of_3_module
