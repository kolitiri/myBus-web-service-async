# MyBus Web Service Async

This is an updated version of the MyBus web service that was initially designed using Flask.

Flask has now been replaced with aiohttp.

The API itself has not changed compared to the previous version, so the same requests apply as earlier.

# The service

This is an API that was created to support the [MyBus Garmin watch app](https://github.com/chris220688/garmin-myBus-app).

It acts as a proxy service between the Garmin application and TFL's endpoints.

Requests from the Garmin watch go through this service and their responses are filtered before they return to the watch app.

This way I can control the size of the responses and avoid crashing the watch application. (This is because the watch can only handle responses of limited size)

All the requests are forwarded to the TFL's unified API that can be found [here](https://api.tfl.gov.uk/)

# API Usage

Currently there are only two requests that are supported:

## Bus stops request

* **URL:** /stops

* **Method:** POST

* **Data**

```json
{
	"location": {
		"latitude": "51.492628",
		"longtitude": "-0.223060",
		"radius": "200",
		"stopTypes": "NaptanPublicBusCoachTram",
		"returnLines": "False"
	}
}
```

* **Sample Call:**
```
curl --header "Content-Type: application/json" --request POST --data @stops.json https://gmmybus-async.herokuapp.com/stops
```

## Bus predictions request

* **URL:** /predictions

* **Method:** POST

* **Data**

```json
{
	"stop": {
		"naptanId": "490004290L"
	}
}
```

* **Sample Call:**
```
curl --header "Content-Type: application/json" --request POST --data @predictions.json https://gmmybus-async.herokuapp.com/predictions
```

Alternatively, just load the **gmmybus.postman_collection.json**.

### Acknowledgements

This application is Powered by TfL Open Data and contains OS data © Crown copyright and database rights 2016

### Authors

Chris Liontos
