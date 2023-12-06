import cv2


"""
Calibration spot (absolute): X 1.20, Y 77.20, Z 85.00
First cell begin corner (abs): X 17.30, Y 147.20, Z 85.00
First cell end corner is at X 23.30


Fifth cell begin X 104.80
Cells are 22 mm away from each other

deriving from that,
Second cell begin X 39.1
Third cell begin 61.05
Fourth cell begin X 82.925


According to CAD, 19mm dist between calibration spot and first cell center
assuming 9 mm datamatrix, first spot should be X 15.7, and last spot should be 24.7
"""

laser_currently_engaged = False


def begin_file_write(gcode):
    gcode.write("M5\nG21\nG90\nG0 Z60 F7000\n\n\n")

def move_to_xy_position(gcode, x, y):
    gcode.write(f"G0 X{x} Y{y}\n")

def move_to_x_position(gcode, x):
    gcode.write(f"G0 X{x}\n")

def engage_laser(gcode):
    global laser_currently_engaged
    if not laser_currently_engaged:
        gcode.write("M3 S0.0750\n")
        laser_currently_engaged = True

def disengage_laser(gcode):
    global laser_currently_engaged
    if laser_currently_engaged:
        gcode.write("M3 S0.0000\n")
        laser_currently_engaged = False

def generate_cell_gcode(should_initialize_gcode=True, input_filename="0000.png", gcode_out_filename="test.gcode", cell_index=0, calibration_spot_x=1.2, calibration_spot_y=77.2, barcode_pixel_edge_size=1.0, laser_passes_per_y_pixel=21):

    # input_filename = '0000.png'
    # gcode_out_filename = "test.gcode"
    # Read the image
    image = cv2.imread(input_filename)
    gcode = open(gcode_out_filename, "a")

    # cell_index = 0
    # calibration_spot_x = 1.2
    # calibration_spot_y = 77.2
    inter_cell_distance = 22.0
    cell_distance_from_calibration_spot = 19.0 + inter_cell_distance * cell_index


    # barcode_pixel_edge_size = 1.0
    # laser_passes_per_y_pixel = 21

    barcode_width = 10.0 * barcode_pixel_edge_size  # TODO: actually grab from image
    barcode_height = 20.0 * barcode_pixel_edge_size

    barcode_begin_x = (calibration_spot_x + cell_distance_from_calibration_spot) - (barcode_width / 2)
    barcode_end_x = (calibration_spot_x + cell_distance_from_calibration_spot) + (barcode_width / 2)

    barcode_begin_y = calibration_spot_y + 70
    # barcode_end_y = barcode_begin_y - barcode_height

    if should_initialize_gcode:
        begin_file_write(gcode)


    rows, cols, _ = image.shape

    for i in range(rows):
        for k in range(laser_passes_per_y_pixel): # todo: go both ways
            move_to_xy_position(gcode, barcode_begin_x, (barcode_begin_y - (i * barcode_pixel_edge_size) - (k/laser_passes_per_y_pixel)))
            base_x_position = barcode_begin_x
            for j in range(cols):
                pixel_value = image[i, j]
                if (pixel_value[0] == 0):
                    engage_laser(gcode)
                else:
                    disengage_laser(gcode)
                move_to_x_position(gcode, base_x_position + (barcode_pixel_edge_size * j))
            move_to_xy_position(gcode, barcode_end_x, (barcode_begin_y - (i * barcode_pixel_edge_size) - (k/laser_passes_per_y_pixel) - (1/(laser_passes_per_y_pixel*2))))
            for j in reversed(range(cols)):
                pixel_value = image[i, j]
                if (pixel_value[0] == 0):
                    engage_laser(gcode)
                else:
                    disengage_laser(gcode)
                move_to_x_position(gcode, barcode_begin_x + (barcode_pixel_edge_size * j) - barcode_pixel_edge_size)

    gcode.close()
    
if __name__ == "__main__":
    generate_cell_gcode()