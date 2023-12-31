import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
import csv
import tkinter.messagebox as messagebox
from tabulate import tabulate
import datetime
from tkinter import Scrollbar
from ttkthemes import ThemedStyle



class MovieSearchApp:
    def __init__(self, root):
        self.root = root
        self.api_key = "your_api_key"
        self.search_count = 0
        self.last_search_time = None
        self.load_search_count()
        self.id_counter = 0  # Initialize the ID counter
        self.detail_labels = [  # Define detail labels here
            "Title", "Genre", "Runtime", "Year", "Director",
            "IMDB Rating", "IMDB Votes", "Rotten Tomatoes",
            "Actors", "IMDB ID", "Type", "Rated", "Released",
            "Writer", "Country", "Awards", "Plot"
        ]
        self.dblabels = [  # Define detail labels here
            "ID", "Title", "Genre", "Runtime", "Year", "Director",
            "IMDB Rating", "IMDB Votes", "Rotten Tomatoes",
            "Actors", "IMDB ID", "Type", "Rated", "Released",
            "Writer", "Country", "Awards", "Plot", "Watched", "I Want to Watch"
        ]
        self.initialize_ui()

    def initialize_ui(self):
        self.root.title("Movie Search App")
        # Create a custom style for the Treeview header
        style = ttk.Style()
        style.theme_use("default")  # Use the default theme as a base
        style.configure("Treeview.Heading", background="gray")  # Set the header background color


        # Create a notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Create the first tab for New Search
        new_search_tab = ttk.Frame(self.notebook)

        self.notebook.add(new_search_tab, text="New Search")
        self.create_search_ui(new_search_tab)


        # Create the second tab for Database
        database_tab = ttk.Frame(self.notebook)
        self.notebook.add(database_tab, text="Database")
        self.create_database_ui(database_tab)

        # Create the third tab for Analyzed Data
        analyzed_data_tab = ttk.Frame(self.notebook)
        self.notebook.add(analyzed_data_tab, text="Analyzed Data")
        self.create_analyzed_data_ui(analyzed_data_tab)

    def create_analyzed_data_ui(self, parent):
        self.analyzed_tree = ttk.Treeview(parent, columns=["Date", "Count"], show="headings")
        self.analyzed_tree.pack(padx=10, pady=10, fill="both", expand=False)

        self.analyzed_tree.heading("Date", text="Date")
        self.analyzed_tree.column("Date", width=10)

        self.analyzed_tree.heading("Count", text="Search Count")
        self.analyzed_tree.column("Count", width=10)

        self.update_analyzed_data_ui()

    def update_analyzed_data_ui(self):
        self.analyzed_tree.delete(*self.analyzed_tree.get_children())  # Clear existing table rows

        try:
            with open("analyze.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)  # Skip header row
                for row in csv_reader:
                    self.analyzed_tree.insert("", "end", values=row)
        except FileNotFoundError:
            pass

    def load_search_count(self):
        # Load the search count and date from the analyze.csv file
        try:
            with open("analyze.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                last_row = list(csv_reader)[-1]
                date_str, count_str = last_row
                self.last_search_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                self.search_count = int(count_str)
        except (FileNotFoundError, IndexError, ValueError):
            self.last_search_date = None
            self.search_count = 0

    def update_database_ui(self, rows=None):
        self.database_tree.delete(*self.database_tree.get_children())  # Clear existing table rows

        data_rows = rows if rows is not None else self.get_all_database_rows()

        for row in data_rows:
            self.database_tree.insert("", "end", values=row)

    def get_all_database_rows(self):
        rows = []

        try:
            with open("movie_results.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                header = next(csv_reader)
                i = 1
                for row in csv_reader:
                    row.insert(0, str(i))
                    i += 1
                    rows.append(row)
        except FileNotFoundError:
            pass

        return rows

    def create_search_ui(self, parent):
        input_frame = tk.Frame(parent)
        input_frame.config(bg="#B5B5B5")
        input_frame.pack(padx=10, pady=10)
        input_frame.place(x=10, y=10, width=980, height=185)
        input_frame.config(borderwidth=1, relief="solid", highlightbackground="#D9D9D9")  # Use a consistent color

        # Load and display an image
        image_path = "header.jpg"  # Use an image with alpha (transparency) channel
        image = Image.open(image_path)

        # Reduce the opacity of the image
        opacity = 128  # Set the desired opacity value (0-255)
        image = image.convert("RGBA")
        data = image.getdata()
        new_data = []
        for item in data:
            new_data.append((item[0], item[1], item[2], opacity))
        image.putdata(new_data)

        photo = ImageTk.PhotoImage(image)
        image_label = tk.Label(input_frame, image=photo)
        image_label.image = photo
        image_label.pack()

        text_frame = tk.Frame(parent)
        text_frame.config(bg="#B5B5B5")
        text_frame.pack(padx=10, pady=10)
        text_frame.place(x=14, y=22, width=185, height=113)
        text_frame.config(borderwidth=1, relief="solid", highlightbackground="#D9D9D9")

        movie_name_label = tk.Label(text_frame, text="Movie Name", font=("Arial", 12, "bold"))
        movie_name_label.config(bg="#B5B5B5")
        movie_name_label.place(x=10, y=0)


        self.movie_name_entry = tk.Entry(input_frame, font=('Arial 14'))
        self.movie_name_entry.place(x=200, y=11)
        self.movie_name_entry.bind("<Return>", self.search_movie)

        movie_year_label = tk.Label(text_frame, text="Year of Release", font=("Arial", 12, "bold"))
        movie_year_label.config(bg="#B5B5B5")
        movie_year_label.place(x=10, y=40)
        self.movie_year_entry = tk.Entry(input_frame, font=('Arial 14'))
        self.movie_year_entry.place(x=200, y=51)

        movie_type_label = tk.Label(text_frame, text="Type", font=("Arial", 12, "bold"))
        movie_type_label.config(bg="#B5B5B5")
        movie_type_label.place(x=10, y=80)
        self.movie_type_combo = ttk.Combobox(input_frame, width=34, values=["movie", "series", "episode"])
        self.movie_type_combo.place(x=200, y=91)

        canvas = tk.Canvas(input_frame, bg="#D9D9D9", width=1, height=110, highlightthickness=0)
        canvas.place(x=180, y=10)
        canvas.create_line(0, 0, 0, 380, fill="black")

        # Apply the "breeze" theme to the button
        style = ThemedStyle(input_frame)
        style.set_theme("breeze")  # Apply the "breeze" theme
        search_button = ttk.Button(input_frame, text="Search", command=self.search_movie)
        search_button.place(x=440, y=11)

        separator = ttk.Separator(parent, orient="horizontal")
        separator.pack(fill="x", padx=10, pady=5)


        self.result_frame = tk.Frame(parent)
        self.result_frame.config(bg="#D9D9D9")
        self.result_frame.pack(padx=10, pady=10)
        self.result_frame.place(x=10, y=200, width=980, height=530)
        self.result_frame.config(borderwidth=1, relief="solid", highlightbackground="#D9D9D9")

        # Load and display an image as the background
        image_path = "cinema5.jpg"  # Replace with the actual image path
        background_image = Image.open(image_path)
        background_image = background_image.resize((980, 530))
        self.background_photo = ImageTk.PhotoImage(background_image)

        self.background_label = tk.Label(self.result_frame, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Place other widgets on top of the background
        self.text_widget = tk.Text(self.result_frame, wrap="none", highlightthickness=2,
                                   highlightbackground="#D9D9D9")
        self.text_widget.place(x=290, y=10)

        self.poster_label = tk.Label(self.result_frame, text="Poster", font=("Arial", 12, "bold"),
                                     borderwidth=2, relief="solid", padx=80, pady=150)
        self.poster_label.place(x=40, y=40)
        self.poster_label.config(bg="#EEE685")


        self.initialize_checkboxes_and_button()

    def create_database_ui(self, parent):
        # Create a frame to hold the Treeview widget and the scrollbars
        database_frame = tk.Frame(parent)
        database_frame.config(bg="#C1C1C1")
        database_frame.pack(padx=10, pady=10, fill="both", expand=True)
        database_frame.place(x=10, y=10, width=980, height=680)  # Adjust the placement and size

        # Add a black line border around the frame
        database_frame.config(borderwidth=1, relief="solid", highlightbackground="black")

        self.database_tree = ttk.Treeview(database_frame, columns=self.dblabels, show="headings")

        self.database_tree.pack(fill="both", expand=False)

        for label in self.dblabels:
            self.database_tree.heading(label, text=label)
            self.database_tree.column(label, width=150)

        # Set the header background color to gray only for self.database_tree
        style = ttk.Style()
        style.configure(
            f"{self.database_tree}._header", background="gray"
        )  # Use the correct style name

        self.update_database_ui()

        horizontal_scrollbar = ttk.Scrollbar(self.database_tree, orient="horizontal", command=self.database_tree.xview)
        horizontal_scrollbar.place(relx=0, rely=0.95, relwidth=0.99, relheight=0.05)
        self.database_tree.config(xscrollcommand=horizontal_scrollbar.set)

        # Create a vertical scrollbar
        vertical_scrollbar = ttk.Scrollbar(self.database_tree, orient="vertical", command=self.database_tree.yview)
        vertical_scrollbar.place(relx=0.98, rely=0, relwidth=0.03, relheight=0.99)
        self.database_tree.config(yscrollcommand=vertical_scrollbar.set)

        # Create a frame for search functionality
        search_frame = tk.Frame(parent)
        search_frame.config(bg="#C1C1C1")
        search_frame.pack(padx=10, pady=(0, 5), fill="x")
        search_frame.place(x=50, y=300)  # Adjust placement here

        title_label = tk.Label(search_frame, text="Search Title:")
        title_label.config(bg="#C1C1C1")
        title_label.pack(side="top", anchor="w")

        self.title_entry = tk.Entry(search_frame)
        self.title_entry.pack(side="top", padx=(5, 0), fill="x", expand=True)
        self.title_entry.bind("<KeyRelease>", self.search_database)

        year_label = tk.Label(search_frame, text="Search Year:")
        year_label.config(bg="#C1C1C1")
        year_label.pack(side="top", anchor="w")

        self.year_entry = tk.Entry(search_frame)
        self.year_entry.pack(side="top", padx=(5, 0), fill="x", expand=True)
        self.year_entry.bind("<KeyRelease>", self.search_database)

        director_label = tk.Label(search_frame, text="Search Director:")
        director_label.config(bg="#C1C1C1")
        director_label.pack(side="top", anchor="w")

        self.director_entry = tk.Entry(search_frame)
        self.director_entry.pack(side="top", padx=(5, 0), fill="x", expand=True)
        self.director_entry.bind("<KeyRelease>", self.search_database)

        genre_label = tk.Label(search_frame, text="Search Genre:")
        genre_label.config(bg="#C1C1C1")
        genre_label.pack(side="top", anchor="w")

        self.genre_entry = tk.Entry(search_frame)
        self.genre_entry.pack(side="top", padx=(5, 0), fill="x", expand=True)
        self.genre_entry.bind("<KeyRelease>", self.search_database)

        imdb_rating_label = tk.Label(search_frame, text="Search IMDb Rating:")
        imdb_rating_label.config(bg="#C1C1C1")
        imdb_rating_label.pack(side="top", anchor="w")

        self.imdb_rating_entry = tk.Entry(search_frame)
        self.imdb_rating_entry.pack(side="top", padx=(5, 0), fill="x", expand=True)
        self.imdb_rating_entry.bind("<KeyRelease>", self.search_database)

        rotten_tomatoes_label = tk.Label(search_frame, text="Search Rotten Tomatoes:")
        rotten_tomatoes_label.config(bg="#C1C1C1")
        rotten_tomatoes_label.pack(side="top", anchor="w")

        self.rotten_tomatoes_entry = tk.Entry(search_frame)
        self.rotten_tomatoes_entry.pack(side="top", padx=(5, 0), fill="x", expand=True)
        self.rotten_tomatoes_entry.bind("<KeyRelease>", self.search_database)

        actors_label = tk.Label(search_frame, text="Search Actors:")
        actors_label.config(bg="#C1C1C1")
        actors_label.pack(side="top", anchor="w")

        self.actors_entry = tk.Entry(search_frame)
        self.actors_entry.pack(side="top", padx=(5, 0), fill="x", expand=True)
        self.actors_entry.bind("<KeyRelease>", self.search_database)

        writer_label = tk.Label(search_frame, text="Search Writer:")
        writer_label.config(bg="#C1C1C1")
        writer_label.pack(side="top", anchor="w")

        self.writer_entry = tk.Entry(search_frame)
        self.writer_entry.pack(side="top", padx=(5, 0), fill="x", expand=True)
        self.writer_entry.bind("<KeyRelease>", self.search_database)

        search_frame_buttons = tk.Frame(parent)  # Create a new frame for the buttons
        search_frame_buttons.config(bg="#C1C1C1")
        search_frame_buttons.pack(padx=10, pady=(0, 5), fill="x")
        search_frame_buttons.place(x=250, y=310)  # Adjust placement here

        # Create buttons to show watched and want to watch movies within the new frame
        show_watched_button = ttk.Button(search_frame_buttons, text="Show Watched",
                                         command=self.search_watched_movies, width=20)
        show_watched_button.pack(side="left", padx=(5, 0), pady=(10, 0), fill="x")

        show_want_to_watch_button = ttk.Button(search_frame_buttons, text="Show I Want to Watch",
                                               command=self.search_want_to_watch_movies, width=20)
        show_want_to_watch_button.pack(side="left", padx=(5, 0), pady=(10, 0), fill="x")

        # Add the delete button
        delete_button = ttk.Button(database_frame, text="Delete", command=self.delete_selected_movie, width=20)
        delete_button.pack(side="left", padx=(5, 0), pady=(10, 0), fill="x")
        delete_button.place(x=245, y=350)

        # Create the "Show All" button
        show_all_button = ttk.Button(database_frame, text="Show All", command=self.show_all_data, width=20)
        show_all_button.pack(side="left", padx=(5, 0), pady=(10, 0), fill="x")
        show_all_button.place(x=412, y=350)

        # Create the "Edit" button
        edit_button = ttk.Button(database_frame, text="Edit", command=self.edit_selected_movie, width=20)
        edit_button.pack(side="left", padx=(5, 0), pady=(10, 0), fill="x")
        edit_button.place(x=245, y=390)  # Adjust the placement as needed

        change_to_watched_button = ttk.Button(database_frame, text="Change to watched", command=self.change_watched_status, width=20)
        change_to_watched_button.pack(side="left", padx=(5, 0), pady=(10, 0), fill="x")
        change_to_watched_button.place(x=412, y=390)  # Adjust the placement as needed


    def edit_selected_movie(self):
        selected_item = self.database_tree.selection()
        if selected_item:
            row = self.database_tree.item(selected_item[0])["values"]
            self.open_edit_window(row)
        else:
            messagebox.showwarning("Warning", "No movie selected. Please select a movie to edit.")

    def change_watched_status(self):
        selected_item = self.database_tree.selection()
        if selected_item:
            row = self.database_tree.item(selected_item[0])["values"]
            self.change_watched_db(row)
        else:
            messagebox.showwarning("Warning", "No movie selected. Please select a movie to edit.")

    def open_edit_window(self, movie_data):
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Edit Movie Data")

        # Create labels, entry fields, and buttons for editing
        labels = ["Title", "Genre", "Runtime", "Year", "Director", "IMDB Rating", "IMDB Votes",
                  "Rotten Tomatoes", "Actors", "IMDB ID", "Type", "Rated", "Released", "Writer",
                  "Country", "Awards", "Plot", "Watched", "I Want to Watch"]

        entry_fields = []
        for label_text, current_value in zip(labels, movie_data[1:]):  # Exclude the first element (ID)
            label = tk.Label(self.edit_window, text=label_text)
            label.pack()

            entry = tk.Entry(self.edit_window)
            entry.insert(tk.END, current_value)
            entry.pack()
            entry_fields.append(entry)

        save_button = ttk.Button(self.edit_window, text="Save Changes",
                                 command=lambda: self.save_edited_data(movie_data, entry_fields))
        save_button.pack()

    def change_watched_db(self, movie_data):
        imdb_id = movie_data[10]
        print(movie_data)
        print(movie_data[10])
        # Load the CSV file into a list of dictionaries
        csv_file = 'movie_results.csv'  # Replace with your CSV file path
        csv_rows = []
        with open(csv_file, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                csv_rows.append(row)

        # Find the row with the specified IMDB ID
        found_row_index = None
        for i, row in enumerate(csv_rows):
            if row['IMDB ID'] == imdb_id:
                found_row_index = i
                break

        # If a matching row is found, update the watch status
        if found_row_index is not None:
            if csv_rows[found_row_index]['Watched'] == 'no':
                csv_rows[found_row_index]['Watched'] = 'yes'
                csv_rows[found_row_index]['I Want to Watch'] = 'no'

                # Write the updated rows back to the CSV file
                with open(csv_file, 'w', newline='') as file:
                    fieldnames = csv_rows[0].keys()
                    csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
                    csv_writer.writeheader()
                    csv_writer.writerows(csv_rows)
                self.update_database_ui()

                messagebox.showinfo("Success", "Movie data updated successfully.")
            else:
                messagebox.showerror("Error", "You have already watched this movie.")
        else:
            messagebox.showerror("Error", "Selected movie not found in the csv file.")
    def save_edited_data(self, movie_data, entry_fields):
        new_data = [entry.get() for entry in entry_fields]

        csv_rows = []
        with open("movie_results.csv", 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                csv_rows.append(row)

        # Find the row with the selected movie ID in column 9
        found_row = None
        for row in csv_rows:
            if row['IMDB ID'] == new_data[9]:
                found_row = row
                break

        # Check if the item ID exists in the tree view
        if found_row:
            found_row.update(zip(found_row.keys(), new_data))

            # Write the updated rows back to the CSV file
            with open("movie_results.csv", 'w', newline='') as file:
                csv_writer = csv.DictWriter(file, fieldnames=csv_rows[0].keys())
                csv_writer.writeheader()
                csv_writer.writerows(csv_rows)

            self.update_database_ui()
            messagebox.showinfo("Success", "Movie data updated successfully.")
        else:
            messagebox.showerror("Error", "Selected movie not found in the treeview.")

        # Close the edit window
        self.edit_window.destroy()

    def show_all_data(self):
        all_rows = self.get_all_database_rows()
        self.update_database_ui(rows=all_rows)

    def get_all_database_rows(self):
        rows = []

        try:
            with open("movie_results.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                header = next(csv_reader)
                i = 1
                for row in csv_reader:
                    row.insert(0, str(i))
                    i += 1
                    rows.append(row)
        except FileNotFoundError:
            pass

        return rows

    def delete_movie_by_title(self, title_to_delete):
        print(f"Deleting movie: {title_to_delete}")

        try:
            with open("movie_results.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                rows = list(csv_reader)

            updated_rows = [row for row in rows if row[0].lower() != title_to_delete.lower()]

            with open("movie_results.csv", "w", newline="") as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerows(updated_rows)

            self.update_database_ui()  # Update the UI after deletion
            messagebox.showinfo("Success", f"Movie '{title_to_delete}' has been deleted.")
        except Exception as e:
            print("Error deleting movie:", e)

    def delete_selected_movie(self):
        selected_item = self.database_tree.selection()
        if selected_item:
            row = self.database_tree.item(selected_item[0])["values"]
            movie_title = row[1]  # Assuming title is in the second column
            self.delete_movie_by_title(movie_title)
        else:
            messagebox.showwarning("Warning", "No movie selected. Please select a movie to delete.")

    def search_database(self, event=None):
        title_text = self.title_entry.get().lower()
        year_text = self.year_entry.get()  # Retrieve year input value
        director_text = self.director_entry.get().lower()
        genre_text = self.genre_entry.get().lower()  # Retrieve genre input value
        imdb_rating_text = self.imdb_rating_entry.get()
        rotten_tomatoes_text = self.rotten_tomatoes_entry.get()
        actors_text = self.actors_entry.get().lower()
        writer_text = self.writer_entry.get().lower()

        filtered_rows = []

        try:
            with open("movie_results.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                header = next(csv_reader)  # Skip the header row
                for idx, row in enumerate(csv_reader, start=1):
                    if title_text in row[0].lower() and year_text in row[3] and \
                            director_text in row[4].lower() and genre_text in row[1].lower() and \
                            imdb_rating_text in row[6] and rotten_tomatoes_text in row[7] and \
                            actors_text in row[8].lower() and writer_text in row[13].lower():
                        filtered_rows.append([idx] + row)  # Insert index at the beginning

        except FileNotFoundError:
            pass

        self.update_database_ui(rows=filtered_rows)  # Update the UI with filtered data

    def search_watched_movies(self):
        filtered_rows = []

        try:
            with open("movie_results.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                header = next(csv_reader)  # Skip the header row
                for idx, row in enumerate(csv_reader, start=1):
                    if row[17] == 'yes':  # Check Watched column
                        filtered_rows.append([idx] + row)  # Insert index at the beginning
        except FileNotFoundError:
            pass

        # Save the filtered rows to a new CSV file named "watched_movies.csv"
        self.save_filtered_to_csv(filtered_rows, "watched_movies.csv")


        self.update_database_ui(rows=filtered_rows)



    def search_want_to_watch_movies(self):
        filtered_rows = []

        try:
            with open("movie_results.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                header = next(csv_reader)  # Skip the header row
                for idx, row in enumerate(csv_reader, start=1):
                    if row[18] == 'yes':  # Check I Want to Watch column
                        filtered_rows.append([idx] + row)  # Insert index at the beginning
        except FileNotFoundError:
            pass

        # Save the filtered rows to a new CSV file named "want_to_watch_movies.csv"
        self.save_filtered_to_csv(filtered_rows, "want_to_watch_movies.csv")

        self.update_database_ui(rows=filtered_rows)

    def save_filtered_to_csv(self, rows, filename):
        try:
            with open(filename, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(self.dblabels[1:])  # Write header without the ID column
                csv_writer.writerows([row[1:] for row in rows])  # Write rows without the ID column
        except Exception as e:
            print("Error saving CSV:", e)

    def delete_selected_rows(self):
        selected_items = self.database_tree.selection()
        if selected_items:
            rows_to_delete = []
            for item in selected_items:
                row = self.database_tree.item(item)["values"]
                rows_to_delete.append(row)

            if rows_to_delete:
                with open("movie_results.csv", "r") as csv_file:
                    csv_reader = csv.reader(csv_file)
                    rows = list(csv_reader)

                updated_rows = [row for row in rows if row[1:] not in rows_to_delete]

                with open("movie_results.csv", "w", newline="") as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerows(updated_rows)

                self.update_database_ui()  # Update the UI after deletion
                messagebox.showinfo("Success", "Selected rows have been deleted.")
        else:
            messagebox.showwarning("Warning", "No rows selected. Please select rows to delete.")

    def save_search_count(self):
        filename = 'analyze.csv'
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        counter_updated = False

        try:
            with open(filename, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                rows = list(csv_reader)

            for row in rows:
                if row[0] == current_date:
                    row[1] = str(int(row[1]) + 1)
                    counter_updated = True
                    break

            if not counter_updated:
                rows.append([current_date, '1'])

            with open(filename, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['Date', 'Count'])
                csv_writer.writerows(rows[1:])  # Write all rows except the header

        except FileNotFoundError:
            with open(filename, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['Date', 'Count'])
                csv_writer.writerow([current_date, '1'])

    def search_movie(self, event=None):
        self.id_counter += 1
        movie_name = self.movie_name_entry.get()
        movie_year = self.movie_year_entry.get()
        movie_type = self.movie_type_combo.get()

        url = f"http://www.omdbapi.com/?apikey={self.api_key}&t={movie_name}&y={movie_year}&type={movie_type}"
        response = requests.get(url)
        movie_data = response.json()
        self.update_ui(movie_data)
        self.save_search_count()  # Update the search count
        self.update_database_ui()
        self.update_analyzed_data_ui()  # Update the Analyzed Data tab

    def update_ui(self, movie_data):
        # Clear previous data from the table and poster image
        self.poster_label.config(image=None, bg="#D9D9D9")
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)

        if movie_data.get("Response") == "True":
            poster_url = movie_data.get("Poster")
            if poster_url != "N/A":
                image = Image.open(requests.get(poster_url, stream=True).raw)
                image.thumbnail((200, 300))
                self.poster_image = ImageTk.PhotoImage(image)
                self.poster_label.config(image=self.poster_image, bg="#D9D9D9")

            self.detail_values = [
                movie_data.get("Title"), movie_data.get("Genre"), movie_data.get("Runtime"),
                movie_data.get("Year"), movie_data.get("Director"), movie_data.get("imdbRating"),
                movie_data.get("imdbVotes"), self.get_rotten_tomatoes_rating(movie_data),
                movie_data.get("Actors"), movie_data.get("imdbID"), movie_data.get("Type"),
                movie_data.get("Rated"), movie_data.get("Released"), movie_data.get("Writer"),
                movie_data.get("Country"), movie_data.get("Awards"), movie_data.get("Plot")
            ]

            movie_details = [
                [label.strip(":"), value] for label, value in zip(self.detail_labels, self.detail_values)
            ]

            table = tabulate(movie_details, tablefmt="grid")
            self.text_widget.config(state="normal", bg="#FFFFE0")
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, table)
            self.text_widget.config(state="disabled")

        else:
            error_message = "Movie data not found."
            self.text_widget.insert(tk.END, error_message)

        # Update the UI of the Database tab
        self.update_database_ui()

        self.initialize_checkboxes_and_button()

    def get_rotten_tomatoes_rating(self, movie_data):
        ratings = movie_data.get("Ratings")
        if ratings:
            for rating in ratings:
                if "Rotten Tomatoes" in rating['Source']:
                    return rating['Value']
        return "N/A"

    def initialize_checkboxes_and_button(self):
        self.watched_var = tk.IntVar()

        # Create a new frame within result_frame for radio buttons and save button
        buttons_frame = tk.Frame(self.result_frame, bg="#D9D9D9")
        buttons_frame.place(x=560, y=420)

        self.watched_var = tk.IntVar()

        watched_radio = tk.Radiobutton(buttons_frame, text="Watched", variable=self.watched_var, value=1)
        watched_radio.config(bg="#D9D9D9")
        watched_radio.pack(side="left")

        want_to_watch_radio = tk.Radiobutton(buttons_frame, text="I Want to Watch", variable=self.watched_var, value=2)
        want_to_watch_radio.config(bg="#D9D9D9")
        want_to_watch_radio.pack(side="left")

        style = ThemedStyle(buttons_frame)
        style.set_theme("breeze")
        themed_save_button = ttk.Button(buttons_frame, text="Save", command=self.save_result)
        themed_save_button.pack(side="left")

    def save_analyze_data(self, count):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        analyze_data = [current_date, count]

        try:
            with open("analyze.csv", "a", newline="") as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(analyze_data)
        except Exception as e:
            print("Error saving analyze data:", e)

    def save_result(self):
        if (self.watched_var.get() == 0):
            messagebox.showwarning("Warning", "You Have To Select Watched or I Want To Watch")
        else:
            watched = 'yes' if self.watched_var.get() == 1 else 'no'
            want_to_watch = 'yes' if self.watched_var.get() == 2 else 'no'

            title = self.detail_values[0]
            year = self.detail_values[3]

            # Check if the title and year combination already exists in the CSV file
            is_entry_exists = False
            try:
                with open("movie_results.csv", 'r', newline='') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    for row in csv_reader:
                        if row and row[0] == title and row[3] == year:
                            is_entry_exists = True
                            break
            except FileNotFoundError:
                pass

            if not is_entry_exists:
                # Write header row if the file is empty
                is_file_empty = False
                try:
                    with open("movie_results.csv", 'r') as csv_file:
                        is_file_empty = csv_file.read().strip() == ''
                except FileNotFoundError:
                    is_file_empty = True

                if is_file_empty:
                    with open("movie_results.csv", 'a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow(self.dblabels[1:] + ["Watched", "I Want to Watch"])  # Add new columns

                # Append the data to the CSV file
                with open("movie_results.csv", 'a', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(self.detail_values[0:] + [watched, want_to_watch])  # Append data

                # Show success message box
                messagebox.showinfo("Success", "Data has been saved")
            else:
                # Show warning message box
                messagebox.showwarning("Warning", f"Entry '{title}' from {year} already exists")



            self.update_database_ui()


if __name__ == "__main__":
    root = tk.Tk()
    root.config(bg="#D9D9D9")
    root.geometry("1000x750")
    root.resizable(False, False)  # Lock resizing
    app = MovieSearchApp(root)
    root.mainloop()
