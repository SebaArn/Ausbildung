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
#include <ctime>
#include <sys/types.h>
       #include <unistd.h>

#include <sys/types.h>
       #include <sys/stat.h>
       #include <fcntl.h>

#include "SLURM_Structures.h"
#include "SLURM_Reader.h"
#include <fcntl.h>

using namespace std;

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
		bool isVerboseDebug(){
#ifdef DEBUG
			return true;
#else
			return false;
#endif
		}
		std::vector<std::string> tokenList;
		
  public:
		void discardRemaining(){
			if (isVerboseDebug())
				std::cerr<<"Discarding >" << input.substr(token_start,std::string::npos) << "<"<<std::endl;
		}
    tokenize(std::string i):input(i){
			if (isVerboseDebug()){			
				// find all delimiters and add each string to the list
				size_t current_delimiter_pos,last_delimiter_pos=0;
				current_delimiter_pos=input.find(delimiter,last_delimiter_pos);
				while(current_delimiter_pos!=std::string::npos) {
					tokenList.push_back(input.substr(last_delimiter_pos,current_delimiter_pos-last_delimiter_pos));
//					std::cerr << "Dbg.: Current element: " << tokenList.back() << std::endl;
					last_delimiter_pos=current_delimiter_pos+1;
					current_delimiter_pos=input.find(delimiter,last_delimiter_pos);
				}

				// last element, since we have not found any delimiters
				tokenList.push_back(input.substr(last_delimiter_pos, std::string::npos));			
				std::cerr << "Found " << tokenList.size() << " tokens in string" << std::endl;
			}

      token_start=0;
      find_next_position();
    }
		unsigned int countElements(){
			size_t buf_token_start=token_start,buf_token_end=token_end;
			
			return 0;
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
			if (isVerboseDebug())
				std::cerr <<  ret_val << std::endl;
      return ret_val;
    }
};


class buffered_file_reader{
				protected:
								size_t buffer_size=1000000;
								size_t buffer_elements=0;
								size_t frame_current_position,frame_next_position;
								size_t absolute_position;
								char * buffer;
								bool at_end,file_at_end;
								int fd;
								bool get_line_retry;
								size_t file_size;
				public:
								buffered_file_reader(std::string filename,int bs=1000000):buffer_size(bs){
												buffer=(char*)malloc(buffer_size+1);
												get_line_retry=false;
												frame_current_position=buffer_size;
												frame_next_position=0;
												//		frame_position=0;		
												at_end=false;
												file_at_end=false;
#if												_POSIX_C_SOURCE >= 200112L
												fd=open(filename.c_str(),O_RDONLY | O_DIRECT );
#else
												fd=open(filename.c_str(),O_RDONLY);
#endif
												if (fd==-1) throw std::string("Some Error when opening file ")+filename;
												file_size=lseek(fd, 0L, SEEK_END);
												lseek(fd,0,SEEK_SET);
#if												_POSIX_C_SOURCE >= 200112L
												posix_fadvise(fd, 0, 0, 1);  // FDADVICE_SEQUENTIAL		
#endif												
												absolute_position=0;
												fill_buffer();		
								};
								~buffered_file_reader(){close(fd);free(buffer);}
								void fill_buffer(){
												size_t elements_to_keep=buffer_elements>frame_current_position?buffer_elements-frame_current_position:0;
												size_t elements_to_load=frame_current_position;
												memcpy(buffer,buffer+frame_current_position,elements_to_keep);
												size_t bytes_read;
												if (!file_at_end) bytes_read=read(fd,buffer+elements_to_keep,elements_to_load);
												else bytes_read=0;
												if (bytes_read<elements_to_load) file_at_end=true;
												buffer_elements=elements_to_keep+bytes_read;
												frame_current_position=0;
												frame_next_position=0;
								}

