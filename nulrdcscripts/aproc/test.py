import winsound
import time
from win10toast import ToastNotifier


print("Notification block entered")
beepcount = 0
while beepcount < 3:
    print("Beep")
    winsound.Beep(1000, 60)
    time.sleep(0.005)
    beepcount += 1
toaster = ToastNotifier()
toaster.show_toast("Script has finished running.", " ")
print("Toast notification shown")
