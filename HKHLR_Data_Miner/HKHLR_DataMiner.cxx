#include <stdlib.h>
#include <stdio.h>
#include <string>
#include <fstream>
#include <iostream>
#include <vector>
#include <stdexcept>
#include <sstream>
#include <unordered_map>
#include <memory>
#include <iomanip>
#include <map>
#include <fstream>
#include <algorithm>
#include <omp.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#include <set>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <map>
#include "SLURM_Reader.h"
#include "SLURM_Structures.h"

using namespace std;

class Histogram
{
  protected:
	std::map<int, unsigned int> hist;
	int bucket_count;

  public:
	Histogram(int num_buckets = 10) : bucket_count(num_buckets)
	{
	}
	void clear()
	{
		hist.clear();
		for (int i = 0; i < (bucket_count + 1); i++)
			hist[i] = 0;
	}
	void add_experiment(int bucket)
	{
		if (bucket > (bucket_count + 1))
			hist[bucket_count]++;
		else
			hist[bucket]++;
	}
	unsigned long long int get_bucket_entry(int bucket_nr)
	{
		if (bucket_nr < bucket_count)
			return hist[bucket_nr];
		else
		{
			int count = 0;
			for (auto i = hist.find(10); i != hist.end(); i++)
				count += i->second;
			return count;
		}
	}
	std::string toString() const
	{
		stringstream ss;
		for (auto i : hist)
		{
			ss << i.second;
		};
		return ss.str();
	}
};

std::ostream &operator<<(std::ostream &os, Histogram const &p)
{
	return os << p.toString();
}

class ProjectEvaluation
{
  protected:
	std::vector<std::shared_ptr<SLURM_Task>> jobs;
	std::vector<long long int> filter_thresholds;
	std::vector<Histogram> cputime_efficiency_histograms,
		allocation_efficiency_histograms,
		memory_efficiency_histograms,
		min_efficiency_histograms;
	//	Histogram cputime_efficiency_histogram_all,cputime_efficiency_histogram_1cpuh,cputime_efficiency_histogram_cpu_min;
	//	std::map<int,unsigned int> cputime_efficiency_histogram;
	//	std::map<int,unsigned int> allocation_efficiency_histogram;
	//	std::map<int,unsigned int> memory_efficiency_histogram;
	//	std::map<int,unsigned int> min_efficiency_histogram;

	unsigned long completed_tasks, failed_tasks;
  public:
	int rank;
	void setRank(int rank){
		if (this->rank!=0) std::cerr << "rank overwrite" << std::endl;
		this->rank=rank;
	}
	std::string get_projectname()
	{
		return jobs[0]->project;
	};
	double get_project_allocation_CPUtime()
	{
		double CPUtime = 0;
		for (auto job : jobs)
			CPUtime += job->get_allocation_CPUtime();
		return CPUtime;
	}
	int get_number_of_filters() { return filter_thresholds.size(); }
	unsigned long long int get_filter_threshold(int number) { return filter_thresholds[number]; }
	std::vector<Histogram> &get_cputime_efficiency_histograms()
	{
		return cputime_efficiency_histograms;
	}
	std::vector<Histogram> &get_allocation_efficiency_histograms()
	{
		return allocation_efficiency_histograms;
	}
	std::vector<Histogram> &get_min_efficiency_histograms()
	{
		return min_efficiency_histograms;
	}
	std::vector<Histogram> &get_memory_efficiency_histograms()
	{
		return memory_efficiency_histograms;
	}
	void clear_histograms()
	{
		cputime_efficiency_histograms.clear();
		allocation_efficiency_histograms.clear();
		memory_efficiency_histograms.clear();
		min_efficiency_histograms.clear();
	}
	ProjectEvaluation()
	{
		rank=0;
		jobs.reserve(10000);
		filter_thresholds.push_back(0);
		completed_tasks = failed_tasks = 0;
		//		clear_histograms();
	}
	void add_filter_threshold(long long int threshold)
	{
		filter_thresholds.push_back(threshold);
		std::sort(filter_thresholds.begin(), filter_thresholds.end());
	}
	void add_task(std::shared_ptr<SLURM_Task> task)
	{
		jobs.push_back(task);
		if (task->job_state > 0)
			completed_tasks++;
		else
			failed_tasks++;
	}
	void generate_min_efficiency_histograms()
	{
		//		min_efficiency_histogrammin_efficiency_histogram
		//		min_efficiency_histogrammin_efficiency_histogram
		min_efficiency_histograms.clear();
		min_efficiency_histograms.resize(filter_thresholds.size());

		int bucket_count = 10;
		int efficiency = 100;
		// for all jobs
		for (auto i : jobs)
		{
			bool done = false;
			// compute the efficiency as the minimumg of memory, allocation and cputime
			efficiency = efficiency < i->compute_memory_efficiency() ? efficiency : i->compute_memory_efficiency();
			efficiency = efficiency < i->compute_cputime_efficiency() ? efficiency : i->compute_cputime_efficiency();
			efficiency = efficiency < i->compute_cpu_allocation_efficiency() ? efficiency : i->compute_cpu_allocation_efficiency();
			int bucket = efficiency / bucket_count;
			long long int cpuwalltime = i->compute_cpu_wall_time();
			int count = 0;
			// go through the filters in an increasing fasion and add while above the limit
			for (auto threshold : filter_thresholds)
			{
				if (cpuwalltime > threshold)
					min_efficiency_histograms[count++].add_experiment(bucket);
				else
					break;
			}
		}
	}

