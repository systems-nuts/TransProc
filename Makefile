.PHONY: all vdso clean get-from-x86 clean-img

BIN ?= loop

all:
	make -C criu-3.15 -j$(shell nproc)
	make -C tools

vdso:
	$(shell ./vdso/vdso.sh)

get-from-x86:
	sshpass -p "asdfqwer" scp -P 5555 -r ubuntu@127.0.0.1:/home/ubuntu/TransProc/test/$(BIN)/aarch64 .

copy-to-arm:
	sshpass -p "asdfqwer" scp -P 5556 -r aarch64/* ubuntu@127.0.0.1:/home/ubuntu/TransProc/test/$(BIN)/

get-from-arm:
	sshpass -p "asdfqwer" scp -P 5556 -r ubuntu@127.0.0.1:/home/ubuntu/TransProc/test/$(BIN)/x86-64 .

copy-to-x86:
	sshpass -p "asdfqwer" scp -P 5555 -r x86-64/* ubuntu@127.0.0.1:/home/ubuntu/TransProc/test/$(BIN)/

get-from-arm-no-recode:
	mkdir aarch64
	sshpass -p "asdfqwer" scp -P 5556 -r ubuntu@127.0.0.1:/home/ubuntu/TransProc/test/$(BIN)/*.img aarch64

get-from-x86-no-recode:
	mkdir x86-64
	sshpass -p "asdfqwer" scp -P 5555 -r ubuntu@127.0.0.1:/home/ubuntu/TransProc/test/$(BIN)/*.img x86-64

copy-to-x86-no-recode:
	sshpass -p "asdfqwer" scp -P 5555 -r aarch64/* ubuntu@127.0.0.1:/home/ubuntu/TransProc/test/$(BIN)/

clean-img:
	rm -rf aarch64 x86-64

clean:
	make -C criu-3.15 clean
	make -C tools clean
