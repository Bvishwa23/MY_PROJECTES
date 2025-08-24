import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pymongo
from pymongo import MongoClient
import webbrowser
import gridfs
from io import BytesIO
from tkinter import filedialog
from PIL import Image, ImageTk 

class HouseDesignerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("SMART ARCHITECTURAL DESIGN")

        # MongoDB Connection
        self.client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
        self.db = self.client["house_design_db"]
        self.users_collection = self.db["users"]
        self.designs_collection = self.db["designs"]
        
        self.max_designs = 5
        self.design = 1
        self.fig = None
        self.ax = None

        self.logged_in_user = None

        self.main_frame = tk.Frame(master)
        self.main_frame.pack()
        self.background_image = None
        self.background_label = None
        self.set_background("img.jpg")

        # Initially show the login page
        self.show_login_page()
        self.fs = gridfs.GridFS(self.db)
    
    def set_background(self, image_name):
        """Set the background image by its name and ensure it fits the window."""
        try:
            # Load the image
            self.original_background_image = Image.open("img.jpg")

            # Dynamically resize the image based on the current window dimensions
            def resize_image(event=None):
                width = self.master.winfo_width()
                height = self.master.winfo_height()

                # Maintain aspect ratio
                aspect_ratio = self.original_background_image.width / self.original_background_image.height
                if width / height > aspect_ratio:
                    new_width = width
                    new_height = int(width / aspect_ratio)
                else:
                    new_height = height
                    new_width = int(height * aspect_ratio)

                resized_image = self.original_background_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.background_image = ImageTk.PhotoImage(resized_image)

                if self.background_label:
                    self.background_label.config(image=self.background_image)
                else:
                    self.background_label = tk.Label(self.master, image=self.background_image)
                    self.background_label.place(relx=0, rely=0, relwidth=1, relheight=1)
                    self.background_label.lower()  # Send to back

            # Bind resize events to dynamically adjust the background image
            self.master.bind("<Configure>", resize_image)

            # Initial call to set the background
            resize_image()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load background image: {e}")
        

    def clear_frame(self):
        """Clear the current frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_login_page(self):
        """Show the login page."""
        self.clear_frame()

        tk.Label(self.main_frame, text="Log In", font=("Arial", 24, 'bold')).pack(pady=10)

        tk.Label(self.main_frame, text="Username:", font=("Arial", 16)).pack()
        self.login_username_entry = tk.Entry(self.main_frame, font=("Arial", 16))
        self.login_username_entry.pack()

        tk.Label(self.main_frame, text="Password:", font=("Arial", 16)).pack()
        self.login_password_entry = tk.Entry(self.main_frame, show="*", font=("Arial", 16))
        self.login_password_entry.pack()

        tk.Button(self.main_frame, text="Log In", font=("Arial", 16), command=self.login).pack(pady=10)
        tk.Button(self.main_frame, text="Don't have an account? Sign Up", font=("Arial", 16), command=self.show_signup_page).pack()

    def login(self):
        """Handle user login."""
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get().strip()

        user = self.users_collection.find_one({"username": username})
        if user and user["password"] == password:
            self.logged_in_user = username
            messagebox.showinfo("Success", f"Welcome, {username}!")
            self.show_design_choice_page()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def show_signup_page(self):
        """Show the sign-up page."""
        self.clear_frame()

        tk.Label(self.main_frame, text="Sign Up", font=("Arial", 24, 'bold')).pack(pady=10)

        tk.Label(self.main_frame, text="Username:", font=("Arial", 16)).pack()
        self.signup_username_entry = tk.Entry(self.main_frame, font=("Arial", 16))
        self.signup_username_entry.pack()

        tk.Label(self.main_frame, text="Password:", font=("Arial", 16)).pack()
        self.signup_password_entry = tk.Entry(self.main_frame, show="*", font=("Arial", 16))
        self.signup_password_entry.pack()

        tk.Button(self.main_frame, text="Sign Up", font=("Arial", 16), command=self.signup).pack(pady=10)
        tk.Button(self.main_frame, text="Already have an account? Log In", font=("Arial", 16), command=self.show_login_page).pack()

    def signup(self):
        """Handle user sign-up."""
        username = self.signup_username_entry.get().strip()
        password = self.signup_password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            messagebox.showerror("Error", "Password must be at least 8 characters long, include an uppercase letter and a number.")
            return

        existing_user = self.users_collection.find_one({"username": username})
        if existing_user:
            messagebox.showerror("Error", "Username already exists.")
            return

        self.users_collection.insert_one({"username": username, "password": password})
        messagebox.showinfo("Success", "Sign up successful! Please log in.")
        self.show_login_page()

    def show_design_choice_page(self):
        """Show the choice page for design input."""
        self.clear_frame()

        tk.Label(self.main_frame, text="Choose Design Option", font=("Arial", 24, 'bold')).pack(pady=10)

        tk.Button(self.main_frame, text="Manually Enter Dimensions", font=("Arial", 16), command=self.show_house_design_page).pack(pady=10)

        tk.Button(self.main_frame, text="Open Through GPS (Google Earth)", font=("Arial", 16), command=self.show_gps_options_page).pack(pady=10)

    def show_gps_options_page(self):
        """Display options for Google Earth."""
        self.clear_frame()

        tk.Label(self.main_frame, text="Google Earth Options", font=("Arial", 24, 'bold')).pack(pady=10)

        # Option 1: Convert area to dimensions
        tk.Button(self.main_frame, text="Convert Area to Length & Breadth", font=("Arial", 16), command=self.show_conversion_page).pack(pady=10)

        # Option 2: Convert parameters to length and breadth
        tk.Button(self.main_frame, text="Convert Parameters to Dimensions", font=("Arial", 16), command=self.show_parameter_conversion_page).pack(pady=10)

        # Option 3: Open Google Earth Website
        tk.Button(self.main_frame, text="Open Google Earth Website", font=("Arial", 16), command=self.open_google_earth).pack(pady=10)

        # Back button
        tk.Button(self.main_frame, text="Back", font=("Arial", 16), command=self.show_design_choice_page).pack(pady=10)

    def show_conversion_page(self):
        """Page to convert area into dimensions."""
        self.clear_frame()

        tk.Label(self.main_frame, text="Convert Area to Dimensions", font=("Arial", 24, 'bold')).pack(pady=10)

        tk.Label(self.main_frame, text="Enter Area (sq meters):", font=("Arial", 16)).pack(pady=10)
        self.area_entry = tk.Entry(self.main_frame, font=("Arial", 16))
        self.area_entry.pack()

        tk.Label(self.main_frame, text="Enter Aspect Ratio (Length:Width):", font=("Arial", 16)).pack(pady=10)
        self.ratio_entry = tk.Entry(self.main_frame, font=("Arial", 16))
        self.ratio_entry.pack()

        tk.Button(self.main_frame, text="Convert", font=("Arial", 16), command=self.convert_area_to_dimensions).pack(pady=10)
        tk.Button(self.main_frame, text="Back to GPS Options", font=("Arial", 16), command=self.show_gps_options_page).pack(pady=10)

    def show_parameter_conversion_page(self):
        """Page to convert parameters into dimensions."""
        self.clear_frame()

        tk.Label(self.main_frame, text="Convert Parameters to Dimensions", font=("Arial", 24, 'bold')).pack(pady=10)

        tk.Label(self.main_frame, text="Enter Parameter (e.g., perimeter):", font=("Arial", 16)).pack(pady=10)
        self.parameter_entry = tk.Entry(self.main_frame, font=("Arial", 16))
        self.parameter_entry.pack()

        tk.Button(self.main_frame, text="Convert", font=("Arial", 16), command=self.convert_parameter_to_dimensions).pack(pady=10)
        tk.Button(self.main_frame, text="Back to GPS Options", font=("Arial", 16), command=self.show_gps_options_page).pack(pady=10)

    def convert_area_to_dimensions(self):
        """Convert area to length and breadth."""
        try:
            area = float(self.area_entry.get())
            ratio = self.ratio_entry.get().split(":")
            length_ratio, width_ratio = map(float, ratio)
            total_ratio = length_ratio + width_ratio

            length = (area * length_ratio / total_ratio) ** 0.5
            width = (area * width_ratio / total_ratio) ** 0.5

            messagebox.showinfo("Conversion Successful", f"Length: {length:.2f} m, Width: {width:.2f} m")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input. Please ensure all fields are filled correctly.\n{e}")

    def convert_parameter_to_dimensions(self):
        """Convert a parameter into dimensions."""
        try:
            parameter = float(self.parameter_entry.get())

            # Example logic: Treating parameter as perimeter and assuming a square.
            length = parameter / 4
            width = parameter / 4

            messagebox.showinfo("Conversion Successful", f"Estimated Length: {length:.2f} m, Width: {width:.2f} m")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input. Please enter a valid parameter.\n{e}")

    def open_google_earth(self):
        """Open the Google Earth website."""
        webbrowser.open("https://earth.google.com")
        messagebox.showinfo("Google Earth", "Google Earth website has been opened.")

    def show_house_design_page(self):
        """Placeholder for house design page."""
        self.clear_frame()
        tk.Label(self.main_frame, text="House Design Page (Coming Soon)", font=("Arial", 24, 'bold')).pack(pady=10)
        tk.Button(self.main_frame, text="Back to Design Choice", font=("Arial", 16), command=self.show_design_choice_page).pack(pady=10)


    def show_house_design_page(self):
        """Show the house design input page."""
        self.clear_frame()
     
        tk.Label(self.main_frame, text="2D Home Designer", font=("Arial", 24, 'bold')).pack(pady=10)

        tk.Label(self.main_frame, text="Enter Length (meters):", font=("Arial", 16)).pack()
        self.length_entry = tk.Entry(self.main_frame, font=("Arial", 16))
        self.length_entry.pack()

        tk.Label(self.main_frame, text="Enter Width (meters):", font=("Arial", 16)).pack()
        self.width_entry = tk.Entry(self.main_frame, font=("Arial", 16))
        self.width_entry.pack()

        tk.Button(self.main_frame, text="Generate Plan", font=("Arial", 16), command=self.generate_plan).pack(pady=10)

        self.previous_button = tk.Button(self.main_frame, text="Previous Design", font=("Arial", 16), command=self.previous_design, state=tk.DISABLED)
        self.previous_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(self.main_frame, text="Next Design", font=("Arial", 16), command=self.next_design, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=10)
        self.confirm_button = tk.Button(self.main_frame, text="Confirm Design", font=("Arial", 16),
                                         command=self.confirm_design, state=tk.DISABLED)
        self.confirm_button.pack(pady=10)
        self.download_button = tk.Button(self.main_frame, text="Download Design", font=("Arial", 16), command=self.download_design, state=tk.DISABLED)
        self.download_button.pack(pady=10)

        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack()

    def save_design_image(self):
        """Save the current design as an image and store it in MongoDB."""
        # Save the current Matplotlib figure to a PNG file in memory
        from io import BytesIO
        buffer = BytesIO()
        self.fig.savefig(buffer, format="png")
        buffer.seek(0)

        # Store the image in MongoDB GridFS
        design_image_id = self.fs.put(
            buffer.getvalue(),
            filename=f"{self.logged_in_user}design{self.design}.png",
            metadata={
                "username": self.logged_in_user,
                "design": self.design,
                "length": self.length,
                "width": self.width,
            }
        )
        return design_image_id
    
    def download_design(self):
        """Download the current design as an image file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.fig.savefig(file_path)
            messagebox.showinfo("Download Complete", f"Design saved as {file_path}")

   

    def generate_plan(self):
        """Generate and display the first house plan sketch."""
        try:
            self.length = float(self.length_entry.get())
            self.width = float(self.width_entry.get())

            if self.length <= 0 or self.width <= 0:
                messagebox.showerror("Error", "Dimensions must be positive values! Please try again.")
                return

            self.fig, self.ax = plt.subplots(figsize=(8, 6))
            self.draw_house_plan(self.ax, self.length, self.width, self.design)

            # Embed Matplotlib figure into Tkinter window
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack()
            
            self.next_button.config(state=tk.NORMAL)
            self.previous_button.config(state=tk.DISABLED)
            self.confirm_button.config(state=tk.NORMAL)
            self.download_button.config(state=tk.NORMAL)
            

            # Save the design to the database
            self.save_design()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numerical values for dimensions.")

    def confirm_design(self):
        """Confirm the current design and save it along with the image."""
        response = messagebox.askyesno("Confirm Design", f"Do you want to confirm Design {self.design}?")
        if response:
            # Save the design image and get its ID
            design_image_id = self.save_design_image()

            # Save the confirmed design to the database
            confirmed_design = {
                "username": self.logged_in_user,
                "length": self.length,
                "width": self.width,
                "design": self.design,
                "confirmed": True,
                "image_id": design_image_id
            }
            self.designs_collection.insert_one(confirmed_design)

            messagebox.showinfo("Design Confirmed", f"Design {self.design} has been confirmed and saved successfully.")
        else:
            messagebox.showinfo("Design Not Confirmed", "You can review other designs or modify your selection.")

    def draw_house_plan(self, ax, length, width, design=1):
        """Generate a proportional house plan sketch for a given design and plot it on the provided axis."""
        ax.clear()

        ax.add_patch(patches.Rectangle((0, 0), width, length, edgecolor='black', facecolor='lightgrey', lw=2))

        room_colors = {
            "Bedroom 1": 'lightblue',
            "Bedroom 2": 'lightgreen',
            "Kitchen": 'lightyellow',
            "Living Room": 'lightsalmon',
            "Bathroom 1": 'lightpink',
            "Bathroom 2": 'lightcyan',
            "Parking Area": 'lightgoldenrodyellow',
            "Staircase": 'lightsteelblue'  
            
        }
        
        if design == 1:
            rooms = {
                "Bedroom 1": (0, length * 0.6, width * 0.4, length * 0.4),
                "Bedroom 2": (width * 0.4, length * 0.6, width * 0.6, length * 0.4),
                "Kitchen": (0, length * 0.3, width * 0.4, length * 0.3),
                "Living Room": (width * 0.4, 0, width * 0.6, length * 0.6),
                "Bathroom 1": (0, length * 0.2, width * 0.2, length * 0.1),
                "Bathroom 2": (width * 0.2, length * 0.2, width * 0.2, length * 0.1),
                "Parking Area": (0, 0, width * 0.4, length * 0.2),
                "Staircase": (width * 0.4, length * 0.9, width * 0.2, length * 0.1)
            }
        elif design == 2:
            rooms = {
                "Bedroom 1": (0, 0, width * 0.5, length * 0.5),
                "Bedroom 2": (width * 0.5, 0, width * 0.5, length * 0.5),
                "Kitchen": (0, length * 0.5, width * 0.4, length * 0.3),
                "Living Room": (width * 0.4, length * 0.5, width * 0.6, length * 0.5),
                "Bathroom 1": (0, length * 0.8, width * 0.2, length * 0.2),
                "Bathroom 2": (width * 0.2, length * 0.8, width * 0.2, length * 0.2),
                "Parking Area": (0, length * 0.5, width * 0.4, length * 0.3),
                "Staircase": (width * 0.8, length * 0.9, width * 0.2, length * 0.1)
            }
        elif design == 3:
            rooms = {
                "Bedroom 1": (0, 0, width * 0.5, length * 0.4),
                "Bedroom 2": (width * 0.5, 0, width * 0.5, length * 0.4),
                "Kitchen": (0, length * 0.4, width * 0.4, length * 0.3),
                "Living Room": (width * 0.4, length * 0.4, width * 0.6, length * 0.6),
                "Bathroom 1": (0, length * 0.7, width * 0.2, length * 0.3),
                "Bathroom 2": (width * 0.2, length * 0.7, width * 0.2, length * 0.3),
                "Staircase": (width * 0.8, length * 0.8, width * 0.2, length * 0.2)
            }
        elif design==4:
            rooms = {
                "Bedroom 1": (0, length * 0.7, width * 0.4, length * 0.3),
                "Bedroom 2": (width * 0.4, length * 0.7, width * 0.4, length * 0.3),
                "Kitchen": (0, length * 0.4, width * 0.4, length * 0.3),
                "Living Room": (width * 0.4, 0, width * 0.6, length * 0.4),
                "Bathroom 1": (0, length * 0.2, width * 0.2, length * 0.2),
                "Parking Area": (width * 0.6, 0, width * 0.4, length * 0.2),
            }
        elif design == 5:
            rooms = {
                "Bedroom 1": (0, length * 0.6, width * 0.4, length * 0.4),
                "Bedroom 2": (width * 0.4, length * 0.6, width * 0.6, length * 0.4),
                "Kitchen": (0, length * 0.3, width * 0.4, length * 0.3),
                "Living Room": (width * 0.4, 0, width * 0.6, length * 0.6),
                "Bathroom 1": (0, length * 0.2, width * 0.2, length * 0.1),
                "Bathroom 2": (width * 0.2, length * 0.2, width * 0.2, length * 0.1),
                "Parking Area": (0, 0, width * 0.4, length * 0.2),
                "Staircase": (width * 0.4, length * 0.9, width * 0.2, length * 0.1)
                
            }
        # Multiple designs with different room layout
        

        # Add rooms to the plot
        for room, (x, y, w, h) in rooms.items():
            ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='black', facecolor=room_colors[room], lw=1))
            ax.text(x + w / 2, y + h / 2, room, color='black', fontsize=8, ha='center', va='center')
            ax.text(x + w / 2, y + h + 0.1, f"{w:.1f}m x {h:.1f}m", color='black', fontsize=8, ha='center', va='bottom')

        ax.set_xlim(-5, width + 5)
        ax.set_ylim(-5, length + 5)
        ax.set_aspect('equal', adjustable='box')
        ax.set_title(f"Design {design}")
        ax.set_xlabel("Width (meters)")
        ax.set_ylabel("Length (meters)")
        ax.grid(True, which='both', color='black', linestyle='--', linewidth=0.5)

        plt.draw()

    def save_design(self):
        """Save the design to MongoDB."""
        design_data = {
            "username": self.logged_in_user,
            "length": self.length,
            "width": self.width,
            "design": self.design
        }
        self.designs_collection.insert_one(design_data)

    def next_design(self):
        """Display the next design and increment the design number."""
        if self.design < 5:
            self.design += 1
            self.draw_house_plan(self.ax, self.length, self.width, self.design)
            self.canvas.draw()  # Update the canvas with the new design
            self.previous_button.config(state=tk.NORMAL)
            
        if self.design == self.max_designs:
            self.next_button.config(state=tk.DISABLED)

    def previous_design(self):
        """Display the previous design and decrement the design number."""
        if self.design > 1:
            self.design -= 1
            self.draw_house_plan(self.ax, self.length, self.width, self.design)
            self.canvas.draw()  # Update the canvas with the new design
            self.next_button.config(state=tk.NORMAL)

        if self.design == 1:
            self.previous_button.config(state=tk.DISABLED)

    def clear_frame(self):
        """Clear the current frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

def main():
    root = tk.Tk()
    app = HouseDesignerApp(root)
    root.mainloop()

if __name__== "__main__":
    main()