								bool isAtEnd(){
												return at_end;
								};
								std::string get_line(){
												std::string ret_string;	
												while(frame_next_position<buffer_elements && buffer[frame_next_position]!='\n')  frame_next_position++;
												if (buffer[frame_next_position]!='\n'){
																if (!file_at_end){
																				fill_buffer();
																				// we have not found a newline
																				// there are two possibilities, we must load more bytes from file and continue
																				// or this is the end of the file
																				fill_buffer();
																				while(frame_next_position<buffer_elements && buffer[frame_next_position]!='\n')  frame_next_position++;
																}
																if (buffer[frame_next_position]!='\n' && file_at_end){
																				at_end=true;
																				// there are no more newlines and we are at the end of the file, return the remainder as a string and done
																				//			ret_string=std::string(buffer,frame_next_position-frame_current_position);
																				//			frame_current_position=frame_next_position;
																}
												}
												absolute_position+=frame_next_position-frame_current_position+1;
												// the string ends at next pos
												ret_string=std::string(buffer+frame_current_position,frame_next_position-frame_current_position);
												frame_current_position=frame_next_position+1;	
												frame_next_position=frame_current_position;
												if (file_at_end && frame_current_position>=buffer_elements) at_end=true;	
												return ret_string;
								};
								//	size_t seek(size_t offset);
								//	size_t relative_seek(size_t offset);
								size_t size(){return file_size;};
								size_t position(){ return absolute_position;};

};

unsigned long long int SLURM_Log_Reader::time_to_seconds(std::string input){
				std::string backup(input);
				unsigned long long int time=0;
				if (!input.size()) return 0;
				//	size_t dash=token.find("-");
				//	size_t point=token.find(".");
				std::vector<int> elements;
				size_t pos=0;
				// get the days
				if ((pos=input.find("-"))!=std::string::npos){
								elements.push_back(std::stoi(input.substr(0,pos)));
								input.erase(0,pos+1);
				}
				// get the hours
				if ((pos=input.find(":"))!=std::string::npos){
								elements.push_back(std::stoi(input.substr(0,pos)));
								input.erase(0,pos+1);
				}
				// get the minutes
				if ((pos=input.find(":"))!=std::string::npos){
								elements.push_back(std::stoi(input.substr(0,pos)));
								input.erase(0,pos+1);
				}
				// get the seconds
				if ((pos=input.find(":"))!=std::string::npos){
								throw std::invalid_argument(std::string("malformated time-string: ")+backup);
				}
				else{
								elements.push_back(std::stoi(input.substr(0,pos)));
								input.erase(0,pos+1);
				}

				// build time
				if (elements.size()) {time+=elements.back();elements.pop_back();}// seconds
				if (elements.size()) {time+=elements.back()*60;elements.pop_back();} // minutes
				if (elements.size()) {time+=elements.back()*60*60;elements.pop_back();} // hours
				if (elements.size()) {time+=elements.back()*60*60*24;elements.pop_back();} // days
				return time;
}

unsigned long long int SLURM_Log_Reader::SLURM_ReqMEM(std::string input,size_t * ppos,char base){
				size_t pos;
				if(!input.size()) return 0;
				unsigned long long int result=std::stoull(input,&pos);
				if (result & 1<<31)
								result=result&0x7fffffff;

				if (pos!=std::string::npos){
								switch(input[pos]){	
												case 'P':
												case 'p':
																result*=1<<40;pos++;break;
												case 'G':
												case 'g': 
																result*=1024*1024*1024;pos++;break;
												case 'M':
												case 'm':
																result*=1024*1024;pos++;break;
												case 'K':
												case 'k': // No Need to scale value as it is in KB
																result*=1024;
																pos++;break;
								}
				}
				switch(base){
								case 'k':
								case 'K': result/=1024;break;
								case 'm': 
								case 'M':result/=1024*1024;break;
								case 'g': 
								case 'G':result/=1024*1024*1024;break;
								case 't': 
								case 'T':result/=1024*1024*1024*1024;break;
				}
				if (ppos!=nullptr) 
								pos>=input.size()?*ppos=(long unsigned int)std::string::npos:*ppos=pos;
				return result;		
}

unsigned long long int SLURM_Log_Reader::suffix_ull(std::string input,size_t * ppos,char base){
				size_t pos;
				if(!input.size()) return 0;
				unsigned long long int result=std::stoull(input,&pos);
				if (result & 1<<31)
								result=result&0x7fffffff;

				if (pos!=std::string::npos){
								switch(input[pos]){	
												case 'G':
												case 'g': 
																result*=1024*1024*1024;
																pos++;break;
												case 'M':
												case 'm':
																result*=1024*1024;
																pos++;break;
												case 'K':
												case 'k': 
																result*=1024;
																pos++;break;
								}
				}
				switch(base){
								case 'k':
								case 'K': result/=1024;break;
								case 'm': 
								case 'M':result/=1024*1024;break;
								case 'g': 
								case 'G':result/=1024*1024*1024;break;
								case 't': 
								case 'T':result/=1024*1024*1024*1024;break;
				}

				if (ppos!=nullptr) 
								pos>=input.size()?*ppos=(long unsigned int)std::string::npos:*ppos=pos+1;
				return result;		
}

