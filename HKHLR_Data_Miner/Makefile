all: HKHLR_DataMiner.exe


old_all: process_slurm_logs.exe process_slurm_logs.prof.exe process_slurm_logs.debug.exe HKHLR_DataMiner.exe


%.o: %.cxx
	g++  -g -std=c++11 -c -o $@ $<

HKHLR_DataMiner.exe:	HKHLR_DataMiner.cxx SLURM_Reader.cxx SLURM_Reader.h SLURM_Structures.h SLURM_Structures.cxx
	g++ -g -std=c++11 -c -o HKHLR_DataMiner.o HKHLR_DataMiner.cxx
	g++ -g -std=c++11 -c -o SLURM_Reader.o SLURM_Reader.cxx
	g++ -g -std=c++11 -c -o SLURM_Structures.o SLURM_Structures.cxx
	g++ -g -o $@ HKHLR_DataMiner.o SLURM_Reader.o SLURM_Structures.o -fopenmp

HKHLR_DataMinerMK2.exe:	HKHLR_DataMinerMK2.o SLURM_Reader.o SLURM_Reader.h SLURM_Structures.h SLURM_Structures.o SLURM_Analyzer.o SLURM_Analyzer.h
	g++ -g -o $@ HKHLR_DataMinerMK2.o SLURM_Reader.o SLURM_Structures.o SLURM_Analyzer.o -fopenmp
#	g++ -g -std=c++11 -c -o HKHLR_DataMinerMK2.o HKHLR_DataMinerMK2.cxx
#	g++ -g -std=c++11 -c -o SLURM_Reader.o SLURM_Reader.cxx
#	g++ -g -std=c++11 -c -o SLURM_Structures.o SLURM_Structures.cxx
#	g++ -g -std=c++11 -c -o SLURM_Analyzer.o	SLURM_Analyzer.cxx

HKHLR_DataMiner.ScorePIO.exe:	HKHLR_DataMiner.cxx SLURM_Reader.cxx SLURM_Reader.h SLURM_Structures.h SLURM_Structures.cxx
	scorep --io=posix g++ -g -std=c++11 -c -o HKHLR_DataMiner.o HKHLR_DataMiner.cxx
	scorep --io=posix g++ -g -std=c++11 -c -o SLURM_Reader.o SLURM_Reader.cxx
	scorep --io=posix g++ -g -std=c++11 -c -o SLURM_Structures.o SLURM_Structures.cxx
	scorep --io=posix g++ -g -o $@ HKHLR_DataMiner.o SLURM_Reader.o SLURM_Structures.o -fopenmp

#process_slurm_logs.exe: main.cxx
#	g++ -o $@ $< -g -std=c++11 -fopenmp


#process_slurm_logs.prof.exe: main.cxx
#	g++ -o $@ $< -pg -std=c++11 -fopenmp

#process_slurm_logs.debug.exe: main.cxx
#	g++ -o $@ $< -pg -std=c++11 -fopenmp -DDEBUG

testV1:	HKHLR_DataMiner.exe
	./HKHLR_DataMiner.exe "2017-W29" 2017_W29 HKHLR_SLURM_Darmstadt_2018-W29.log "2017-W30" 2017_30 HKHLR_SLURM_Darmstadt_2018-W30.log "2017-W31" 2017_W31 HKHLR_SLURM_Darmstadt_2018-W31.log 

testV2:	HKHLR_DataMinerMK2.exe
	./HKHLR_DataMinerMK2.exe "2017/01" 2017_01 test_data.log

testV3:	HKHLR_DataMiner.exe
	./HKHLR_DataMiner.exe "2017-W29" 2017_W29 HKHLR_SLURM_Darmstadt_2018-W29.log.small "2017-W30" 2017_30 HKHLR_SLURM_Darmstadt_2018-W30.log.small "2017-W31" 2017_W31 HKHLR_SLURM_Darmstadt_2018-W31.log.small 

test_all:	HKHLR_DataMiner.exe
	./HKHLR_DataMiner.exe "2017/01" 2017_01 2017_01.log "2017/02" 2017_02 2017_02.log

clean:
	rm -f HKHLR_DataMiner.exe
	rm -f core.*
	rm *.o

