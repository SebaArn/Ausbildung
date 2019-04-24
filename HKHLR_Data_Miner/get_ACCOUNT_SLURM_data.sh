#!/bin/bash
log_prefix="HKHLR_SLURM_Darmstadt_Account"
report_date=`date +$Y-%m-%d` 
report_week=`date +$V`

SLURM_METRIC_FORMAT_STRING="JobIDRaw,Account,User,ReqCPUS,ReqMem,ReqNodes,AllocNodes,AllocCPUS,NNodes,NCPUS,NTasks,State,CPUTimeRAW,ElapsedRaw,TotalCPU,SystemCPU,UserCPU,MinCPU,AveCPU,MaxDiskRead,AveDiskRead,MaxDiskWrite,AveDiskWrite,MaxRSS,AveRSS,Submit,Start,End,Layout,ReqTRES,AllocTRES,ReqGRES,AllocGRES,Cluster,Partition,Submit,Start,End"
export SLURM_TIME_FORMAT="%Y-%m-%d-%H-%M-%S"

#echo Arguments: $#
echo "get_SLURM_data.sh ACCOUNT/PROJECT_NAME [week]"
case $# in
	0) 
		echo No Arguments given. Aborting
		echo Usage:
		echo get_ACCOUNT_SLURM_data.sh ACCOUNT [PREFIX] START_DATE END_DATE

		exit
		;;
#		echo "Note: get_SLURM_data.sh {[start-date] end-date}*"
	1)
		account=$1
		echo "One argument given. Generating data for account $1 and current week $report_week"
		;;
	3)
		account=$1
		report_date=$2
		
		start_date=`date -d $2 +%Y-%m-%d`
		end_date=`date -d $3 +%Y-%m-%d`
		echo Two arguments given. Using range $start_date - $end_date
		;;
	4)
		log_prefix=$2
		account=$1
		start_date=`date -d $3 +%Y-%m-%d`
		end_date=`date -d $4 +%Y-%m-%d`
		echo Three arguments given. Using range $start_date - $end_date
		;;
	*)
		echo "More than three arguments given ($#): >$@<, aborting"
		exit
		;;
esac

log_prefix=$account

function slurm_week_of(){
	local week=$2 year=$1
	local week_num_of_Jan_1st week_day_of_Jan_1st
	local first_Mon
	local date_format="+%a %b %d %Y"
	local date_format="+%Y-%m-%d"
	week_num_of_Jan_1st=$(date -d $year-01-01 +%W)
	week_day_of_Jan_1st=$(date -d $year-01-01 +%u)

	if ((week_num_of_Jan_1st)); then
		first_Mon=$year-01-01
	else
		first_Mon=$year-01-$((01 + (7 - week_day_of_Jan_1st + 1) ))
																fi

	mon=$(date -d "$first_Mon +$((week - 1)) week" "$date_format")
	sun=$(date -d "$first_Mon +$((week - 1)) week + 6 day" "$date_format")
	
  echo "-S$mon -E$sun"

}

function slurm_month_of(){
	local week=$2 year=$1
	local week_num_of_Jan_1st week_day_of_Jan_1st
	local date_format="+%Y-%m-%d"
	local start=$1-$2-1
	local end=$1-$2-$(last_day_in_month_of $1 $2)
	start_date=$(date -d "$start" "$date_format")
	end_date=$(date -d "$end" "$date_format")
	echo "-S$start_date -E$end_date"
}

function last_day_in_month_of()
{
	echo `date -d "$1/$2/1 + 1 month - 1 day" "+%b - %d days"` | awk '{print $3}'
	
}


function last_week_of_year(){
	local date_offset=0
	local current_week
	for date_offset in `seq 0 6`; do	
#		echo Day `date -d "$1/12/31 - $date_offset day" +%j`
		current_week=`date -d "$1/12/31 - $date_offset day" +%V`
		if [ "$current_week" != "01" ]; then break;
		fi 
	done
	echo $current_week
}


