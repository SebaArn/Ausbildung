module cone_volume_module
implicit none

contains

function volume(r,h) result(volum)
real,intent(in)::r,h
real::volum
	volum = 3.1415*(r*r)*h/3
	end function volume

end module cone_volume_module
