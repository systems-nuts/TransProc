
#FIXME Path to TranProc
TRANSPROC := /home/abhishek/TransProc

#FIXME Destination IP address
DEST := 10.1.1.222

CRIU := $(TRANSPROC)/criu-3.15/criu/criu
CRIT := $(TRANSPROC)/criu-3.15/crit/crit

PYTHON := $(shell which python3)

DEBUGGER := $(TRANSPROC)/tools/debugger

TRACER := $(TRANSPROC)/tools/tracer

CURR := $(shell pwd)
USER := $(shell whoami)

BINDIR := $(CURR)/bin

CP := cp

ADDR := 0x501052
TGT := aarch64
PID := $(shell pidof cg)
BIN := cg
DEBUG := y

spawn:
	$(DEBUGGER) $(BIN) $(ADDR) &

dump:
	sudo $(CRIU) dump -vvv --shell-job -o dump.log -t $(PID)

transform:
	sudo $(PYTHON) $(CRIT) recode $(CURR) $(CURR)/$(TGT) $(TGT) $(BIN) $(BINDIR) $(DEBUG) 

shuffle:
	sudo $(PYTHON) $(CRIT) ss $(CURR) $(BIN)
	
restore:
	chmod +x $(BIN)
	sudo $(CRIU) restore -vvv --shell-job -o restore.log

scp:
	scp $(TGT)/* $(USER)@$(DEST):$(CURR)/.