#slurm_week_of $1 $2


start_year=`echo $start_date |tr "-" " " | awk '{print $1}'`
start_year=`date -d $start_date +%Y`
end_year=`date -d $end_date +%Y`
start_month=`date -d $start_date +%m`
end_month=`date -d $end_date +%m`
start_week=`date -d $start_date +%V`
start_week_year=`date -d $start_date +%G`
end_week=`date -d $end_date +%V`
end_week_year=`date -d $end_date +%G`

echo "Weekly reports starting with week $start_week of $start_week_year, ending with week $end_week of $end_week_year"
echo "Monthly reports starting with $start_month/$start_year, ending with $end_month/$end_year"

for y in `seq $start_year $end_year`; do
	echo Year = $y
	lwy=$(last_week_of_year $y)
	echo Last Week of Year $lwy
	if [ "$y" = "$start_year" ] && [ "$y" = "$end_year" ]; then
		echo "Case #1"
		mls=$start_month
		mle=$end_month

		wls=`date -d "$start_date" +%V`
		wle=`date -d "$end_date" +%V`

		else 
			if [ "$y" = "$start_year" ]; then
				echo "Case #2"
				mls=$start_month
				mle=12

				wls=`date -d "$start_date" +%V`
				wle=$(last_week_of_year $y)
			else if [ "$y" = "$end_year" ]; then
				echo "Case #3"
				mls=1
				mle=$end_month
				
				wls=1
				wle=`date -d "$end_date" +%V`
			else
				echo "Case #4"
				mls=1
				mle=12
				
				wls=1
				wle=$(last_week_of_year $y)
			fi
		fi
	fi
	echo "Plotting MOnths $mls to $mle"

	for m in `seq $mls $mle`; do
		echo "Plotting $y $m"
		# Generate file-name string from date
		filename_string=`echo $log_prefix $y $m | awk '{printf "%s_%4i-%02d.log",$1,$2,$3}'`
		#	echo Month-file-name $filename_string
		#i		echo "Generating logdata for $y-$m"
		if [ ! -f "$filename_string" ]; then
			echo "sudo sacct -A $account -n -P $(slurm_month_of $y $m) --format $SLURM_METRIC_FORMAT_STRING > $filename_string"
			sudo sacct -A $account -n -P $(slurm_month_of $y $m) --format $SLURM_METRIC_FORMAT_STRING > $filename_string
		else
			echo "$filename_string for period $(slurm_month_of $y $m) already exists"
		fi 
	done
	echo "Plotting Weeks"
  for w in `seq $wls $wle`; do
		# Generate file-name string from date
		filename_string=`echo $log_prefix $y $w | awk '{printf "%s_%.4i-W%02d.log",$1,$2,$3}'`
		echo Week-file-name $filename_string
		if [ ! -f "$filename_string" ]; then
			echo "sudo sacct -A $account -n -P $(slurm_week_of $y $w) --format $SLURM_METRIC_FORMAT_STRING > $filename_string"
			sudo sacct -A $account -n -P $(slurm_week_of $y $w) --format $SLURM_METRIC_FORMAT_STRING > $filename_string
		else
			echo "$filename_string for period $y-w$w already exists"
		fi 
	done
	
	echo Plotting Year:
	filename_string=`echo $log_prefix $y $w | awk '{printf "%s_%.4i-fullYear.log",$1,$2}'`
	if [ ! -f "$filename_string" ]; then			
		end_date=`date +%Y-%m-%d`
		start_date=`date -d "${end_date} - 1 year" +%Y-%m-%d`
		echo "sudo sacct -A $account -n -P -S $y-01-01 -E $y-12-31  --format $SLURM_METRIC_FORMAT_STRING > $filename_string"
		sudo sacct -A $account -n -P -S$y-01-01 -E $y-12-31  --format $SLURM_METRIC_FORMAT_STRING > $filename_string
	else
		echo "$filename_string for year $y already exists"
	fi
	
done
