import math

# ================= BASIC OPERATIONS =================

def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        return "Error: can't divide by zero."
    return a / b


def modulus(a, b):
    if b == 0:
        return "Error: can't perform modulus by zero."
    return a % b


# ================= POWER AND ROOT OPERATIONS =================

def square(a):
    return a ** 2


def cube(a):
    return a ** 3


def square_root(a):
    if a < 0:
        return "Error: There is no real square root of a negative number."
    return math.sqrt(a)


def cube_root(a):
    return math.cbrt(a)


def power(a, b):
    return a ** b


# ================= OTHER OPERATIONS =================

def percentage(a, b):
    return (a / 100) * b


# ================= HISTORY =================

history = []


def save_history(calculation):
    history.append(calculation)


def clear_history():
    history.clear()


# ================= TERMINAL CALCULATOR =================

def main():

    print("==== CALCULATOR ====")

    while True:

        print("\nChoose an operation:")
        print("1. Addition")
        print("2. Subtraction")
        print("3. Multiply")
        print("4. Divide")
        print("5. Modulus")
        print("6. Square")
        print("7. Cube")
        print("8. Square root")
        print("9. Cube root")
        print("10. Power")
        print("11. Percentage")
        print("12. View history")
        print("13. Clear history")
        print("14. Exit")

        choice = input("Enter your choice (1-14): ")

        if choice == "14":
            print("Thank you for using the calculator!")
            break

        # ================= TWO-NUMBER OPERATIONS =================

        if choice in ["1", "2", "3", "4", "5", "10"]:

            try:
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))

                if choice == "1":
                    result = add(num1, num2)
                    operation = "+"

                elif choice == "2":
                    result = subtract(num1, num2)
                    operation = "-"

                elif choice == "3":
                    result = multiply(num1, num2)
                    operation = "*"

                elif choice == "4":
                    result = divide(num1, num2)
                    operation = "/"

                elif choice == "5":
                    result = modulus(num1, num2)
                    operation = "%"

                else:
                    result = power(num1, num2)
                    operation = "^"

                calculation = f"{num1} {operation} {num2} = {result}"
                save_history(calculation)

                print("Result:", result)

            except ValueError:
                print("Invalid input. Please enter valid numbers.")

            except OverflowError:
                print("Error: The result is too large.")

        # ================= ONE-NUMBER OPERATIONS =================

        elif choice in ["6", "7", "8", "9"]:

            try:
                num = float(input("Enter your number: "))

                if choice == "6":
                    result = square(num)
                    operation = "square"

                elif choice == "7":
                    result = cube(num)
                    operation = "cube"

                elif choice == "8":
                    result = square_root(num)
                    operation = "square_root"

                else:
                    result = cube_root(num)
                    operation = "cube_root"

                calculation = f"{operation}({num}) = {result}"
                save_history(calculation)

                print("Result:", result)

            except ValueError:
                print("Invalid input. Please enter a valid number.")

            except OverflowError:
                print("Error: The result is too large.")

        # ================= PERCENTAGE =================

        elif choice == "11":

            try:
                percentage_value = float(input("Enter percentage: "))
                number = float(input("Enter number: "))

                result = percentage(percentage_value, number)

                calculation = (
                    f"{percentage_value}% of {number} = {result}"
                )

                save_history(calculation)

                print("Result:", result)

            except ValueError:
                print("Invalid input. Please enter valid numbers.")

        # ================= VIEW HISTORY =================

        elif choice == "12":

            if not history:
                print("No calculation history available.")

            else:
                print("\n===== CALCULATION HISTORY =====")

                for index, calculation in enumerate(history, start=1):
                    print(f"{index}. {calculation}")

        # ================= CLEAR HISTORY =================

        elif choice == "13":

            if not history:
                print("History is already empty.")

            else:
                clear_history()
                print("Calculation history has been cleared.")

        # ================= INVALID CHOICE =================

        else:
            print("Invalid choice. Please select between 1 and 14.")


# ================= RUN TERMINAL CALCULATOR =================

if __name__ == "__main__":
    main()

    