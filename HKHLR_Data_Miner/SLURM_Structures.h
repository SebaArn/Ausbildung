#ifndef SLURM_structures_h
#define SLURM_structures_h

#include <stdlib.h>
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
#include <ctime>

using namespace std;
#if 0
class tokenize{
	protected:
		std::string input;
		size_t token_start = 0;
		size_t token_end = 0;
		size_t input_size;
		std::string delimiter = "|";
		void find_next_position(){
			if (token_start!=std::string::npos)
				token_end=input.find(delimiter,token_start);
		}
	public:
		tokenize(std::string i):input(i){
			token_start=0;
			find_next_position();
		}

		bool end(){
			if (token_start==std::string::npos) return true;
			else return false;
		}
	  
	  bool isEmpty(){
			if (input.size()==0) return true;
			else return false;
    }

		std::string next(){
			if (end()) throw std::string("Insufficient tokes in string");
			std::string ret_val;
			if (token_end==std::string::npos){
				ret_val=input.substr(token_start);
				token_start=token_end;
			}
			else {
				ret_val=input.substr(token_start,token_end-token_start);
				token_start=token_end+1;
			}
			find_next_position();
			return ret_val;
		}
}; 
#endif
class SLURM_Task{
public:
	SLURM_Task(SLURM_Task* const){
		throw std::string("Who calls this??");
	}
	SLURM_Task(){
		submit_time_set=start_time_set=end_time_set=false;
		job_script=false;
		job_steps.reserve(10);
		job_id=array_step_id=req_cpu=req_mem=req_nodes=alloc_nodes=alloc_cpu=nnodes=ncpus=ntasks=job_state=
		cpu_time_raw=elapsed_raw=total_cpu=system_cpu=user_cpu=min_cpu=average_cpu=max_disk_read=ave_disk_read=max_disk_write=ave_disk_write=max_rss=ave_rss=0;
		start_time=submit_time=end_time=0;	
}
	void add_parent(std::shared_ptr<SLURM_Task> pj){
		parent_job=pj;
	}
	size_t job_id,array_step_id;
	bool job_step,array_job;
	bool job_script,exclusive_job;
	std::string job_id_str;
	std::string project;
	std::string username;
	int req_cpu;
	size_t req_mem;
	bool req_mem_per_core,req_mem_per_node;
	int req_nodes, alloc_nodes,alloc_cpu,nnodes,ncpus,ntasks;
	int job_state;
	unsigned long long int cpu_time_raw,elapsed_raw,total_cpu,system_cpu,user_cpu,min_cpu,average_cpu,max_disk_read,ave_disk_read,max_disk_write,ave_disk_write,max_rss,ave_rss;
	time_t submit_time,start_time,end_time;
	bool submit_time_set,start_time_set,end_time_set;
	std::vector<std::shared_ptr<SLURM_Task> > job_steps;
	std::shared_ptr<SLURM_Task> parent_job=nullptr;
	std::vector<std::shared_ptr<SLURM_Task> > & get_job_steps(){
		return job_steps;
	};
	char job_type_letter(){
		if (array_job) return 'T';
		if (job_step) return 'S';
		return 'J';
	}
	char job_state_letter(){
		switch(job_state){
			case  0: return '?';
			case -1: return 'T';  // Timeout
			case -2: return 'F';  // Canceled
			case  3: return 'C';  // Completed
			case -4: return 'F';  // NodeFail
		}
		return 0;
	}
	int job_state_to_id(std::string _input){
		size_t pos;
		std::string input;
		if ((pos=_input.find(" "))!=std::string::npos)
			input=_input.substr(0,pos);
		else input=_input;
		if (input==std::string("TIMEOUT")) return -1;
		else if (input==std::string("CANCELLED")) return -2;
		else if (input==std::string("COMPLETED")) return 3;
		else if (input==std::string("FAILED")) return -4;
		else if (input==std::string("NODE_FAIL")) return -5;
		else if (input==std::string("RESIZING")) return -6;
		throw std::invalid_argument(std::string("Unknown inputfield: ")+input);
		return 0;
	}


