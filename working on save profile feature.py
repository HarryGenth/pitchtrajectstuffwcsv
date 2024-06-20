import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os


def calculate_coordinates(release_height, release_side, extension, velocity_mph, tarp_distance, horizontal_break,
                          induced_vertical_break):
    # Constants
    mound_to_plate_distance = 60.5
    strikezone_height = 2.5
    plate_center_horizontal = 0.0
    g = 32.174  # Acceleration due to gravity in feet/s^2

    # Convert velocity from mph to fps
    velocity = velocity_mph * 1.467

    # Calculate time taken to reach the plate
    time_to_plate = (mound_to_plate_distance - extension) / velocity

    # Calculate initial vertical velocity component
    vertical_velocity = ((strikezone_height - release_height) + 0.5 * g * time_to_plate ** 2) / time_to_plate

    # Calculate the horizontal velocity component (assuming release_side is the horizontal displacement)
    horizontal_velocity = -release_side / time_to_plate

    # Incorporate breaks into the positions at the plate
    horizontal_position_at_plate = release_side + horizontal_break
    vertical_position_at_plate = strikezone_height + induced_vertical_break

    # Calculate the positions at the tarp
    time_to_tarp = (tarp_distance - extension) / velocity

    horizontal_position_at_tarp = release_side + horizontal_velocity * time_to_tarp + (
                horizontal_break / time_to_plate) * time_to_tarp
    vertical_position_at_tarp = release_height + vertical_velocity * time_to_tarp - 0.5 * g * time_to_tarp ** 2 + (
                induced_vertical_break / time_to_plate) * time_to_tarp

    return horizontal_position_at_tarp, vertical_position_at_tarp


