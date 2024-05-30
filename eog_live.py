import serial
import queue
import time
import threading
import json
import os

def read_from_arduino(ser):
    
    sample_delay = 0.03  # Delay between each sample in seconds. Useful for saving CPU time.
    line = ser.readline().decode().strip()
    voltage_values = line.split(',')
        
    time.sleep(sample_delay)
    return voltage_values

def load_calibration_data(filename):

    with open(filename, 'r') as f:
        calibration_data = json.load(f)

    return calibration_data['thresholds'], calibration_data['peak_locations']


def classify_eye_movement(ser,voltage, thresholds, peak_location):
    
    # Assign threshold and peak location values to variables
    up_threshold = thresholds['up']['threshold']
    down_threshold = thresholds['down']['threshold']

    blink_threshold = thresholds['blink']['threshold']

    left_threshold = thresholds['left']['threshold']
    right_threshold = thresholds['right']['threshold']

    up_peak_location = peak_location['up']
    down_peak_location = peak_location['down']
    left_peak_location = peak_location['left']
    right_peak_location = peak_location['right']

    volt_vertical = voltage['vertical']
    volt_horizontal = voltage['horizontal']
    
    # Classify eye movement based on thresholds and peak locations
    # Special case for blink
    if up_peak_location == 'high' and volt_vertical > up_threshold:
        time.sleep(0.05)  
        voltage_values = read_from_arduino(ser)
        volt_vertical = float(voltage_values[0])  
        if volt_vertical > blink_threshold:  
            return 'blink'
        else:  
            return   'up'
    elif up_peak_location == 'low' and  volt_vertical< up_threshold:
        time.sleep(0.05)  
        voltage_values = read_from_arduino(ser)
        volt_vertical = float(voltage_values[0])  
        if volt_vertical < blink_threshold:  
            return 'blink'
        else:  
            return   'up'
    elif down_peak_location == 'high' and volt_vertical > down_threshold:
        return  'down'
    elif down_peak_location == 'low' and volt_vertical < down_threshold:
        return  'down'
    elif left_peak_location == 'high' and volt_horizontal > left_threshold:
        return  'left'
    elif left_peak_location == 'low' and volt_horizontal < left_threshold:
        return  'left'
    elif right_peak_location == 'high' and volt_horizontal > right_threshold:
        return  'right'
    elif right_peak_location == 'low' and volt_horizontal < right_threshold:
        return  'right'
    
    # Return 'unknown' if no movement is detected 
    return 'unknown'

def send_to_arduino(ser, movement):
    
    # Define the movement commands
    if movement == 'up':
        ser.write(b'1')
    elif movement == 'right':
        ser.write(b'2')
    elif movement == 'down':
        ser.write(b'3')
    elif movement == 'left':
        ser.write(b'4')
    elif movement == 'blink':
        ser.write(b'5')

def check_user_input(q):
    
    # Check for user input to stop the live acquisition
    while True:
        user_input = input()
        if user_input == "":
            q.put('stop')


def open_session(filename, new_session=False):
    
    # Check if a recording file already exists
    if new_session and os.path.isfile(filename + '.csv'):
        i = 1
        while os.path.isfile(f"{filename}_{i}.csv"):
            i += 1
        filename = f"{filename}_{i}"
        
    # Open the file and store the file object
    return open(filename + '.csv', 'a')

def record_voltage(voltage, file_obj):
    # Write the voltage into the file
    file_obj.write(str(voltage['vertical']) + ',' + str(voltage['horizontal']) + '\n')

def record_movement(movement, file_obj):
    # Write the detected movement into the file
    file_obj.write(f"{movement}\n")
        
def close_session(file_obj):
    # Close the file if it's open
    if file_obj is not None:
        file_obj.close()
        file_obj = None
        
def live_acquisition(ser_eog,ser_robot, thresholds, peak_location, recording,q):

    print("Starting live acquisition...")
    print("Press Enter to stop.")

    cooldown_end_time = 1 # Time to wait before detecting another eye movement

    try:
        while True:
            try:
                command = q.get_nowait()
            except queue.Empty:
                command = None

            if command == 'stop':
                print("Live acquisition stopped.")
                break

            voltage_values = read_from_arduino(ser_eog)
            
            # Check if the first or second voltage value is an empty string
            if not voltage_values[0]:
                continue
            if len(voltage_values) < 2 or not voltage_values[1]:
                continue
            
            voltage = {'vertical': float(voltage_values[0]), 'horizontal': float(voltage_values[1])}
            record_voltage(voltage,recording)

            # Classify eye movement based on thresholds
            if time.time() >= cooldown_end_time:
                movement = classify_eye_movement(ser_eog,voltage, thresholds, peak_location)
                if movement != 'unknown':
                    print(f"Detected eye movement: {movement}")
                    record_movement(movement, recording) 
                    cooldown_end_time = time.time() + 1
                    send_to_arduino(ser_robot, movement)
                    
    except KeyboardInterrupt:
        print("Live acquisition stopped interrupt.")

        
# Main function
def main():
    
    ser_eog = serial.Serial('COM5', 9600) 
    ser_robot =serial.Serial('COM6', 9600)
    
    # Create a queue to communicate between threads for stopping the live acquisition
    q = queue.Queue()
    thread = threading.Thread(target=check_user_input, args=(q,))
    thread.daemon = True
    thread.start()
    
    recording = open_session('session', new_session=True)

    # Load calibration data
    thresholds, peak_location = load_calibration_data('calibration_thresholds.json')

    # Start live acquisition
    live_acquisition(ser_eog,ser_robot, thresholds, peak_location, recording,q)
    
    # Close everything
    close_session(recording)
    ser_eog.close()
    ser_robot.close()
    print("Serial connection closed.")

if __name__ == "__main__":
    main()
