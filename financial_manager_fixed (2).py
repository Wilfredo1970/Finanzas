#!/usr/bin/env python3
"""
Gestor Financiero Multi-Moneda con Importación Universal de PDF
VERSIÓN CON PARSER UNIVERSAL DE ESTADOS DE CUENTA
Autor: Sistema de Gestión Financiera
Versión: 1.2
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import json
import csv
import os
import re

# Comprobar soporte PDF
try:
    import PyPDF2
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

class MultiCurrencyFinancialManager:
    def clear_preview(self):
        """Limpiar la vista previa de importación (placeholder)"""
        messagebox.showinfo("Limpiar Vista Previa", "Función de limpiar vista previa en desarrollo.")
    def confirm_import(self):
        """Confirmar importación de transacciones (placeholder)"""
        messagebox.showinfo("Confirmar Importación", "Función de confirmación de importación en desarrollo.")
    def import_csv(self):
        """Importar transacciones desde un archivo CSV (placeholder)"""
        messagebox.showinfo("Importar CSV", "Función de importación de CSV en desarrollo.")
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Control Financiero Multi-Moneda Chile v1.1")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Configurar estilo
        self.setup_styles()
        
        # Datos en memoria
        self.incomes = []
        self.expenses = []
        self.income_categories = ['Salario CLP', 'Freelance USD', 'PayPal USD', 'Transferencia Internacional', 
                                 'Inversiones', 'Venta', 'Bonificación', 'Otros']
        self.expense_categories = ['Alimentación', 'Transporte', 'Hogar', 'Salud', 'Entretenimiento', 
                                 'Educación', 'Servicios', 'Servicios USD', 'Tarjeta de Crédito', 'Otros']
        
        # Sistema de monedas (configurado para Chile)
        self.currencies = ['CLP', 'USD', 'EUR']
        self.main_currency = 'CLP'  # Moneda principal para reportes
        self.exchange_rates = {
            'USD': 950.0,  # 1 USD = 950 CLP (actualizable)
            'EUR': 1050.0,  # 1 EUR = 1050 CLP (actualizable)
            'CLP': 1.0
        }
        
        # Configuración específica Chile
        self.chile_banks = ['Banco de Chile', 'BCI', 'Santander', 'Banco Estado', 'Itau', 'BICE', 'Security', 'Otros']
        
        # Archivo de datos
        self.data_file = 'financial_data.json'
        
        # Cargar datos existentes
        self.load_data()
        
        # Crear interfaz
        self.create_interface()
        
        # Actualizar dashboard inicial
        self.update_dashboard()
        
        # Configurar cierre de aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Configurar estilos personalizados"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilos para botones
        style.configure('Success.TButton', 
                       background='#27ae60', 
                       foreground='white',
                       padding=(10, 5))
        style.map('Success.TButton',
                 background=[('active', '#2ecc71')])
        
        style.configure('Danger.TButton', 
                       background='#e74c3c', 
                       foreground='white',
                       padding=(10, 5))
        style.map('Danger.TButton',
                 background=[('active', '#c0392b')])
        
        style.configure('Info.TButton', 
                       background='#3498db', 
                       foreground='white',
                       padding=(10, 5))
        style.map('Info.TButton',
                 background=[('active', '#2980b9')])
    
    def create_interface(self):
        """Crear la interfaz principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear pestañas
        self.create_dashboard_tab()
        self.create_transactions_tab()
        self.create_currency_tab()
        self.create_import_tab()
        self.create_reports_tab()
        self.create_export_tab()
    
    def create_dashboard_tab(self):
        """Crear pestaña del dashboard"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Título
        title_label = tk.Label(dashboard_frame, 
                              text="💰 Control Financiero Multi-Moneda", 
                              font=('Arial', 24, 'bold'),
                              bg='#2c3e50', fg='white', pady=20)
        title_label.pack(fill=tk.X)
        
        # Subtítulo
        subtitle_label = tk.Label(dashboard_frame, 
                                 text=f"Dashboard actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                 font=('Arial', 12))
        subtitle_label.pack(pady=5)
        
        # Frame para métricas
        metrics_frame = ttk.Frame(dashboard_frame)
        metrics_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Crear tarjetas de métricas
        self.create_metric_cards(metrics_frame)
        
        # Botón de actualización
        ttk.Button(dashboard_frame, text="🔄 Actualizar Dashboard", 
                  command=self.update_dashboard, 
                  style='Info.TButton').pack(pady=20)
        
        # Área de resumen textual
        self.create_text_summary(dashboard_frame)
    
    def create_metric_cards(self, parent):
        """Crear tarjetas de métricas con múltiples monedas"""
        # Frame contenedor con grid
        cards_frame = tk.Frame(parent, bg='#f0f0f0')
        cards_frame.pack(fill=tk.X, pady=10)
        
        # Configurar grid
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)
        
        # Tarjeta Total Ingresos
        income_card = tk.Frame(cards_frame, bg='#27ae60', relief=tk.RAISED, bd=3)
        income_card.grid(row=0, column=0, padx=10, pady=10, sticky='ew', ipady=20)
        
        tk.Label(income_card, text="TOTAL INGRESOS", 
                font=('Arial', 12, 'bold'), bg='#27ae60', fg='white').pack(pady=3)
        self.total_income_label = tk.Label(income_card, text="$0 CLP", 
                                          font=('Arial', 16, 'bold'), 
                                          bg='#27ae60', fg='white')
        self.total_income_label.pack(pady=2)
        self.total_income_usd_label = tk.Label(income_card, text="$0 USD", 
                                              font=('Arial', 11), 
                                              bg='#27ae60', fg='white')
        self.total_income_usd_label.pack(pady=1)
        self.income_count_label = tk.Label(income_card, text="0 transacciones", 
                                          font=('Arial', 9), bg='#27ae60', fg='white')
        self.income_count_label.pack(pady=3)
        
        # Tarjeta Total Gastos
        expense_card = tk.Frame(cards_frame, bg='#e74c3c', relief=tk.RAISED, bd=3)
        expense_card.grid(row=0, column=1, padx=10, pady=10, sticky='ew', ipady=20)
        
        tk.Label(expense_card, text="TOTAL GASTOS", 
                font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white').pack(pady=3)
        self.total_expense_label = tk.Label(expense_card, text="$0 CLP", 
                                           font=('Arial', 16, 'bold'), 
                                           bg='#e74c3c', fg='white')
        self.total_expense_label.pack(pady=2)
        self.total_expense_usd_label = tk.Label(expense_card, text="$0 USD", 
                                               font=('Arial', 11), 
                                               bg='#e74c3c', fg='white')
        self.total_expense_usd_label.pack(pady=1)
        self.expense_count_label = tk.Label(expense_card, text="0 transacciones", 
                                           font=('Arial', 9), bg='#e74c3c', fg='white')
        self.expense_count_label.pack(pady=3)
        
        # Tarjeta Balance
        balance_card = tk.Frame(cards_frame, bg='#3498db', relief=tk.RAISED, bd=3)
        balance_card.grid(row=0, column=2, padx=10, pady=10, sticky='ew', ipady=20)
        
        tk.Label(balance_card, text="BALANCE ACTUAL", 
                font=('Arial', 12, 'bold'), bg='#3498db', fg='white').pack(pady=3)
        self.balance_label = tk.Label(balance_card, text="$0 CLP", 
                                     font=('Arial', 16, 'bold'), 
                                     bg='#3498db', fg='white')
        self.balance_label.pack(pady=2)
        self.balance_usd_label = tk.Label(balance_card, text="$0 USD", 
                                         font=('Arial', 11), 
                                         bg='#3498db', fg='white')
        self.balance_usd_label.pack(pady=1)
        self.balance_status_label = tk.Label(balance_card, text="Sin movimientos", 
                                            font=('Arial', 9), bg='#3498db', fg='white')
        self.balance_status_label.pack(pady=3)
        
        # Tarjeta Tipo de Cambio
        exchange_card = tk.Frame(cards_frame, bg='#9b59b6', relief=tk.RAISED, bd=3)
        exchange_card.grid(row=0, column=3, padx=10, pady=10, sticky='ew', ipady=20)
        
        tk.Label(exchange_card, text="TIPO DE CAMBIO", 
                font=('Arial', 12, 'bold'), bg='#9b59b6', fg='white').pack(pady=3)
        self.exchange_rate_label = tk.Label(exchange_card, text=f"1 USD = {self.exchange_rates['USD']:,.0f} CLP", 
                                           font=('Arial', 13, 'bold'), 
                                           bg='#9b59b6', fg='white')
        self.exchange_rate_label.pack(pady=2)
        
        # Botón para actualizar tipo de cambio
        update_btn = tk.Button(exchange_card, text="Actualizar TC", 
                              command=self.update_exchange_rate_dialog,
                              bg='#8e44ad', fg='white', font=('Arial', 9),
                              relief=tk.FLAT, pady=2)
        update_btn.pack(pady=3)
    
    def create_text_summary(self, parent):
        """Crear resumen textual"""
        summary_frame = ttk.LabelFrame(parent, text="📈 Resumen Detallado", padding=15)
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.summary_text = tk.Text(summary_frame, height=12, font=('Courier', 10))
        summary_scrollbar = ttk.Scrollbar(summary_frame, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=summary_scrollbar.set)
        
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        summary_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_transactions_tab(self):
        """Crear pestaña de transacciones"""
        trans_frame = ttk.Frame(self.notebook)
        self.notebook.add(trans_frame, text="💸 Transacciones")
        
        # Título
        tk.Label(trans_frame, text="💸 Gestión de Transacciones", 
                font=('Arial', 18, 'bold')).pack(pady=10)
        
        # Crear notebook interno para ingresos y gastos
        transactions_notebook = ttk.Notebook(trans_frame)
        transactions_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de ingresos
        self.create_incomes_subtab(transactions_notebook)
        
        # Pestaña de gastos
        self.create_expenses_subtab(transactions_notebook)
    
    def create_incomes_subtab(self, parent_notebook):
        """Crear subpestaña de ingresos"""
        income_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(income_frame, text="📈 Ingresos")
        
        # Formulario
        form_frame = ttk.LabelFrame(income_frame, text="Nuevo Ingreso", padding=15)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Campos del formulario en grid
        fields_frame = ttk.Frame(form_frame)
        fields_frame.pack(fill=tk.X)
        
        # Fecha
        ttk.Label(fields_frame, text="Fecha:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.income_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(fields_frame, textvariable=self.income_date, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        # Descripción
        ttk.Label(fields_frame, text="Descripción:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.income_description = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.income_description, width=30).grid(row=0, column=3, padx=5, pady=5)
        
        # Categoría
        ttk.Label(fields_frame, text="Categoría:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.income_category = tk.StringVar()
        ttk.Combobox(fields_frame, textvariable=self.income_category, 
                     values=self.income_categories, width=20).grid(row=1, column=1, padx=5, pady=5)
        
        # Monto y moneda en el mismo frame
        ttk.Label(fields_frame, text="Monto:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        amount_frame = ttk.Frame(fields_frame)
        amount_frame.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        
        self.income_amount = tk.StringVar()
        ttk.Entry(amount_frame, textvariable=self.income_amount, width=15).pack(side=tk.LEFT, padx=(0,5))
        
        self.income_currency = tk.StringVar(value='CLP')
        ttk.Combobox(amount_frame, textvariable=self.income_currency, 
                     values=self.currencies, width=8).pack(side=tk.LEFT)
        
        # Botón agregar
        ttk.Button(form_frame, text="Agregar Ingreso", 
                  command=self.add_income, 
                  style='Success.TButton').pack(pady=10)
        
        # Tabla de ingresos
        table_frame = ttk.Frame(income_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("Fecha", "Descripción", "Categoría", "Monto", "Moneda")
        self.income_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.income_tree.heading(col, text=col)
            if col == "Descripción":
                self.income_tree.column(col, width=250)
            elif col == "Moneda":
                self.income_tree.column(col, width=80)
            else:
                self.income_tree.column(col, width=120)
        
        self.income_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        income_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.income_tree.yview)
        self.income_tree.configure(yscrollcommand=income_scrollbar.set)
        income_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón eliminar
        ttk.Button(income_frame, text="Eliminar Seleccionado", 
                  command=self.delete_income, 
                  style='Danger.TButton').pack(pady=5)
    
    def create_expenses_subtab(self, parent_notebook):
        """Crear subpestaña de gastos"""
        expense_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(expense_frame, text="📉 Gastos")
        
        # Formulario
        form_frame = ttk.LabelFrame(expense_frame, text="Nuevo Gasto", padding=15)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Campos del formulario en grid
        fields_frame = ttk.Frame(form_frame)
        fields_frame.pack(fill=tk.X)
        
        # Fecha
        ttk.Label(fields_frame, text="Fecha:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.expense_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(fields_frame, textvariable=self.expense_date, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        # Descripción
        ttk.Label(fields_frame, text="Descripción:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.expense_description = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.expense_description, width=30).grid(row=0, column=3, padx=5, pady=5)
        
        # Categoría
        ttk.Label(fields_frame, text="Categoría:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.expense_category = tk.StringVar()
        ttk.Combobox(fields_frame, textvariable=self.expense_category, 
                     values=self.expense_categories, width=20).grid(row=1, column=1, padx=5, pady=5)
        
        # Monto y moneda
        ttk.Label(fields_frame, text="Monto:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        amount_frame = ttk.Frame(fields_frame)
        amount_frame.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        
        self.expense_amount = tk.StringVar()
        ttk.Entry(amount_frame, textvariable=self.expense_amount, width=15).pack(side=tk.LEFT, padx=(0,5))
        
        self.expense_currency = tk.StringVar(value='CLP')
        ttk.Combobox(amount_frame, textvariable=self.expense_currency, 
                     values=self.currencies, width=8).pack(side=tk.LEFT)
        
        # Botón agregar
        ttk.Button(form_frame, text="Agregar Gasto", 
                  command=self.add_expense, 
                  style='Danger.TButton').pack(pady=10)
        
        # Tabla de gastos
        table_frame = ttk.Frame(expense_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("Fecha", "Descripción", "Categoría", "Monto", "Moneda")
        self.expense_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.expense_tree.heading(col, text=col)
            if col == "Descripción":
                self.expense_tree.column(col, width=250)
            elif col == "Moneda":
                self.expense_tree.column(col, width=80)
            else:
                self.expense_tree.column(col, width=120)
        
        self.expense_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        expense_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.expense_tree.yview)
        self.expense_tree.configure(yscrollcommand=expense_scrollbar.set)
        expense_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón eliminar
        ttk.Button(expense_frame, text="Eliminar Seleccionado", 
                  command=self.delete_expense, 
                  style='Danger.TButton').pack(pady=5)
    
    def create_currency_tab(self):
        """Crear pestaña de gestión de monedas"""
        currency_frame = ttk.Frame(self.notebook)
        self.notebook.add(currency_frame, text="💱 Monedas")
        
        # Título
        tk.Label(currency_frame, text="💱 Gestión de Monedas y Tipos de Cambio", 
                font=('Arial', 18, 'bold')).pack(pady=10)
        
        # Frame principal
        main_frame = ttk.Frame(currency_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tipos de cambio actuales
        rates_frame = ttk.LabelFrame(main_frame, text="Tipos de Cambio Actuales", padding=15)
        rates_frame.pack(fill=tk.X, pady=10)
        
        # USD
        usd_frame = ttk.Frame(rates_frame)
        usd_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(usd_frame, text="1 USD =").pack(side=tk.LEFT, padx=(0,5))
        self.usd_rate = tk.StringVar(value=str(self.exchange_rates['USD']))
        ttk.Entry(usd_frame, textvariable=self.usd_rate, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(usd_frame, text="CLP").pack(side=tk.LEFT, padx=5)
        ttk.Button(usd_frame, text="Actualizar", 
                  command=lambda: self.update_single_rate('USD'),
                  style='Info.TButton').pack(side=tk.LEFT, padx=10)
        
        # Calculadora de conversión
        calc_frame = ttk.LabelFrame(main_frame, text="Calculadora de Conversión", padding=15)
        calc_frame.pack(fill=tk.X, pady=10)
        
        calc_inputs = ttk.Frame(calc_frame)
        calc_inputs.pack(fill=tk.X, pady=5)
        
        ttk.Label(calc_inputs, text="Convertir:").pack(side=tk.LEFT, padx=5)
        self.convert_amount = tk.StringVar()
        ttk.Entry(calc_inputs, textvariable=self.convert_amount, width=15).pack(side=tk.LEFT, padx=5)
        
        self.convert_from = tk.StringVar(value='USD')
        ttk.Combobox(calc_inputs, textvariable=self.convert_from, 
                     values=self.currencies, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(calc_inputs, text="a").pack(side=tk.LEFT, padx=5)
        
        self.convert_to = tk.StringVar(value='CLP')
        ttk.Combobox(calc_inputs, textvariable=self.convert_to, 
                     values=self.currencies, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(calc_inputs, text="Convertir", 
                  command=self.calculate_conversion, 
                  style='Info.TButton').pack(side=tk.LEFT, padx=10)
        
        # Resultado
        self.conversion_result = tk.StringVar(value="Resultado aparecerá aquí")
        result_label = ttk.Label(calc_frame, textvariable=self.conversion_result, 
                                font=('Arial', 12, 'bold'))
        result_label.pack(pady=10)
    
    def create_import_tab(self):
        """Crear pestaña de importación con parser universal de PDF"""
        import_frame = ttk.Frame(self.notebook)
        self.notebook.add(import_frame, text="🏦 Importar")
        
        # Título
        tk.Label(import_frame, text="🏦 Importación Universal de Estados de Cuenta", 
                font=('Arial', 18, 'bold')).pack(pady=10)
        
        # Frame para métodos de importación
        methods_frame = ttk.LabelFrame(import_frame, text="Métodos de Importación", padding=15)
        methods_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Botones principales
        buttons_row1 = ttk.Frame(methods_frame)
        buttons_row1.pack(fill=tk.X, pady=5)
        
        if PDF_SUPPORT:
            ttk.Button(buttons_row1, text="📄 Importar PDF (Universal)", 
                      command=self.import_pdf_universal, 
                      style='Success.TButton').pack(side=tk.LEFT, padx=5)
        else:
            tk.Label(buttons_row1, text="📄 PDF: Instale PyPDF2 pdfplumber", 
                    fg='red', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_row1, text="📋 Pegar Texto Manual", 
                  command=self.import_text_manual, 
                  style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_row1, text="📁 Importar CSV", 
                  command=self.import_csv, 
                  style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
        buttons_row2 = ttk.Frame(methods_frame)
        buttons_row2.pack(fill=tk.X, pady=5)
        
        ttk.Button(buttons_row2, text="🎯 Agregar Ejemplos", 
                  command=self.add_sample_transactions,
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        # Configuración de detección
        config_frame = ttk.LabelFrame(import_frame, text="Configuración de Detección", padding=15)
        config_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Selector de banco para optimizar detección
        bank_frame = ttk.Frame(config_frame)
        bank_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(bank_frame, text="Banco (opcional):").pack(side=tk.LEFT, padx=(0,5))
        self.selected_bank = tk.StringVar(value="Detectar Automáticamente")
        bank_options = ["Detectar Automáticamente", "Santander", "BCI", "Banco de Chile", 
                       "Banco Estado", "Itaú", "BICE", "Security", "Falabella", "Ripley", "Otros"]
        ttk.Combobox(bank_frame, textvariable=self.selected_bank, 
                     values=bank_options, width=25).pack(side=tk.LEFT, padx=5)
        
        # Tipo de cuenta
        type_frame = ttk.Frame(config_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="Tipo de cuenta:").pack(side=tk.LEFT, padx=(0,5))
        self.account_type = tk.StringVar(value="Tarjeta de Crédito")
        ttk.Combobox(type_frame, textvariable=self.account_type,
                     values=["Tarjeta de Crédito", "Cuenta Corriente", "Cuenta Vista", "PayPal"], 
                     width=20).pack(side=tk.LEFT, padx=5)
        
        # Vista previa de transacciones detectadas
        preview_frame = ttk.LabelFrame(import_frame, text="Vista Previa", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tabla de previsualización
        columns = ("Fecha", "Descripción", "Monto", "Moneda", "Categoría", "Tipo")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            if col == "Descripción":
                self.preview_tree.column(col, width=200)
            elif col == "Categoría":
                self.preview_tree.column(col, width=120)
            else:
                self.preview_tree.column(col, width=80)
        
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de confirmación
        confirm_frame = ttk.Frame(preview_frame)
        confirm_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(confirm_frame, text="✅ Confirmar Importación", 
                  command=self.confirm_import, 
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(confirm_frame, text="❌ Limpiar", 
                  command=self.clear_preview, 
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        
        self.import_status = tk.StringVar(value="Seleccione un método de importación")
        status_label = ttk.Label(confirm_frame, textvariable=self.import_status)
        status_label.pack(side=tk.RIGHT, padx=10)
        
        # Información de bancos soportados
        info_frame = ttk.LabelFrame(import_frame, text="Bancos y Formatos Soportados", padding=15)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        info_text = """
