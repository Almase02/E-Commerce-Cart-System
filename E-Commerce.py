import re
from threading import Timer
import pandas as pd
import random

Shopping = {
    "Kitkat": {"quantity": 1, "price": 120},
    "Perk": {"quantity": 1, "price": 80},
    "Diary_milk": {"quantity": 1, "price": 200},
    "Celebrations": {"quantity": 1, "price": 110},
    "Shots": {"quantity": 1, "price": 104},
    "Kisses": {"quantity": 1, "price": 300},
    "Snickers": {"quantity": 1, "price": 530},
    "Ferrero_rocher": {"quantity": 1, "price": 500},
    "Dark_chocolate": {"quantity": 1, "price": 100},
    "Fuse": {"quantity": 1, "price": 50},
    "Munch": {"quantity": 1, "price": 160}
}


flash_sale_items = {
    "Snickers": {"flash_price": 200, "duration": 1300},
    "Fuse": {"flash_price": 30, "duration": 30}
}
flash_sale_active = {}

shared_carts=[]
cart = {}
Login_ids = {}
Budget = {}
budget=None


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def insert_at_end(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node

    def print_cart_items(self):
        current_node = self.head
        cart_items = {}
        while current_node:
            item_data = list(current_node.data.items())[0]
            item_name, details = item_data
            cart_items[item_name] = {"quantity": details["quantity"], "price": details["price"]}
            current_node = current_node.next
        return cart_items

    def node_present_or_not(self, item_name):
        current_node = self.head
        while current_node:
            if item_name in current_node.data:
                return current_node.data[item_name]
            current_node = current_node.next
        return False

    def delete_node(self, key):
        current_node = self.head
        if current_node and current_node.data == key:
            self.head = current_node.next
            return
        prev = None
        while current_node and current_node.data != key:
            prev = current_node
            current_node = current_node.next
        if current_node:
            prev.next = current_node.next


def start_flash_sale():
    for item, sale_info in flash_sale_items.items():
        flash_sale_active[item] = True
        Timer(sale_info["duration"], end_flash_sale, [item]).start()

def end_flash_sale(item):
    flash_sale_active[item] = False
    print(f"The flash sale for {item} has ended. Regular pricing will now apply.")


def get_price(item_name):
    if item_name in flash_sale_items and flash_sale_active.get(item_name, False):
        return flash_sale_items[item_name]["flash_price"]
    return Shopping[item_name]["price"]


def display_available_items():
    print("Available items for shopping (flash sale items marked with *):")
    Shopping_with_serial = {f"{i+1}. {k}": v for i, (k, v) in enumerate(Shopping.items())}
    for item, details in Shopping_with_serial.items():
        print(f"{item}: {details}")

def display_flash_sale_items():
    print("Flash sale items:")
    for item, sale_info in flash_sale_items.items():
        if flash_sale_active.get(item, False):
            print(f"{item}: Flash Sale Price - {sale_info['flash_price']}")


def set_budget(user_id):
    try:
        budget = float(input("Enter your budget limit: "))
        Budget[user_id] = budget
        print(f"Budget set to {budget}.")
    except ValueError:
        print("Invalid input. Please enter a valid budget.")


def add_items_to_cart(user_id):
    linked_list = get_cart_for_user(user_id)
    current_total = sum(item["price"] for item in linked_list.print_cart_items().values())
    
    while True:
        try:
            item_numbers = input("Enter the numbers of the items to add (comma-separated or 0 to stop): ")
            if item_numbers == "0":
                break

            item_numbers = [int(num.strip()) for num in item_numbers.split(",")]

            for item_num in item_numbers:
                item_name = get_item_by_number(item_num)
                if item_name is None:
                    continue

                quantity = int(input(f"Enter the quantity for {item_name}: "))
                price_per_unit = get_price(item_name)
                total_item_price = price_per_unit * quantity

                
                if Budget.get(user_id) is not None and (current_total + total_item_price) > Budget[user_id]:
                    print(f"Adding {item_name} would exceed your budget by {current_total + total_item_price - Budget[user_id]}.")
                    extend_budget = input("Do you want to extend your budget? (yes/no): ").strip().lower()
                    if extend_budget == "yes":
                        new_budget = float(input("Enter the new budget: "))
                        Budget[user_id] = new_budget
                        print(f"Budget extended to {new_budget}.")
                    else:
                        print(f"{item_name} not added to the cart due to budget restriction.")
                        continue

                nodepresentornot = linked_list.node_present_or_not(item_name)
                if not nodepresentornot:
                    item_data = {"quantity": quantity, "price": total_item_price}
                    linked_list.insert_at_end({item_name: item_data})
                    current_total += total_item_price
                else:
                    nodepresentornot["quantity"] += quantity
                    nodepresentornot["price"] += total_item_price
                    current_total += total_item_price

                print(f"Added {quantity} of {item_name}. Current total: {current_total}")

        except ValueError:
            print("Invalid input. Please enter valid item numbers and quantities.")

def remove_items_from_cart(user_id):
    linked_list = get_cart_for_user(user_id)
    cart_items = linked_list.print_cart_items()

    if not cart_items:
        print("Your cart is empty. There are no items to remove.")
        return

    current_total = sum(item["price"] for item in cart_items.values())
    print(f"Current total price: {current_total}")

    while True:
        try:
            item_nums = input("Enter the numbers of the items to remove (e.g., 1,2,3) or 0 to stop: ")
            if item_nums == "0":
                break

            item_nums = [int(num.strip()) for num in item_nums.split(",")]

            for item_num in item_nums:
                item_name = get_item_by_number(item_num)
                if item_name is None:
                    continue

                node = linked_list.node_present_or_not(item_name)
                if node:
                    current_price = get_price(item_name)
                    max_quantity = node["quantity"]
                    quantity_to_remove = int(input(f"Enter quantity to remove for {item_name} (Current quantity: {max_quantity}): "))

                    if quantity_to_remove > max_quantity:
                        print(f"You only have {max_quantity} of {item_name}. Adjusting quantity to {max_quantity}.")
                        quantity_to_remove = max_quantity

                    if quantity_to_remove == max_quantity:
                        current_total -= node["price"]
                        linked_list.delete_node({item_name: node})
                        print(f"Removed all of {item_name}.")
                    else:
                        node["quantity"] -= quantity_to_remove
                        price_removed = current_price * quantity_to_remove
                        node["price"] -= price_removed
                        current_total -= price_removed
                        print(f"Removed {quantity_to_remove} of {item_name}. Remaining quantity: {node['quantity']}")

        except ValueError:
            print("Invalid input. Please enter valid item numbers and quantities.")


def get_cart_for_user(user_id):
    
    
    if user_id not in cart:
        cart[user_id] = LinkedList()  
    return cart[user_id]


def get_item_by_number(number):
    if 1 <= number <= len(Shopping):
        item_name = list(Shopping.keys())[number - 1]
        return item_name
    else:
        print("Invalid item number.")
        return None

def display_initial_menu(user_id):
    while True:
        print("\n Categories ")
        print("1. Display all available items")
        print("2. Display items in cart")
        print("3. Display total amount")
        print("4. Show flash sale items")
        print("5. Add items to cart")
        print("6. Remove items from cart")
        print("7. Set budget limit")
        print("8. Place Order")
        print("9. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            display_available_items()
        elif choice == "2":
            items = get_cart_for_user(user_id).print_cart_items()
            if items:
                df = pd.DataFrame.from_dict((items), orient="index")
                print("Items in your cart so far:")
                print(df)
            else:
                print("Your cart is empty.")
        elif choice == "3":
            total_price = sum(item["price"] for item in get_cart_for_user(user_id).print_cart_items().values())
            print(f"Total amount for items in your cart: {total_price}")
        elif choice == "4":
            display_flash_sale_items()
        elif choice == "5":
            add_items_to_cart(user_id)
        elif choice == "6":
            remove_items_from_cart(user_id)
        elif choice == "7":
            set_budget(user_id)
        elif choice == "8":
            place_order(user_id)
            break
        elif choice == "9":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter again.")


def place_order(user_id):
    cart_items = get_cart_for_user(user_id).print_cart_items()
    if not cart_items:
        print("Your cart is empty. Add items to your cart before placing an order.")
        return

    
    if (budget is not None and total_price < budget):
        order_id = random.randint(1000, 9999)
        total_price = sum(item["price"] for item in cart_items.values())
        print(f"Order placed successfully. Order ID: {order_id}")
        print(f"Total amount: {total_price}")
        print("Your order is confirmed!")

    elif(budget==None):
        order_id = random.randint(1000, 9999)
        total_price = sum(item["price"] for item in cart_items.values())
        print(f"Order placed successfully. Order ID: {order_id}")
        print(f"Total amount: {total_price}")
        print("Your order is confirmed!")

def get_valid_user_id():
    while True:
        user_id = input("Please enter your user ID to start shopping: ")

         
        if re.match(r"^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z0-9]+$", user_id):
            print("User ID accepted. You may start shopping!")
            return user_id
        else:
            print("Error: User ID must contain both alphabets and numbers. Please try again.")


user_id = get_valid_user_id()
Login_ids[user_id] = user_id
start_flash_sale()
display_initial_menu(user_id)
