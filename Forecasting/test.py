from time import sleep

def write_message(message):
        sleep(10)
        f = open("hello.txt", "a")
        f.write("Now the file has more content!")
        f.close()
        return

write_message("hello")