	unsigned long long int compute_cpu_wall_time(){	
		if (parent_job!=nullptr){
			return parent_job->ncpus*elapsed_raw;
		}
		else {
			return elapsed_raw*ncpus;
		}
	}
	
	unsigned long long int compute_unused_memory(){
		unsigned long long int result=0;
		if (parent_job!=nullptr){
			if (parent_job->req_mem_per_core) result=parent_job->req_mem*parent_job->req_cpu-ave_rss*ncpus;
			if (parent_job->req_mem_per_node) result=parent_job->req_mem*parent_job->req_nodes-ave_rss*ncpus;
		}
		else {
			unsigned long long int child_memory_usage=0;
			for (auto i: job_steps)	child_memory_usage+=i->ave_rss*i->ncpus;
			for (auto i: job_steps)	{
				unsigned long long int child_usage=i->ave_rss*i->ncpus;
				child_memory_usage=child_usage>child_memory_usage?child_usage:child_memory_usage;
			}
			if (parent_job->req_mem_per_core) result=parent_job->req_mem*parent_job->req_cpu-child_memory_usage;
			if (parent_job->req_mem_per_node) result=parent_job->req_mem*parent_job->req_nodes-child_memory_usage;
		

		}	
		return result;
	}
	double compute_memory_efficiency(){
		if (parent_job!=nullptr){
			if (parent_job->req_mem_per_core) {
			if (parent_job->req_mem*parent_job->req_cpu==0) return 100.0;
				return (ave_rss*ncpus)/(double)(parent_job->req_mem*parent_job->req_cpu)*100.0;
}
			else if (parent_job->req_mem_per_node) {
				if (parent_job->req_mem*parent_job->req_nodes==0) return 100.0;
				return (ave_rss*ncpus)/(double)(parent_job->req_mem*parent_job->req_nodes)*100.0;
}
		}
		else {
			// memory efficiency is the max used memory for a job step
			unsigned long long int child_memory_usage=0;
			for (auto i: job_steps)	{
				unsigned long long int child_usage=i->ave_rss*i->ncpus;
				child_memory_usage=child_usage>child_memory_usage?child_usage:child_memory_usage;
			}
			if (req_mem_per_core) return req_mem*req_cpu==0?100.0:child_memory_usage/(double)(req_mem*req_cpu)*100.0;
			if (req_mem_per_node) return req_mem*req_nodes==0?100.0:child_memory_usage/(double)(req_mem*req_nodes)*100.0;
			/*
			if (parent_job->req_mem_per_core) return child_memory_usage/(double)(parent_job->req_mem*parent_job->req_cpu);
			if (parent_job->req_mem_per_node) return child_memory_usage/(double)(parent_job->req_mem*parent_job->req_nodes);
*/
		

		}	
	}
	double compute_cputime_efficiency(){
		// if this is the parent -> get data from children, else get allocation from parent and compute cput-time
		if (parent_job!=nullptr){
			if (parent_job->ncpus*elapsed_raw==0) return 100.0;
			return total_cpu/(double)(parent_job->ncpus*elapsed_raw)*100.0;
		}
		else {
			if (ncpus*elapsed_raw==0) return 100.0;
			return total_cpu/(double)cpu_time_raw*100;
			return compute_idle_cputime()/(double)(elapsed_raw*ncpus)*100.0;
		}			
	}

