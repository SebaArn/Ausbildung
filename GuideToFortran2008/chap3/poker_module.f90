module poker_module
implicit none
!integer :: x,y
!private
!public::suit,face_value
!character(len=8)::f
public
contains


function suit(m) result f
	integer, intent(in)::m
	integer::x
	character(len=10)::f
	x = (m/12) 
	select case  (x)
		case (0)
	f= "Heart"
			case(1)
	f= "Spade"
		case (2)
	f = "club"
		case (3)
	f= "diamond"
	end select
end function suit



function face_value(n) result f
	integer, intent(in)::n
	integer::x
	character(len=10)::f
	x = mod(n,12)
	select case (x)
		case (1)
	f= "Ace"
		case (2)
	f= "2"	
	        case (3)
	f= "3"
        	case (4)
	f= "4"
       		 case (5)
	f= "5"
        	case (6)
	f= "6"
       	 	case (7)
	f= "7"
        	case (8)
	f= "8"
        	case (9)
	f= "9"
       		 case (10)
	f= "10" 
        	case (11)
	f= "Jack"
        	case (12)
	f= "Queen"
        	case (0)
	f= "King"
	end select
end function face_value
end module poker_module
