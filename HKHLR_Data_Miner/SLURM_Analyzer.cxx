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


SLURM_Analyzer::SLURM_Analyzer(){
	setDebugLevelError();
}
/*int SLURM_Analyzer::currentDebugLevel() { 	return debugLevel; };
int SLURM_Analyzer::debugLevelVerbose() {	return 4;};
int SLURM_Analyzer::debugLevelWarn() {	return 3;};
int SLURM_Analyzer::debugLevelError() {	return 1;};
int SLURM_Analyzer::debugLevelOps() {	return 2;};

int SLURM_Analyzer::debugLevelSilent() {return 0;};


void SLURM_Analyzer::setDebugLevelVerbose(){	debugLevel=debugLevelVerbose();}
void SLURM_Analyzer::setDebugLevelWarn(){	debugLevel=debugLevelWarn();}
void SLURM_Analyzer::setDebugLevelOps(){	debugLevel=debugLevelOps();}
void SLURM_Analyzer::setDebugLevelError(){	debugLevel=debugLevelError();;}
void SLURM_Analyzer::setDebugLevelAll(){	debugLevel=1001;		SLURM_reader.setDebugLevelAll();}


int SLURM_Analyzer::debugLevelReallyNoisyVerbose() { 
	return 1000; 
};
*/
template <typename Func>	void SLURM_Analyzer::debugLevelGuard(int i, Func f){
			if (currentDebugLevel() >= i)
			f();
};


void SLURM_Analyzer::addSLURMlogfile(std::string filename, std::string inFileDesc, std::string filePostFix){
	SLURM_reader.read_file(filename);
	debugLevelGuard(debugLevelVerbose(), [this](void) { SLURM_reader.DEBUG_print_statistics(); });
	auto local_joblist = SLURM_reader.get_job_list();
	debugLevelGuard(debugLevelOps(), [local_joblist](void) { std::cout << "[OPS]: read " << local_joblist.size() << " items from file " << std::endl; });
	std::cout << "Test" <<std::endl;
	std::cout << "Test" <<std::endl;;
	jobList.insert(jobList.end(),local_joblist.begin(),local_joblist.end());
};

void SLURM_Analyzer::addSLURMlogfile(std::string filename){

};
//void SLURM_Analyzer::readSLURMdb() = delete;
void SLURM_Analyzer::generateTopProjectTable(std::string output_filename){
	debugLevelGuard(debugLevelOps(), [](void) { std::cout << "[OPS]: generating Top Projects Table" << std::endl;});
};
