from machine import Pin, UART
import time

# set up UART for client
uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

def send_command(command):
    uart1.write(command + "\n")

def receive_response():
    if uart1.any():
        try:
            response = uart1.readline().decode('utf-8').strip()
            print(f"Server Response: {response}")
            return response
        except Exception as e:
            print(f"Error reading response: {e}")

def send_mail(message):
    print(f"Sending mail: {message}")
    send_command(f"SEND:{message}")

def retrieve_mail():
    print("Retrieving mail...")
    send_command("RETR")
    time.sleep(1)  # Wait for server response
    receive_response()

def delete_mail():
    print("Deleting all mail...")
    send_command("DELE")
    time.sleep(1)  # Wait for server response
    receive_response()

def main():
    while True:
        # Send a new mail message every 10 seconds
        send_mail("Hello! This is a new message.")
        time.sleep(10)
        
        # Retrieve mail after 5 seconds
        retrieve_mail()
        
        # After 20 seconds, delete all messages
        time.sleep(20)
        delete_mail()

main()
