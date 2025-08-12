from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def temperature_converter():
    if request.method == "POST":
        try:
            # Get the value and unit from the form
            temperature = float(request.form.get("temperature"))
            unit = request.form.get("unit")
            
            # Perform the conversion
            if unit == "celsius":
                result = (temperature * 9/5) + 32
                output = f"{temperature}°C is {result:.2f}°F"
            elif unit == "fahrenheit":
                result = (temperature - 32) * 5/9
                output = f"{temperature}°F is {result:.2f}°C"
            else:
                output = "Invalid unit selected."
            
            return render_template("index.html", output=output, temperature=temperature, unit=unit)
        
        except (ValueError, TypeError):
            # Handle non-numeric input
            output = "Please enter a valid number."
            return render_template("index.html", output=output)
            
    # For GET requests, show the initial form with no result
    return render_template("index.html", output="")

if __name__ == "__main__":
    app.run(debug=True)