import serial
import time
import threading

class UARTCommunicator:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.lock = threading.Lock()
        self.incoming = []
        self.running = True
        self.listen_thread = threading.Thread(target=self.listen_serial)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def listen_serial(self):
        while self.running:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode().strip()
                    if line:
                        self.incoming.append(line)
            except Exception as e:
                print("Error reading serial:", e)

    def send(self, message, retries=3, ack_timeout=1):
        with self.lock:
            for attempt in range(retries):
                try:
                    full_msg = message.strip() + '\n'
                    self.ser.write(full_msg.encode())
                    print(f"[TX] {message} (attempt {attempt+1})")
                    
                    start_time = time.time()
                    while time.time() - start_time < ack_timeout:
                        if self.incoming:
                            response = self.incoming.pop(0)
                            print(f"[RX] {response}")
                            if response == f"ACK:{message}":
                                return True
                    print("No ACK, retrying...")
                except Exception as e:
                    print("Error sending message:", e)
            print("Failed to get ACK after retries.")
            return False

    def get_messages(self):
        with self.lock:
            messages = self.incoming.copy()
            self.incoming.clear()
        return messages

    def close(self):
        self.running = False
        self.listen_thread.join()
        self.ser.close()


# Example usage for testing only
if __name__ == "__main__":
    comm = UARTCommunicator('/dev/ttyUSB0')  # Adjust port if needed
    comm.send("MODE:bongo")
    comm.send("FEED:2")
    comm.send("BUZZ")
    time.sleep(2)
    print("Messages received:", comm.get_messages())
    comm.close()

