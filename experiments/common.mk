.PHONY: all vdso clean get-from-x86 get-from-arm clean-img

BIN ?= loop
# Folder inside the TransProc repo
LOCATION ?= test/$(BIN)
BINDIR := $(CURDIR)/bin
PYTHON := python3

## Server configs
SERVER_X86 ?= nettuno
SERVER_ARM ?= sole

## QEMU configs
QEMU_TRANSPROC_X86 ?= /home/ubuntu/TransProc
QEMU_TRANSPROC_ARM ?= /home/ubuntu/TransProc
QEMU_USER_X86 ?= ubuntu
QEMU_USER_ARM ?= ubuntu
QEMU_IP_X86 ?= 127.0.0.1
QEMU_IP_ARM ?= 127.0.0.1
QEMU_PORT_X86 ?= 5555
QEMU_PORT_ARM ?= 5556

## Tool configs
TRANSPROC ?= /home/ubuntu/TransProc
DEBUG ?= y
ARM_TARGET := aarch64
X86_TARGET := x86-64

## Tools
RM := rm -rf
TRACER := $(TRANSPROC)/tools/tracer
CRIU := $(TRANSPROC)/criu-3.15/criu/criu -vvv --shell-job
CRIT := $(TRANSPROC)/criu-3.15/crit/crit
SERVER_TO_QEMU := $(TRANSPROC)/tools/server_to_qemu.py --password-file $(TRANSPROC)/tools/pass.txt

all:
	make -C criu-3.15 -j$(shell nproc)
	make -C tools

vdso:
	$(shell ./vdso/vdso.sh)

## Targets to invoke the process, criu, and crit

trace:
	sudo $(TRACER) $(shell pidof $(BIN))

dump:
	sudo $(CRIU) dump -o dump.log -t $(shell pidof $(BIN))

recode-x86:
	$(PYTHON) $(CRIT) recode $(CURDIR) $(CURDIR)/$(ARM_TARGET) $(ARM_TARGET) $(BIN) $(BINDIR) $(DEBUG)

recode-arm:
	$(PYTHON) $(CRIT) recode $(CURDIR) $(CURDIR)/$(X86_TARGET) $(X86_TARGET) $(BIN) $(BINDIR) $(DEBUG)

restore:
	sudo $(CRIU) restore -o restore.log

## Targets to get and copy binaries and images

broadcast-bin:
	cp $(BINDIR)/$(BIN)_$(X86_TARGET) $(BIN)
	scp -P $(QEMU_PORT_X86) -r $(BINDIR) $(QEMU_USER_X86)@$(QEMU_IP_X86):$(QEMU_TRANSPROC_X86)/$(LOCATION)/
	scp -P $(QEMU_PORT_X86) $(BIN) $(QEMU_USER_X86)@$(QEMU_IP_X86):$(QEMU_TRANSPROC_X86)/$(LOCATION)/
	cp $(BINDIR)/$(BIN)_$(ARM_TARGET) $(BIN)
	$(PYTHON) $(SERVER_TO_QEMU) $(SERVER_ARM) $(QEMU_PORT_ARM) $(QEMU_TRANSPROC_ARM)/$(LOCATION)/bin $(BINDIR)
	$(PYTHON) $(SERVER_TO_QEMU) $(SERVER_ARM) $(QEMU_PORT_ARM) $(QEMU_TRANSPROC_ARM)/$(LOCATION) $(BIN)

get-from-x86: clean-arm
	scp -P $(QEMU_PORT_X86) -r $(QEMU_USER_X86)@$(QEMU_IP_X86):$(QEMU_TRANSPROC_X86)/$(LOCATION)/$(ARM_TARGET) .

copy-to-arm:
	scp -P $(QEMU_PORT_ARM) -r $(ARM_TARGET)/* $(QEMU_USER_ARM)@$(QEMU_IP_ARM):$(QEMU_TRANSPROC_ARM)/$(LOCATION)/

get-from-arm: clean-x86
	scp -P $(QEMU_PORT_ARM) -r $(QEMU_USER_ARM)@$(QEMU_IP_ARM):$(QEMU_TRANSPROC_ARM)/$(LOCATION)/$(X86_TARGET) .

copy-to-x86:
	scp -P $(QEMU_PORT_X86) -r $(X86_TARGET)/* $(QEMU_USER_X86)@$(QEMU_IP_X86):$(QEMU_TRANSPROC_X86)/$(LOCATION)/

copy-to-qemu-arm: get-from-x86
	$(PYTHON) $(SERVER_TO_QEMU) $(SERVER_ARM) $(QEMU_PORT_ARM) $(QEMU_TRANSPROC_ARM)/$(LOCATION) $(ARM_TARGET)

copy-to-qemu-x86: get-from-arm
	$(PYTHON) $(SERVER_TO_QEMU) $(SERVER_X86) $(QEMU_PORT_X86) $(QEMU_TRANSPROC_X86)/$(LOCATION) $(X86_TARGET)

### The next three take the images without recoding, for debugging purposes

get-from-x86-no-recode: clean-x86
	mkdir $(X86_TARGET)
	scp -P $(QEMU_PORT_X86) -r $(QEMU_USER_X86)@$(QEMU_IP_X86):$(QEMU_TRANSPROC_X86)/$(LOCATION)/*.img $(X86_TARGET)

get-from-arm-no-recode: clean-arm
	mkdir $(ARM_TARGET)
	scp -P $(QEMU_PORT_ARM) -r $(QEMU_USER_ARM)@$(QEMU_IP_ARM):$(QEMU_TRANSPROC_ARM)/$(LOCATION)/*.img $(ARM_TARGET)

copy-to-x86-no-recode:
	scp -P $(QEMU_PORT_X86) -r $(ARM_TARGET)/* $(QEMU_USER_X86)@$(QEMU_IP_X86):$(QEMU_TRANSPROC_X86)/$(LOCATION)/

### Clean targets

clean-arm:
	$(RM) $(ARM_TARGET)

clean-x86:
	$(RM) $(X86_TARGET)

clean-img:
	$(RM) *.img

clean: clean-arm clean-x86 clean-img
