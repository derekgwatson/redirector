from flask import Flask, request, render_template_string
import requests
from math import radians, cos, sin, sqrt, atan2

app = Flask(__name__)

# Store details
STORES = {
    "Tweed": {
        "lat": -28.2002826,
        "lon": 153.5435657,
        "url": "https://watsonblinds.com.au/secure-payment-tweed-heads"
    },
    "Wollongong": {
        "lat": -34.3818936,
        "lon": 150.8952402,
        "url": "https://watsonblinds.com.au/secure-payment-wollongong"
    },
    "Wagga": {
        "lat": -35.1248811,
        "lon": 147.3781942,
        "url": "https://watsonblinds.com.au/secure-payment-wagga"
    },
    "Shoalhaven": {
        "lat": -34.8776065,
        "lon": 150.6027014,
        "url": "https://watsonblinds.com.au/secure-payment-shoalhaven"
    },
    "Canberra": {
        "lat": -35.3238619,
        "lon": 149.1780576,
        "url": "https://watsonblinds.com.au/secure-payment"
    },
    "Batemans Bay": {
        "lat": -35.7097644,
        "lon": 150.1771133,
        "url": "https://watsonblinds.com.au/secure-payment-bb"
    }
}


def get_user_location(ip):
    try:
        res = requests.get(f"https://ipinfo.io/{ip}/json")
        res.raise_for_status()
        loc = res.json().get("loc")  # e.g. "34.4203,150.8931"
        if loc:
            lat, lon = map(float, loc.split(","))
            print(f"Geo lookup for {ip}: lat={lat}, lon={lon}")
            return lat, lon
    except Exception as e:
        print(f"ipinfo lookup failed: {e}")
    return None, None


def haversine(lat1, lon1, lat2, lon2):
    # Haversine formula to calculate distance between two lat/lon points
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def find_nearest_store(lat, lon):
    if lat is None or lon is None:
        return None
    closest = None
    min_distance = float('inf')
    for store, data in STORES.items():
        dist = haversine(lat, lon, data['lat'], data['lon'])
        if dist < min_distance:
            min_distance = dist
            closest = store
    return closest


@app.route("/", methods=["GET"])
def home():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    lat_param = request.args.get("lat")
    lon_param = request.args.get("lon")
    if lat_param and lon_param:
        try:
            lat = float(lat_param)
            lon = float(lon_param)
        except ValueError:
            lat, lon = get_user_location(ip)
    else:
        lat, lon = get_user_location(ip)

    nearest_store = find_nearest_store(lat, lon)
    print("User IP:", ip)
    print("User location:", lat, lon)
    print("Nearest store:", nearest_store)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Store Redirect</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                background-color: #f1f3f5;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

        header {
            background-color: #4CAF50;
            color: white;
            padding: 16px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }
        
        h2 {
            font-size: 26px;
            margin: 0;
        }
        
        .lead {
            font-size: 16px;
            font-weight: 400;
            color: #e0f2e9;
        }

            h1 {
                font-size: 36px;
                margin: 0;
            }

            .btn {
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
            }

            .btn-primary {
                background-color: #007bff;
                color: white !important;  /* <-- force white text */
                border: none;
            }

            .btn-primary:hover {
                background-color: #0056b3;
                color: white !important;
            }

            .btn-outline-secondary {
                background-color: #f8f9fa;
                color: #007bff;
                border: 1px solid #007bff;
            }

            .btn-outline-secondary:hover {
                background-color: #007bff;
                color: white;
            }

            .location-message {
                background-color: #d1ecf1;
                color: #0c5460;
                border-radius: 5px;
                padding: 10px;
                margin: 20px auto;
                font-size: 16px;
                max-width: 600px;
            }

            .location-message a {
                color: #0056b3;
                text-decoration: none;
                font-weight: bold;
            }

            .location-message a:hover {
                text-decoration: underline;
            }

            .store-list {
                margin: 20px auto;
                padding: 0 1rem;
                width: 100%;
                max-width: 500px;
            }

            .store-list a {
                display: block;
                width: 100%;
                text-align: center;
                padding: 12px;
                margin: 6px 0;
                background-color: white;
                border-radius: 6px;
                text-decoration: none;
                color: #212529;
                border: 1px solid #dee2e6;
                transition: background-color 0.2s ease;
            }
            
            .store-list a:hover {
                background-color: #e9ecef;
            }

        </style>
    </head>
    <body>
        <header>
            <h2 class="mb-1">Let's get started</h2>
            <p class="lead mb-0">Select your store so we can send you to the right payment page.</p>
        </header>

        <div class="container text-center mt-4">
            <button class="btn btn-outline-secondary mb-4" onclick="detectLocation()">Use my current location</button>

            {% if nearest_store %}
                <div class="location-message">
                    Looks like you're near <strong>{{ nearest_store }}</strong> — or at least that's our best guess!
                    <a href="{{ stores[nearest_store]['url'] }}" class="btn btn-primary btn-sm ms-2">Go to {{ nearest_store }}</a>
                </div>
                <p class="mt-4">Or choose another store:</p>
            {% endif %}

            <div class="store-list">
                {% for name, info in stores.items() %}
                    {% if name != nearest_store %}
                        <a href="{{ info['url'] }}">{{ name }}</a>
                    {% endif %}
                {% endfor %}
            </div>
        </div>

        <script>
            function detectLocation() {
                if (!navigator.geolocation) {
                    alert("Geolocation is not supported by your browser.");
                    return;
                }

                navigator.geolocation.getCurrentPosition(function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const newUrl = new URL(window.location.href);
                    newUrl.searchParams.set("lat", lat);
                    newUrl.searchParams.set("lon", lon);
                    window.location.href = newUrl.toString();
                }, function(error) {
                    alert("Unable to retrieve your location.");
                });
            }
        </script>
    </body>
    </html>
    """

    return render_template_string(html, stores=STORES, nearest_store=nearest_store)


@app.route("/rework")
def rework():
    """Staff rework form selector - remembers their store choice."""
    return app.send_static_file('rework.html')


if __name__ == "__main__":
    app.run(debug=True)