	void generate_memory_efficiency_histograms()
	{

		int bucket_count = 10;
		memory_efficiency_histograms.clear();
		memory_efficiency_histograms.resize(filter_thresholds.size());
		for (auto i : jobs)
		{
			int efficiency = i->compute_memory_efficiency();
			int bucket = efficiency / bucket_count;
			int count = 0;
			long long int cpuwalltime = i->compute_cpu_wall_time();
			for (auto threshold : filter_thresholds)
			{
				if (cpuwalltime > threshold)
					memory_efficiency_histograms[count++].add_experiment(bucket);
				else
					break;
			}
			//memory_efficiency_histogram[bucket]++;
		}
	}

	void generate_cputime_efficiency_histograms()
	{
		cputime_efficiency_histograms.clear();
		cputime_efficiency_histograms.resize(filter_thresholds.size());
		int bucket_count = 10;
		for (auto i : jobs)
		{
			int efficiency = i->compute_cputime_efficiency();
			int bucket = efficiency / bucket_count;
			int count = 0;
			long long int cpuwalltime = i->compute_cpu_wall_time();
			for (auto threshold : filter_thresholds)
			{
				if (cpuwalltime > threshold)
					cputime_efficiency_histograms[count++].add_experiment(bucket);
				else
					break;
			}
		}
	}

	void generate_allocation_efficiency_histograms()
	{
		int bucket_count = 10;
		allocation_efficiency_histograms.clear();
		allocation_efficiency_histograms.resize(filter_thresholds.size());
		//		for (int buckets=0;buckets<bucket_count;buckets++) allocation_efficiency_histogram[buckets]=0;
		for (auto i : jobs)
		{
			int efficiency = i->compute_cpu_allocation_efficiency();
			int bucket = efficiency / bucket_count;
			int count = 0;
			long long int cpuwalltime = i->compute_cpu_wall_time();
			for (auto threshold : filter_thresholds)
			{
				if (cpuwalltime > threshold)
					allocation_efficiency_histograms[count++].add_experiment(bucket);
				else
					break;
			}
		}
	}
	void generate_all_histograms()
	{
		generate_min_efficiency_histograms();
		generate_memory_efficiency_histograms();
		generate_cputime_efficiency_histograms();
		generate_allocation_efficiency_histograms();
	}

	std::string toString() const { return to_string(); }
	std::string to_string() const
	{
		stringstream ss;
		ss << "Number of Jobs: " << std::setw(9) << jobs.size() << "(" << completed_tasks << "," << failed_tasks << ")\t";
		//		for (auto i:cputime_efficiency_histograms[0].)
		//		ss<<cputime_efficiency_histograms[0].toString()<<std::string(" ");
		return ss.str();
	}

