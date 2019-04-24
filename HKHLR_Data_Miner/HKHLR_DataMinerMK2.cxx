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

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include "SLURM_Reader.h"
#include "SLURM_Structures.h"
#include "SLURM_Analyzer.h"

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

int main(int argc, char **argv)
{
    SLURM_Analyzer analyzer=SLURM_Analyzer();;
		analyzer.setDebugLevelOps();
//		analyzer.setDebugLevelAll();
	// SLURM_Log_Reader SLURM_reader;
	int current_set = 0;
	if (argc % 3 != 1 || argc < 4)
	{
		std::cerr << "Expecting slurm datafile as input.\n Expected format: \"sacct -n -P -S2017-01-01 -E2017-01-31 --format JobIDRaw,Account,User,ReqCPUS,ReqMem,ReqNodes,AllocNodes,AllocCPUS,NNodes,NCPUS,NTasks,State,CPUTimeRAW,ElapsedRaw,TotalCPU,SystemCPU,UserCPU,MaxCPU,AveCPU,MinCPU,MaxDiskRead,AveDiskRead,MaxDiskWrite,AveDiskWrite,MaxRSS,AveRSS\"" << std::endl;
		exit(-1);
	}
	current_set = 1;
	std::vector<std::string> history_names;
	std::vector<std::unordered_map<std::string, ProjectEvaluation>> history_data;
	while (current_set + 3 <= argc)
	{
		analyzer.addSLURMlogfile(argv[current_set + 2],argv[current_set + 0],argv[current_set + 1]);
		current_set+=3;
	}

    //

	return 0;
}
