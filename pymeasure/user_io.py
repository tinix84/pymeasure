import sys, time, msvcrt
askuser_timeout = 3

def ask_user():
    print('\n================================')
    check = str(input("Continue ? ([y]/n): ")).lower().strip()
    try:
        if check[:1] == 'y':
            return True
        elif check[:1] == 'n':
            return False
        elif check[:1] == '':
            return True
        else:
            print('Invalid Input')
            return ask_user()
    except Exception as error:
        print("Please enter valid inputs")
        print(error)
        return ask_user()


def ask_user_timeout():
    startTime = time.time()
    inp = None
    print('\n================================')
    print("Press any key to stop or wait x seconds...")
    while True:
        if msvcrt.kbhit():
            inp = msvcrt.getch()
            break
        elif time.time() - startTime > askuser_timeout:
            break
    if inp:
        print("Stopping...")
        return False
    else:
        print("Timed out and go on...")
        return True