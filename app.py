from flask import Flask, render_template, request, jsonify
import calculator
import math

app = Flask(__name__)

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

app.config["JSON_SORT_KEYS"] = False

# Maximum number of history entries to retain
MAX_HISTORY = 100

# Map frontend operation names to Python functions
OPERATIONS = {
    "add": calculator.add,
    "subtract": calculator.subtract,
    "multiply": calculator.multiply,
    "divide": calculator.divide,
    "modulus": calculator.modulus,
    "square": calculator.square,
    "cube": calculator.cube,
    "square_root": calculator.square_root,
    "cube_root": calculator.cube_root,
    "power": calculator.power,
    "percentage": calculator.percentage,
}

# Operations that require only one number
UNARY_OPERATIONS = {
    "square",
    "cube",
    "square_root",
    "cube_root",
}

# Symbols displayed in calculation history
OPERATION_SYMBOLS = {
    "add": "+",
    "subtract": "−",
    "multiply": "×",
    "divide": "÷",
    "modulus": "%",
    "power": "^",
}


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def parse_number(value, field_name="number"):
    """Convert a value to a valid finite number."""

    if isinstance(value, bool) or value is None:
        raise ValueError(f"{field_name} must be a valid number.")

    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError):
        raise ValueError(f"{field_name} must be a valid number.")

    if not math.isfinite(number):
        raise ValueError(f"{field_name} must be a finite number.")

    return number


def format_number(number):
    """Format numbers cleanly for the display and history."""

    if isinstance(number, bool):
        return str(number)

    if isinstance(number, (int, float)):
        if not math.isfinite(number):
            return str(number)

        if number == 0:
            return "0"

        if number.is_integer() if isinstance(number, float) else False:
            return str(int(number))

        return f"{number:.12g}"

    return str(number)


def make_history_entry(operation, a, b, result):
    """Create a readable calculation history entry."""

    first = format_number(a)
    answer = format_number(result)

    if operation in UNARY_OPERATIONS:
        names = {
            "square": "square",
            "cube": "cube",
            "square_root": "square root",
            "cube_root": "cube root",
        }

        return f"{names[operation]}({first}) = {answer}"

    second = format_number(b)

    if operation == "percentage":
        return f"{first}% of {second} = {answer}"

    symbol = OPERATION_SYMBOLS[operation]

    return f"{first} {symbol} {second} = {answer}"


def save_calculation(calculation):
    """Save a calculation and limit the history size."""

    calculator.save_history(calculation)

    # Keep only the most recent MAX_HISTORY entries.
    del calculator.history[:-MAX_HISTORY]


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# CALCULATION API
# --------------------------------------------------

@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Invalid request. Expected JSON data."
        }), 400

    operation = data.get("operation")

    if not isinstance(operation, str) or operation not in OPERATIONS:
        return jsonify({
            "success": False,
            "error": "Invalid operation selected."
        }), 400

    try:
        # Validate the first number.
        a = parse_number(data.get("a"), "First number")

        # Execute unary operations.
        if operation in UNARY_OPERATIONS:
            result = OPERATIONS[operation](a)

        else:
            # Binary operations require a second number.
            b = parse_number(data.get("b"), "Second number")

            result = OPERATIONS[operation](a, b)

        # Handle errors returned by calculator.py.
        if isinstance(result, str) and result.startswith("Error:"):
            return jsonify({
                "success": False,
                "error": result
            }), 400

        # Reject unsupported result types.
        if isinstance(result, bool) or not isinstance(
            result, (int, float)
        ):
            return jsonify({
                "success": False,
                "error": "The calculation returned an invalid result."
            }), 400

        # Reject infinity and NaN.
        if not math.isfinite(result):
            return jsonify({
                "success": False,
                "error": "The result is undefined or too large."
            }), 400

        # Convert integral floating-point results to integers.
        if isinstance(result, float) and result.is_integer():
            result = int(result)

        # Generate readable history.
        calculation = make_history_entry(
            operation,
            a,
            data.get("b"),
            result
        )

        save_calculation(calculation)

        return jsonify({
            "success": True,
            "result": result,
            "display_result": format_number(result),
            "calculation": calculation
        }), 200

    except (ValueError, TypeError, OverflowError) as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 400

    except ZeroDivisionError:
        return jsonify({
            "success": False,
            "error": "Cannot divide by zero."
        }), 400


# --------------------------------------------------
# GET CALCULATION HISTORY
# --------------------------------------------------

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify({
        "success": True,
        "history": calculator.history
    }), 200


# --------------------------------------------------
# CLEAR CALCULATION HISTORY
# --------------------------------------------------

@app.route("/api/history", methods=["DELETE"])
def clear_history():
    calculator.history.clear()

    return jsonify({
        "success": True,
        "message": "History cleared successfully.",
        "history": []
    }), 200


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "success": True,
        "message": "Calculator API is running.",
        "operations": list(OPERATIONS.keys())
    }), 200


# --------------------------------------------------
# ERROR HANDLERS
# --------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "The requested API endpoint was not found."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "This HTTP method is not supported for this endpoint."
    }), 405


# --------------------------------------------------
# START FLASK APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)

    