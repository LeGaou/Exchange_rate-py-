from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import requests

# Note: It's best practice to keep API keys outside of the source code
# For simplicity, keep it here but in a real-world app, you might
# load it from a configuration file or environment variable.
API_KEY = "ac60f1e030747f714e5d826f"
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/"

class Converter(BoxLayout):
    """
    The main widget for the currency converter application.
    """
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)

        # Input Widgets
        self.base_input = TextInput(
            hint_text="Base currency (e.g., USD)",
            multiline=False,
            size_hint_y=None,
            height=45,
            font_size='18sp'
        )
        self.amount_input = TextInput(
            hint_text="Amount",
            multiline=False,
            input_filter='float',
            size_hint_y=None,
            height=45,
            font_size='18sp'
        )
        self.targets_input = TextInput(
            hint_text="Target currencies (comma-separated, e.g., EUR,GBP)",
            multiline=False,
            size_hint_y=None,
            height=45,
            font_size='18sp'
        )

        # Button
        self.convert_button = Button(
            text="Convert",
            size_hint_y=None,
            height=55,
            background_color=(0.2, 0.6, 0.8, 1), # A nice blue color
            font_size='20sp',
            bold=True
        )
        self.convert_button.bind(on_press=self.start_conversion)

        # Result Display
        self.result_label = Label(
            text="",
            halign="left",
            valign="top",
            size_hint_y=None,
            text_size=(self.width - 40, None), # Set text_size for wrapping
            font_size='16sp'
        )
        self.result_label.bind(width=lambda *x: self.result_label.setter('text_size')(
            self.result_label, (self.result_label.width, None)))
        self.result_label.bind(texture_size=lambda *x: self.result_label.setter('height')(
            self.result_label, self.result_label.texture_size[1]))

        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.scroll_view.add_widget(self.result_label)

        # Add widgets to the layout
        self.add_widget(Label(text="Currency Converter 💲", size_hint_y=None, height=40, font_size='24sp'))
        self.add_widget(self.base_input)
        self.add_widget(self.amount_input)
        self.add_widget(self.targets_input)
        self.add_widget(self.convert_button)
        self.add_widget(self.scroll_view)

    def start_conversion(self, instance):
        """Starts the currency conversion process in a separate thread."""
        self.result_label.text = "🔄 Fetching exchange rates..."
        self.convert_button.disabled = True
        Clock.schedule_once(self.convert_currency, 0)

    def convert_currency(self, dt):
        """Fetches exchange rates and performs the conversion."""
        base = self.base_input.text.strip().upper()
        targets = [t.strip().upper() for t in self.targets_input.text.strip().split(",") if t.strip()]

        # Basic input validation
        try:
            amount = float(self.amount_input.text.strip())
        except ValueError:
            self.result_label.text = "❌ Error: Please enter a valid number for the amount."
            self.convert_button.disabled = False
            return
        if not base:
            self.result_label.text = "❌ Error: Please enter a base currency."
            self.convert_button.disabled = False
            return

        # Make the API request
        try:
            response = requests.get(f"{API_URL}{base}", timeout=10)
            response.raise_for_status()  # This will raise an exception for bad status codes
            data = response.json()

            if data.get("result") == "error":
                error_type = data.get("error-type", "Unknown error")
                self.result_label.text = f"❌ API Error: {error_type.replace('_', ' ').title()}"
                self.convert_button.disabled = False
                return

            rates = data["conversion_rates"]
            output_lines = []

            # Convert to requested targets
            if targets:
                for target in targets:
                    if target in rates:
                        converted = amount * rates[target]
                        output_lines.append(f"💰 {amount:,.2f} {base} = {converted:,.2f} {target}")
                    else:
                        output_lines.append(f"❌ Target currency '{target}' not found.")

            # Add top 5 rates for context
            output_lines.append("\n---")
            output_lines.append("💹 Top 5 Exchange Rates for 1 " + base + ":")
            top_5 = sorted(rates.items(), key=lambda item: item[1], reverse=True)[:5]
            for currency, rate in top_5:
                output_lines.append(f"  • {rate:,.2f} {currency}")

            self.result_label.text = "\n".join(output_lines)

        except requests.exceptions.RequestException as e:
            self.result_label.text = f"❌ Network Error: Could not connect to API.\nCheck your internet connection. ({e})"
        except Exception as e:
            self.result_label.text = f"❌ An unexpected error occurred: {e}"
        finally:
            self.convert_button.disabled = False

class CurrencyConverterApp(App):
    """The Kivy application class."""
    def build(self):
        self.title = "Currency Converter"
        return Converter()

if __name__ == "__main__":
    CurrencyConverterApp().run()
