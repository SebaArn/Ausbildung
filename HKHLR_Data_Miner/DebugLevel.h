#pragma once

class DebugLevel{
	private:
	int debugLevel;
	protected:
	int currentDebugLevel(){return debugLevel;};
  int debugLevelVerbose(){return 10;}
  int debugLevelAll(){return 11;}
  int debugLevelSilent(){return 0;}
  int debugLevelWarn(){return 3;}
  int debugLevelError(){return 1;};
  int debugLevelOps(){return 4;};
	public:
	DebugLevel():debugLevel(0){};
	void setDebugLevelVerbose(){debugLevel=debugLevelVerbose();};
  void setDebugLevelWarn(){debugLevel=debugLevelWarn();};
  void setDebugLevelOps(){debugLevel=debugLevelOps();};
  void setDebugLevelError(){debugLevel=debugLevelError();};
  void setDebugLevelAll(){debugLevel=debugLevelAll();};
  void setVerbosity(int i);
};