	unsigned long long int compute_idle_cputime(){
		// if this is the parent -> get data from children, else get allocation from parent and compute cput-time
		if (parent_job!=nullptr){
			return parent_job->ncpus*elapsed_raw-total_cpu;
		}
		else {
			unsigned long long int result=0;
			for (auto i: job_steps)
				result+=i->compute_idle_cputime();
			return result;
		}			
	}
	// this is just from the allocation information, no os measurement
	unsigned long long int compute_idle_allocation(){
		// if this is the parent -> get data from children, else get allocation from parent and compute cput-time
		if (parent_job!=nullptr){
			return (parent_job->ncpus-ncpus)*elapsed_raw;
		}
		else {
			unsigned long long int result=0;
			for (auto i: job_steps)
				result+=i->compute_idle_allocation();
			return result;
		}			
	}
	double get_allocation_CPUtime(){
		if (parent_job!=nullptr){
			return (double)(parent_job->ncpus*parent_job->elapsed_raw);
		}
		else {
			return (double)(elapsed_raw*ncpus);
		}
		return -1;
	}
	double compute_cpu_allocation_efficiency(){
//		throw std::string("This is broken!!");
//		return 0.0;
		// if this is the parent -> get data from children, else get allocation from parent and compute cput-time
		if (parent_job!=nullptr){
			if (parent_job->ncpus==0) return 100.0;
			return ncpus/(double)parent_job->ncpus*100.0;
		}
		else {
			if (elapsed_raw*ncpus==0) return 100.0;
			return compute_idle_cputime()/(double)(elapsed_raw*ncpus)*100.0;
		}			
	}

	bool isArrayJob(){return array_job;};
	bool isJobStep(){return job_step;};
	void add_job_step(std::shared_ptr<SLURM_Task> sub_task){
		job_steps.push_back(sub_task);
		//sub_task->parent_job=std::make_shared<SLURM_Task>(*this);
	}
	std::string filed_descr(){
		stringstream ss;
		std::string delim(" ");
		ss << "job_id" << delim;
		ss << "project" << delim;
		ss << "username"<< delim;
		ss << "req_cpu"<< delim;
		ss << "req_mem"<< delim;
//		ss << "req_mem_per_core?std::string("c"):std::string("") "<< delim;
//		ss << "req_mem_per_node?std::string("n"):std::string("") "<< delim;
		ss << "req_nodes"<< delim;
		ss << "alloc_nodes"<< delim;
		ss << "alloc_cpu"<< delim;
		ss << "nnodes"<< delim;
		ss << "ncpus"<< delim;
		ss << "ntasks"<< delim;
		ss << "job_state"<< delim;
		ss << "cpu_time_raw"<< delim;
		ss << "elapsed_raw"<< delim;
		ss << "total_cpu"<< delim;
		ss << "system_cpu"<< delim;
		ss << "user_cpu"<< delim;
		ss << "min_cpu"<< delim;
		ss << "average_cpu"<< delim;
		ss << "max_disk_read"<< delim;
		ss << "ave_disk_read"<< delim;
		ss << "max_disk_write"<< delim;
		ss << "ave_disk_write"<< delim;
		ss << "max_rss" << delim; 
		ss << "ave_rss";
	
		return ss.str();	
}
	std::string to_string() const{
		stringstream ss;
		std::string delim(" ");
		ss << job_id << delim;
		ss << project << delim;
		ss << username << delim;
		ss << req_cpu << delim;
		ss << req_mem;// << delim;
		ss << (req_mem_per_core?std::string("c"):std::string(""));;// << delim;
		ss << (req_mem_per_node?std::string("n"):std::string(""));;// << delim;
		ss << delim;
		ss << req_nodes << delim;
		ss << alloc_nodes << delim;
		ss << alloc_cpu << delim;
		ss << nnodes << delim;
		ss << ncpus << delim;
		ss << ntasks << delim;
		ss << job_state << delim;
		ss << cpu_time_raw << delim;
		ss << elapsed_raw << delim;
		ss << total_cpu << delim;
		ss << system_cpu << delim;
		ss << user_cpu << delim;
		ss << min_cpu << delim;
		ss << average_cpu << delim;
		ss << max_disk_read << delim;
		ss << ave_disk_read << delim;
		ss << max_disk_write << delim;
		ss << ave_disk_write << delim;
		ss << max_rss << delim; 
		ss << ave_rss;
	
		return ss.str();	
	}
	
};

std::ostream &operator<<(std::ostream &os, SLURM_Task const &m);

#endif
