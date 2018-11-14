#pragma once
#ifndef SLURM_Analyzer_h 
#define SLURM_Analyzer_h

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
#include "DebugLevel.h"

class SLURM_Analyzer:public DebugLevel
{
  private:

  protected:
	std::vector<std::string> project_name_list;
	SLURM_Log_Reader SLURM_reader;
	std::vector<std::shared_ptr<SLURM_Task>> jobList;
	template <typename Func>	void debugLevelGuard(int i, Func f);

  public:
	explicit SLURM_Analyzer();
	void addSLURMlogfile(std::string filename, std::string inFileDesc, std::string filePostFix);
	void addSLURMlogfile(std::string filename);
	void readSLURMdb() = delete;
	void generateTopProjectTable(std::string output_filename);
	std::vector<std::string> getProjects();
};
#endif

