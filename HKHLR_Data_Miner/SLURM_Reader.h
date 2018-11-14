#ifndef SLURM_Reader_h
#define SLURM_Reader_h
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

#include "SLURM_Structures.h"
#include "DebugLevel.h"
#include <ctime>

using namespace std;

class SLURM_Log_Reader:public DebugLevel{
	protected:
		std::vector<std::shared_ptr<SLURM_Task> > job_list,task_list;
		std::string filename;
		std::string current_element_string;
		unsigned long long int jobsteps_read,jobs_read,lines_processed;
		bool file_set,file_read;
		bool debugOn=false;

		bool isVerboseDebug(){
#ifdef DEBUG
			return true;
#else
			return debugOn;
#endif
	}
		void setCurrentElementString(std::string currentElement){
		
			current_element_string=currentElement;
		if(isVerboseDebug())	std::cerr << "Current Element: >" << current_element_string << "< ";
		}
		std::string currentElementString(){
			return current_element_string;
}
		std::string getCurrentElementString(){
				return current_element_string;
		}
	public:
		void setDebugLevelAll(){
			debugOn=true;
		}
		SLURM_Log_Reader();
		void reset();
		void set_file(std::string f){
			if (filename!=f) reset();
			filename=f;
			file_set=true;
	}
		unsigned long long int time_to_seconds(std::string input);
		unsigned long long int SLURM_ReqMEM(std::string input,size_t * ppos=nullptr,char base='k');
		unsigned long long int suffix_ull(std::string input,size_t * ppos=nullptr,char base='b');
		double suffix_double(std::string input,size_t ** ppos=NULL,char base='b');
		unsigned long long int date_to_ull(std::string input);
		time_t date_to_timet(std::string input);
		unsigned long long int suffix_double_to_ull(std::string input,size_t ** ppos=NULL,char base='b');
		int state_to_id(std::string _input);
		void read_file(string filename);
		void read();

		std::vector<std::shared_ptr<SLURM_Task> > get_job_list(){return job_list;}
		std::vector<std::shared_ptr<SLURM_Task> > get_task_list(){return task_list;}
		void DEBUG_print_statistics();
};
#endif
