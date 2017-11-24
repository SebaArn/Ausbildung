program pokerhand
use randomnumbermodule
use poker_module
implicit none
integer::card
char(len=10)::b

card = call random_int(0,51)
b= call suit(card)
print *,b
b= call face_falue(card)
print*,b


end program pokerhand
