.PHONY: dev-shell clean clean-nix clean-general patch build

BINPATH	:=	bin
VPATH	:=	utils:src:validation:$(BINPATH)

export PATH := utils:$(BINPATH):$(PATH)

# System env
PWD=$(shell pwd)

# Compiler settings
COMPILER	:=	$(shell root-config --cxx)
CXXFLAGS	:=	$(shell root-config --cflags)
LINKFLAGS	:=	$(shell root-config --libs)
ADDLINKFLAGS	:=	-lHammerTools -lHammerBase -lHammerCore -lFormFactors -lAmplitudes -lRates
VALLINKFLAGS	:=	-lff_dstaunu

clean:
	@rm -rf ./bin/*
	@rm -rf ./gen/*

###############
# Sample plot #
###############

sample-plots: gen/el_true.png gen/q2_true.png gen/mm2_true.png

gen/el_true.png gen/q2_true.png gen/mm2_true.png &: \
	samples/rdst-run1.root \
	gen/rdst-run1-ff_w.root \
	plot_ratio.py
	$(word 3, $^) -d $< -w $(word 2, $^) -t dst_iso -T mc_dst_tau_ff_w

gen/rdst-run1-ff_w.root: \
	samples/rdst-run1.root \
	rdx-run1-sample.w
	$(word 2, $^) $< $@


##############
# Validation #
##############

validation-plots: gen/validate_ff.png

gen/validate_ff.png: \
	samples/rdst-run1.root \
	gen/rdst-run1-ff_w.root \
	validate_ff_calc.v
	$(word 3, $^) $< $(word 2, $^) gen


####################
# Generic patterns #
####################

# Reweighters with HAMMER
%.w: %.cpp
	$(COMPILER) $(CXXFLAGS) -o $(BINPATH)/$@ $< $(LINKFLAGS) $(ADDLINKFLAGS)

# Validation scripts
%.v: %.cpp
	$(COMPILER) $(CXXFLAGS) -o $(BINPATH)/$@ $< $(LINKFLAGS) $(VALLINKFLAGS)
