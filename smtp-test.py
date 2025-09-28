import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import threading
from datetime import datetime
import os

class SMTPTester:
    def __init__(self, root):
        self.root = root
        self.root.title("SMTP Mail Server Tester")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="SMTP Configuration")
        
        self.email_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.email_frame, text="Compose Email")
        
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="Logs")
        
        self.setup_config_tab()
        self.setup_email_tab()
        self.setup_log_tab()
        
    def setup_config_tab(self):
        config_group = ttk.LabelFrame(self.config_frame, text="SMTP Server Configuration", padding="10")
        config_group.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(config_group, text="SMTP Server:").grid(row=0, column=0, sticky='w', pady=2)
        self.smtp_server = tk.StringVar(value="SMTP Host")
        ttk.Entry(config_group, textvariable=self.smtp_server, width=40).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(config_group, text="SMTP Port:").grid(row=1, column=0, sticky='w', pady=2)
        self.smtp_port = tk.StringVar(value="465")
        ttk.Entry(config_group, textvariable=self.smtp_port, width=10).grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(config_group, text="Security:").grid(row=2, column=0, sticky='w', pady=2)
        self.security_type = tk.StringVar(value="SSL/TLS")
        security_combo = ttk.Combobox(config_group, textvariable=self.security_type, 
                                     values=["SSL/TLS", "STARTTLS", "None"], state="readonly")
        security_combo.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        auth_group = ttk.LabelFrame(self.config_frame, text="Authentication", padding="10")
        auth_group.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(auth_group, text="Email:").grid(row=0, column=0, sticky='w', pady=2)
        self.email = tk.StringVar(value="Email Account")
        ttk.Entry(auth_group, textvariable=self.email, width=40).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(auth_group, text="Password:").grid(row=1, column=0, sticky='w', pady=2)
        self.password = tk.StringVar(value="Email Password")
        password_entry = ttk.Entry(auth_group, textvariable=self.password, show="*", width=40)
        password_entry.grid(row=1, column=1, padx=5, pady=2)
        
        self.show_password = tk.BooleanVar()
        show_pass_cb = ttk.Checkbutton(auth_group, text="Show Password", variable=self.show_password,
                                      command=lambda: password_entry.config(show="" if self.show_password.get() else "*"))
        show_pass_cb.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        test_btn = ttk.Button(self.config_frame, text="Test SMTP Connection", command=self.test_connection)
        test_btn.pack(pady=10)
        
    def setup_email_tab(self):
        email_group = ttk.LabelFrame(self.email_frame, text="Compose Email", padding="10")
        email_group.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(email_group, text="To:").grid(row=0, column=0, sticky='w', pady=2)
        self.to_email = tk.StringVar()
        ttk.Entry(email_group, textvariable=self.to_email, width=50).grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Label(email_group, text="Subject:").grid(row=1, column=0, sticky='w', pady=2)
        self.subject = tk.StringVar(value="SMTP Test Email")
        ttk.Entry(email_group, textvariable=self.subject, width=50).grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Label(email_group, text="Message:").grid(row=2, column=0, sticky='nw', pady=2)
        self.message_body = scrolledtext.ScrolledText(email_group, height=15, width=60)
        self.message_body.grid(row=2, column=1, padx=5, pady=2, sticky='nsew')
        self.message_body.insert('1.0', "This is a test email sent from the SMTP Mail Server Tester.\n\nTimestamp: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        email_group.columnconfigure(1, weight=1)
        email_group.rowconfigure(2, weight=1)
        
        send_btn = ttk.Button(self.email_frame, text="Send Test Email", command=self.send_email)
        send_btn.pack(pady=10)
        
    def setup_log_tab(self):
        log_group = ttk.LabelFrame(self.log_frame, text="Activity Log", padding="10")
        log_group.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_group, height=25, state='disabled')
        self.log_text.pack(fill='both', expand=True)
        
        clear_btn = ttk.Button(self.log_frame, text="Clear Log", command=self.clear_log)
        clear_btn.pack(pady=5)
        
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state='normal')
        self.log_text.insert('end', log_entry)
        self.log_text.see('end')
        self.log_text.config(state='disabled')
        
    def clear_log(self):
        """Clear the log display"""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state='disabled')
        
    def test_connection(self):
        """Test SMTP connection in a separate thread"""
        threading.Thread(target=self._test_connection_thread, daemon=True).start()
        
    def _test_connection_thread(self):
        """Test SMTP connection"""
        try:
            self.log_message("Testing SMTP connection...")
            
            server_addr = self.smtp_server.get().strip()
            port = int(self.smtp_port.get().strip())
            email_addr = self.email.get().strip()
            password_val = self.password.get()
            security = self.security_type.get()
            
            self.log_message(f"Connecting to {server_addr}:{port} with {security}")
            
            if security == "SSL/TLS":
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(server_addr, port, context=context)
            else:
                server = smtplib.SMTP(server_addr, port)
                if security == "STARTTLS":
                    context = ssl.create_default_context()
                    server.starttls(context=context)
            
            self.log_message("Connection established successfully")
            
            self.log_message("Testing authentication...")
            server.login(email_addr, password_val)
            self.log_message("Authentication successful")
            
            server.quit()
            self.log_message("SMTP connection test completed successfully!")
            
            self.root.after(0, lambda: messagebox.showinfo("Success", "SMTP connection test passed!"))
            
        except Exception as e:
            error_msg = f"SMTP connection test failed: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Connection Failed", error_msg))
            
    def send_email(self):
        """Send test email in a separate thread"""
        if not self.to_email.get().strip():
            messagebox.showerror("Error", "Please enter a recipient email address")
            return
            
        threading.Thread(target=self._send_email_thread, daemon=True).start()
        
    def _send_email_thread(self):
        """Send email"""
        try:
            self.log_message("Preparing to send email...")
            
            server_addr = self.smtp_server.get().strip()
            port = int(self.smtp_port.get().strip())
            email_addr = self.email.get().strip()
            password_val = self.password.get()
            security = self.security_type.get()
            
            msg = MIMEMultipart()
            msg['From'] = email_addr
            msg['To'] = self.to_email.get().strip()
            msg['Subject'] = self.subject.get()
            
            body = self.message_body.get('1.0', 'end-1c')
            msg.attach(MIMEText(body, 'plain'))
            
            self.log_message(f"Connecting to SMTP server {server_addr}:{port}")
            
            if security == "SSL/TLS":
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(server_addr, port, context=context)
            else:
                server = smtplib.SMTP(server_addr, port)
                if security == "STARTTLS":
                    context = ssl.create_default_context()
                    server.starttls(context=context)
            
            self.log_message("Authenticating...")
            server.login(email_addr, password_val)
            
            self.log_message("Sending email...")
            server.send_message(msg)
            server.quit()
            
            success_msg = f"Email sent successfully to {self.to_email.get()}"
            self.log_message(success_msg)
            self.root.after(0, lambda: messagebox.showinfo("Success", success_msg))
            
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Send Failed", error_msg))

def main():
    root = tk.Tk()
    app = SMTPTester(root)
    root.mainloop()

if __name__ == "__main__":
    main()
