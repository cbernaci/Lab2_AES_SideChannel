#!/bin/csh -f

cd /afs/andrew.cmu.edu/usr16/cbernaci/private/18632/Lab2_AES/Lab2_AES_SideChannel/AES-Core-engine--master

#This ENV is used to avoid overriding current script in next vcselab run 
setenv SNPS_VCSELAB_SCRIPT_NO_OVERRIDE  1

/afs/ece.cmu.edu/support/synopsys/synopsys.release/T-Foundation/vcs/T-2022.06/linux64/bin/vcselab $* \
    -o \
    simv \
    -nobanner \

cd -