double SLURM_Log_Reader::suffix_double(std::string input,size_t ** ppos,char base){
				size_t pos;
				if(!input.size()) return 0;
				double result=std::stod(input,&pos);

				if (pos!=std::string::npos){
								switch(input[pos]){	
												case 'G':
												case 'g': 
																result*=1024*1024*1024;break;
												case 'M':
												case 'm':
																result*=1024*1024;break;
												case 'K':
												case 'k': 
																result*=1024;
																break;
								}
				}
				switch(base){
								case 'k':
								case 'K': result/=1024;break;
								case 'm': 
								case 'M':result/=1024*1024;break;
								case 'g': 
								case 'G':result/=1024*1024*1024;break;
								case 't': 
								case 'T':result/=1024*1024*1024*1024;break;
				}
				return result;		
}
time_t SLURM_Log_Reader::date_to_timet(std::string input){
				unsigned long long int date=0;
				// 
				std::vector<int> elements;
				size_t pos=0;
				//mktime 
				struct tm time_info;
				memset(&time_info,sizeof(tm),0);

				if (input == std::string("Unknown")) {
								std::cerr << "Found \"Unknown\" for timestamp " << std::endl;
								return 0;
				}
				if (input == std::string("Cyclic")) {
					std::cerr << "Found \"Cyclic\" for timestamp " << std::endl;
					return 0;	
				}
				if (input == std::string("Block")) {
					std::cerr << "Found \"Block\" for timestamp " << std::endl;
					return 0;	
				}
				// 2018-03-26T07:13:00	
//				pos=input.find("-");
//				std::cout << "input:" << input << std::endl;
//			First element is the year
	try{
				pos=input.find("-");
				time_info.tm_year=std::stoi(input.substr(0,pos));input.erase(0,pos+1);
				pos=input.find("-");
				time_info.tm_mon=std::stoi(input.substr(0,pos));input.erase(0,pos+1);
				pos=input.find("-");
				if (pos==std::string::npos) pos=input.find("T");
				time_info.tm_mday=std::stoi(input.substr(0,pos));input.erase(0,pos+1);

				pos=input.find("-");
				if (pos==std::string::npos) pos=input.find(":");
				time_info.tm_hour=std::stoi(input.substr(0,pos));input.erase(0,pos+1);
				pos=input.find("-");
				if (pos==std::string::npos) pos=input.find(":");
				time_info.tm_min=std::stoi(input.substr(0,pos));input.erase(0,pos+1);
				pos=input.find("-");
				time_info.tm_sec=std::stoi(input.substr(0,pos));input.erase(0,pos+1);
}catch(...){	
			std::cerr << "Failed on string " << input << " in " << getCurrentElementString() <<std::endl;
			throw;
}
				return  mktime(&time_info);
}

unsigned long long int SLURM_Log_Reader::suffix_double_to_ull(std::string input,size_t ** ppos,char base){
				size_t pos;
				if(!input.size()) return 0;
				double result=std::stod(input,&pos);

				if (pos!=std::string::npos){
								switch(input[pos]){	
												case 'G':
												case 'g': 
																result*=1024*1024*1024;break;
												case 'M':
												case 'm':
																result*=1024*1024;break;
												case 'K':
												case 'k': 
																result*=1024;
																break;
								}
				}
				switch(base){
								case 'k':
								case 'K':result/=1024;break;
								case 'm': 
								case 'M':result/=1024*1024;break;
								case 'g': 
								case 'G':result/=1024*1024*1024;break;
								case 't': 
								case 'T':result/=1024*1024*1024*1024;break;
				}
				return result;		
}
//unsigned long long int date_to_ull(std::string input){
//	return 0;
//}

