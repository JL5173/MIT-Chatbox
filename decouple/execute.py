import decouple.functions as func

state = func.INIT
mess = ""
while mess != "stop":
    mess = input("user: ")
    state,_ = func.send_message(state, mess)


