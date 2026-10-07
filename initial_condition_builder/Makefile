
CXX = c++

CFLAGS = -O3 -std=c++0x -Wall -g
INCLUDES = 
LFLAGS = 
LIBS = 

src = $(wildcard *.cc)
obj = $(src:.cc=.o)
deps = $(obj:.o=.d)

###########

generate_IC_unwrapableNuclesomes_SRC = 	generate_IC_unwrapableNuclesomes.cpp

generate_IC_unwrapableNuclesomes_EXE = generate_ic

###########


all: generate_IC_unwrapableNuclesomes

generate_IC_unwrapableNuclesomes: $(generate_IC_unwrapableNuclesomes_SRC:.cc=.o)
	$(CXX) $(CFLAGS) $(INCLUDES) $(LFLAGS) $(LIBS) -o $(generate_IC_unwrapableNuclesomes_EXE) $^



%.o : %.cc
	$(CXX) $(CFLAGS) $(INCLUDES) -c $< -o $@ -MMD -MF $(@:.o=.d)

-include $(deps)

.PHONY: clean

clean:
	rm -f $(obj) $(generate_IC_unwrapableNuclesomes_EXE) $(wildcard *.d)
