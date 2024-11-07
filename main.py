import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from mutagen.mp3 import MP3
import threading
import pygame
import time
import os

# Initialize pygame mixer
pygame.mixer.init()

# Store the current position of the music
current_position = 0
paused = False
selected_folder_path = ""  # Store the selected folder path

def update_progress():
    global current_position
    while True:
        if pygame.mixer.music.get_busy() and not paused:
            current_position = pygame.mixer.music.get_pos() / 1000
            pbar.set(current_position)  # Update the progress bar

            # Check if the current song has reached its maximum duration
            audio_length = pbar.cget("maximum")  # Get the maximum duration from the progress bar's 'maximum' property
            if current_position >= audio_length:
                stop_music()  # Stop the music playback
                pbar.set(0)  # Reset the progress bar
            
            window.update()
        time.sleep(0.1)

# Create a thread to update the progress bar
pt = threading.Thread(target=update_progress)
pt.daemon = True
pt.start()

def select_music_folder():
    global selected_folder_path
    selected_folder_path = filedialog.askdirectory()
    print(f"Selected Folder: {selected_folder_path}")  # Debugging: check folder path
    if selected_folder_path:
        lbox.delete(0, tk.END)
        for filename in os.listdir(selected_folder_path):
            if filename.endswith(".mp3"):
                lbox.insert(tk.END, filename)  # Insert only the filename, not the full path
        print(f"Available Songs: {lbox.get(0, tk.END)}")  # Debugging: check song list

def previous_song():
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        if current_index > 0:
            lbox.selection_clear(0, tk.END)
            lbox.selection_set(current_index - 1)
            play_selected_song()

def next_song():
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        if current_index < lbox.size() - 1:
            lbox.selection_clear(0, tk.END)
            lbox.selection_set(current_index + 1)
            play_selected_song()

def play_music():
    global paused
    print("Play music clicked")  # Debugging
    if paused:
        # If the music is paused, unpause it
        pygame.mixer.music.unpause()
        paused = False
    else:
        # If the music is not paused, play the selected song
        play_selected_song()

def play_selected_song():
    global current_position, paused
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        selected_song = lbox.get(current_index)
        full_path = os.path.join(selected_folder_path, selected_song)  # Add the full path again
        print(f"Playing: {full_path}")  # Debugging: check song path
        
        try:
            pygame.mixer.music.load(full_path)  # Load the selected song
            pygame.mixer.music.play(start=current_position)  # Play the song from the current position
            paused = False
            audio = MP3(full_path)
            song_duration = audio.info.length
            pbar.set(0)  # Reset the progress bar to 0 at the start
            pbar.configure(minimum=0, maximum=song_duration)  # Set the maximum value to the song's duration
            print(f"Song duration: {song_duration}")  # Debugging: check song duration
        except Exception as e:
            print(f"Error loading or playing song: {e}")  # Debugging: if there's an error
    else:
        print("No song selected")  # Debugging: if no song is selected

def pause_music():
    global paused
    # Pause the currently playing music
    pygame.mixer.music.pause()
    paused = True
    print("Music paused")  # Debugging

def stop_music():
    global paused
    # Stop the currently playing music and reset the progress bar
    pygame.mixer.music.stop()
    paused = False
    print("Music stopped")  # Debugging

# Create the main window
window = tk.Tk()
window.title("Music Player")
window.geometry("400x400")  # Reduced the window size

# Set the background color for the window
window.config(bg="#333333")

# Remove the window border and title bar (optional)
window.overrideredirect(True)

# Optional: Add transparency (This might not work on all systems)
window.attributes("-alpha", 0.9)

# Make the window draggable
def on_drag_start(event):
    window.x = event.x
    window.y = event.y

def on_drag_motion(event):
    deltax = event.x - window.x
    deltay = event.y - window.y
    window.geometry(f'+{window.winfo_x() + deltax}+{window.winfo_y() + deltay}')

# Bind the drag start and motion events to the window
window.bind("<Button-1>", on_drag_start)
window.bind("<B1-Motion>", on_drag_motion)

# Create a label for the music player title
l_music_player = ctk.CTkLabel(window, text="Music Player", font=("Comfortaa", 22, "bold"), fg_color="#666666", text_color="white", corner_radius=10)
l_music_player.pack(pady=10)

# Create a button to select the music folder
btn_select_folder = ctk.CTkButton(window, text="Select Folder", command=select_music_folder, font=("Comfortaa", 14),
                                  width=200, height=40, fg_color="#555555", hover_color="#444444", corner_radius=10)
btn_select_folder.pack(pady=10)

# Create a listbox to display the available songs
lbox = tk.Listbox(window, width=40, height=8, font=("Comfortaa", 12), bg="#444444", fg="white", selectmode=tk.SINGLE, bd=0, highlightthickness=0)
lbox.pack(pady=10)

# Create a frame to hold the control buttons
btn_frame = tk.Frame(window, bg="#333333")
btn_frame.pack(pady=10)

# Create a button to go to the previous song
btn_previous = ctk.CTkButton(btn_frame, text="<", command=previous_song, width=40, height=40, font=("Comfortaa", 18),
                             fg_color="#666666", hover_color="#555555", corner_radius=10)
btn_previous.pack(side=tk.LEFT, padx=10)

# Create a button to play the music
btn_play = ctk.CTkButton(btn_frame, text="Play", command=play_music, width=60, height=40, font=("Comfortaa", 18),
                         fg_color="#888888", hover_color="#777777", corner_radius=10)
btn_play.pack(side=tk.LEFT, padx=10)

# Create a button to pause the music
btn_pause = ctk.CTkButton(btn_frame, text="Pause", command=pause_music, width=60, height=40, font=("Comfortaa", 18),
                          fg_color="#888888", hover_color="#777777", corner_radius=10)
btn_pause.pack(side=tk.LEFT, padx=10)
# Create a button to go to the next song
btn_next = ctk.CTkButton(btn_frame, text=">", command=next_song, width=40, height=40, font=("Comfortaa", 18),
                         fg_color="#666666", hover_color="#555555", corner_radius=10)
btn_next.pack(side=tk.LEFT, padx=10)

# Create a progress bar to indicate the current song's progress using customtkinter ProgressBar
pbar = ctk.CTkProgressBar(window, width=300, height=10, corner_radius=5)
pbar.pack(pady=10)

# Run the Tkinter event loop
window.mainloop()