	/*
	int get_memory_efficiency_histogram_entry(int bucket_nr){
		if (bucket_nr<10)
		return memory_efficiency_histogram[bucket_nr];
		else {
			int count=0;
			for (auto i=memory_efficiency_histogram.find(10);i!=memory_efficiency_histogram.end();i++)
				count+=i->second;
			return count;
		}
	}
	int get_cputime_efficiency_histogram_entry(int bucket_nr){
		if (bucket_nr<10)
		return cputime_efficiency_histogram[bucket_nr];
		else {
			int count=0;
			for (auto i=cputime_efficiency_histogram.find(10);i!=cputime_efficiency_histogram.end();i++)
				count+=i->second;
			return count;
		}
	}
	int get_allocation_efficiency_histogram_entry(int bucket_nr){
		if (bucket_nr<10)
		return allocation_efficiency_histogram[bucket_nr];
		else {
			int count=0;
			for (auto i=allocation_efficiency_histogram.find(10);i!=allocation_efficiency_histogram.end();i++)
				count+=i->second;
			return count;
		}
	}
	
	int get_min_efficiency_histogram_entry(int bucket_nr){
		auto & hist =min_efficiency_histogram;
		if (bucket_nr<10)
		return hist[bucket_nr];
		else {
			int count=0;
			for (auto i=hist.find(10);i!=hist.end();i++)
				count+=i->second;
			return count;
		}
	}	

	*/
};

std::ostream &operator<<(std::ostream &os, ProjectEvaluation const &p)
{
	return os << p.to_string();
}

