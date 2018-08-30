with open('input.txt') as inpt_file:
    opt=''
    start = 0
    cntr = 1
    for x in inpt_file.read().split("\n"):
        if x:
            print ('in')
            # if (start == 1):
            with open(str(cntr) + '.txt','w') as opt_file:
                opt_file.write(x)
                opt_file.close()
                opt = ''
                cntr += 1
            # else:

        #         # start = 1
        else:
            opt = opt + '\n' + x

    inpt_file.close()