from math import fabs
import tkinter as tk
import customtkinter
import cv2
import mediapipe as mp
from PIL import ImageTk, Image
from hand_detection import process_image_hand_detection

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
	WIDTH = 930
	HEIGHT = 580

	def __init__(self):
		super().__init__()
		
		self.mp_drawing = mp.solutions.drawing_utils
		self.mp_drawing_styles = mp.solutions.drawing_styles
		self.mp_hands = mp.solutions.hands
		self.hands = self.mp_hands.Hands(
		static_image_mode=False,
		max_num_hands=2, # TODO: Implement Multiplayer with multiple hands
		model_complexity=0, # for faster speed
		min_detection_confidence=0.8,
		min_tracking_confidence=0.5)
		
		self.current_pose = "hand" # Can be "face" or "body"

		self.stored_hand_keys = {}
		self.stored_face_keys = {}
		self.stored_body_keys = {}

		self.running_stored_keys = False
		self.storing_key = False # Will be used to check if we are storing hand keys
		
		# self.resizable(False, False) # Remove the option to resize, TODO: Fix it so we can enable that

		self.cap = cv2.VideoCapture(0)
		self.title("Motional: Motion is All You Need") 
		self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
		self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

		# ============ create two frames ============

		# configure grid layout (2x1)
		self.grid_columnconfigure(1, weight=1)
		self.grid_rowconfigure(0, weight=1)

		self.frame_left = customtkinter.CTkFrame(master=self,
												 width=150,
												 corner_radius=0)
		self.frame_left.grid(row=0, column=0, sticky="nswe")

		self.frame_right = customtkinter.CTkFrame(master=self)
		self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

		# ============ frame_left ============
		# configure grid layout (1x11)
		self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
		self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
		self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
		self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

		self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
											  text="CustomTkinter",
											  text_font=("Roboto Medium", -16))  # font name and size in px
		self.label_1.grid(row=1, column=0, pady=10, padx=10)

		self.button_1 = customtkinter.CTkButton(master=self.frame_left,
												text="CTkButton",
												command=self.button_event)
		self.button_1.grid(row=2, column=0, pady=10, padx=20)

		self.button_2 = customtkinter.CTkButton(master=self.frame_left,
												text="CTkButton",
												command=self.button_event)
		self.button_2.grid(row=3, column=0, pady=10, padx=20)

		self.button_3 = customtkinter.CTkButton(master=self.frame_left,
												text="CTkButton",
												command=self.button_event)
		self.button_3.grid(row=4, column=0, pady=10, padx=20)

		self.label_mode = customtkinter.CTkLabel(master=self.frame_left, text="Appearance Mode:")
		self.label_mode.grid(row=9, column=0, pady=0, padx=20, sticky="w")

		self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
														values=["Light", "Dark", "System"],
														command=self.change_appearance_mode)
		self.optionmenu_1.grid(row=10, column=0, pady=10, padx=20, sticky="w")

		# # ============ frame_right ============
		# # configure grid layout (3x7)
		self.frame_right.rowconfigure((0, 1, 2), weight=1)
		self.frame_right.columnconfigure((0, 1), weight=1)
		self.frame_info = customtkinter.CTkFrame(master=self.frame_right, width=1000)
		self.frame_info.grid(row=0, column=0, columnspan=8, rowspan=4, pady=20, padx=20, sticky="nsew")

		# ============ frame_info ============

		# configure grid layout (1x1)
		self.frame_info.rowconfigure(0, weight=1)
		self.frame_info.columnconfigure(0, weight=1)


		#Capture video frames
		self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
												   height=540,
												   width=960,
												   corner_radius=6,  # <- custom corner radius
												   )
		self.label_info_1.grid(column=0, row=0, padx=5, pady=10)


		# # ============ frame_right ============
		self.text = customtkinter.CTkLabel(master=self.frame_right,
													 text="Key: ",
													 justify=tk.LEFT)
		self.text.grid(row=4, column=0)

		self.key_entry = customtkinter.CTkEntry(master=self.frame_right,
													 text="Enter Key")
		self.key_entry.grid(row=4, column=1, pady=10, padx=20, sticky="w")

		self.save_button = customtkinter.CTkButton(master=self.frame_right,
													 text="Save",
													 command=self.save_key
													 )
		self.save_button.grid(row=4, column=2, pady=10, padx=20, sticky="w")

		self.stored_keys_text = customtkinter.CTkLabel(master=self.frame_right,
													 text=self.stored_hand_keys,
													 justify=tk.LEFT)
		self.stored_keys_text.grid(row=5, column=0)
		self.run_button = customtkinter.CTkButton(master=self.frame_right,
													 text="Run" if self.running_stored_keys else "Stop",
													 command=self.toggle_running_stored_keys)
		self.run_button.grid(row=5, column=2, pady=10, padx=20, sticky="w")


		# set default values
		self.optionmenu_1.set("System")
		self.button_3.configure(state="disabled", text="Disabled CTkButton")

	def show_frame(self):
		_, image = self.cap.read()
		if self.storing_key:
			image = process_image_hand_detection(self.hands, image, self.stored_hand_keys, key=self.key_entry.get())
			self.storing_key = False
			self.key_entry.delete(0, tk.END)
			
			# TODO: Put in a function, Update the text
			self.stored_keys_text = customtkinter.CTkLabel(master=self.frame_right,
														text="Registered Keys " + self.stored_hand_keys.keys(),
														justify=tk.LEFT)
			self.stored_keys_text.grid(row=5, column=0)

		else:
			image = process_image_hand_detection(self.hands, image, self.stored_hand_keys)
		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
		image = cv2.resize(image, (640, 360))
		image = Image.fromarray(image)
		imgtk = ImageTk.PhotoImage(image=image)
		self.label_info_1.imgtk = imgtk
		self.label_info_1.configure(image=imgtk)
		self.label_info_1.after(50, self.show_frame) 

	def save_key(self):
		self.storing_key = True # This will be updated after self.show_frame, where self.storing_key will be reset to False

	def toggle_running_stored_keys(self):
		self.running_stored_keys = not self.running_stored_keys
		# TODO: I don't know if this is REALLY BAD practice, i feel like it's stacking buttons on top of each other
		self.run_button = customtkinter.CTkButton(master=self.frame_right,
													 text="Run" if self.running_stored_keys else "Stop",
													 command=self.toggle_running_stored_keys)
		self.run_button.grid(row=5, column=2, pady=10, padx=20, sticky="w")

	def button_event(self):
		print("Button pressed")

	def change_appearance_mode(self, new_appearance_mode):
		customtkinter.set_appearance_mode(new_appearance_mode)

	def on_closing(self, event=0):
		self.destroy()


if __name__ == "__main__":
	app = App()
	app.show_frame()
	app.mainloop()