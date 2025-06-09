import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import serial
import serial.tools.list_ports
from datetime import datetime

class DatabaseViewer:
    def __init__(self, parent, db_name):
        self.window = tk.Toplevel(parent)
        self.window.title("Visualizador do Banco de Dados")
        self.window.geometry("1000x600")
        
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        # Frame para filtros
        filter_frame = ttk.Frame(self.window, padding="10")
        filter_frame.pack(fill="x")
        
        ttk.Label(filter_frame, text="Filtrar por data:").pack(side="left", padx=5)
        
        # Data inicial
        ttk.Label(filter_frame, text="De:").pack(side="left", padx=5)
        self.date_from = ttk.Entry(filter_frame, width=10)
        self.date_from.pack(side="left", padx=5)
        
        # Data final
        ttk.Label(filter_frame, text="Até:").pack(side="left", padx=5)
        self.date_to = ttk.Entry(filter_frame, width=10)
        self.date_to.pack(side="left", padx=5)
        
        # Botão de filtrar
        ttk.Button(filter_frame, text="Filtrar", command=self.load_data).pack(side="left", padx=5)
        
        # Botão de exportar
        ttk.Button(filter_frame, text="Exportar CSV", command=self.export_csv).pack(side="left", padx=5)
        
        # Treeview para mostrar os dados
        self.tree = ttk.Treeview(self.window, columns=("ID", "Data/Hora", "Evento"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Data/Hora", text="Data/Hora")
        self.tree.heading("Evento", text="Evento")
        
        self.tree.column("ID", width=50)
        self.tree.column("Data/Hora", width=200)
        self.tree.column("Evento", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def load_data(self):
        # Limpa a treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Prepara a query
        query = "SELECT id, timestamp, event_type FROM events"
        params = []
        
        # Adiciona filtros de data se preenchidos
        if self.date_from.get() and self.date_to.get():
            query += " WHERE timestamp BETWEEN ? AND ?"
            params.extend([self.date_from.get(), self.date_to.get()])
            
        query += " ORDER BY timestamp DESC"
        
        # Executa a query
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)
            
    def export_csv(self):
        import csv
        from tkinter import filedialog
        
        # Abre diálogo para salvar arquivo
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Escreve o cabeçalho
                writer.writerow(["ID", "Data/Hora", "Evento"])
                # Escreve os dados
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)["values"])
                    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

class AlertWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("ALERTA DE SEGURANÇA!")
        self.window.geometry("400x200")
        self.window.configure(bg='red')
        
        # Configura a janela para ficar sempre no topo
        self.window.attributes('-topmost', True)
        
        # Adiciona o texto de alerta
        alert_label = tk.Label(
            self.window,
            text="ALARME ATIVADO!",
            font=("Helvetica", 24, "bold"),
            bg='red',
            fg='white'
        )
        alert_label.pack(expand=True)
        
        # Adiciona botão para fechar o alerta
        close_button = tk.Button(
            self.window,
            text="Fechar Alerta",
            command=self.window.destroy,
            font=("Helvetica", 12)
        )
        close_button.pack(pady=20)

class AlarmMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Alarme Arduino")
        self.root.geometry("800x600")
        
        # Variável para controlar o estado do alerta
        self.alert_window = None

        self.db_name = "alarm_history.db"
        self.conn = None
        self.cursor = None
        self.init_database()

        self.serial_port = None
        self.baud_rate = 9600
        self.arduino = None

        self.create_widgets()
        self.update_serial_ports()

    def init_database(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL
                )
            """)
            self.conn.commit()
            print(f"Banco de dados '{self.db_name}' inicializado com sucesso.")
        except sqlite3.Error as e:
            print(f"Erro ao inicializar o banco de dados: {e}")

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para status do alarme
        status_frame = ttk.LabelFrame(main_frame, text="Status do Alarme", padding="10")
        status_frame.pack(fill="x", pady=5)

        self.alarm_status_label = ttk.Label(
            status_frame, 
            text="Desconectado", 
            font=("Helvetica", 16, "bold")
        )
        self.alarm_status_label.pack(pady=5)

        # Frame para configuração serial
        serial_frame = ttk.LabelFrame(main_frame, text="Configuração Serial", padding="10")
        serial_frame.pack(fill="x", pady=5)

        # Grid para os controles seriais
        self.port_label = ttk.Label(serial_frame, text="Porta Serial:")
        self.port_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.port_combobox = ttk.Combobox(serial_frame, state="readonly", width=30)
        self.port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.port_combobox.bind("<<ComboboxSelected>>", self.on_port_selected)

        self.refresh_button = ttk.Button(
            serial_frame, 
            text="Atualizar Portas", 
            command=self.update_serial_ports
        )
        self.refresh_button.grid(row=0, column=2, padx=5, pady=5)

        self.connect_button = ttk.Button(
            serial_frame, 
            text="Conectar", 
            command=self.connect_serial
        )
        self.connect_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.disconnect_button = ttk.Button(
            serial_frame, 
            text="Desconectar", 
            command=self.disconnect_serial, 
            state=tk.DISABLED
        )
        self.disconnect_button.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Botão para visualizar banco de dados
        self.view_db_button = ttk.Button(
            serial_frame,
            text="Ver Banco de Dados",
            command=self.open_database_viewer
        )
        self.view_db_button.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Frame para histórico de eventos
        history_frame = ttk.LabelFrame(main_frame, text="Histórico de Eventos", padding="10")
        history_frame.pack(fill="both", expand=True, pady=5)

        # Configuração da Treeview
        self.history_tree = ttk.Treeview(
            history_frame, 
            columns=("Timestamp", "Evento"), 
            show="headings",
            height=10
        )
        
        # Configuração das colunas
        self.history_tree.heading("Timestamp", text="Data/Hora")
        self.history_tree.heading("Evento", text="Evento")
        self.history_tree.column("Timestamp", width=200)
        self.history_tree.column("Evento", width=400)

        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        # Posicionamento da Treeview e Scrollbar
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Carregar histórico inicial
        self.load_history()

    def open_database_viewer(self):
        DatabaseViewer(self.root, self.db_name)

    def update_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        self.available_ports = [port.device for port in ports]
        self.port_combobox['values'] = self.available_ports
        if self.available_ports:
            self.port_combobox.set(self.available_ports[0])
            self.serial_port = self.available_ports[0]
        else:
            self.port_combobox.set("Nenhuma porta encontrada")
            self.serial_port = None

    def on_port_selected(self, event):
        self.serial_port = self.port_combobox.get()

    def connect_serial(self):
        if self.serial_port:
            try:
                self.arduino = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
                self.alarm_status_label.config(
                    text="Conectado (Aguardando Alarme)", 
                    foreground="blue"
                )
                self.connect_button.config(state=tk.DISABLED)
                self.disconnect_button.config(state=tk.NORMAL)
                self.read_serial_data()
                print(f"Conectado à porta serial {self.serial_port}")
            except serial.SerialException as e:
                self.alarm_status_label.config(
                    text=f"Erro de Conexão: {e}", 
                    foreground="red"
                )
                print(f"Erro ao conectar à porta serial {self.serial_port}: {e}")
        else:
            self.alarm_status_label.config(
                text="Selecione uma porta serial", 
                foreground="orange"
            )

    def disconnect_serial(self):
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
            self.alarm_status_label.config(
                text="Desconectado", 
                foreground="black"
            )
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            print("Desconectado da porta serial.")

    def read_serial_data(self):
        if self.arduino and self.arduino.is_open:
            try:
                line = self.arduino.readline().decode('utf-8').strip()
                if line:
                    print(f"Dados recebidos: {line}")
                    self.process_serial_data(line)
            except serial.SerialException as e:
                print(f"Erro de leitura serial: {e}")
                self.disconnect_serial()
            except UnicodeDecodeError:
                print("Erro de decodificação Unicode, ignorando linha.")

        self.root.after(100, self.read_serial_data)

    def show_alert(self):
        # Se já existe uma janela de alerta, não cria outra
        if self.alert_window is None or not self.alert_window.window.winfo_exists():
            self.alert_window = AlertWindow(self.root)
            # Toca um som de alerta (beep do sistema)
            self.root.bell()
            # Faz a janela principal piscar
            self.flash_window()

    def flash_window(self):
        # Faz a janela principal piscar em vermelho
        original_color = self.root.cget("bg")
        self.root.configure(bg='red')
        self.root.after(500, lambda: self.root.configure(bg=original_color))
        self.root.after(1000, lambda: self.root.configure(bg='red'))
        self.root.after(1500, lambda: self.root.configure(bg=original_color))

    def process_serial_data(self, data):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if data == "ALARME_ON":
            self.alarm_status_label.config(
                text="ALARME ATIVADO!", 
                foreground="red"
            )
            self.insert_event(current_time, "Alarme Ativado")
            # Mostra o alerta quando o alarme é ativado
            self.show_alert()
        elif data == "ALARME_OFF":
            self.alarm_status_label.config(
                text="Alarme Desativado", 
                foreground="green"
            )
            # Se existir uma janela de alerta, fecha ela
            if self.alert_window and self.alert_window.window.winfo_exists():
                self.alert_window.window.destroy()

    def insert_event(self, timestamp, event_type):
        try:
            self.cursor.execute(
                "INSERT INTO events (timestamp, event_type) VALUES (?, ?)", 
                (timestamp, event_type)
            )
            self.conn.commit()
            self.history_tree.insert("", 0, values=(timestamp, event_type))
            print(f"Evento registrado: {event_type} em {timestamp}")
        except sqlite3.Error as e:
            print(f"Erro ao inserir evento no banco de dados: {e}")

    def load_history(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        try:
            self.cursor.execute(
                "SELECT timestamp, event_type FROM events ORDER BY timestamp DESC LIMIT 100"
            )
            for row in self.cursor.fetchall():
                self.history_tree.insert("", "end", values=row)
        except sqlite3.Error as e:
            print(f"Erro ao carregar histórico: {e}")

    def on_closing(self):
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        if self.conn:
            self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AlarmMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop() 