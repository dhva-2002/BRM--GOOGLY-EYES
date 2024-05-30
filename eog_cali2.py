import serial
import time
import json

def read_from_arduino(ser):

    line = ser.readline().decode().strip()
    voltage_values = line.split(',')

    return voltage_values

def collect_calibration_data(ser):

    print("Collecting calibration data...")
    
    calibration_data = {'up': {'vertical': [], 'horizontal': [], 'peak_location': None}, 
                        'down': {'vertical': [], 'horizontal': [], 'peak_location': None}, 
                        'left': {'vertical': [], 'horizontal': [], 'peak_location': None}, 
                        'right': {'vertical': [], 'horizontal': [], 'peak_location': None}, 
                        'blink': {'vertical': [], 'horizontal': [], 'peak_locations': None}}

    direction_time = input(f"Enter acquisition time for each step of calibration: ")
    direction_time = float(direction_time)

    for direction in calibration_data.keys():
        print(f"Starting acquisition for {direction.upper()}. Press Enter when ready.")
        input()  # Wait for user to press Enter
        print(f"Acquiring data for {direction}")
        direction_start_time = time.time()
        
        while time.time() - direction_start_time < direction_time:
            voltage_values = read_from_arduino(ser)
            
            # Check if the first voltage value contains '\r'
            if '\r' in voltage_values[0]:
                voltage_values = voltage_values[0].split('\r') + voltage_values[1:]
                
            # Check if the first or second voltage value is an empty string, and skip the iteration if so
            if not voltage_values[0]:
                continue
            elif len(voltage_values) < 2 or not voltage_values[1]:
                continue
                
            calibration_data[direction]['vertical'].append(float(voltage_values[0]))
            calibration_data[direction]['horizontal'].append(float(voltage_values[1]))
            
    # Calculculate max values and indexes for each direction
    max_value_up = max(calibration_data['up']['vertical'])
    max_index_up = calibration_data['up']['vertical'].index(max_value_up)
    print(f"Max value up: {max_index_up}")

    max_value_down = max(calibration_data['down']['vertical'])
    max_index_down = calibration_data['down']['vertical'].index(max_value_down)
    print(f"Max value down: {max_index_down}")

    max_value_left = max(calibration_data['left']['horizontal'])
    max_index_left = calibration_data['left']['horizontal'].index(max_value_left)
    print(f"Max value left: {max_index_left}")

    max_value_right = max(calibration_data['right']['horizontal'])
    max_index_right = calibration_data['right']['horizontal'].index(max_value_right)
    print(f"Max value right: {max_index_right}")
    
    # Determine peak locations
    if max_index_up > max_index_down:
                calibration_data['up']['peak_location'] = 'low'
                calibration_data['down']['peak_location'] = 'high'
                calibration_data['blink']['peak_location'] = 'lower'
    else:
                calibration_data['up']['peak_location'] = 'high'
                calibration_data['down']['peak_location'] = 'low'
                calibration_data['blink']['peak_location'] = 'higher'

    if max_index_left > max_index_right:
                calibration_data['left']['peak_location'] = 'low'
                calibration_data['right']['peak_location'] = 'high'
    else:
                calibration_data['left']['peak_location'] = 'high'
                calibration_data['right']['peak_location'] = 'low'
   
    return calibration_data


def analyze_calibration_data(calibration_data):

    distance = 2 # Value to multiply standard deviation by to get threshold
    thresholds = {}
    
    # Set channel from which to get data
    for direction, data in calibration_data.items():
        if direction in ['up', 'down', 'blink']:
            voltages = data['vertical']
        elif direction in ['left', 'right']:
            voltages = data['horizontal']

        # Calculate mean
        mean_voltage = sum(voltages) / len(voltages)
        
        # Calculate standard deviation according to peak location
        if calibration_data[direction]['peak_location'] == 'low' or calibration_data[direction]['peak_location'] == 'lower':
            voltages = [v for v in voltages if v < mean_voltage]
            std_dev = (sum([(v - mean_voltage) ** 2 for v in voltages]) / len(voltages)) ** 0.5
            threshold = mean_voltage - distance * std_dev
        
        elif calibration_data[direction]['peak_location'] == 'high' or calibration_data[direction]['peak_location'] == 'higher':
            voltages = [v for v in voltages if v > mean_voltage]
            std_dev = (sum([(v - mean_voltage) ** 2 for v in voltages]) / len(voltages)) ** 0.5
            threshold = mean_voltage + distance * std_dev

        thresholds[direction] = {
            'mean_voltage': mean_voltage,
            'std_dev': std_dev,
            'threshold': threshold,

        }

    return thresholds


def save_data(thresholds, calibration_data, filename):
    data = {}
    data['thresholds'] = thresholds.copy()
    data['peak_locations'] = {}
    
    # Set peak locations to None if they are not present in calibration_data
    for direction in ['up', 'down', 'left', 'right','blink']:
        calibration_data[direction].setdefault('peak_location', None)
        
        data['peak_locations'][direction] = calibration_data[direction]['peak_location']
        
    # Save data to file
    with open(filename, 'w') as f:
        json.dump(data, f)

def main():
    
    ser = serial.Serial('COM5', 9600)

    calibration_data = collect_calibration_data(ser)
    thresholds = analyze_calibration_data(calibration_data)

    print("Calibration thresholds:")
    print(thresholds)
    print("Peak locations:")
    print("Up: ", calibration_data['up']['peak_location'])
    print("Down: ", calibration_data['down']['peak_location'])
    print("Left: ", calibration_data['left']['peak_location'])
    print("Right: ", calibration_data['right']['peak_location'])

    save_data(thresholds, calibration_data, 'calibration_thresholds.json')
    
    ser.close()

if __name__ == "__main__":
    main()
