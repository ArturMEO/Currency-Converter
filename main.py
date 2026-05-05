import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x500")

        # Список валют (можно расширить)
        self.currencies = ["USD", "EUR", "GBP", "JPY", "RUB", "CNY", "CAD"]

        # Создание интерфейса
        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        # Поле ввода суммы
        tk.Label(self.root, text="Сумма:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.amount_entry = tk.Entry(self.root, width=20)
        self.amount_entry.grid(row=0, column=1, padx=10, pady=10)

        # Выбор валюты "Из"
        tk.Label(self.root, text="Из валюты:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.from_currency = ttk.Combobox(self.root, values=self.currencies, state="readonly", width=17)
        self.from_currency.grid(row=1, column=1, padx=10, pady=10)
        self.from_currency.set("USD")

        # Выбор валюты "В"
        tk.Label(self.root, text="В валюту:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.to_currency = ttk.Combobox(self.root, values=self.currencies, state="readonly", width=17)
        self.to_currency.grid(row=2, column=1, padx=10, pady=10)
        self.to_currency.set("EUR")

        # Кнопка конвертации
        self.convert_btn = tk.Button(self.root, text="Конвертировать", command=self.convert, bg="lightblue", width=15)
        self.convert_btn.grid(row=3, column=0, columnspan=2, pady=20)

        # Таблица истории
        tk.Label(self.root, text="История операций:").grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        columns = ("Amount", "From", "To", "Result", "Rate")
        self.history_tree = ttk.Treeview(self.root, columns=columns, show="headings", height=8)

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)

        self.history_tree.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Полосы прокрутки для таблицы
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.history_tree.yview)
        scrollbar.grid(row=5, column=2, sticky="ns")
        self.history_tree.configure(yscrollcommand=scrollbar.set)

    def get_exchange_rate(self, from_curr, to_curr):
        """Получение курса через API"""
        try:
            api_key = "YOUR_API_KEY"  # Замените на ваш ключ
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_curr}"

            response = requests.get(url)
            data = response.json()

            if response.status_code == 200 and to_curr in data["conversion_rates"]:
                return data["conversion_rates"][to_curr]
            else:
                messagebox.showerror("Ошибка", "Не удалось получить курс валюты")
                return None
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения к API: {e}")
            return None

    def convert(self):
        """Конвертация валюты"""
        # Проверка ввода суммы
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")
            return

        # Проверка выбора валют
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()

        if not from_curr or not to_curr:
            messagebox.showerror("Ошибка", "Выберите валюты для конвертации")
            return

        # Получение курса
        rate = self.get_exchange_rate(from_curr, to_curr)
        if rate:
            result = amount * rate

            # Отображение результата
            messagebox.showinfo(
                "Результат",
                f"{amount} {from_curr} = {result:.2f} {to_curr}\nКурс: 1 {from_curr} = {rate:.4f} {to_curr}"
            )

            # Сохранение в историю
            self.save_history(amount, from_curr, to_curr, result, rate)

    def save_history(self, amount, from_curr, to_curr, result, rate):
        """Сохранение операции в историю (JSON)"""
        record = {
            "Amount": amount,
            "From": from_curr,
            "To": to_curr,
            "Result": f"{result:.2f}",
            "Rate": f"{rate:.4f}"
        }

        # Добавление в таблицу
        self.history_tree.insert("", "end", values=(
            record["Amount"],
            record["From"],
            record["To"],
            record["Result"],
            record["Rate"]
        ))

        # Сохранение в JSON
        history = []
        for item in self.history_tree.get_children():
            history.append(self.history_tree.item(item)["values"])

        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

    def load_history(self):
        """Загрузка истории из JSON"""
        if os.path.exists("history.json"):
            try:
                with open("history.json", "r", encoding="utf-8") as f:
                    history = json.load(f)
                    for record in history:
                        self.history_tree.insert("", "end", values=record)
            except (json.JSONDecodeError, IOError):
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()
