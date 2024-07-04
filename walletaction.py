import time
import tkinter as tk
import requests
from tkinter import ttk, messagebox
import mainscreen  # Ana ekran modülü
from delegate import delegate_to_validator  # delegate.py'den fonksiyonu import et
from transfer import transfer_token  # transfer.py'den transfer_token fonksiyonunu import et
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

valid_adr = None

def clear_content(root):
    for widget in root.winfo_children():
        widget.destroy()

def copy_to_clipboard(root, content):
    root.clipboard_clear()
    root.clipboard_append(content)
    root.update()
    messagebox.showinfo("Copy Success", f"{content} Copied!")

def fetch_balances(address):
    url = f"https://initia-api.coinsspor.com/cosmos/bank/v1beta1/spendable_balances/{address}"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        data = response.json()
        balances = data.get('balances', [])
        uinit_balance = 0
        gas_balance = 0
        for balance in balances:
            if balance['denom'] == 'uinit':
                uinit_balance = int(balance['amount'])
            elif balance['denom'].startswith('move/944'):
                gas_balance = int(balance['amount'])
        return {'uinit': uinit_balance, 'gas': gas_balance}
    else:
        print("Failed to fetch balances:", response.status_code)
        return {'uinit': 0, 'gas': 0}

def fetch_validators():
    url = "https://initia-api.coinsspor.com/initia/mstaking/v1/validators?pagination.limit=300&status=BOND_STATUS_BONDED"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        validators = response.json().get('validators', [])
        return [(v['description']['moniker'] + ' (' + f"{float(v['commission']['commission_rates']['rate']) * 100:.1f}%)", v['operator_address']) for v in validators]
    else:
        print("Failed to fetch validators:", response.status_code)
        return []

def format_balance(amount):
    return f"{float(amount) / 10**6:.6f}"

def update_max_amount(entry, initia_address, root):
    current_balances = fetch_balances(initia_address)  # Her seferinde güncel bakiyeleri çek
    total_balance_wei = current_balances['uinit']
    total_balance_initia = total_balance_wei / 1e6
    max_transferable_initia = max(0, total_balance_initia - 1.5)

    entry.delete(0, tk.END)
    if max_transferable_initia > 0:
        entry.insert(0, f"{max_transferable_initia:.6f}")
    else:
        entry.insert(0, "0.000000")
        messagebox.showinfo("Insufficient Balance", "You need at least 1.5 INITIA more in your wallet to perform transactions.", parent=root)

def update_balance(balance_label, address):
    balances = fetch_balances(address)
    uinit_balance = format_balance(balances['uinit'])
    gas_balance = format_balance(balances['gas'])
    balance_str = f"Balances: {uinit_balance} init, {gas_balance} gas"
    balance_label.config(text=balance_str)

def perform_transfer(entry, target_address_entry, initia_address, private_key, root, balance_label):
    try:
        amount_initia = float(entry.get())  # Kullanıcıdan alınan miktarı INITIA cinsinden al
        amount_wei = int(amount_initia * 10**6)  # Wei'ye çevir
    except ValueError:
        messagebox.showerror("Error", "Invalid amount entered. Please enter a numeric value.", parent=root)
        return

    current_balances = fetch_balances(initia_address)  # Güncel bakiyeleri çek
    total_balance_wei = current_balances['uinit']

    if amount_wei > total_balance_wei:
        messagebox.showwarning("Warning", "Insufficient funds for this transaction.", parent=root)
        return

    if total_balance_wei - amount_wei < 1.5 * 10**6:
        messagebox.showwarning("Warning", "Insufficient balance after transfer. Minimum balance of 1.5 INITIA required.", parent=root)
        return

    # Tüm kontroller geçilirse, transfer işlemini doğru sıra ile parametreleri vererek gerçekleştir
    success = transfer_token(target_address_entry.get(), amount_wei, private_key, initia_address)
    print("sonuc", success)

    if success and success.get('tx_response', {}).get('code') == 0:
        messagebox.showinfo("Success", "Transfer completed successfully!", parent=root)
        time.sleep(5)
        update_balance(balance_label, initia_address)
    else:
        error_message = success.get('tx_response', {}).get('raw_log', 'Unknown error occurred.')
        messagebox.showerror("Error", f"Transfer failed: {error_message}", parent=root)

