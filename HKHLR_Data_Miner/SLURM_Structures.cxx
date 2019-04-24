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

std::ostream &operator<<(std::ostream &os, SLURM_Task const &m) { 
    return os << m.to_string();
}
