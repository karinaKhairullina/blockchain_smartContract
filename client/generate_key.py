from eth_account import Account


def main():
    acct = Account.create()
    print("PRIVATE_KEY=", acct._private_key.hex())


if __name__ == "__main__":
    main()
