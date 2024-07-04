# Initia Desktop Wallet

Initia Desktop Wallet is a desktop application that allows users to create new wallets, log in to existing wallets, perform token transfers, and delegate tokens on the Initia network.

![image](https://github.com/coinsspor/initia-desktop-wallet/assets/38142283/d75def76-96bc-43ab-8dc9-3c5daca9567e) 

![image](https://github.com/coinsspor/initia-desktop-wallet/assets/38142283/763c8951-7ee9-4945-9a7d-c8e632db5021)

![image](https://github.com/coinsspor/initia-desktop-wallet/assets/38142283/9dbba19e-b4a7-4132-af78-486541a85df9)






## Features

- **Create New Wallet:** Users can create a new Initia wallet.
- **Log In to Existing Wallet:** Users can log in to an existing Initia wallet using their private key.
- **Token Transfer:** Users can transfer tokens from their wallet to another wallet.
- **Delegation:** Users can delegate their tokens to a chosen validator.

## Files and Their Functions

### 1. `main.py`
The entry point of the application, responsible for creating the main window and initializing the main screen.

### 2. `mainscreen.py`
Contains functions for the main screen, providing options for creating a new wallet or logging in to an existing wallet.

### 3. `newwallet.py`
Contains functions for generating a new Initia wallet and displaying wallet information to the user, including private key and Initia address.

### 4. `login_prvtkey.py`
Allows users to log in to an existing wallet using their private key. It includes validation and processing of the provided private key.

### 5. `walletaction.py`
Contains functions for managing wallet actions, including:
- **Fetching balances:** Retrieve the balance of tokens in the wallet.
- **Token transfers:** Perform token transfer operations.
- **Delegations:** Perform token delegation operations to a chosen validator.

### 6. `transfer.py`
Contains functions for performing token transfer operations. It includes creating and signing transactions and broadcasting them to the Initia network.

### 7. `delegate.py`
Contains functions for performing delegation operations. It includes creating and signing delegation transactions and broadcasting them to the Initia network.

## Quick Start Guide

### Prerequisites
- Python 3.x
- Required Python libraries: `tkinter`, `requests`, `bech32`, `cosmospy`, `ecdsa`, `google.protobuf`

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/initia-desktop-wallet.git
    cd initia-desktop-wallet
    ```

2. Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

### Usage
1. Run the application:
    ```bash
    python main.py
    ```

2. **Main Screen:**
    - Choose to create a new wallet or log in with a private key.

3. **Create a New Wallet:**
    - A new wallet will be generated, displaying the private key and Initia address.
    - You can copy the wallet information and proceed to wallet actions (transfer and delegate).

4. **Log In to Existing Wallet:**
    - Enter your private key to log in to your existing wallet.
    - Once logged in, you can perform wallet actions (transfer and delegate).

5. **Wallet Actions:**
    - **Transfer:** Enter the target wallet address and amount to transfer tokens.
    - **Delegate:** Select a validator and enter the amount to delegate tokens.

## Contributions
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