def save_to_csv():
    last_name = entry_last_name.get()
    first_name = entry_first_name.get()
    release_height = entry_release_height.get()
    release_side = entry_release_side.get()
    extension = entry_extension.get()
    velocity_mph = entry_velocity.get()
    horizontal_break = entry_horizontal_break.get()
    induced_vertical_break = entry_induced_vertical_break.get()

    profile = [last_name, first_name, release_height, release_side, extension, velocity_mph, horizontal_break, induced_vertical_break]

    if not all(profile):
        messagebox.showerror("Input Error", "Please fill all the fields before saving.")
        return

    profiles = []

    # Load existing profiles if file exists
    if os.path.isfile('pitch_data.csv'):
        with open('pitch_data.csv', mode='r', newline='') as file:
            reader = csv.reader(file)
            profiles = list(reader)

    header = profiles[0] if profiles else ['Last Name', 'First Name', 'Release Height', 'Release Side', 'Extension', 'Velocity', 'Horizontal Break', 'Induced Vertical Break']
    profiles_dict = {tuple(row[:2]): row for row in profiles[1:]}  # Dictionary for quick lookup

    # Add or update the profile in the dictionary
    profiles_dict[(last_name, first_name)] = profile

    # Convert dictionary back to list and sort
    profiles = [header] + sorted(profiles_dict.values(), key=lambda x: (x[0], x[1]))

    # Write back to CSV
    with open('pitch_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(profiles)

    load_profiles()


def load_profiles():
    try:
        profiles = []
        if os.path.isfile('pitch_data.csv'):
            with open('pitch_data.csv', mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                profiles = [row for row in reader]

        profile_dropdown['values'] = ["{} {}".format(profile[0], profile[1]) for profile in profiles]
        profile_dropdown.bind("<<ComboboxSelected>>", lambda event: select_profile(profiles))
    except Exception as e:
        print(f"Error loading profiles: {e}")


def select_profile(profiles):
    selected_profile = profile_dropdown.get()
    last_name, first_name = selected_profile.split()
    for profile in profiles:
        if profile[0] == last_name and profile[1] == first_name:
            entry_last_name.delete(0, tk.END)
            entry_last_name.insert(0, profile[0])
            entry_first_name.delete(0, tk.END)
            entry_first_name.insert(0, profile[1])
            entry_release_height.delete(0, tk.END)
            entry_release_height.insert(0, profile[2])
            entry_release_side.delete(0, tk.END)
            entry_release_side.insert(0, profile[3])
            entry_extension.delete(0, tk.END)
            entry_extension.insert(0, profile[4])
            entry_velocity.delete(0, tk.END)
            entry_velocity.insert(0, profile[5])
            entry_horizontal_break.delete(0, tk.END)
            entry_horizontal_break.insert(0, float(profile[6]))  # convert to inches
            entry_induced_vertical_break.delete(0, tk.END)
            entry_induced_vertical_break.insert(0, float(profile[7]))  # convert to inches
            break


def calculate_and_display(event=None):
    try:
        release_height = float(entry_release_height.get())
        release_side = float(entry_release_side.get())
        extension = float(entry_extension.get())
        velocity_mph = float(entry_velocity.get())
        tarp_distance = slider_tarp_distance.get()
        horizontal_break = float(entry_horizontal_break.get()) * 1 / -12  # convert to inches
        induced_vertical_break = float(entry_induced_vertical_break.get()) * 1 / -12  # convert to inches

        coordinates = calculate_coordinates(release_height, release_side, extension, velocity_mph, tarp_distance,
                                            horizontal_break, induced_vertical_break)

        plot_coordinates(coordinates)
        coordinates_label.config(text=f"Coordinates on the tarp: ({coordinates[0]:.2f}, {coordinates[1]:.2f})")
        error_label.config(text="")
    except ValueError:
        plot_coordinates(None)  # Clear the canvas in case of error
        error_label.config(text="Please enter valid numerical values", fg="red")
    except Exception as e:
        print(f"Unexpected error: {e}")
        plot_coordinates(None)  # Clear the canvas in case of error


def plot_coordinates(coordinates):
    try:
        # Clear previous plot
        canvas.delete("all")

        # Get the current size of the canvas
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if canvas_width == 0 or canvas_height == 0:
            return  # Prevent drawing if the canvas size is not valid yet

        # Calculate the size of each grid square
        grid_size = min(canvas_width, canvas_height) // 8

        # Calculate offsets to center the grid
        x_offset = (canvas_width - grid_size * 8) // 2
        y_offset = (canvas_height - grid_size * 8) // 2

        # Fill the background with dark gray
        canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="darkgray")

        # Draw grid
        for i in range(9):
            canvas.create_line(x_offset + i * grid_size, y_offset, x_offset + i * grid_size, y_offset + grid_size * 8,
                               fill="gray")
            canvas.create_line(x_offset, y_offset + i * grid_size, x_offset + grid_size * 8, y_offset + i * grid_size,
                               fill="gray")

        # Draw the center intersections with '*'
        for i in range(1, 8):
            for j in range(0, 6):
                x = x_offset + i * grid_size
                y = y_offset + j * grid_size + grid_size  # Adjust vertical position
                canvas.create_text(x, y, text='+', fill="white", font=("Arial", int(grid_size * 0.6)))

        if coordinates is not None:
            # Draw the point
            x = x_offset + (coordinates[0] + 4) * grid_size  # Convert feet to canvas coordinates
            y = y_offset + (8 - coordinates[1]) * grid_size  # Convert feet to canvas coordinates
            canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="red")
            canvas.create_text(x, y - 10, text=f"({coordinates[0]:.2f}, {coordinates[1]:.2f})", fill="red")

        # Draw the outer border of the grid
        canvas.create_rectangle(
            x_offset, y_offset, x_offset + grid_size * 8, y_offset + grid_size * 8,
            outline="royalblue", width=3
        )
    except Exception as e:
        print(f"Error during plotting: {e}")


def on_resize(event):
    canvas_size = min(event.width, event.height)
    canvas.config(width=canvas_size, height=canvas_size)
    plot_coordinates(None)  # Redraw the grid without the target


# Create the main window
root = tk.Tk()
root.title("Pitch Trajectory Calculator")

# Get screen width and height using tkinter
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set the window to take up the left half of the screen
root.geometry(f"{screen_width // 2}x{screen_height}+0+0")

# Create and place the input fields and labels
inputs_frame = tk.Frame(root)
inputs_frame.grid(row=0, column=0, padx=10, pady=10)

# Create and place the input fields and labels
inputs_frame = tk.Frame(root)
inputs_frame.grid(row=0, column=0, padx=10, pady=10)