def perform_delegate(valid_adr, entry, initia_address, private_key, root, balance_label):
    try:
        amount_initia = float(entry.get())  # Kullanıcıdan alınan miktarı INITIA cinsinden al
        amount_wei = int(amount_initia * 10**6)  # Wei'ye çevir
    except ValueError:
        messagebox.showerror("Error", "Invalid amount entered. Please enter a numeric value.", parent=root)
        return

    current_balances = fetch_balances(initia_address)  # Güncel bakiyeleri çek
    total_balance_wei = current_balances['uinit']

    if amount_wei > total_balance_wei:
        messagebox.showwarning("Warning", "Insufficient funds for this transaction.", parent=root)
        return

    if total_balance_wei - amount_wei < 1.5 * 10**6:
        messagebox.showwarning("Warning", "Insufficient balance after transfer. Minimum balance of 1.5 INITIA required.", parent=root)
        return

    # Tüm kontroller geçilirse, delegate işlemini doğru sıra ile parametreleri vererek gerçekleştir
    success = delegate_to_validator(private_key, initia_address, valid_adr, amount_wei)
    print("sonuc", success)
    if success and success.get('tx_response', {}).get('code') == 0:
        messagebox.showinfo("Success", "Delegation completed successfully!", parent=root)
        time.sleep(5)
        update_balance(balance_label, initia_address)
    else:
        error_message = success.get('tx_response', {}).get('raw_log', 'Unknown error occurred.')
        messagebox.showerror("Error", f"Delegation failed: {error_message}", parent=root)

def wallet_actions(root, initia_address, private_key):
    clear_content(root)
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background='#000')
    style.configure('TButton', background='#1E90FF', foreground='white', font=('Arial', 12))
    style.configure('TLabel', background='#000', foreground='white', font=('Arial', 12))
    style.configure('TEntry', fieldbackground='#D9EAF7', foreground='#000', font=('Arial', 12))
    style.configure('TCombobox', fieldbackground='#D9EAF7', foreground='#000', font=('Arial', 12))
    style.map('TCombobox', fieldbackground=[('readonly', '#D9EAF7')])
    style = ttk.Style()
    style.configure('Small.TButton', font=('Helvetica', 8), padding=2)

    frame = ttk.Frame(root, style='TFrame')
    frame.pack(fill='both', expand=True)
    title_label = ttk.Label(frame, text="Wallet Information", font=('Arial', 20), background="#4C72B0", foreground="white", anchor="center", padding=(0, 10))
    title_label.pack(fill='x')

    panel1 = ttk.Frame(frame, style='TFrame')
    panel1.pack(fill='x', pady=10)

    address_frame = ttk.Frame(panel1, style='TFrame')
    address_frame.pack(fill='x', pady=5)
    ttk.Label(address_frame, text="Initia Address:", font=('Arial', 12, 'bold', 'underline'), foreground='orange').pack(side='left', padx=(10, 5))
    address_label = ttk.Label(address_frame, text=initia_address, font=('Arial', 12, 'bold'))
    address_label.pack(side='left')
    address_copy_button = ttk.Button(address_frame, text="Copy", style='Small.TButton', command=lambda: copy_to_clipboard(root, initia_address))
    address_copy_button.pack(side='left', padx=5)

    panel3 = ttk.Frame(frame, style='TFrame')
    panel3.pack(fill='both', expand=True, pady=(20, 10))

    tab_control = ttk.Notebook(frame, style='TNotebook')
    tab_transfer = ttk.Frame(tab_control, style='TFrame')
    tab_delegate = ttk.Frame(tab_control, style='TFrame')
    tab_control.add(tab_transfer, text='INITIA Transfer')
    tab_control.add(tab_delegate, text='Delegate')

    validators = fetch_validators()
    setup_tab(tab_transfer, "Transfer", validators, initia_address, private_key, root)
    setup_tab(tab_delegate, "Delegate", validators, initia_address, private_key, root)

    global balance_label
    balance_label = ttk.Label(frame, text="Please click 'Update Balance' to view balance", style='TLabel')
    balance_label.pack(fill='x', pady=(10, 10))
    update_balance(balance_label, initia_address)

    update_balance_button = ttk.Button(frame, text="Update Balance", command=lambda: update_balance(balance_label, initia_address))
    update_balance_button.pack(fill='x', pady=(10, 10))
    tab_control.pack(expand=1, fill='both', pady=(0, 10))

    logout_button = ttk.Button(frame, text="Logout", command=lambda: mainscreen.show_main_screen(root))
    logout_button.pack(fill='x', pady=(10, 20))