void SLURM_Log_Reader::DEBUG_print_statistics(){
	std::cout << "file: " << filename << std::endl;
	std::cout << "read " << jobs_read << " with " << jobsteps_read << " jobsteps" << std::endl;
	std::cout << "total lines processed: " << lines_processed << std::endl;
	std::cout << "No Statistics yet" << std::endl;
}

int SLURM_Log_Reader::state_to_id(std::string _input){
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
				else if (input==std::string("RESIZING")) return  -6;
				else if (input==std::string("OUT_OF_MEMORY")) return -7;
				else if (input==std::string("REQUEUED")) return -8;
				else if (input==std::string("RUNNING")) return 0;
				else if (input==std::string("PENDING")) return 0;
				throw std::invalid_argument(std::string("Unknown inputfield: ")+input);
				return 0;
}

void SLURM_Log_Reader::reset(){
	jobsteps_read=jobs_read=lines_processed=0;
	filename="";
	job_list.clear();
	task_list.clear();
	file_set=false;
	file_read=false;
}

void SLURM_Log_Reader::read_file(std::string filename){
	reset();
	set_file(filename);
	read();
	return ;
}
void SLURM_Log_Reader::read(){
				if (!file_set) throw std::string("Must define file to process");
				if (file_read) return;
				//		std::vector<std::shared_ptr<SLURM_Task> > SLURM_Log_Reader::read_file(string filename){
				//		file=filename;
				std::cout << "Reading file from" << this->filename << std::endl;
				//CI: open file
				std::string line;
				//	std::ifstream data_file(argv[current_set+2]);
				auto data_file=buffered_file_reader(filename,10000000);

				// this is our work-data	
				/////////////////////////////////////			std::unordered_map<std::string,ProjectEvaluation > data_storage;
				//	std::vector<std::shared_ptr<SLURM_Task> > job_list,task_list;
				job_list.reserve(4000000);
				//task_list.reserve(3978426);
				unsigned long long total_tasks=0,total_tasks_completed=0,total_tasks_failed=0,total_jobs_completed=0, total_jobs_failed=0;
				std::shared_ptr<SLURM_Task> last_job=nullptr;

				std::string last_project;
				//CI: read the file given by arg1 line by line
				unsigned int line_count=0;
				//	data_file.seekg(0,data_file.end);
				unsigned long long int file_size=data_file.size();
				//	data_file.seekg(0,data_file.beg);
				std::cout << "Filesize = " << file_size<< std::endl;;
				std::cout << "Reading file. Progress: \n" << std::flush;
				unsigned long long int old_file_pos=0;
				double start_time=omp_get_wtime(),end_time=omp_get_wtime();


				//CI: read all the entries in a log-file 
				std::vector<char> buffer;
				size_t buffer_size=1000000;
				buffer.resize(buffer_size);
				int buffer_pos=0,buffer_next_pos=0;

				unsigned long int exception_count=0;

				// Read the file line by line
				while(!data_file.isAtEnd()){
								try {
												line=data_file.get_line();
								}
								catch (...){
												// file I/O 
												exception_count++;
												std::cerr << "Error reading file at line: " << lines_processed << std::endl;
												
								}
								try {
												if (isVerboseDebug()){	
													std::cerr<<"Dbg: Processing line >" << line << "<" << std::endl;
												}
												lines_processed++;
												//	std::cout << ">>"<<line<<"<<"<<std::endl;
												line_count++;
												if (line_count%1000==0) {
																unsigned long long int file_pos=data_file.position();
																double progress=file_pos/(double)file_size*100;
																end_time=omp_get_wtime();
																double rate=(file_pos-old_file_pos)/(end_time-start_time);
																old_file_pos=file_pos;
																start_time=omp_get_wtime();
																std::cout << std::setw(1)<<progress<< "@"<<std::setw(4)<<rate<<"elements per second "<< file_pos<< std::endl<<std::flush;
												}
												//		std::cout << "line = \"" << line << "\""<<std::endl;
												//try{}catch(const std::exception & exception){}
												auto tokens=tokenize(line);
												// CI: check if the string is empty. If so, break the while and generate the output
												if (tokens.isEmpty())
																goto loop_end;

												SLURM_Task job_info;		
												// first one is the job id
												setCurrentElementString("JobID");
												std::string token=tokens.next();
												size_t pos=token.find(".");
												if (pos==std::string::npos)
																job_info.job_step=false;
												else{
																job_info.job_step=true;
																if (token.substr(pos,std::string::npos)==std::string(".batch")){
																				job_info.job_script=true;
																}
																else job_info.job_script=false;
												}
												job_info.job_id=std::stoi(token.substr(0,pos),NULL,10);
												job_info.job_id_str=token;
												pos=token.find("_");
												if (pos==std::string::npos) {
																job_info.array_job=false;
																job_info.array_step_id=0;
												}
												else {
																job_info.array_job=true;
																job_info.array_step_id=std::stoi(token.substr(pos+1,std::string::npos),NULL,10);
												}
												// Account	
												setCurrentElementString("Account");
												job_info.project=tokens.next();
												if (job_info.project.size())
																last_project=job_info.project;
												// User
												setCurrentElementString("User");
												job_info.username=tokens.next();
												// ReqCPUS
												setCurrentElementString("ReqCPUs");
												token=tokens.next();job_info.req_cpu=std::stoi(token);
												// ReqMem
												setCurrentElementString("ReqMEM");
												token=tokens.next();
												uint32_t req_mem=std::stoul(token,NULL,10);
												if (req_mem&1<<31)	{	
																//				std::cout << "Exclusive?:" << req_mem<<std::endl;
																//				req_mem=req_mem&0x7fffffff;
																//				std::cout  << "Job reqested "<< req_mem<<"of memory" << std::endl;
																job_info.exclusive_job=true;
												}
												job_info.req_mem=SLURM_ReqMEM(token,&pos);
												job_info.req_mem_per_core=false;
												job_info.req_mem_per_node=false;
												if(pos!=std::string::npos && token[pos]=='c')	job_info.req_mem_per_core=true;
												if(pos!=std::string::npos && token[pos]=='n')	job_info.req_mem_per_node=true;
												// ReqNodes
												setCurrentElementString("ReqNodes");
												token=tokens.next();
												token.size()?job_info.req_nodes=std::stoi(token):job_info.req_nodes=0;
												// AllocNodes
												setCurrentElementString("AllocNodes");
												token=tokens.next();
												token.size()?job_info.alloc_nodes=std::stoi(token):job_info.alloc_nodes=0;
												// AllocCPUS
												setCurrentElementString("AllocCPUS");
												token=tokens.next();
												token.size()?job_info.alloc_cpu=std::stoi(token):job_info.alloc_cpu=0;
												// NNodes
												setCurrentElementString("NNodes");
												token=tokens.next();
												token.size()?job_info.nnodes=std::stoi(token):job_info.nnodes=0;
												// NCPUS
												setCurrentElementString("NCPUs");
												token=tokens.next();
												token.size()?job_info.ncpus=std::stoi(token):job_info.ncpus=0;
												// NTasks
												//
												setCurrentElementString("NTasks");
												token=tokens.next();token.size()>0?job_info.ntasks=std::stoi(token):job_info.ntasks=0;
												// State
												setCurrentElementString("State");
												token=tokens.next();job_info.job_state=state_to_id(token);
												// CPUTimeRAW
												setCurrentElementString("CPUTimeRAW");
												token=tokens.next();job_info.cpu_time_raw=std::stoull(token);
												// ElapsedRaw
												setCurrentElementString("ElapsedRAW");
												token=tokens.next();job_info.elapsed_raw=std::stoull(token);
												// TotalCPU
												setCurrentElementString("TotalCPU");
												token=tokens.next();job_info.total_cpu=time_to_seconds(token);
												// SystemCPU
												setCurrentElementString("SystemCPU");
												token=tokens.next();job_info.system_cpu=time_to_seconds(token);
												// UserCPU
												setCurrentElementString("UserCPU");
												token=tokens.next();job_info.user_cpu=time_to_seconds(token);
												// MinCPU
												setCurrentElementString("MinCPU");
												token=tokens.next();
												job_info.min_cpu=time_to_seconds(token);
												// AveCPU
												setCurrentElementString("AveCPU");
												token=tokens.next();job_info.average_cpu=time_to_seconds(token);
												// MaxDiskRead
												setCurrentElementString("MaxDiskRead");
												token=tokens.next();
												job_info.max_disk_read=suffix_ull(token,NULL,'b');
												// AveDiskRead
												setCurrentElementString("AveDiskRead");
												token=tokens.next();job_info.ave_disk_read=suffix_ull(token,NULL,'b');
												// MaxDiskWrit
												setCurrentElementString("MaxDiskWrite");
												token=tokens.next();job_info.max_disk_write=suffix_ull(token,NULL,'b');
												// AveDiskWrite
												setCurrentElementString("AveDiskWrite");
												token=tokens.next();job_info.ave_disk_write=suffix_ull(token,NULL,'b');
												// MaxRSS
												setCurrentElementString("MaxRSS");
												token=tokens.next();job_info.max_rss=suffix_double_to_ull(token,NULL,'k');
												// AveRSS
												setCurrentElementString("AveRSS");
												token=tokens.next();job_info.ave_rss=suffix_double_to_ull(token,NULL,'k');
												// Submit
												setCurrentElementString("Submit");
												token=tokens.next();
												if (token.size()) {job_info.submit_time=date_to_timet(token);job_info.submit_time_set=true;}
												// Start
												setCurrentElementString("Start");
												token=tokens.next();
												if (token.size()){job_info.start_time=date_to_timet(token);job_info.start_time_set=true;}
												// End
												setCurrentElementString("End");
												token=tokens.next();
												if (token.size()) {
													if (token == std::string("Cyclic") || token == std::string("Unknown")) {	
														job_info.end_time=0;
														job_info.end_time_set=false;
													}
													else {
														job_info.end_time=date_to_timet(token);job_info.end_time_set=true;
													}
												}
												else {job_info.end_time=0;job_info.end_time_set=false;}
												setCurrentElementString("Layout");
												if (!tokens.end()) {
													tokens.next();
												}
												setCurrentElementString("ReqTRES");
												if (!tokens.end()) {
													tokens.next();
												}
												setCurrentElementString("AllocTRES");
												if (!tokens.end()) {
													tokens.next();
												}
												setCurrentElementString("ReqGRES");
												if (!tokens.end()) {
													tokens.next();
												}
												setCurrentElementString("AllocGRES");
												if (!tokens.end()) {
													tokens.next();
												}
												setCurrentElementString("Cluster");
												if (!tokens.end()) {
													tokens.next();
												}
												setCurrentElementString("Partition");
												if (!tokens.end()) {
													tokens.next();
												}
												setCurrentElementString("Submit");
												if (!tokens.end()) {
													tokens.next();
												}
												setCurrentElementString("Start");
												if (!tokens.end()) {
													tokens.next();
												}
												setCurrentElementString("End");
												if (!tokens.end()) {
													tokens.next();
												}
												// Remaining entries
												tokens.discardRemaining();
												//					std::cout << "token: \""<<tokens.next()<<"\""<<std::endl;
												//
												//		if (line_count==5) break;
												//		std::cout << job_info << std::endl;

												if (job_info.job_state==0) continue;  // skip running jobs

												auto task=std::make_shared<SLURM_Task>(job_info);

												if (job_info.job_step)	{
																last_job->add_job_step(task);
																task->add_parent(last_job);
																jobsteps_read++;
												}
												else {
																job_list.push_back(task);	
																last_job=task;
																jobs_read++;
												}		
								}
								catch(...){
												// something happened in here, lets try to conintue, but increment the catch counter	
												exception_count++;
												std::cerr << "Failed interpreting line \"" << line << std::endl;
								}
				}
loop_end:
				std::cout << std::endl;
#ifdef DEBUG
				std::cout << "Read " << line_count <<" lines from file" << std::endl;
				std::cout << "Found " << data_storage.size() << " projects" << std::endl;
				std::cout << job_list[0]->filed_descr() << std::endl;;
				for (auto i:job_list){
								std::cout << "  "<< *i << "\tmemeff"<<i->compute_memory_efficiency()<< std::endl;
								// TODO
								for (auto step:i->get_job_steps()){
												std::cout << "* " << *step<< "\tmemeff"<<i->compute_memory_efficiency()<<std::endl;
								}
				}
				exit (0);
#endif
}

SLURM_Log_Reader::SLURM_Log_Reader(){
				jobs_read=jobsteps_read=0;
				lines_processed=0;
				reset();
}
