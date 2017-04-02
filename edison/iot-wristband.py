import time, sys, signal, atexit
import pyupm_lsm9ds0 as sensorObj

def main():
    # Instantiate an LSM9DS0 using default parameters (bus 1, gyro addr 6b,
    # xm addr 1d)
    sensor = sensorObj.LSM9DS0()
    f = open('values.csv', 'w')

    ## Exit handlers ##
    # This function stops python from printing a stacktrace when you hit control-C
    def SIGINTHandler(signum, frame):
        raise SystemExit

    # This function lets you run code on exit
    def exitHandler():
        f.close()
        print("Exiting")
        sys.exit(0)

    # Register exit handlers
    atexit.register(exitHandler)
    signal.signal(signal.SIGINT, SIGINTHandler)

    sensor.init()

    cur_acc, cur_gyr, cur_mag = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
    while (1):
        sensor.update()

        prev_acc, prev_gyr, prev_mag = (cur_acc, cur_gyr, cur_mag)
        (cur_acc, dif_acc, cur_gyr, dif_gyr, cur_mag, dif_mag) = load_values(sensor, prev_acc, prev_gyr, prev_mag)

        #print_to_console(cur_acc, "A")
        print_to_console(cur_gyr, "G")
        #print_to_console(dif_gyr, "DG")

        print_to_file(f, cur_acc, cur_gyr, cur_mag)
        command = get_command(cur_acc, cur_gyr, cur_mag)
        if command:
            print(command)
            write_file('data.txt', command)
            time.sleep(1.0)

        time.sleep(0.1)

def write_file(filename, value):
    with open(filename, 'w') as f:
        f.write(value)

def load_values(sensor, prev_acc, prev_gyr, prev_mag):
    (x, y, z) = (sensorObj.new_floatp(), sensorObj.new_floatp(), sensorObj.new_floatp())

    sensor.getAccelerometer(x, y, z)
    cur_acc = (sensorObj.floatp_value(x), sensorObj.floatp_value(y), sensorObj.floatp_value(z))
    dif_acc = get_differential(cur_acc, prev_acc)

    sensor.getGyroscope(x, y, z)
    cur_gyr = (sensorObj.floatp_value(x), sensorObj.floatp_value(y), sensorObj.floatp_value(z))
    dif_gyr = get_differential(cur_gyr, prev_gyr)

    sensor.getMagnetometer(x, y, z)
    cur_mag = (sensorObj.floatp_value(x), sensorObj.floatp_value(y), sensorObj.floatp_value(z))
    dif_mag = get_differential(cur_mag, prev_mag)

    return (cur_acc, dif_acc, cur_gyr, dif_gyr, cur_mag, dif_mag)

def get_differential(current, previous):
    (cx, cy, cz) = current
    (px, py, pz) = previous
    return (cx - px, cy - py, cz - pz)

def print_to_console(data, prefix):
    (x, y, z) = data
    print("{0}X: {1}\t{0}Y: {2}\t{0}Z: {3}".format(prefix, x, y, z))

def print_to_file(f, acc, gyr, mag):
    (ax, ay, az) = acc
    (gx, gy, gz) = gyr
    (mx, my, mz) = mag

    f.write('{0},{1},{2},'.format(ax, ay, az))
    f.write('{0},{1},{2},'.format(gx, gy, gz))
    f.write('{0},{1},{2}\n'.format(mx, my, mz))

def round_data(data, threshold):
    (x, y, z) = data
    return (round_value(x, threshold), round_value(y, threshold), round_value(z, threshold))

def round_value(value, threshold):
    if value >= threshold:
        return 1
    elif value < -threshold:
        return -1
    else:
        return 0

def get_command(acc, gyr, mag):
    (ax, ay, az) = round_data(acc, 0.7)
    (gx, gy, gz) = round_data(gyr, 80)
    (mx, my, mz) = round_data(mag, 0.05)

    if gy: # is moving in Y
        if not ax and ay and not az: # is facing an horizontal side
            if ay < 0:
                return "right"
            else:
                return "left"
    if mz and gy and not gz: # is moving in Y
        if ax:
            if gy < 0:
                return "up"
            #else:
            #    return "down"s
    return None

if __name__ == '__main__':
    main()