def paste_to_entry(entry_widget, root):
    try:
        content = root.clipboard_get()
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, content)
    except tk.TclError:
        print("Nothing to paste")

def setup_tab(tab, action_type, validators, initia_address, private_key, root):
    if action_type == "Transfer":
        current_balances = fetch_balances(initia_address)

        ttk.Label(tab, text='Target Wallet Address:').pack(pady=(10, 0))

        address_frame = ttk.Frame(tab)
        address_frame.pack(pady=(0, 10))

        target_address_entry = ttk.Entry(address_frame, width=60)
        target_address_entry.pack(side=tk.LEFT, padx=(0, 5))

        style = ttk.Style()
        style.configure('Small.TButton', font=('Helvetica', 8), padding=2)

        paste_button = ttk.Button(address_frame, text="Paste", style='Small.TButton', command=lambda: paste_to_entry(target_address_entry, root))
        paste_button.pack(side=tk.LEFT)

        ttk.Label(tab, text='Amount:').pack(pady=(10, 0))
        amount_entry_transfer = ttk.Entry(tab, width=20)
        amount_entry_transfer.pack(pady=(0, 10))

        max_button = ttk.Button(tab, text="Max", command=lambda: update_max_amount(amount_entry_transfer, initia_address, root))
        max_button.pack(pady=(5, 10))

        transfer_button = ttk.Button(tab, text='Transfer', command=lambda: perform_transfer(amount_entry_transfer, target_address_entry, initia_address, private_key, root, balance_label))
        transfer_button.pack(pady=(10, 20))

    elif action_type == "Delegate":
        ttk.Label(tab, text='Validator:').pack(pady=(10, 0))
        validator_combobox = ttk.Combobox(tab, values=[v[0] for v in validators], state='readonly', width=40)
        validator_combobox.pack(pady=(0, 10))
        validator_combobox.bind('<<ComboboxSelected>>', lambda event: on_validator_selected(event, validators, validator_combobox, initia_address, private_key))

        ttk.Label(tab, text='Amount:').pack(pady=(10, 0))
        amount_entry_delegate = ttk.Entry(tab, width=20)
        amount_entry_delegate.pack(pady=(0, 10))

        max_button = ttk.Button(tab, text="Max", command=lambda: update_max_amount(amount_entry_delegate, initia_address, root))
        max_button.pack(pady=(5, 10))

        delegate_button = ttk.Button(tab, text='Delegate', command=lambda: perform_delegate(valid_adr, amount_entry_delegate, initia_address, private_key, root, balance_label))
        delegate_button.pack(pady=(10, 20))

def on_validator_selected(event, validators, combobox, initia_address, private_key):
    selected_index = combobox.current()
    target_validator_address = validators[selected_index][1]
    print(f"Selected validator address: {target_validator_address}")
    global valid_adr
    valid_adr = target_validator_address

   