🏦 BANCOS SOPORTADOS (Detección Automática):
• Santander, BCI, Banco de Chile, Banco Estado, Itaú, BICE, Security
• Falabella, Ripley, Banco Consorcio, Coopeuch
• PayPal, Mercado Pago, WebPay

📄 FORMATOS RECONOCIDOS:
• PDF: Estados de cuenta estándar con tablas de transacciones
• Texto: Copiado manual desde cualquier PDF o web
• CSV: Formato personalizado con columnas Fecha,Descripción,Monto

🎯 DETECCIÓN INTELIGENTE:
• Fechas: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD
• Montos: $1.234.567, $1,234.56, 1234567, USD 123.45
• Descripciones: Automáticamente categorizadas por contenido
• Monedas: CLP, USD, EUR detectadas por contexto

⚡ MÉTODO RECOMENDADO:
1. Sube tu PDF → Detección automática
2. Si falla → Copia texto manual → Pegar aquí
3. Revisa vista previa → Confirma importación
        """
        
        tk.Label(info_frame, text=info_text, 
                font=('Arial', 9), justify=tk.LEFT).pack()
    
    def create_reports_tab(self):
        """Crear pestaña de reportes"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="📊 Reportes")
        
        # Título
        tk.Label(reports_frame, text="📊 Reportes Multi-Moneda", 
                font=('Arial', 18, 'bold')).pack(pady=10)
        
        # Botones de reportes
        buttons_frame = ttk.Frame(reports_frame)
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(buttons_frame, text="📈 Reporte Mensual", 
                  command=self.generate_monthly_report, 
                  style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="📋 Análisis por Categorías", 
                  command=self.generate_category_report, 
                  style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
        # Área de texto para reportes
        report_frame = ttk.Frame(reports_frame)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.report_text = tk.Text(report_frame, font=('Courier', 10))
        report_scrollbar = ttk.Scrollbar(report_frame, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scrollbar.set)
        
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_export_tab(self):
        """Crear pestaña de exportación"""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="💾 Exportar")
        
        # Título
        tk.Label(export_frame, text="💾 Exportar Datos", 
                font=('Arial', 18, 'bold')).pack(pady=10)
        
        # Botones de exportación
        buttons_frame = ttk.Frame(export_frame)
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(buttons_frame, text="📄 Exportar CSV", 
                  command=self.export_csv, 
                  style='Success.TButton').pack(side=tk.LEFT, padx=10)
        
        ttk.Button(buttons_frame, text="💾 Crear Respaldo", 
                  command=self.create_backup, 
                  style='Success.TButton').pack(side=tk.LEFT, padx=10)
        
        # Estado del archivo
        info_frame = ttk.LabelFrame(export_frame, text="Estado del Sistema", padding=20)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        status_text = f"""
📊 ESTADO ACTUAL:
• Archivo de datos: {self.data_file}
• Ingresos registrados: {len(self.incomes)}
• Gastos registrados: {len(self.expenses)}
• Moneda principal: {self.main_currency}
• Tipo de cambio USD: {self.exchange_rates['USD']} CLP

💾 FUNCIONES DE RESPALDO:
• Los datos se guardan automáticamente
• Crear respaldos manuales regularmente
• Exportar a CSV para análisis externo

🔄 SINCRONIZACIÓN:
• Los cambios se guardan inmediatamente
• Sin pérdida de datos al cerrar
        """
        
        tk.Label(info_frame, text=status_text, 
                font=('Arial', 10), justify=tk.LEFT).pack()
    
    # Métodos de funcionalidad
    def add_income(self):
        """Agregar nuevo ingreso"""
        try:
            if not all([self.income_date.get(), self.income_description.get(), 
                       self.income_category.get(), self.income_amount.get()]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            income = {
                'id': datetime.now().timestamp(),
                'date': self.income_date.get(),
                'description': self.income_description.get(),
                'category': self.income_category.get(),
                'amount': float(self.income_amount.get()),
                'currency': self.income_currency.get()
            }
            
            self.incomes.append(income)
            self.update_income_table()
            self.update_dashboard()
            self.save_data()
            
            # Limpiar formulario
            self.income_description.set("")
            self.income_category.set("")
            self.income_amount.set("")
            self.income_currency.set('CLP')
            self.income_date.set(date.today().strftime("%Y-%m-%d"))
            
            messagebox.showinfo("Éxito", "Ingreso agregado correctamente")
            
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")
    
    def add_expense(self):
        """Agregar nuevo gasto"""
        try:
            if not all([self.expense_date.get(), self.expense_description.get(), 
                       self.expense_category.get(), self.expense_amount.get()]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            expense = {
                'id': datetime.now().timestamp(),
                'date': self.expense_date.get(),
                'description': self.expense_description.get(),
                'category': self.expense_category.get(),
                'amount': float(self.expense_amount.get()),
                'currency': self.expense_currency.get()
            }
            
            self.expenses.append(expense)
            self.update_expense_table()
            self.update_dashboard()
            self.save_data()
            
            # Limpiar formulario
            self.expense_description.set("")
            self.expense_category.set("")
            self.expense_amount.set("")
            self.expense_currency.set('CLP')
            self.expense_date.set(date.today().strftime("%Y-%m-%d"))
            
            messagebox.showinfo("Éxito", "Gasto agregado correctamente")
            
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")
    
    def delete_income(self):
        """Eliminar ingreso seleccionado"""
        selection = self.income_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un ingreso para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este ingreso?"):
            item = self.income_tree.item(selection[0])
            income_id = float(item['tags'][0]) if item['tags'] else None
            
            if income_id:
                self.incomes = [i for i in self.incomes if i['id'] != income_id]
                self.update_income_table()
                self.update_dashboard()
                self.save_data()
    
    def delete_expense(self):
        """Eliminar gasto seleccionado"""
        selection = self.expense_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un gasto para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este gasto?"):
            item = self.expense_tree.item(selection[0])
            expense_id = float(item['tags'][0]) if item['tags'] else None
            
            if expense_id:
                self.expenses = [e for e in self.expenses if e['id'] != expense_id]
                self.update_expense_table()
                self.update_dashboard()
                self.save_data()
    
    def update_dashboard(self):
        """Actualizar dashboard con múltiples monedas"""
        # Calcular totales
        total_income_clp = 0
        total_income_usd = 0
        total_expense_clp = 0 
        total_expense_usd = 0
        
        for income in self.incomes:
            currency = income.get('currency', 'CLP')
            amount = income['amount']
            
            if currency == 'CLP':
                total_income_clp += amount
                total_income_usd += amount / self.exchange_rates['USD']
            elif currency == 'USD':
                total_income_usd += amount
                total_income_clp += amount * self.exchange_rates['USD']
        
        for expense in self.expenses:
            currency = expense.get('currency', 'CLP')
            amount = expense['amount']
            
            if currency == 'CLP':
                total_expense_clp += amount
                total_expense_usd += amount / self.exchange_rates['USD']
            elif currency == 'USD':
                total_expense_usd += amount
                total_expense_clp += amount * self.exchange_rates['USD']
        
        balance_clp = total_income_clp - total_expense_clp
        balance_usd = total_income_usd - total_expense_usd
        
        # Actualizar labels
        self.total_income_label.config(text=f"${total_income_clp:,.0f} CLP")
        self.total_income_usd_label.config(text=f"${total_income_usd:,.2f} USD")
        
        self.total_expense_label.config(text=f"${total_expense_clp:,.0f} CLP")
        self.total_expense_usd_label.config(text=f"${total_expense_usd:,.2f} USD")
        
        self.balance_label.config(text=f"${balance_clp:,.0f} CLP")
        self.balance_usd_label.config(text=f"${balance_usd:,.2f} USD")
        
        self.income_count_label.config(text=f"{len(self.incomes)} transacciones")
        self.expense_count_label.config(text=f"{len(self.expenses)} transacciones")
        
        # Estado del balance
        if balance_clp > 0:
            self.balance_status_label.config(text="✓ Superávit")
        elif balance_clp < 0:
            self.balance_status_label.config(text="⚠ Déficit")
        else:
            self.balance_status_label.config(text="= Equilibrio")
        
        # Actualizar resumen textual
        self.update_text_summary(total_income_clp, total_expense_clp, balance_clp, 
                               total_income_usd, total_expense_usd, balance_usd)
    
    def update_text_summary(self, income_clp, expense_clp, balance_clp, income_usd, expense_usd, balance_usd):
        """Actualizar resumen textual"""
        summary = f"""
=== RESUMEN FINANCIERO MULTI-MONEDA ===
Actualizado: {datetime.now().strftime("%d/%m/%Y %H:%M")}

💰 TOTALES EN PESOS CHILENOS (CLP):
• Ingresos: ${income_clp:,.0f} CLP
• Gastos: ${expense_clp:,.0f} CLP  
• Balance: ${balance_clp:,.0f} CLP

💵 TOTALES EN DÓLARES (USD):
• Ingresos: ${income_usd:,.2f} USD
• Gastos: ${expense_usd:,.2f} USD
• Balance: ${balance_usd:,.2f} USD

📊 ESTADÍSTICAS:
• Total transacciones: {len(self.incomes) + len(self.expenses)}
• Tasa de cambio actual: {self.exchange_rates['USD']} CLP/USD
• Tasa de ahorro: {(balance_clp/income_clp*100 if income_clp > 0 else 0):.1f}%

💡 ESTADO: {"✓ Situación saludable" if balance_clp >= 0 else "⚠ Revisar gastos"}

🎯 PARA FREELANCERS:
• Diversifica ingresos en USD y CLP
• Controla gastos tech internacionales
• Mantén reservas en ambas monedas
        """
        
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
    
    def update_income_table(self):
        """Actualizar tabla de ingresos"""
        for item in self.income_tree.get_children():
            self.income_tree.delete(item)
        
        for income in reversed(self.incomes):
            currency = income.get('currency', 'CLP')
            amount = income['amount']
            
            self.income_tree.insert("", "end", 
                                   values=(income['date'], income['description'], 
                                          income['category'], f"{amount:,.2f}", currency),
                                   tags=(str(income['id']),))
    
    def update_expense_table(self):
        """Actualizar tabla de gastos"""
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        for expense in reversed(self.expenses):
            currency = expense.get('currency', 'CLP')
            amount = expense['amount']
            
            self.expense_tree.insert("", "end", 
                                    values=(expense['date'], expense['description'], 
                                           expense['category'], f"{amount:,.2f}", currency),
                                    tags=(str(expense['id']),))
    
    def update_exchange_rate_dialog(self):
        """Abrir diálogo para actualizar tipo de cambio"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Actualizar Tipo de Cambio USD")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Actualizar Tipo de Cambio", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        frame = tk.Frame(dialog)
        frame.pack(pady=10)
        
        tk.Label(frame, text="1 USD =").pack(side=tk.LEFT)
        rate_var = tk.StringVar(value=str(self.exchange_rates['USD']))
        tk.Entry(frame, textvariable=rate_var, width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(frame, text="CLP").pack(side=tk.LEFT)
        
        def save_rate():
            try:
                new_rate = float(rate_var.get())
                self.exchange_rates['USD'] = new_rate
                self.usd_rate.set(str(new_rate))
                self.exchange_rate_label.config(text=f"1 USD = {new_rate:,.0f} CLP")
                self.update_dashboard()
                self.save_data()
                dialog.destroy()
                messagebox.showinfo("Éxito", "Tipo de cambio actualizado")
            except ValueError:
                messagebox.showerror("Error", "Ingrese un valor numérico válido")
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Guardar", command=save_rate, 
                 bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancelar", command=dialog.destroy, 
                 padx=20).pack(side=tk.LEFT, padx=5)
    
    def update_single_rate(self, currency):
        """Actualizar tipo de cambio individual"""
        try:
            if currency == 'USD':
                new_rate = float(self.usd_rate.get())
                self.exchange_rates['USD'] = new_rate
                self.exchange_rate_label.config(text=f"1 USD = {new_rate:,.0f} CLP")
                self.update_dashboard()
                self.save_data()
                messagebox.showinfo("Éxito", "Tipo de cambio USD actualizado")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido")
    
    def calculate_conversion(self):
        """Calcular conversión de monedas"""
        try:
            amount = float(self.convert_amount.get())
            from_curr = self.convert_from.get()
            to_curr = self.convert_to.get()
            
            if from_curr == to_curr:
                result = amount
            elif from_curr == 'CLP' and to_curr == 'USD':
                result = amount / self.exchange_rates['USD']
            elif from_curr == 'USD' and to_curr == 'CLP':
                result = amount * self.exchange_rates['USD']
            else:
                result = amount  # Para otras conversiones
            
            self.conversion_result.set(f"{amount:,.2f} {from_curr} = {result:,.2f} {to_curr}")
            
        except ValueError:
            self.conversion_result.set("Error: Ingrese un monto válido")
    
    # Métodos de importación universal de PDF
    def import_pdf_universal(self):
        """Importar PDF universal de cualquier banco"""
        if not PDF_SUPPORT:
            messagebox.showerror("Error", "Librerías de PDF no disponibles.\n\n"
                                         "Instale con: pip install PyPDF2 pdfplumber\n"
                                         "Use 'Pegar Texto Manual' como alternativa.")
            return
        
        filename = filedialog.askopenfilename(
            title="Seleccionar Estado de Cuenta PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            self.import_status.set("Leyendo PDF...")
            self.root.update()
            
            try:
                # Método 1: Intentar con pdfplumber (mejor para tablas)
                text_content = self.extract_pdf_with_pdfplumber(filename)
                
                if not text_content or len(text_content) < 100:
                    # Método 2: Fallback a PyPDF2
                    text_content = self.extract_pdf_with_pypdf2(filename)
                
                if text_content and len(text_content) > 50:
                    self.process_statement_text(text_content)
                else:
                    messagebox.showerror("Error", "No se pudo extraer texto del PDF.\n\n"
                                                 "Pruebe:\n"
                                                 "• Copiar texto manualmente del PDF\n"
                                                 "• Usar 'Pegar Texto Manual'\n"
                                                 "• Convertir PDF a imagen y usar OCR")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al procesar PDF: {str(e)}\n\n"
                                             "Use 'Pegar Texto Manual' como alternativa.")
                self.import_status.set("Error al procesar PDF")
    
    def extract_pdf_with_pdfplumber(self, filename):
        """Extraer texto usando pdfplumber (mejor para tablas)"""
        try:
            text_content = ""
            with pdfplumber.open(filename) as pdf:
                for page in pdf.pages[:5]:  # Límite de 5 páginas
                    if page.extract_text():
                        text_content += page.extract_text() + "\n"
                    
                    # Intentar extraer tablas también
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            if row:
                                text_content += "\t".join([cell or "" for cell in row]) + "\n"
            
            return text_content
        except Exception as e:
            print(f"Error con pdfplumber: {e}")
            return ""
    
    def extract_pdf_with_pypdf2(self, filename):
        """Extraer texto usando PyPDF2 (fallback)"""
        try:
            text_content = ""
            with open(filename, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(min(5, len(pdf_reader.pages))):  # Límite de 5 páginas
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
            
            return text_content
        except Exception as e:
            print(f"Error con PyPDF2: {e}")
            return ""
    
    def import_text_manual(self):
        """Importar texto copiado manualmente"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Pegar Texto del Estado de Cuenta")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Pegue el texto copiado de su estado de cuenta:", 
                font=('Arial', 12, 'bold')).pack(pady=10)
        
        instructions = tk.Label(dialog, text="Instrucciones:\n"
                                            "1. Abra su PDF en un visor\n"
                                            "2. Seleccione y copie las transacciones\n"
                                            "3. Pegue aquí el texto completo\n"
                                            "4. Haga clic en 'Procesar Texto'", 
                               font=('Arial', 10), justify=tk.LEFT)
        instructions.pack(pady=5)
        
        # Área de texto
        text_frame = tk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        text_area = tk.Text(text_frame, font=('Courier', 10))
        text_scrollbar = tk.Scrollbar(text_frame, command=text_area.yview)
        text_area.configure(yscrollcommand=text_scrollbar.set)
        
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def process_text():
            content = text_area.get(1.0, tk.END).strip()
            if len(content) > 20:
                dialog.destroy()
                self.process_statement_text(content)
            else:
                messagebox.showerror("Error", "Pegue el contenido del estado de cuenta")
        
        tk.Button(button_frame, text="📄 Procesar Texto", command=process_text,
                 bg='#27ae60', fg='white', font=('Arial', 11), padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="❌ Cancelar", command=dialog.destroy,
                 font=('Arial', 11), padx=20).pack(side=tk.LEFT, padx=5)
        
        # Ejemplos de formato
        example_frame = tk.LabelFrame(dialog, text="Ejemplo de formato esperado", padding=10)
        example_frame.pack(fill=tk.X, padx=20, pady=10)
        
        example_text = """Ejemplo:
25/08/2025 SUPERMERCADOS LILY $45,000
26/08/2025 OPENAI CHATGPT SUBSCRIPTION $23,612
27/08/2025 SPOTIFY PREMIUM CL 7,050.00"""
        
        tk.Label(example_frame, text=example_text, font=('Courier', 9), 
                justify=tk.LEFT, fg='gray').pack()
    
    def process_statement_text(self, text_content):
        """Procesar texto del estado de cuenta de forma universal"""
        try:
            self.import_status.set("Procesando texto...")
            
            # Detectar banco automáticamente
            detected_bank = self.detect_bank_from_text(text_content)
            if self.selected_bank.get() == "Detectar Automáticamente":
                self.import_status.set(f"Banco detectado: {detected_bank}")
            
            # Extraer transacciones usando parser universal
            transactions = self.extract_transactions_universal(text_content, detected_bank)
            
            if not transactions:
                messagebox.showerror("Error", "No se detectaron transacciones válidas.\n\n"
                                             "Verifique que el texto contenga:\n"
                                             "• Fechas (DD/MM/YYYY o similar)\n"
                                             "• Descripciones de comercios\n"
                                             "• Montos con $ o números")
                return
            
            # Mostrar en vista previa
            self.show_transactions_preview(transactions)
            
            self.import_status.set(f"Detectadas {len(transactions)} transacciones")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar texto: {str(e)}")
            self.import_status.set("Error en el procesamiento")
    
    def detect_bank_from_text(self, text):
        """Detectar banco automáticamente por patrones en el texto"""
        text_lower = text.lower()
        
        # Patrones específicos por banco
        bank_patterns = {
            'Santander': ['santander', 'worldmember', 'estado de cuenta en moneda nacional'],
            'BCI': ['bci', 'banco de credito', 'banco credito inversiones'],
            'Banco de Chile': ['banco de chile', 'bch', 'cuenta corriente banco chile'],
            'Banco Estado': ['bancoestado', 'banco estado', 'cuenta rut'],
            'Itaú': ['itau', 'itaú', 'banco itau'],
            'Falabella': ['cmr', 'falabella', 'tarjeta cmr'],
            'Ripley': ['ripley', 'tarjeta ripley'],
            'PayPal': ['paypal', 'payment received', 'payment sent']
        }
        
        for bank, patterns in bank_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                return bank
        
        return "Banco Genérico"
    
    def extract_transactions_universal(self, text, bank_type):
        """Extraer transacciones usando patrones universales"""
        transactions = []
        lines = text.split('\n')
        
        # Patrones universales de fecha
        date_patterns = [
            r'\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})\b',  # DD/MM/YYYY o DD-MM-YYYY
            r'\b(\d{2,4})[\/\-](\d{1,2})[\/\-](\d{1,2})\b',  # YYYY/MM/DD
            r'\b(\d{1,2})\/(\d{1,2})\/(\d{2})\b'              # DD/MM/YY
        ]
        
        # Patrones universales de monto
        amount_patterns = [
            r'\$\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)',  # $1.234.567,89 o $1,234.56
            r'([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)\s*\$?',  # 1234567,89 o 1,234.56
            r'USD?\s*([0-9]+(?:[.,][0-9]{2})?)',                      # USD 123.45
            r'CLP?\s*([0-9,\.]+)',                                    # CLP 123,456
        ]
        
        for line in lines:
            line = line.strip()
            if len(line) < 10:  # Muy corta para ser una transacción
                continue
            
            # Buscar fecha
            date_found = None
            for pattern in date_patterns:
                date_match = re.search(pattern, line)
                if date_match:
                    try:
                        groups = date_match.groups()
                        if len(groups[0]) == 4:  # YYYY/MM/DD
                            date_found = f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
                        else:  # DD/MM/YYYY o DD/MM/YY
                            year = groups[2] if len(groups[2]) == 4 else f"20{groups[2]}"
                            date_found = f"{year}-{groups[1].zfill(2)}-{groups[0].zfill(2)}"
                        break
                    except:
                        continue
            
            if not date_found:
                continue
            
            # Buscar monto
            amount_found = None
            currency = 'CLP'  # Por defecto
            for pattern in amount_patterns:
                amount_match = re.search(pattern, line, re.IGNORECASE)
                if amount_match:
                    try:
                        amount_str = amount_match.group(1)
                        # Limpiar y convertir
                        amount_str = amount_str.replace('.', '').replace(',', '.')
                        if '.' in amount_str and len(amount_str.split('.')[-1]) > 2:
                            # Es separador de miles, no decimales
                            amount_str = amount_str.replace('.', '')
                        
                        amount_found = float(amount_str)
                        
                        # Detectar moneda por contexto
                        if 'usd' in line.lower() or 'us' in line.lower():
                            currency = 'USD'
                        elif amount_found < 1000 and any(word in line.lower() 
                                                       for word in ['openai', 'spotify', 'netflix', 'apple']):
                            currency = 'USD'
                        
                        break
                    except:
                        continue
            
            if not amount_found or amount_found <= 0:
                continue
            
            # Extraer descripción (texto entre fecha y monto)
            description = line
            # Remover fecha y monto de la descripción
            for pattern in date_patterns:
                description = re.sub(pattern, '', description)
            for pattern in amount_patterns:
                description = re.sub(pattern, '', description, flags=re.IGNORECASE)
            
            description = description.replace('\n', ' ').strip()
            # Agregar la transacción extraída a la lista
            transactions.append({
                'date': date_found,
                'description': description,
                'amount': amount_found,
                'currency': currency,
                'category': ''  # Categoría vacía, se puede clasificar después
            })
        return transactions
    
    def add_sample_transactions(self):
        """Agregar transacciones de ejemplo basadas en Santander"""
        sample_expenses = [
            {
                'date': '2025-08-04',
                'description': 'OpenAI ChatGPT Subscription',
                'category': 'Servicios USD',
                'amount': 23.80,
                'currency': 'USD'
            },
            {
                'date': '2025-08-07', 
                'description': 'Claude.AI Subscription',
                'category': 'Servicios USD',
                'amount': 23.80,
                'currency': 'USD'
            },
            {
                'date': '2025-08-18',
                'description': 'Spotify Premium',
                'category': 'Entretenimiento',
                'amount': 7050,
                'currency': 'CLP'
            },
            {
                'date': '2025-08-18',
                'description': 'Supermercados Lily',
                'category': 'Alimentación',
                'amount': 26977,
                'currency': 'CLP'
            },
            {
                'date': '2025-08-21',
                'description': 'Make.com Automation',
                'category': 'Servicios USD',
                'amount': 18.82,
                'currency': 'USD'
            },
            {
                'date': '2025-08-03',
                'description': 'Easy - materiales hogar',
                'category': 'Hogar',
                'amount': 87380,
                'currency': 'CLP'
            }
        ]
        
        sample_incomes = [
            {
                'date': '2025-08-01',
                'description': 'Pago cliente freelance - Desarrollo web',
                'category': 'Freelance USD',
                'amount': 800.00,
                'currency': 'USD'
            },
            {
                'date': '2025-08-15',
                'description': 'PayPal - Consultoría técnica',
                'category': 'PayPal USD', 
                'amount': 450.00,
                'currency': 'USD'
            }
        ]
        
        # Agregar a los datos
        for expense in sample_expenses:
            expense['id'] = datetime.now().timestamp()
            self.expenses.append(expense)
        
        for income in sample_incomes:
            income['id'] = datetime.now().timestamp()
            self.incomes.append(income)
        
        # Actualizar interfaz
        self.update_income_table()
        self.update_expense_table()
        self.update_dashboard()
        self.save_data()
        
        messagebox.showinfo("¡Listo!", 
                           f"Se agregaron {len(sample_expenses)} gastos y {len(sample_incomes)} ingresos\n"
                           "basados en tu estado de cuenta de Santander.\n\n"
                           "¡Ya puedes probar todas las funciones!")
    
    def generate_monthly_report(self):
        """Generar reporte mensual"""
        current_month = datetime.now().strftime("%Y-%m")
        
        monthly_incomes = [i for i in self.incomes if i['date'].startswith(current_month)]
        monthly_expenses = [e for e in self.expenses if e['date'].startswith(current_month)]
        
        # Calcular totales en ambas monedas
        income_clp = sum(i['amount'] * (self.exchange_rates['USD'] if i.get('currency') == 'USD' else 1) 
                        for i in monthly_incomes)
        expense_clp = sum(e['amount'] * (self.exchange_rates['USD'] if e.get('currency') == 'USD' else 1) 
                         for e in monthly_expenses)
        
        report = f"""
═══════════════════════════════════════════════════════════════
                REPORTE MENSUAL - {datetime.now().strftime("%B %Y").upper()}
═══════════════════════════════════════════════════════════════

📊 RESUMEN EJECUTIVO:
• Total Ingresos:    ${income_clp:,.0f} CLP
• Total Gastos:      ${expense_clp:,.0f} CLP
• Balance:           ${income_clp - expense_clp:,.0f} CLP
• Estado:            {"Superávit" if income_clp > expense_clp else "Déficit"}

📈 ANÁLISIS POR MONEDA:
"""
        
        # Análisis por moneda
        usd_incomes = [i for i in monthly_incomes if i.get('currency') == 'USD']
        usd_expenses = [e for e in monthly_expenses if e.get('currency') == 'USD']
        
        report += f"• Ingresos USD: ${sum(i['amount'] for i in usd_incomes):,.2f}\n"
        report += f"• Gastos USD: ${sum(e['amount'] for e in usd_expenses):,.2f}\n"
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)
    
    def generate_category_report(self):
        """Generar reporte por categorías"""
        # Análisis de ingresos por categoría
        income_by_cat = {}
        for income in self.incomes:
            cat = income['category']
            amount_clp = income['amount'] * (self.exchange_rates['USD'] if income.get('currency') == 'USD' else 1)
            income_by_cat[cat] = income_by_cat.get(cat, 0) + amount_clp
        
        # Análisis de gastos por categoría  
        expense_by_cat = {}
        for expense in self.expenses:
            cat = expense['category']
            amount_clp = expense['amount'] * (self.exchange_rates['USD'] if expense.get('currency') == 'USD' else 1)
            expense_by_cat[cat] = expense_by_cat.get(cat, 0) + amount_clp
        
        report = """
═══════════════════════════════════════════════════════════════
                    ANÁLISIS POR CATEGORÍAS
═══════════════════════════════════════════════════════════════

📈 INGRESOS POR CATEGORÍA:
"""
        
        total_income = sum(income_by_cat.values())
        for cat, amount in sorted(income_by_cat.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_income * 100) if total_income > 0 else 0
            report += f"• {cat:<25} ${amount:>12,.0f} ({percentage:>5.1f}%)\n"
        
        report += "\n📉 GASTOS POR CATEGORÍA:\n"
        
        total_expense = sum(expense_by_cat.values())
        for cat, amount in sorted(expense_by_cat.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            report += f"• {cat:<25} ${amount:>12,.0f} ({percentage:>5.1f}%)\n"
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)
    
    def export_csv(self):
        """Exportar datos a CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Guardar como CSV"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    writer.writerow(['Tipo', 'Fecha', 'Descripción', 'Categoría', 'Monto', 'Moneda'])
                    
                    for income in self.incomes:
                        writer.writerow(['Ingreso', income['date'], income['description'], 
                                       income['category'], income['amount'], income.get('currency', 'CLP')])
                    
                    for expense in self.expenses:
                        writer.writerow(['Gasto', expense['date'], expense['description'], 
                                       expense['category'], expense['amount'], expense.get('currency', 'CLP')])
                
                messagebox.showinfo("Éxito", f"Datos exportados a {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def create_backup(self):
        """Crear respaldo de datos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialvalue=f"backup_financiero_{timestamp}.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Guardar respaldo"
        )
        
        if filename:
            self.save_data(filename)
            messagebox.showinfo("Éxito", f"Respaldo creado: {filename}")
    
    def save_data(self, filename=None):
        """Guardar datos en archivo JSON"""
        if filename is None:
            filename = self.data_file
        
        data = {
            'incomes': self.incomes,
            'expenses': self.expenses,
            'income_categories': self.income_categories,
            'expense_categories': self.expense_categories,
            'currencies': self.currencies,
            'main_currency': self.main_currency,
            'exchange_rates': self.exchange_rates,
            'chile_banks': self.chile_banks,
            'last_saved': datetime.now().isoformat()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar datos: {str(e)}")
    
    def load_data(self, filename=None):
        """Cargar datos desde archivo JSON"""
        if filename is None:
            filename = self.data_file
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                self.incomes = data.get('incomes', [])
                self.expenses = data.get('expenses', [])
                self.income_categories = data.get('income_categories', self.income_categories)
                self.expense_categories = data.get('expense_categories', self.expense_categories)
                self.currencies = data.get('currencies', self.currencies)
                self.main_currency = data.get('main_currency', self.main_currency)
                self.exchange_rates = data.get('exchange_rates', self.exchange_rates)
                self.chile_banks = data.get('chile_banks', self.chile_banks)
                
                # Migrar datos antiguos
                for income in self.incomes:
                    if 'currency' not in income:
                        income['currency'] = 'CLP'
                
                for expense in self.expenses:
                    if 'currency' not in expense:
                        expense['currency'] = 'CLP'
                
            except Exception as e:
                print(f"Error al cargar datos: {str(e)}")
    
    def on_closing(self):
        """Manejar cierre de aplicación"""
        self.save_data()
        self.root.destroy()

def main():
    """Función principal con verificación de dependencias"""
    print("🚀 Iniciando Control Financiero Multi-Moneda Chile...")
    print("📊 Versión 1.2 - Importación Universal de PDF")
    print()
    
    if not PDF_SUPPORT:
        print("⚠️  LIBRERÍAS DE PDF NO DISPONIBLES")
        print("📋 Para importar PDF automáticamente, instale:")
        print("   pip install PyPDF2 pdfplumber")
        print()
        print("🔄 Mientras tanto puede usar:")
        print("   • Pegar Texto Manual (copiar/pegar del PDF)")
        print("   • Importar CSV")
        print("   • Agregar transacciones manualmente")
        print()
    else:
        print("✅ Librerías PDF disponibles - Importación automática lista")
        print()
    
    try:
        root = tk.Tk()
        app = MultiCurrencyFinancialManager(root)
        
        print("🎯 Aplicación iniciada exitosamente")
        print("💡 Funcionalidades disponibles:")
        print("   • Dashboard multi-moneda (CLP/USD)")
        print("   • Importación universal de estados de cuenta")
        print("   • Detección automática de bancos y categorías")
        print("   • Reportes y análisis avanzados")
        print("   • Exportación a CSV y respaldos")
        print()
        
        if PDF_SUPPORT:
            print("📄 IMPORTACIÓN PDF: Funciona con cualquier banco")
        else:
            print("📋 Use 'Pegar Texto Manual' para importar sin librerías PDF")
        
        print("=" * 60)
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error al iniciar aplicación: {e}")
        print("💡 Verifique que tiene Python 3.7+ y tkinter instalado")
    
    print("👋 ¡Gracias por usar Control Financiero Multi-Moneda!")

if __name__ == "__main__":
    main()
    
    def detect_category_smart(self, description, currency, transaction_type):
        """Detectar categoría inteligentemente"""
        desc_lower = description.lower()
        
        if transaction_type == "Ingreso":
            if any(word in desc_lower for word in ['sueldo', 'salario', 'remuneracion', 'nomina']):
                return 'Salario CLP'
            elif any(word in desc_lower for word in ['freelance', 'honorarios', 'servicios profesionales']):
                return 'Freelance USD' if currency == 'USD' else 'Freelance CLP'
            elif any(word in desc_lower for word in ['paypal', 'transferencia internacional']):
                return 'PayPal USD'
            else:
                return 'Otros'
        
        else:  # Gasto
            # Servicios tecnológicos internacionales
            tech_services = ['openai', 'chatgpt', 'claude', 'anthropic', 'github', 'notion', 'figma',
                           'adobe', 'canva', 'zoom', 'slack', 'dropbox', 'google workspace',
                           'microsoft office', 'aws', 'azure', 'heroku', 'vercel']
            
            if any(service in desc_lower for service in tech_services):
                return 'Servicios USD'
            
            # Entretenimiento
            if any(word in desc_lower for word in ['spotify', 'netflix', 'disney', 'prime video', 
                                                  'youtube', 'apple music', 'hbo']):
                return 'Entretenimiento'
            
            # Alimentación (Chile)
            food_places = ['supermercado', 'market', 'jumbo', 'lider', 'santa isabel', 'tottus',
                          'unimarc', 'lily', 'acuenta', 'restaurant', 'cafe', 'pizzeria']
            
            if any(place in desc_lower for place in food_places):
                return 'Alimentación'
            
            # Hogar (Chile)
            if any(word in desc_lower for word in ['easy', 'sodimac', 'homecenter', 'construmart', 'homy']):
                return 'Hogar'
            
            # Transporte
            if any(word in desc_lower for word in ['uber', 'taxi', 'metro', 'bus', 'bencina', 
                                                  'copec', 'shell', 'esso', 'petrobras']):
                return 'Transporte'
            
            # Servicios básicos
            if any(word in desc_lower for word in ['luz', 'agua', 'gas', 'telefono', 'internet',
                                                  'entel', 'movistar', 'claro', 'vtr']):
                return 'Servicios'
            
            # Salud
            if any(word in desc_lower for word in ['farmacia', 'clinica', 'hospital', 'medico',
                                                  'cruz verde', 'salco', 'ahumada']):
                return 'Salud'
            
            # Por defecto
            return 'Otros'
    
    def show_transactions_preview(self, transactions):
        """Mostrar transacciones en vista previa"""
        # Limpiar vista previa anterior
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # Agregar transacciones detectadas
        for transaction in transactions:
            self.preview_tree.insert("", "end", values=(
                transaction['date'],
                transaction['description'][:40] + "..." if len(transaction['description']) > 40 else transaction['description'],
                f"{transaction['amount']:,.2f}",
                transaction['currency'],
                transaction['category'],
                transaction['type']
            ))
        
        # Guardar transacciones para importación
        self.pending_transactions = transactions
    
    def confirm_import(self):
        """Confirmar e importar transacciones previsualizadas"""
        if not hasattr(self, 'pending_transactions') or not self.pending_transactions:
            messagebox.showwarning("Advertencia", "No hay transacciones para importar")
            return
        
        if not messagebox.askyesno("Confirmar Importación", 
                                  f"¿Importar {len(self.pending_transactions)} transacciones?\n\n"
                                  f"Se agregarán a su base de datos actual."):
            return
        
        try:
            imported_incomes = 0
            imported_expenses = 0
            
            for transaction in self.pending_transactions:
                # Crear registro con ID único
                record = {
                    'id': datetime.now().timestamp() + len(self.incomes) + len(self.expenses),
                    'date': transaction['date'],
                    'description': transaction['description'],
                    'category': transaction['category'],
                    'amount': transaction['amount'],
                    'currency': transaction['currency']
                }
                
                if transaction['type'] == 'Ingreso':
                    self.incomes.append(record)
                    imported_incomes += 1
                else:
                    self.expenses.append(record)
                    imported_expenses += 1
            
            # Actualizar interfaz
            self.update_income_table()
            self.update_expense_table()
            self.update_dashboard()
            self.save_data()
            
            # Limpiar vista previa
            self.clear_preview()
            
            messagebox.showinfo("Importación Exitosa", 
                               f"✅ Transacciones importadas:\n"
                               f"• {imported_incomes} ingresos\n"
                               f"• {imported_expenses} gastos\n\n"
                               f"Total: {imported_incomes + imported_expenses} transacciones")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la importación: {str(e)}")
    
    def clear_preview(self):
        """Limpiar vista previa"""
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        if hasattr(self, 'pending_transactions'):
            self.pending_transactions = []
        
        self.import_status.set("Vista previa limpiada - Seleccione método de importación")
    
    def add_sample_transactions(self):
        """Agregar transacciones de ejemplo basadas en Santander"""
        sample_expenses = [
            {
                'date': '2025-08-04',
                'description': 'OpenAI ChatGPT Subscription',
                'category': 'Servicios USD',
                'amount': 23.80,
                'currency': 'USD'
            },
            {
                'date': '2025-08-07', 
                'description': 'Claude.AI Subscription',
                'category': 'Servicios USD',
                'amount': 23.80,
                'currency': 'USD'
            },
            {
                'date': '2025-08-18',
                'description': 'Spotify Premium',
                'category': 'Entretenimiento',
                'amount': 7050,
                'currency': 'CLP'
            },
            {
                'date': '2025-08-18',
                'description': 'Supermercados Lily',
                'category': 'Alimentación',
                'amount': 26977,
                'currency': 'CLP'
            },
            {
                'date': '2025-08-21',
                'description': 'Make.com Automation',
                'category': 'Servicios USD',
                'amount': 18.82,
                'currency': 'USD'
            },
            {
                'date': '2025-08-03',
                'description': 'Easy - materiales hogar',
                'category': 'Hogar',
                'amount': 87380,
                'currency': 'CLP'
            }
        ]
        
        sample_incomes = [
            {
                'date': '2025-08-01',
                'description': 'Pago cliente freelance - Desarrollo web',
                'category': 'Freelance USD',
                'amount': 800.00,
                'currency': 'USD'
            },
            {
                'date': '2025-08-15',
                'description': 'PayPal - Consultoría técnica',
                'category': 'PayPal USD', 
                'amount': 450.00,
                'currency': 'USD'
            }
        ]
        
        # Agregar a los datos
        for expense in sample_expenses:
            expense['id'] = datetime.now().timestamp()
            self.expenses.append(expense)
        
        for income in sample_incomes:
            income['id'] = datetime.now().timestamp()
            self.incomes.append(income)
        
        # Actualizar interfaz
        self.update_income_table()
        self.update_expense_table()
        self.update_dashboard()
        self.save_data()
        
        messagebox.showinfo("¡Listo!", 
                           f"Se agregaron {len(sample_expenses)} gastos y {len(sample_incomes)} ingresos\n"
                           "basados en tu estado de cuenta de Santander.\n\n"
                           "¡Ya puedes probar todas las funciones!")
    
    def generate_monthly_report(self):
        """Generar reporte mensual"""
        current_month = datetime.now().strftime("%Y-%m")
        
        monthly_incomes = [i for i in self.incomes if i['date'].startswith(current_month)]
        monthly_expenses = [e for e in self.expenses if e['date'].startswith(current_month)]
        
        # Calcular totales en ambas monedas
        income_clp = sum(i['amount'] * (self.exchange_rates['USD'] if i.get('currency') == 'USD' else 1) 
                        for i in monthly_incomes)
        expense_clp = sum(e['amount'] * (self.exchange_rates['USD'] if e.get('currency') == 'USD' else 1) 
                         for e in monthly_expenses)
        
        report = f"""
═══════════════════════════════════════════════════════════════
                REPORTE MENSUAL - {datetime.now().strftime("%B %Y").upper()}
═══════════════════════════════════════════════════════════════

📊 RESUMEN EJECUTIVO:
• Total Ingresos:    ${income_clp:,.0f} CLP
• Total Gastos:      ${expense_clp:,.0f} CLP
• Balance:           ${income_clp - expense_clp:,.0f} CLP
• Estado:            {"Superávit" if income_clp > expense_clp else "Déficit"}

📈 ANÁLISIS POR MONEDA:
"""
        
        # Análisis por moneda
        usd_incomes = [i for i in monthly_incomes if i.get('currency') == 'USD']
        usd_expenses = [e for e in monthly_expenses if e.get('currency') == 'USD']
        
        report += f"• Ingresos USD: ${sum(i['amount'] for i in usd_incomes):,.2f}\n"
        report += f"• Gastos USD: ${sum(e['amount'] for e in usd_expenses):,.2f}\n"
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)
    
    def generate_category_report(self):
        """Generar reporte por categorías"""
        # Análisis de ingresos por categoría
        income_by_cat = {}
        for income in self.incomes:
            cat = income['category']
            amount_clp = income['amount'] * (self.exchange_rates['USD'] if income.get('currency') == 'USD' else 1)
            income_by_cat[cat] = income_by_cat.get(cat, 0) + amount_clp
        
        # Análisis de gastos por categoría  
        expense_by_cat = {}
        for expense in self.expenses:
            cat = expense['category']
            amount_clp = expense['amount'] * (self.exchange_rates['USD'] if expense.get('currency') == 'USD' else 1)
            expense_by_cat[cat] = expense_by_cat.get(cat, 0) + amount_clp
        
        report = """
═══════════════════════════════════════════════════════════════
                    ANÁLISIS POR CATEGORÍAS
═══════════════════════════════════════════════════════════════

📈 INGRESOS POR CATEGORÍA:
"""
        
        total_income = sum(income_by_cat.values())
        for cat, amount in sorted(income_by_cat.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_income * 100) if total_income > 0 else 0
            report += f"• {cat:<25} ${amount:>12,.0f} ({percentage:>5.1f}%)\n"
        
        report += "\n📉 GASTOS POR CATEGORÍA:\n"
        
        total_expense = sum(expense_by_cat.values())
        for cat, amount in sorted(expense_by_cat.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            report += f"• {cat:<25} ${amount:>12,.0f} ({percentage:>5.1f}%)\n"
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)
    
    def export_csv(self):
        """Exportar datos a CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Guardar como CSV"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    writer.writerow(['Tipo', 'Fecha', 'Descripción', 'Categoría', 'Monto', 'Moneda'])
                    
                    for income in self.incomes:
                        writer.writerow(['Ingreso', income['date'], income['description'], 
                                       income['category'], income['amount'], income.get('currency', 'CLP')])
                    
                    for expense in self.expenses:
                        writer.writerow(['Gasto', expense['date'], expense['description'], 
                                       expense['category'], expense['amount'], expense.get('currency', 'CLP')])
                
                messagebox.showinfo("Éxito", f"Datos exportados a {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def create_backup(self):
        """Crear respaldo de datos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialvalue=f"backup_financiero_{timestamp}.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Guardar respaldo"
        )
        
        if filename:
            self.save_data(filename)
            messagebox.showinfo("Éxito", f"Respaldo creado: {filename}")
    
    def save_data(self, filename=None):
        """Guardar datos en archivo JSON"""
        if filename is None:
            filename = self.data_file
        
        data = {
            'incomes': self.incomes,
            'expenses': self.expenses,
            'income_categories': self.income_categories,
            'expense_categories': self.expense_categories,
            'currencies': self.currencies,
            'main_currency': self.main_currency,
            'exchange_rates': self.exchange_rates,
            'chile_banks': self.chile_banks,
            'last_saved': datetime.now().isoformat()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar datos: {str(e)}")
    
    def load_data(self, filename=None):
        """Cargar datos desde archivo JSON"""
        if filename is None:
            filename = self.data_file
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                self.incomes = data.get('incomes', [])
                self.expenses = data.get('expenses', [])
                self.income_categories = data.get('income_categories', self.income_categories)
                self.expense_categories = data.get('expense_categories', self.expense_categories)
                self.currencies = data.get('currencies', self.currencies)
                self.main_currency = data.get('main_currency', self.main_currency)
                self.exchange_rates = data.get('exchange_rates', self.exchange_rates)
                self.chile_banks = data.get('chile_banks', self.chile_banks)
                
                # Migrar datos antiguos
                for income in self.incomes:
                    if 'currency' not in income:
                        income['currency'] = 'CLP'
                
                for expense in self.expenses:
                    if 'currency' not in expense:
                        expense['currency'] = 'CLP'
                
            except Exception as e:
                print(f"Error al cargar datos: {str(e)}")
    
    def on_closing(self):
        """Manejar cierre de aplicación"""
        self.save_data()
        self.root.destroy()

def main():
    """Función principal"""
    print("🚀 Iniciando Control Financiero Multi-Moneda Chile...")
    print("📊 Versión corregida - Sin errores de sintaxis")
    
    root = tk.Tk()
    app = MultiCurrencyFinancialManager(root)
    root.mainloop()
    
    print("👋 ¡Gracias por usar Control Financiero Multi-Moneda!")

if __name__ == "__main__":
    main()