bool fileExists(std::string fileName)
{
	ifstream infile(fileName);
	return infile.good();
}
template<typename A, typename B>
pair<B,A> flip_pair(const pair<A,B> &p)
{
    return pair<B,A>(p.second, p.first);
}
int main(int argc, char **argv)
{
	SLURM_Log_Reader SLURM_reader;
	int current_set = 0;
	if (argc % 3 != 1 || argc < 4)
	{
		std::cerr << "Expecting slurm datafile as input.\n Expected format: \"sacct -n -P -S2017-01-01 -E2017-01-31 --format JobIDRaw,Account,User,ReqCPUS,ReqMem,ReqNodes,AllocNodes,AllocCPUS,NNodes,NCPUS,NTasks,State,CPUTimeRAW,ElapsedRaw,TotalCPU,SystemCPU,UserCPU,MaxCPU,AveCPU,MinCPU,MaxDiskRead,AveDiskRead,MaxDiskWrite,AveDiskWrite,MaxRSS,AveRSS\"" << std::endl;
		exit(-1);
	}
	current_set = 1;
	std::vector<std::string> history_names;
	std::vector<std::unordered_map<std::string, ProjectEvaluation>> history_data;
	std::vector<double> total_cpuh_history;
	std::vector<std::string> project_list;
	while (current_set + 3 <= argc)
	{

		double total_cpuh = 0.0;

		std::cout << "Reading file from " << argv[current_set + 2] << std::endl;

		std::string current_file_basename = std::string(argv[current_set + 2]);

		//CI: open file given by arg2
		std::string date_token = std::string(argv[current_set]);
		std::string file_token = std::string(argv[current_set + 1]);
		std::string line;

		// this is our work-data
		std::unordered_map<std::string, ProjectEvaluation> data_storage;
		std::vector<std::shared_ptr<SLURM_Task>> job_list, task_list;
		//task_list.reserve(3978426);
		//
		SLURM_reader.read_file(std::string(argv[current_set + 2]));

		SLURM_reader.DEBUG_print_statistics();

		job_list = SLURM_reader.get_job_list();

		std::cout << "read " << job_list.size() << "items from file " << std::endl;

		for (auto job : job_list)
		{
			total_cpuh += job->get_allocation_CPUtime();
			data_storage[job->project].add_task(job);
		}

		// CI: all data is processed. Now analyze it

		std::string delimiter = " ";
#ifdef USE_STDOUT
		std::ostream &output = std::cout;
#else
		ofstream output;
		//	std::ostream & output=outfile;
#endif

		// statistis for the year
		//
		{
			std::string summary_statistics = std::string("JobSummaryStatistics.Extended.dat");
			std::string summary_statistics_ALL = std::string("JobSummaryStatistics.All.dat");
			std::string summary_statistics_1CPUHr = std::string("JobSummaryStatistics.1CPUHr.dat");
			std::string summary_statistics_10CPUMi = std::string("JobSummaryStatistics.10CPUMi.dat");
			bool JSS_exists = fileExists(summary_statistics);
			bool JSS_ALL_exists = fileExists(summary_statistics_ALL);
			bool JSS_1CPUHr_exists = fileExists(summary_statistics_1CPUHr);
			bool JSS_10CPUMi_exists = fileExists(summary_statistics_10CPUMi);
			unsigned long long int JSS_ALL_total_tasks, JSS_ALL_total_jobs_completed, JSS_ALL_total_tasks_failed, JSS_ALL_total_tasks_completed;
			unsigned long long int JSS_1CPUHr_total_tasks, JSS_1CPUHr_total_jobs_completed, JSS_1CPUHr_total_tasks_failed, JSS_1CPUHr_total_tasks_completed;
			unsigned long long int JSS_10CPUMi_total_tasks, JSS_10CPUMi_total_jobs_completed, JSS_10CPUMi_total_tasks_failed, JSS_10CPUMi_total_tasks_completed;
			JSS_ALL_total_tasks = JSS_ALL_total_jobs_completed = JSS_ALL_total_tasks_failed = JSS_ALL_total_tasks_completed =
				JSS_1CPUHr_total_tasks = JSS_1CPUHr_total_jobs_completed = JSS_1CPUHr_total_tasks_failed = JSS_1CPUHr_total_tasks_completed =
					JSS_10CPUMi_total_tasks = JSS_10CPUMi_total_jobs_completed = JSS_10CPUMi_total_tasks_failed = JSS_10CPUMi_total_tasks_completed = 0;
			for (auto job : job_list)
			{
				auto cpu_walltime = job->compute_cpu_wall_time();
				if (cpu_walltime > 0)
				{
					JSS_ALL_total_tasks++;
					if (!job->array_job)
						JSS_ALL_total_jobs_completed++;
					if (job->job_state < 0)
						JSS_ALL_total_tasks_failed++;
					else
						JSS_ALL_total_tasks_completed++;
				}
				if (cpu_walltime > 600)
				{ // 10 Minutes in CPU Seconds
					JSS_10CPUMi_total_tasks++;
					if (!job->array_job)
						JSS_10CPUMi_total_jobs_completed++;
					if (job->job_state < 0)
						JSS_10CPUMi_total_tasks_failed++;
					else
						JSS_10CPUMi_total_tasks_completed++;
				}
				if (cpu_walltime > 3600)
				{ // 10 Minutes in CPU Seconds
					JSS_1CPUHr_total_tasks++;
					if (!job->array_job)
						JSS_1CPUHr_total_jobs_completed++;
					if (job->job_state < 0)
						JSS_1CPUHr_total_tasks_failed++;
					else
						JSS_1CPUHr_total_tasks_completed++;
				}
			}
#ifndef USE_STDOUT
			output.open(summary_statistics_ALL, std::ofstream::out | std::ofstream::app);
#endif
			if (!JSS_ALL_exists)
				output << "# MONTH TOTAL_TASKS TASKS_COMPLETED JOBS_COMPLETED TASKS_FAILED\n";
			output << date_token
				   << delimiter << JSS_ALL_total_tasks
				   << delimiter << JSS_ALL_total_tasks_completed
				   << delimiter << JSS_ALL_total_jobs_completed
				   << delimiter << JSS_ALL_total_tasks_failed << std::endl;
#ifndef USE_STDOUT
			output.close();
#endif

#ifndef USE_STDOUT
			output.open(summary_statistics_10CPUMi, std::ofstream::out | std::ofstream::app);
#endif
			if (!JSS_10CPUMi_exists)
				output << "# MONTH TOTAL_TASKS TASKS_COMPLETED JOBS_COMPLETED TASKS_FAILED\n";
			output << date_token
				   << delimiter << JSS_10CPUMi_total_tasks
				   << delimiter << JSS_10CPUMi_total_tasks_completed
				   << delimiter << JSS_10CPUMi_total_jobs_completed
				   << delimiter << JSS_10CPUMi_total_tasks_failed << std::endl;
#ifndef USE_STDOUT
			output.close();
#endif

#ifndef USE_STDOUT
			output.open(summary_statistics_1CPUHr, std::ofstream::out | std::ofstream::app);
#endif
			if (!JSS_1CPUHr_exists)
				output << "# MONTH TOTAL_TASKS TASKS_COMPLETED JOBS_COMPLETED TASKS_FAILED\n";
			output << date_token
				   << delimiter << JSS_1CPUHr_total_tasks
				   << delimiter << JSS_1CPUHr_total_tasks_completed
				   << delimiter << JSS_1CPUHr_total_jobs_completed
				   << delimiter << JSS_1CPUHr_total_tasks_failed << std::endl;
#ifndef USE_STDOUT
			output.close();
#endif

#ifndef USE_STDOUT
			output.open(summary_statistics, std::ofstream::out | std::ofstream::app);
#endif
			if (!JSS_exists)
				output << "# MONTH TOTAL_TASKS TASKS_COMPLETED JOBS_COMPLETED TASKS_FAILED\n";
			output << date_token
				   << delimiter << "3600"
				   << delimiter << "600"
				   << delimiter << "0"
				   << delimiter << JSS_1CPUHr_total_tasks
				   << delimiter << JSS_10CPUMi_total_tasks - JSS_1CPUHr_total_tasks
				   << delimiter << JSS_ALL_total_tasks - JSS_10CPUMi_total_tasks
				   << delimiter << JSS_1CPUHr_total_tasks_completed
				   << delimiter << JSS_10CPUMi_total_tasks_completed - JSS_1CPUHr_total_tasks_completed
				   << delimiter << JSS_ALL_total_tasks_completed - JSS_10CPUMi_total_tasks_completed
				   << delimiter << JSS_1CPUHr_total_jobs_completed
				   << delimiter << JSS_10CPUMi_total_jobs_completed - JSS_1CPUHr_total_jobs_completed
				   << delimiter << JSS_ALL_total_jobs_completed - JSS_10CPUMi_total_jobs_completed

				   << delimiter << JSS_1CPUHr_total_tasks_failed
				   << delimiter << JSS_10CPUMi_total_tasks_failed - JSS_1CPUHr_total_tasks_failed
				   << delimiter << JSS_ALL_total_tasks_failed - JSS_10CPUMi_total_tasks_failed
				   << std::endl;
#ifndef USE_STDOUT
			output.close();
#endif
		}
		// Monthly Job Statistics

		std::string job_statistics_name = std::string("JobStatistics.") + file_token + std::string(".dat");
#ifndef USE_STDOUT
		output.open(job_statistics_name, std::ofstream::out | std::ofstream::trunc);
#endif

		output << "# CI: I have been contemplating about the data. I would suggest the following data-fields:\n"
			   << "# USER_IDENTIFYER: If data protection rules allow it, the user identifyer or a sufficient subistitute, e.g. project-id.\n"
			   << "# AGGREGATED_CPU_TIME: the data of cpu-time\n"
			   << "# JOB_ID: id of the task\n"
			   << "# JOB_WALL_TIME: walltime of the job (in seconds)\n"
			   << "# JOB_CPU_TIME: aggregated used cpu-time (in seconds)\n"
			   << "# JOB_WALL_CORETIME: walltime * number-of-cores (in seconds)\n"
			   << "# JOB_RESSOURCE_UTILIZATION_EFFICIENCY: JOB_CPU_TIME/JOB_WALL_CPUTIME*100 (i.e. in percent)\n"
			   << "# JOB_RESSOURCE_UNUSED: JOB_WALL_CPUTIME - JOB_CPU_TIME\n"
			   << "# ALLOCAETD_RESSOURCES_CORE: number of cores allocated (reserved)\n"
			   << "# JOB_STATE: State of the job (F) Failed, (C) Completed (T) Timeout\n"
			   << "# JOB_TYPE: (T) Task, (J) Job\n"
			   << "# USER_IDENTIFYER JOB_ID JOB_WALL_TIME JOB_CPU_TIME JOB_WALL_CORETIME JOB_RESSOURCE_UTILIZATION_EFFICIENCY JOB_RESSOURCE_UNUSED ALLOCAETD_RESSOURCES_CORES JOB_STATE JOB_TYPE\n";

		for (auto job : job_list)
		{
			output
				<< job->project
				<< delimiter << job->job_id;
			if (job->array_job)
				output << "_" << job->array_step_id;
			output
				<< delimiter << job->elapsed_raw
				<< delimiter << job->total_cpu
				<< delimiter << job->compute_cpu_wall_time()
				<< delimiter << job->compute_cputime_efficiency()
				<< delimiter << job->compute_idle_cputime()
				<< delimiter << job->ncpus
				<< delimiter << job->job_state_letter()
				<< delimiter << job->job_type_letter() << std::endl;
		}
#ifndef USE_STDOUT
		output.close();
#endif

		// for all projects
		for (auto i : data_storage)
		{
			//		i.second.generate_cputime_efficiency_histograms();
			i.second.add_filter_threshold(60 * 10);
			i.second.add_filter_threshold(3600);
			i.second.add_filter_threshold(60 * 60 * 10);
			i.second.generate_all_histograms();
			std::cout << "Project " << std::setw(12) << i.first << ": " << i.second << "" << std::endl;

			std::string group_hist_filename = std::string("Project.") + i.first + std::string(".") + file_token + ".hist.dat";
			std::cout << "Creating file \"" << group_hist_filename << "\"" << std::endl;

#ifndef USE_STDOUT
			output.open(group_hist_filename, std::ofstream::out | std::ofstream::trunc);
#endif

			//		std::ostream & output=outfile;
			//		std::ostream & output=std::cout;
			//		outfile.open(group_hist_filename,std::ofstream::out |std::ofstream::trunc);
			//		auto cputime_efficiency_histogram_iterator=i.second.cputime_efficiency_histogram.begin();
			output << "# Data for project: " << i.first << std::endl;
			output << "#"
				   << delimiter << "NR=Row Number"
				   << delimiter << "RG=Range"
				   << delimiter << "FLT=min CPU*Hour filter"
				   << delimiter << "OEH=overall_efficiency_histogram"
				   << delimiter << "AEH=allocation_efficiency_histogram"
				   << delimiter << "CEH=cputime_efficiency_histogram"
				   << delimiter << "MEH=memory_efficiency_histogram" << std::endl;
			output << "#"
				   << delimiter << "NR"
				   << delimiter << "RG";
			for (int filter = 0; filter < i.second.get_number_of_filters(); filter++)
			{
				output
					<< delimiter << "FLT"
					<< delimiter << "OEH@" << i.second.get_filter_threshold(filter)
					<< delimiter << "AEH@" << i.second.get_filter_threshold(filter)
					<< delimiter << "CEH@" << i.second.get_filter_threshold(filter)
					<< delimiter << "MEH@" << i.second.get_filter_threshold(filter);
			}
			output << std::endl;
			for (int bucket_nr = 0; bucket_nr < 10; bucket_nr++)
			{
				output << bucket_nr << delimiter << "[" << bucket_nr << "0%-" << bucket_nr + 1 << "0%[ ";
				if (bucket_nr < 9)
					output << " ";
				for (int filter = 0; filter < i.second.get_number_of_filters(); filter++)
				{
					output
						<< delimiter << std::setw(3) << i.second.get_filter_threshold(filter)
						<< delimiter << std::setw(3) << i.second.get_min_efficiency_histograms()[filter].get_bucket_entry(bucket_nr)
						<< delimiter << std::setw(3) << i.second.get_allocation_efficiency_histograms()[filter].get_bucket_entry(bucket_nr)
						<< delimiter << std::setw(3) << i.second.get_cputime_efficiency_histograms()[filter].get_bucket_entry(bucket_nr)
						<< delimiter << std::setw(3) << i.second.get_memory_efficiency_histograms()[filter].get_bucket_entry(bucket_nr);
				}
				output << std::endl;
			}
			output << 10 << delimiter << "[100%     "; //<< i.second.get_cputime_efficiency_histograms()[0].get_bucket_entry(10);
			for (int filter = 0; filter < i.second.get_number_of_filters(); filter++)
			{
				output
					<< delimiter << std::setw(3) << i.second.get_filter_threshold(filter)
					<< delimiter << std::setw(3) << i.second.get_min_efficiency_histograms()[filter].get_bucket_entry(10)
					<< delimiter << std::setw(3) << i.second.get_allocation_efficiency_histograms()[filter].get_bucket_entry(10)
					<< delimiter << std::setw(3) << i.second.get_cputime_efficiency_histograms()[filter].get_bucket_entry(10)
					<< delimiter << std::setw(3) << i.second.get_memory_efficiency_histograms()[filter].get_bucket_entry(10);
			}
			output << std::endl;
			//		for (int bucket_nr=0;bucket_nr<i.second.cputime_efficiency_histogram.size();bucket_nr++){
			//			int count=*cputime_efficiency_histogram_iterator;
			//			output << bucket_nr << " ["<<bucket_nr<<"0%-"<<bucket_nr+1<<"0%[ " << cputime_efficiency_histogram_iterator->second<< std::endl;
			//			cputime_efficiency_histogram_iterator++;
			//		}
			//
			//
			//
			// for all projects
#ifndef USE_STDOUT
			output.close();
#endif
		}

		std::map<double, vector<ProjectEvaluation>> project_ordered_list;
		for (auto i : data_storage)
		{
						//												std::cout.setf(ios::fixed, ios::floatfield);
						std::cout
										<< "Project >"
										<< i.first
										<< "\t"
										<< setw(10) << fixed << setprecision(0)
										<< i.second.get_project_allocation_CPUtime();
						std::cout
										<< " ("
										//<< setf(ios::fixed, ios::floatfield)
										<< setw(5) << std::setprecision(1) << setw(5) << fixed
										<< i.second.get_project_allocation_CPUtime() / total_cpuh * 100.0 << "%)"
										<< setw(5) << std::setprecision(1) << setw(5)
										<< std::endl;
						int percent = i.second.get_project_allocation_CPUtime() / total_cpuh * 1000;
						project_ordered_list[percent].push_back(i.second);
		}
		std::cout << " ----------------------------------------------------------------------------- " << std::endl;



		int rank=1;


#ifndef USE_STDOUT
		std::string period_report_string = std::string(current_file_basename) + ".report";
		output.open(period_report_string, std::ofstream::out | std::ofstream::trunc);
#endif
		output << "Project [] " << date_token << " ";
		if (history_names.size())
		{
						for (int k = history_data.size() - 1; k >= 0; k--)
										output << history_names[k] << " ";
						//									for (int k=0;k<history_names.size();k++) output << history_names[k] << " ";
		}
		output << std::endl;
		for (auto i = project_ordered_list.rbegin(); i != project_ordered_list.rend(); i++)
		{
						for (auto j : i->second)
						{
										output << "Project " << j.get_projectname() << " " << i->first / 10.0 << " ";
										data_storage[j.get_projectname()].setRank(rank);
										j.setRank(rank);
										rank++;
										// check if there are any preceeding measurements
										if (history_data.size())
										{
														for (int k = history_data.size() - 1; k >= 0; k--)
														{
																		output << (int)(history_data[k][j.get_projectname()].get_project_allocation_CPUtime() / total_cpuh_history[k] * 1000.0) / 10.0 << " ";
														}
										}
										output << std::endl;
						}
		}
#ifndef USE_STDOUT
		output.close();
#endif


		// add projects to the history data (I know this may become huge!!!
		//
		history_names.push_back(date_token);
		history_data.push_back(std::unordered_map<std::string, ProjectEvaluation>());
		total_cpuh_history.push_back(total_cpuh);
		total_cpuh=0.0;
		for (auto i : data_storage)
		{		
						history_data.back()[i.first] = i.second;
		}

		current_set += 3;
	}


	std::map<std::string,int> project_name_list;	

	for (auto set_of_projects: history_data){
					// this is a map of all projects in this data-set
					for (auto project: set_of_projects){
									// if the project has no rank, it has no runtime for this period, skip it
									if (!project.second.rank) continue;
									if (project_name_list.find(project.first)==project_name_list.end())
										project_name_list[project.first]=project.second.rank;
									else if (project_name_list.find(project.first)->second>project.second.rank)
										project_name_list[project.first]=project.second.rank;
									std::cout << "Name: "<< project.first<<std::endl;
					}
	}	
	std::cout << "Number of Projects: " << project_name_list.size() << std::endl;
	for (auto project = project_name_list.rbegin(); project != project_name_list.rend(); project++){
////	for (auto project: project_name_list){
		std::cout << project->first << " " << project->second << std::endl;
	}
	std::multimap<int,std::string> project_ranking;
	std::transform(project_name_list.begin(),project_name_list.end(),std::inserter(project_ranking,project_ranking.begin()),flip_pair<std::string,int>);

	for (auto i: project_ranking){
			std::cout << i.first;
				std::cout << " " << i.second << std::endl;
	}	

#ifndef USE_STDOUT
	std::string period_report_string = "history.tex";
	ofstream output;
	output.open(period_report_string, std::ofstream::out | std::ofstream::trunc);
#endif
	output << "\\begin{tabular}{";
	for (int v=0;v<history_data.size()+1 && v<18;v++){
					output <<"|c";
	}
	output <<"|c|}" << std::endl << "\\hline"<<std::endl;
	output <<"project";
	if (history_data.size()) 
					for (int k = (history_data.size()-1>18?18:history_data.size()-1);k>=0;k--)
									output << "&"<<history_names[k];
	output << "\\\\\\hline"<<std::endl;
//	for (auto i = project_ordered_list.rbegin(); i != project_ordered_list.rend(); i++)
	int project_counter=0;
  for (auto i: project_ranking)
	{
				if (project_counter>28) break;
				project_counter++;
					bool toContinue=true;
					if (history_data.size())	
									for (int k = (history_data.size()-1>18?18:history_data.size()-1);k>=0;k--){
													if (history_data[k][i.second].rank>0)
																	toContinue=false;
									}
					if (toContinue) continue;
					//											toContinue|=history_data[k][j.get_projectname()].rank>0;

//					if (!data_storage[j.get_projectname()].rank ||toContinue) continue;
					output << i.second;
					if (history_data.size())
					{
									for (int k = history_data.size() - 1; k >= 0; k--)
									{
													output <<"&";	
													switch (history_data[k][i.second].rank){
																	case 1: output << "\\,\\topA";break;
																	case 2: output << "\\,\\topB";break;
																	case 3: output << "\\,\\topC";break;
																	case 0: output << "\\,\\noVal";break;
																	default: if (history_data[k][i.second].rank>10)output << "\\tooLow"; break;
													}
													if (history_data[k][i.second].rank && history_data[k][i.second].rank<11)	
																	output << (int)(history_data[k][i.second].get_project_allocation_CPUtime() / total_cpuh_history[k] * 1000.0) / 10.0 ;
									}
					}
					output << "\\\\"<<"\\hline" <<std::endl;

	}
#ifndef USE_STDOUT
	output<<"\\end{tabular}"<<std::endl;
	output.close();
#endif
	// Generate History Usage Table
	// Iterate of the history items and print an ordered list
	/*
#ifndef USE_STDOUT
std::string period_report_string = std::string(current_file_basename) + ".tex";
output.open(period_report_string, std::ofstream::out | std::ofstream::trunc);
#endif
output << "Project [] " << date_token << " ";
if (history_names.size())
{
for (int k = history_data.size() - 1; k >= 0; k--)
output << history_names[k] << " ";
	//									for (int k=0;k<history_names.size();k++) output << history_names[k] << " ";
	}
	output << std::endl;
	int rank=1;
	for (auto i = project_ordered_list.rbegin(); i != project_ordered_list.rend(); i++)
	{
	for (auto j : i->second)
	{
	output << "Project " << j.get_projectname() << " " << i->first / 10.0 << " ";
	j.rank=rank;
	switch (rank){
	case 1: output << "+ ";break;
	case 2: output << "0 ";break;
	case 3: output << "- ";break;
	default: output << "  "; break;
	}
	rank++;
	// check if there are any preceeding measurements
	if (history_data.size())
	{
	for (int k = history_data.size() - 1; k >= 0; k--)
	{
	output << (int)(history_data[k][j.get_projectname()].get_project_allocation_CPUtime() / total_cpuh * 1000.0) / 10.0 << " ";
	switch (history_data[k][j.get_projectname()].rank){
	case 1: output << "+ ";break;
	case 2: output << "0 ";break;
	case 3: output << "- ";break;
	default: output << "  "; break;
	}
	}
	}
	output << std::endl;
	}
	}
#ifndef USE_STDOUT
output.close();
#endif*/
	std::cout << "New Analysis: history data" << std::endl;
for (auto hn: history_names)
{
				std::cout << "Histroy element " << hn << std::endl;
}		


auto name_iter = history_names.begin();
for (auto &week : history_data)
{
				/* code */
}

return 0;
}
