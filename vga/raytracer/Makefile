CXX := ~/pyston_deps/gcc-4.8.2-install/bin/g++
CXXFLAGS := -O2 -std=c++11
LDFLAGS := -lglut -lGL -lGLU
SRCS := mandlebrot.cpp
OBJS := $(SRCS:.cpp=.o)

all: mandlebrot

.PHONY: run
run: mandlebrot
	./mandlebrot

mandlebrot: $(OBJS)
	$(CXX) $(LDFLAGS) $(CXXFLAGS) $(OBJS) -o $@

$(OBJS): %.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm $(OBJS) $(PROG)

