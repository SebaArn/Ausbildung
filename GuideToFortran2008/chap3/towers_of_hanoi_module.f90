module towers_of_hanoi_module
implicit none 
private
public::hanoi_

contains
recursive subroutine hanoi_(number_of_disks, starting_post, goal_post)
integer, intent(in)::number_of_disks, starting_post, goal_post
integer :: free_post
integer, parameter :: all_posts = 6
if (number_of_disks .gt. 0) then
free_post = all_posts - starting_post - goal_post
call hanoi_(number_of_disks - 1, starting_post, free_post)
print *, "Move disk ", number_of_disks, "from post ",starting_post, "to post ", goal_post
call hanoi_(number_of_disks - 1, free_post, goal_post)
end if
end subroutine hanoi_

end module towers_of_hanoi_module