tk.Label(inputs_frame, text="Last Name:").grid(row=0, column=0, pady=5)
entry_last_name = tk.Entry(inputs_frame)
entry_last_name.grid(row=0, column=1, pady=5)

tk.Label(inputs_frame, text="First Name:").grid(row=1, column=0, pady=5)
entry_first_name = tk.Entry(inputs_frame)
entry_first_name.grid(row=1, column=1, pady=5)

tk.Label(inputs_frame, text="Release Height (feet):").grid(row=2, column=0, pady=5)
entry_release_height = tk.Entry(inputs_frame)
entry_release_height.grid(row=2, column=1, pady=5)

tk.Label(inputs_frame, text="Release Side (feet):").grid(row=3, column=0, pady=5)
entry_release_side = tk.Entry(inputs_frame)
entry_release_side.grid(row=3, column=1, pady=5)

tk.Label(inputs_frame, text="Extension (feet):").grid(row=4, column=0, pady=5)
entry_extension = tk.Entry(inputs_frame)
entry_extension.grid(row=4, column=1, pady=5)

tk.Label(inputs_frame, text="Velocity (mph):").grid(row=5, column=0, pady=5)
entry_velocity = tk.Entry(inputs_frame)
entry_velocity.grid(row=5, column=1, pady=5)

tk.Label(inputs_frame, text="Horizontal Break (inches):").grid(row=6, column=0, pady=5)
entry_horizontal_break = tk.Entry(inputs_frame)
entry_horizontal_break.grid(row=6, column=1, pady=5)

tk.Label(inputs_frame, text="Induced Vertical Break (inches):").grid(row=7, column=0, pady=5)
entry_induced_vertical_break = tk.Entry(inputs_frame)
entry_induced_vertical_break.grid(row=7, column=1, pady=5)

tk.Label(inputs_frame, text="Tarp Distance (feet):").grid(row=8, column=0, pady=5)
slider_tarp_distance = tk.Scale(inputs_frame, from_=11, to=60.5, orient=tk.HORIZONTAL, resolution=0.5, command=lambda x: calculate_and_display())
slider_tarp_distance.grid(row=8, column=1, pady=5)

# Dropdown menu for selecting profiles
tk.Label(inputs_frame, text="Select Profile:").grid(row=9, column=0, pady=5)
profile_dropdown = ttk.Combobox(inputs_frame, state="readonly")
profile_dropdown.grid(row=9, column=1, pady=5)
load_profiles()

# Create and place the calculate button
calculate_button = tk.Button(inputs_frame, text="Calculate", command=calculate_and_display)
calculate_button.grid(row=10, columnspan=2, pady=10)

# Create and place the save profile button
save_button = tk.Button(inputs_frame, text="Save Profile", command=save_to_csv)
save_button.grid(row=11, columnspan=2, pady=10)

# Label to display the coordinates
coordinates_label = tk.Label(inputs_frame, text="")
coordinates_label.grid(row=12, columnspan=2)

# Label to display input errors
error_label = tk.Label(inputs_frame, text="", fg="red")
error_label.grid(row=13, columnspan=2)

# Create a frame for the canvas
canvas_frame = tk.Frame(root)
canvas_frame.grid(row=0, column=1, rowspan=14, sticky="nsew", padx=10, pady=10)

# Make the canvas frame resize with the window
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
canvas_frame.grid_rowconfigure(0, weight=1)
canvas_frame.grid_columnconfigure(0, weight=1)

# Create a canvas for plotting
canvas = tk.Canvas(canvas_frame, bg="darkgray")
canvas.grid(row=0, column=0, sticky="nsew")

# Bind the canvas frame's size changes to the on_resize function
canvas_frame.bind("<Configure>", on_resize)

# Bind the "Return" key to the calculate_and_display function for live updates
entry_release_height.bind("<Return>", calculate_and_display)
entry_release_side.bind("<Return>", calculate_and_display)
entry_extension.bind("<Return>", calculate_and_display)
entry_velocity.bind("<Return>", calculate_and_display)

# Draw the initial grid without the target
root.update_idletasks()  # Ensure the window is fully rendered
plot_coordinates(None)

# Run the main event loop
root.mainloop()

