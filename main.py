import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# Файл для хранения избранных пользователей
FAVORITES_FILE = "favorites.json"

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("600x500")

        # Загрузка избранных пользователей
        self.favorites = self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Поле поиска
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(search_frame, text="Имя пользователя GitHub:").pack(side="left")
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        tk.Button(search_frame, text="Найти", command=self.search_user).pack(side="left")

        # Список результатов
        results_frame = tk.Frame(self.root)
        results_frame.pack(pady=10, padx=20, fill="both", expand=True)

        tk.Label(results_frame, text="Результаты поиска:").pack(anchor="w")
        columns = ("login", "name", "public_repos", "followers")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True, side="left")

        # Кнопки действий
        button_frame = tk.Frame(results_frame)
        button_frame.pack(side="right", fill="y")
        tk.Button(button_frame, text="Добавить в избранное",
                  command=self.add_to_favorites).pack(pady=2)
        tk.Button(button_frame, text="Удалить из избранного",
                  command=self.remove_from_favorites).pack(pady=2)

        # Список избранных
        favorites_frame = tk.Frame(self.root)
        favorites_frame.pack(pady=10, padx=20, fill="both", expand=True)

        tk.Label(favorites_frame, text="Избранные пользователи:").pack(anchor="w")
        self.favorites_listbox = tk.Listbox(favorites_frame, height=8)
        self.favorites_listbox.pack(fill="both", expand=True)

        self.update_favorites_display()

    def search_user(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return

        try:
            response = requests.get(f"https://api.github.com/users/{username}")
            if response.status_code == 200:
                user_data = response.json()
                self.display_user(user_data)
            else:
                messagebox.showerror("Ошибка", f"Пользователь не найден (код: {response.status_code})")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {str(e)}")

    def display_user(self, user_data):
        # Очищаем предыдущие результаты
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавляем найденного пользователя
        self.tree.insert("", "end", values=(
            user_data.get("login", ""),
            user_data.get("name", "Не указано"),
            user_data.get("public_repos", 0),
            user_data.get("followers", 0)
        ))

    def add_to_favorites(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из результатов поиска")
            return

        user_data = self.tree.item(selection[0])["values"]
        login = user_data[0]

        if login not in self.favorites:
            self.favorites[login] = {
                "name": user_data[1],
                "public_repos": user_data[2],
                "followers": user_data[3]
            }
            self.save_favorites()
            self.update_favorites_display()
            messagebox.showinfo("Успех", f"{login} добавлен в избранное!")

    def remove_from_favorites(self):
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из избранного")
            return

        login = self.favorites_listbox.get(selection[0])
        if login in self.favorites:
            del self.favorites[login]
            self.save_favorites()
            self.update_favorites_display()
            messagebox.showinfo("Успех", f"{login} удалён из избранного!")

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_favorites(self):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, indent=4, ensure_ascii=False)

    def update_favorites_display(self):
        self.favorites_listbox.delete(0, tk.END)
        for login in self.favorites.keys():
            self.favorites_listbox.insert(tk.END, login)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
